import logging
import mimetypes
import os
import re
import shutil
import subprocess
import uuid
from pathlib import Path
from typing import Optional
import requests
from django.conf import settings

from ..exceptions import SAPConnectionError, SAPDataError, SAPValidationError
from ..hana.connection import HanaConnection
from .auth import ServiceLayerSession

logger = logging.getLogger(__name__)


class AttachmentWriter:
    """Attachment Writer for SAP Service Layer Attachments2 endpoint"""

    def __init__(self, context):
        self.context = context
        self.sl_config = context.service_layer

    def _get_session_cookies(self):
        """Get authenticated session cookies from Service Layer"""
        try:
            session = ServiceLayerSession(self.sl_config)
            return session.login()
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Failed to connect to SAP Service Layer: {e}")
            raise SAPConnectionError("Unable to connect to SAP Service Layer")
        except requests.exceptions.Timeout as e:
            logger.error(f"SAP Service Layer connection timeout: {e}")
            raise SAPConnectionError("SAP Service Layer connection timeout")
        except requests.exceptions.HTTPError as e:
            logger.error(f"SAP Service Layer authentication failed: {e}")
            raise SAPConnectionError("SAP Service Layer authentication failed")

    def _get_attachment_source_path(self, cookies=None) -> str:
        """
        Read SAP's configured attachment path.

        Multipart upload is preferred. This path is used only as a fallback for
        SAP systems where Service Layer cannot resolve the attachment-folder
        mount, but the backend can write to the same Windows/shared folder.
        """
        hana_config = getattr(self.context, "hana", None)
        if hana_config:
            connection = HanaConnection(hana_config)
            conn = None
            cursor = None
            try:
                conn = connection.connect()
                cursor = conn.cursor()
                cursor.execute(
                    f'SELECT "AttachPath" FROM "{connection.schema}"."OADP"'
                )
                row = cursor.fetchone()
                if row and row[0]:
                    return str(row[0]).strip()
            except Exception as exc:
                logger.warning("Failed to read SAP attachment path from OADP: %s", exc)
            finally:
                if cursor:
                    try:
                        cursor.close()
                    except Exception:
                        pass
                if conn:
                    try:
                        conn.close()
                    except Exception:
                        pass

        if cookies is None:
            cookies = self._get_session_cookies()
        url = (
            f"{self.sl_config['base_url']}/b1s/v2/Attachments2"
            "?$top=1&$select=Attachments2_Lines"
        )
        try:
            response = requests.get(url, cookies=cookies, timeout=30, verify=False)
            if response.status_code == 200:
                data = response.json()
                entries = data.get("value", [])
                if entries:
                    lines = entries[0].get("Attachments2_Lines", [])
                    if lines and lines[0].get("SourcePath"):
                        return str(lines[0]["SourcePath"]).strip()
        except Exception as exc:
            logger.warning("Failed to read SAP attachment path from Attachments2: %s", exc)
        return ""

    @staticmethod
    def _safe_sap_filename(filename: str) -> str:
        """Return an extension-less filename that is safe for SAP Attachments2."""
        stem = Path(filename).stem or "attachment"
        stem = re.sub(r"[^A-Za-z0-9._ -]+", "_", stem).strip(" ._")
        if not stem:
            stem = "attachment"
        return f"{stem[:80]}_{uuid.uuid4().hex[:8]}"

    @staticmethod
    def _is_attachment_folder_error(error_msg: str, response_text: str = "") -> bool:
        value = f"{error_msg} {response_text}".lower()
        return (
            "-43" in value
            or "linux mount point" in value
            or "attachmentsfolderpath" in value
            or "internal error (-43)" in value
        )

    def _get_direct_copy_path(self, sap_source_path: str) -> str:
        direct_copy_paths = getattr(settings, "SAP_ATTACHMENT_DIRECT_COPY_PATHS", {})
        company_code = getattr(self.context, "company_code", "").upper()
        configured_path = direct_copy_paths.get(company_code) if company_code else ""
        return (configured_path or sap_source_path or "").strip()

    def _get_direct_copy_credentials(self) -> tuple[str, str]:
        credentials = getattr(settings, "SAP_ATTACHMENT_DIRECT_COPY_CREDENTIALS", {})
        company_code = getattr(self.context, "company_code", "").upper()
        company_credentials = credentials.get(company_code, {}) if company_code else {}
        return (
            (company_credentials.get("username") or "").strip(),
            company_credentials.get("password") or "",
        )

    def _resolve_attachment_paths(self, sap_source_path: str) -> tuple[str, str]:
        sap_path = os.path.normpath(sap_source_path)
        copy_path = os.path.normpath(self._get_direct_copy_path(sap_source_path))
        return sap_path, copy_path

    @staticmethod
    def _unc_share_root(path: str) -> str:
        match = re.match(r"^(\\\\[^\\]+\\[^\\]+)", path)
        return match.group(1) if match else ""

    def _ensure_direct_copy_path_access(self, copy_path: str) -> None:
        if os.path.isdir(copy_path):
            return

        share_root = self._unc_share_root(copy_path)
        if not share_root or os.name != "nt":
            return

        username, password = self._get_direct_copy_credentials()
        if not username or not password:
            return

        command = [
            "net",
            "use",
            share_root,
            password,
            f"/user:{username}",
            "/persistent:no",
        ]
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
        if result.returncode == 0 or os.path.isdir(copy_path):
            return

        message = (result.stderr or result.stdout or "").strip()
        raise SAPValidationError(
            "SAP attachment direct-copy share login failed for "
            f"'{share_root}' as '{username}': {message}"
        )

    def _upload_from_accessible_source_path(
        self,
        file_path: str,
        filename: str,
        cookies,
        url: str,
        original_error: str,
    ) -> dict:
        """
        Fallback for SAP systems whose Service Layer cannot multipart-copy files.

        This is intentionally stricter than the old metadata fallback: it first
        copies the actual file to SAP's configured attachment folder, then creates
        the Attachments2 metadata row. If the folder is not accessible from the
        backend, we fail with a useful error instead of creating an SAP row that
        points at a missing file.
        """
        source_path = self._get_attachment_source_path(cookies=cookies)
        if not source_path:
            raise SAPValidationError(
                "SAP attachment upload failed because Service Layer cannot resolve "
                f"the attachment folder ({original_error}), and no SAP AttachPath "
                "could be read from OADP."
            )

        sap_source_path, copy_path = self._resolve_attachment_paths(source_path)
        self._ensure_direct_copy_path_access(copy_path)
        if not os.path.isdir(copy_path):
            raise SAPValidationError(
                "SAP attachment upload failed because Service Layer cannot copy the "
                f"file ({original_error}). SAP AttachPath is '{source_path}', but "
                f"the backend copy path '{copy_path}' is not accessible from the "
                "backend host. Configure the Service Layer attachment-folder mount, "
                "run the backend where that path exists, or set "
                "SAP_ATTACHMENT_DIRECT_COPY_PATH for this company to a writable "
                "network/local path that maps to the SAP attachment folder."
            )

        extension = Path(filename).suffix.lstrip(".") or Path(file_path).suffix.lstrip(".")
        sap_file_stem = self._safe_sap_filename(filename)
        sap_filename = f"{sap_file_stem}.{extension}" if extension else sap_file_stem
        target_path = os.path.join(copy_path, sap_filename)

        try:
            shutil.copyfile(file_path, target_path)
        except OSError as exc:
            raise SAPValidationError(
                "SAP attachment upload failed because the backend could not copy "
                f"the file into backend copy path '{copy_path}': {exc}"
            ) from exc

        payload = {
            "Attachments2_Lines": [
                {
                    "SourcePath": sap_source_path,
                    "FileName": sap_file_stem,
                    "FileExtension": extension,
                    "Override": "tYES",
                    "CopyToTargetDoc": "tYES",
                }
            ]
        }
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(
                url,
                json=payload,
                cookies=cookies,
                headers=headers,
                timeout=30,
                verify=False,
            )
        except Exception:
            try:
                os.unlink(target_path)
            except OSError:
                pass
            raise

        if response.status_code == 201:
            result = response.json()
            logger.info(
                "Attachment copied to SAP AttachPath and registered. "
                "AbsoluteEntry: %s",
                result.get("AbsoluteEntry"),
            )
            return result

        try:
            os.unlink(target_path)
        except OSError:
            pass
        error_msg = self._extract_error_message(response)
        raise SAPValidationError(
            "SAP attachment upload failed after copying the file into "
            f"backend copy path '{copy_path}': {error_msg}"
        )

    def _add_line_from_accessible_source_path(
        self,
        absolute_entry: int,
        file_path: str,
        filename: str,
        cookies,
        patch_url: str,
        original_error: str,
    ) -> dict:
        """
        Add a line to an existing Attachments2 entry after copying the file to
        an attachment folder that the backend can access.
        """
        get_response = requests.get(
            patch_url,
            cookies=cookies,
            timeout=30,
            verify=False,
        )
        if get_response.status_code != 200:
            error_msg = self._extract_error_message(get_response)
            raise SAPDataError(f"Failed to get existing attachment entry: {error_msg}")

        existing_data = get_response.json()
        existing_lines = existing_data.get("Attachments2_Lines", [])
        source_path = ""
        if existing_lines:
            source_path = existing_lines[0].get("SourcePath") or ""
        if not source_path:
            source_path = self._get_attachment_source_path(cookies=cookies)
        if not source_path:
            raise SAPValidationError(
                "SAP attachment upload failed because Service Layer cannot resolve "
                f"the attachment folder ({original_error}), and no SAP AttachPath "
                "could be read from OADP."
            )

        sap_source_path, copy_path = self._resolve_attachment_paths(source_path)
        self._ensure_direct_copy_path_access(copy_path)
        if not os.path.isdir(copy_path):
            raise SAPValidationError(
                "SAP attachment upload failed because Service Layer cannot copy the "
                f"file ({original_error}). SAP AttachPath is '{source_path}', but "
                f"the backend copy path '{copy_path}' is not accessible from the "
                "backend host. Configure the Service Layer attachment-folder mount, "
                "run the backend where that path exists, or set "
                "SAP_ATTACHMENT_DIRECT_COPY_PATH for this company to a writable "
                "network/local path that maps to the SAP attachment folder."
            )

        extension = Path(filename).suffix.lstrip(".") or Path(file_path).suffix.lstrip(".")
        sap_file_stem = self._safe_sap_filename(filename)
        sap_filename = f"{sap_file_stem}.{extension}" if extension else sap_file_stem
        target_path = os.path.join(copy_path, sap_filename)

        try:
            shutil.copyfile(file_path, target_path)
            existing_lines.append(
                {
                    "SourcePath": sap_source_path,
                    "FileName": sap_file_stem,
                    "FileExtension": extension,
                    "Override": "tYES",
                    "CopyToTargetDoc": "tYES",
                }
            )
            response = requests.patch(
                patch_url,
                json={"Attachments2_Lines": existing_lines},
                cookies=cookies,
                headers={"Content-Type": "application/json"},
                timeout=30,
                verify=False,
            )
        except Exception:
            try:
                os.unlink(target_path)
            except OSError:
                pass
            raise

        if response.status_code in (200, 204):
            logger.info("Added copied attachment line to Attachments2(%s)", absolute_entry)
            return {"AbsoluteEntry": absolute_entry, "FileName": filename}

        try:
            os.unlink(target_path)
        except OSError:
            pass
        error_msg = self._extract_error_message(response)
        raise SAPValidationError(
            "SAP attachment upload failed after copying the file into "
            f"backend copy path '{copy_path}': {error_msg}"
        )

    def upload(self, file_path: str, filename: str) -> dict:
        """
        Upload a file to SAP Attachments2 endpoint.
        Uses multipart upload so SAP receives and copies the actual file bytes.

        Args:
            file_path: Absolute path to the file on disk (from FileField.path)
            filename: Original filename to use in the upload

        Returns:
            dict: SAP response containing AbsoluteEntry
        """
        cookies = self._get_session_cookies()
        url = f"{self.sl_config['base_url']}/b1s/v2/Attachments2"

        try:
            content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
            with open(file_path, "rb") as f:
                files = {
                    "files": (filename, f, content_type)
                }
                response = requests.post(
                    url,
                    files=files,
                    cookies=cookies,
                    timeout=60,
                    verify=False
                )

            if response.status_code == 201:
                result = response.json()
                logger.info(
                    f"Attachment uploaded to SAP. "
                    f"AbsoluteEntry: {result.get('AbsoluteEntry')}"
                )
                return result

            if response.status_code == 400:
                error_msg = self._extract_error_message(response)
                if self._is_attachment_folder_error(error_msg, response.text):
                    logger.warning(
                        "Multipart attachment upload failed with SAP folder error; "
                        "trying accessible source-path fallback: %s",
                        error_msg,
                    )
                    return self._upload_from_accessible_source_path(
                        file_path=file_path,
                        filename=filename,
                        cookies=cookies,
                        url=url,
                        original_error=error_msg,
                    )
                logger.error(f"SAP validation error uploading attachment: {error_msg}")
                raise SAPValidationError(error_msg)

            if response.status_code in (401, 403):
                logger.error("SAP authentication/authorization error during attachment upload")
                raise SAPConnectionError("SAP authentication failed")

            error_msg = self._extract_error_message(response)
            logger.error(f"SAP error uploading attachment: {error_msg}")
            raise SAPDataError(f"Failed to upload attachment: {error_msg}")

        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error uploading attachment: {e}")
            raise SAPConnectionError("Unable to connect to SAP Service Layer")
        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout uploading attachment: {e}")
            raise SAPConnectionError("SAP Service Layer request timeout")
        except (SAPConnectionError, SAPDataError, SAPValidationError):
            raise
        except Exception as e:
            logger.error(f"Unexpected error uploading attachment: {e}")
            raise SAPDataError(f"Unexpected error: {str(e)}")

    def get_document_attachment_entry(self, doc_entry: int) -> Optional[int]:
        """
        Get the existing AttachmentEntry from a GRPO document.

        Returns:
            The AttachmentEntry (AbsoluteEntry) if one exists, else None.
        """
        cookies = self._get_session_cookies()
        url = (
            f"{self.sl_config['base_url']}/b1s/v2"
            f"/PurchaseDeliveryNotes({doc_entry})"
            f"?$select=AttachmentEntry"
        )

        try:
            response = requests.get(
                url, cookies=cookies, timeout=30, verify=False
            )
            if response.status_code == 200:
                data = response.json()
                entry = data.get("AttachmentEntry")
                if entry and entry > 0:
                    return entry
        except Exception as e:
            logger.warning(
                f"Failed to get AttachmentEntry for DocEntry {doc_entry}: {e}"
            )
        return None

    def add_line_to_existing_attachment(
        self, absolute_entry: int, file_path: str, filename: str
    ) -> dict:
        """
        Add a new file line to an existing Attachments2 entry using multipart
        upload so SAP receives and copies the actual file bytes.

        Args:
            absolute_entry: The existing Attachments2 AbsoluteEntry
            file_path: Path to the file on disk
            filename: Original filename

        Returns:
            dict: Updated Attachments2 response
        """
        cookies = self._get_session_cookies()

        patch_url = (
            f"{self.sl_config['base_url']}/b1s/v2"
            f"/Attachments2({absolute_entry})"
        )

        try:
            content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
            with open(file_path, "rb") as f:
                files = {"files": (filename, f, content_type)}
                response = requests.patch(
                    patch_url,
                    files=files,
                    cookies=cookies,
                    timeout=60,
                    verify=False,
                )

            if response.status_code in (200, 204):
                logger.info(
                    f"Added line '{filename}' to Attachments2({absolute_entry})"
                )
                return {
                    "AbsoluteEntry": absolute_entry,
                    "FileName": filename,
                }

            if response.status_code == 400:
                error_msg = self._extract_error_message(response)
                if self._is_attachment_folder_error(error_msg, response.text):
                    logger.warning(
                        "Multipart attachment line upload failed with SAP folder "
                        "error; trying accessible source-path fallback: %s",
                        error_msg,
                    )
                    return self._add_line_from_accessible_source_path(
                        absolute_entry=absolute_entry,
                        file_path=file_path,
                        filename=filename,
                        cookies=cookies,
                        patch_url=patch_url,
                        original_error=error_msg,
                    )
                logger.error(f"SAP validation error adding attachment line: {error_msg}")
                raise SAPValidationError(error_msg)

            error_msg = self._extract_error_message(response)
            raise SAPDataError(f"Failed to add attachment line: {error_msg}")

        except (SAPConnectionError, SAPDataError, SAPValidationError):
            raise
        except Exception as e:
            logger.error(f"Unexpected error adding attachment line: {e}")
            raise SAPDataError(f"Unexpected error: {str(e)}")

    def link_to_document(self, doc_entry: int, absolute_entry: int) -> dict:
        """
        Link an uploaded attachment to a GRPO document (PurchaseDeliveryNotes)
        by PATCHing the AttachmentEntry field.

        Args:
            doc_entry: The GRPO's DocEntry in SAP
            absolute_entry: The AbsoluteEntry from Attachments2 upload

        Returns:
            dict: Updated document response from SAP
        """
        cookies = self._get_session_cookies()
        url = (
            f"{self.sl_config['base_url']}/b1s/v2"
            f"/PurchaseDeliveryNotes({doc_entry})"
        )

        payload = {
            "AttachmentEntry": absolute_entry
        }

        headers = {
            "Content-Type": "application/json",
        }

        try:
            response = requests.patch(
                url,
                json=payload,
                cookies=cookies,
                headers=headers,
                timeout=30,
                verify=False
            )

            if response.status_code in (200, 204):
                logger.info(
                    f"Attachment {absolute_entry} linked to GRPO DocEntry {doc_entry}"
                )
                if response.status_code == 204:
                    return {"DocEntry": doc_entry, "AttachmentEntry": absolute_entry}
                return response.json()

            if response.status_code == 400:
                error_msg = self._extract_error_message(response)
                logger.error(f"SAP validation error linking attachment: {error_msg}")
                raise SAPValidationError(error_msg)

            if response.status_code in (401, 403):
                logger.error("SAP auth error linking attachment")
                raise SAPConnectionError("SAP authentication failed")

            error_msg = self._extract_error_message(response)
            logger.error(f"SAP error linking attachment: {error_msg}")
            raise SAPDataError(f"Failed to link attachment: {error_msg}")

        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error linking attachment: {e}")
            raise SAPConnectionError("Unable to connect to SAP Service Layer")
        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout linking attachment: {e}")
            raise SAPConnectionError("SAP Service Layer request timeout")
        except (SAPConnectionError, SAPDataError, SAPValidationError):
            raise
        except Exception as e:
            logger.error(f"Unexpected error linking attachment: {e}")
            raise SAPDataError(f"Unexpected error: {str(e)}")

    def _extract_error_message(self, response) -> str:
        """Extract error message from SAP response"""
        try:
            error_data = response.json()
            if "error" in error_data:
                message = error_data["error"].get("message")
                if isinstance(message, dict):
                    return message.get("value", str(error_data))
                if message:
                    return str(message)
                return str(error_data)
            return str(error_data)
        except Exception:
            return response.text or f"HTTP {response.status_code}"
