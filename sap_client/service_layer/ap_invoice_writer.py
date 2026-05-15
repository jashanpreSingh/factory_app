import logging
from decimal import Decimal

import requests

from ..exceptions import SAPConnectionError, SAPDataError, SAPValidationError
from .auth import ServiceLayerSession

logger = logging.getLogger(__name__)


def _convert_decimals(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, dict):
        return {key: _convert_decimals(value) for key, value in obj.items()}
    if isinstance(obj, list):
        return [_convert_decimals(value) for value in obj]
    return obj


class APInvoiceWriter:
    """A/P Invoice writer for SAP Business One Service Layer."""

    def __init__(self, context):
        self.context = context
        self.sl_config = context.service_layer

    def _get_session_cookies(self):
        try:
            session = ServiceLayerSession(self.sl_config)
            return session.login()
        except requests.exceptions.ConnectionError as exc:
            logger.error("Failed to connect to SAP Service Layer: %s", exc)
            raise SAPConnectionError("Unable to connect to SAP Service Layer") from exc
        except requests.exceptions.Timeout as exc:
            logger.error("SAP Service Layer connection timeout: %s", exc)
            raise SAPConnectionError("SAP Service Layer connection timeout") from exc
        except requests.exceptions.HTTPError as exc:
            logger.error("SAP Service Layer authentication failed: %s", exc)
            raise SAPConnectionError("SAP Service Layer authentication failed") from exc

    def create(self, payload: dict) -> dict:
        """Create an SAP A/P Invoice through `/PurchaseInvoices`."""
        cookies = self._get_session_cookies()
        url = f"{self.sl_config['base_url']}/b1s/v2/PurchaseInvoices"
        payload = _convert_decimals(payload)

        try:
            response = requests.post(
                url,
                json=payload,
                cookies=cookies,
                headers={"Content-Type": "application/json"},
                timeout=30,
                verify=False,
            )

            if response.status_code == 201:
                logger.info(
                    "A/P Invoice created successfully: %s",
                    response.json().get("DocNum"),
                )
                return response.json()

            if response.status_code == 400:
                error_msg = self._extract_error_message(response)
                logger.error("SAP A/P Invoice validation error: %s", error_msg)
                raise SAPValidationError(error_msg)

            if response.status_code in (401, 403):
                logger.error("SAP authentication/authorization error creating A/P Invoice")
                raise SAPConnectionError("SAP authentication failed")

            error_msg = self._extract_error_message(response)
            logger.error("SAP error creating A/P Invoice: %s", error_msg)
            raise SAPDataError(f"Failed to create A/P Invoice: {error_msg}")

        except requests.exceptions.ConnectionError as exc:
            logger.error("Connection error while creating A/P Invoice: %s", exc)
            raise SAPConnectionError("Unable to connect to SAP Service Layer") from exc
        except requests.exceptions.Timeout as exc:
            logger.error("Timeout while creating A/P Invoice: %s", exc)
            raise SAPConnectionError("SAP Service Layer request timeout") from exc
        except (SAPConnectionError, SAPDataError, SAPValidationError):
            raise
        except Exception as exc:
            logger.error("Unexpected error creating A/P Invoice: %s", exc)
            raise SAPDataError(f"Unexpected error: {str(exc)}") from exc

    @staticmethod
    def _extract_error_message(response) -> str:
        try:
            error_data = response.json()
            if "error" in error_data:
                return error_data["error"].get("message", {}).get("value", str(error_data))
            return str(error_data)
        except Exception:
            return response.text or f"HTTP {response.status_code}"
