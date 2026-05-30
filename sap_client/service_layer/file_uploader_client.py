import logging
import mimetypes
from typing import Any

import requests
from django.conf import settings

from ..exceptions import SAPConnectionError, SAPDataError, SAPValidationError

logger = logging.getLogger(__name__)


class FileUploaderClient:
    """Client for the SAP-server file uploader service."""

    def __init__(self, company_code: str):
        self.company_code = (company_code or "").upper()
        self.base_url = (
            getattr(settings, "SAP_FILE_UPLOADER_BASE_URL", "") or ""
        ).rstrip("/")
        self.api_key = getattr(settings, "SAP_FILE_UPLOADER_API_KEY", "") or ""
        self.timeout = getattr(settings, "SAP_FILE_UPLOADER_TIMEOUT_SECONDS", 120)
        folder_ids = getattr(settings, "SAP_FILE_UPLOADER_FOLDER_IDS", {}) or {}
        self.folder_id = folder_ids.get(self.company_code)

    @classmethod
    def is_enabled(cls) -> bool:
        return bool(getattr(settings, "SAP_FILE_UPLOADER_ENABLED", False))

    def _headers(self) -> dict[str, str]:
        return {
            "X-API-Key": self.api_key,
            "X-Uploader": "factory_app_v2",
        }

    def _validate_config(self) -> None:
        missing = []
        if not self.base_url:
            missing.append("SAP_FILE_UPLOADER_BASE_URL")
        if not self.api_key:
            missing.append("SAP_FILE_UPLOADER_API_KEY")
        if not self.folder_id:
            missing.append(f"SAP_FILE_UPLOADER_FOLDER_ID_{self.company_code}")
        if missing:
            raise SAPValidationError(
                "SAP file uploader is enabled but missing config: "
                + ", ".join(missing)
            )

    def upload(self, file_path: str, filename: str) -> dict[str, Any]:
        self._validate_config()
        content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        url = f"{self.base_url}/upload"

        try:
            with open(file_path, "rb") as handle:
                response = requests.post(
                    url,
                    data={"folder_id": self.folder_id},
                    files={"files": (filename, handle, content_type)},
                    headers=self._headers(),
                    timeout=self.timeout,
                )
        except requests.exceptions.ConnectionError as exc:
            logger.error("Could not connect to SAP file uploader: %s", exc)
            raise SAPConnectionError("Unable to connect to SAP file uploader") from exc
        except requests.exceptions.Timeout as exc:
            logger.error("SAP file uploader request timed out: %s", exc)
            raise SAPConnectionError("SAP file uploader request timeout") from exc

        if response.status_code in (401, 403):
            raise SAPConnectionError("SAP file uploader authentication failed")

        if response.status_code >= 400:
            raise SAPDataError(
                "SAP file uploader upload failed: "
                f"{self._extract_error_message(response)}"
            )

        try:
            payload = response.json()
        except ValueError as exc:
            raise SAPDataError("SAP file uploader returned invalid JSON") from exc

        files = (payload.get("data") or {}).get("files") or []
        if not files:
            failures = (payload.get("data") or {}).get("failures") or []
            raise SAPDataError(
                "SAP file uploader did not save the attachment"
                + (f": {failures}" if failures else "")
            )

        return files[0]

    def delete(self, file_id: int) -> None:
        if not file_id:
            return
        self._validate_config()
        try:
            response = requests.delete(
                f"{self.base_url}/files/{file_id}",
                headers=self._headers(),
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            logger.warning("Could not delete orphan uploader file %s: %s", file_id, exc)
            return

        if response.status_code >= 400:
            logger.warning(
                "Could not delete orphan uploader file %s: %s",
                file_id,
                self._extract_error_message(response),
            )

    @staticmethod
    def _extract_error_message(response) -> str:
        try:
            payload = response.json()
            error = payload.get("error") if isinstance(payload, dict) else None
            if isinstance(error, dict):
                return error.get("message") or str(error)
            return str(payload)
        except Exception:
            return response.text or f"HTTP {response.status_code}"
