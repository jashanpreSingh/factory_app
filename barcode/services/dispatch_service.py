from __future__ import annotations

import uuid
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any

from django.db import transaction
from django.db.models import F, Q, Sum
from django.utils import timezone

from company.models import Company
from dispatch_plans.models import DispatchPlanStatus
from dispatch_plans.services import DispatchPlansService
from sap_client.exceptions import SAPConnectionError, SAPDataError

from ..models import (
    BarcodeMaster,
    BarcodeMasterType,
    Box,
    BoxMovement,
    BoxMovementType,
    BoxStatus,
    DispatchSapObjectType,
    DispatchSapSyncLog,
    DispatchSapSystemType,
    DispatchSapUpdateStatus,
    DispatchScanEntityType,
    DispatchScanLog,
    DispatchScanResult,
    DispatchScannedUnit,
    DispatchSession,
    DispatchSessionLine,
    DispatchSessionStatus,
    DispatchSettings,
    Pallet,
    PalletBoxHistory,
    PalletMovement,
    PalletMovementType,
    PalletStatus,
)
from .scan_service import ScanService


class DispatchValidationError(ValueError):
    def __init__(self, code: str, message: str, status_code: int = 400):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


@dataclass(frozen=True)
class SapUpdateResult:
    status: str
    message: str = ""
    request_payload: dict[str, Any] | None = None
    response_payload: dict[str, Any] | None = None


class SapDispatchAdapter:
    """
    SAP Business One adapter used by the barcode dispatch workflow.

    The workflow treats the invoice/bill number as the input key, then keeps the
    outbound delivery reference from SAP as the preferred final logistics object
    when SAP exposes it.
    """

    def __init__(self, company_code: str):
        self.company_code = company_code
        self._dispatch_plan_service: DispatchPlansService | None = None

    @property
    def dispatch_plan_service(self) -> DispatchPlansService:
        if self._dispatch_plan_service is None:
            self._dispatch_plan_service = DispatchPlansService(self.company_code)
        return self._dispatch_plan_service

    def lookup_bill(self, bill_number: str) -> dict[str, Any] | None:
        try:
            bill = self.dispatch_plan_service.get_bill_by_number(bill_number)
        except (SAPConnectionError, SAPDataError) as exc:
            raise DispatchValidationError("SAP_UNAVAILABLE", str(exc), status_code=503) from exc

        if not bill:
            return None

        plan = bill.get("plan") or {}
        base_refs = self._split_values(bill.get("base_refs") or "")
        already_dispatched = bool(bill.get("sap_dispatch_date")) or (
            plan.get("booking_status") == DispatchPlanStatus.DISPATCHED
        )

        return {
            "source_system": DispatchSapSystemType.BUSINESS_ONE,
            "sap_object_type": DispatchSapObjectType.AR_INVOICE,
            "bill_number": bill.get("doc_num") or bill_number,
            "bill_internal_id": str(bill.get("doc_entry") or ""),
            "bill_date": bill.get("doc_date"),
            "already_dispatched": already_dispatched,
            "sap_dispatch_status": "DISPATCHED" if already_dispatched else "OPEN",
            "reference_delivery_number": base_refs[0] if base_refs else "",
            "customer": {
                "code": bill.get("card_code") or "",
                "name": bill.get("card_name") or "",
                "ship_to_code": bill.get("ship_to_code") or "",
                "ship_to_name": bill.get("ship_to_address") or "",
            },
            "lines": [
                {
                    "sequence_no": index + 1,
                    "sap_line_no": str(line.get("line_num") if line.get("line_num") is not None else index + 1),
                    "material_code": line.get("item_code") or "",
                    "material_description": line.get("item_name") or "",
                    "quantity": str(line.get("quantity") or "0"),
                    "total_boxes": str(self._line_total_boxes(line)),
                    "uom": line.get("uom") or "",
                    "batch_number": line.get("batch_number") or "",
                    "warehouse_code": line.get("warehouse_code") or "",
                    "serial_required": False,
                    "reference_delivery_number": line.get("base_ref") or "",
                }
                for index, line in enumerate(bill.get("items") or [])
            ],
            "raw": bill,
        }

    def update_dispatch_status(self, session: DispatchSession) -> SapUpdateResult:
        return SapUpdateResult(
            status=DispatchSapUpdateStatus.NOT_CONFIGURED,
            message="SAP dispatch status update is not configured for this company.",
            request_payload={
                "bill_number": session.bill_number,
                "delivery_number": session.delivery_number or session.reference_delivery_number,
            },
            response_payload={},
        )

    @staticmethod
    def _split_values(value: str) -> list[str]:
        return [part.strip() for part in str(value or "").split(",") if part.strip()]

    @staticmethod
    def _line_total_boxes(line: dict[str, Any]) -> Decimal:
        explicit_boxes = SapDispatchAdapter._to_decimal(line.get("total_boxes"))
        if explicit_boxes > 0:
            return explicit_boxes

        quantity = SapDispatchAdapter._to_decimal(line.get("quantity"))
        if quantity <= 0:
            return Decimal("0")

        item_name = str(line.get("item_name") or "")
        pack_size = SapDispatchAdapter._pack_size_from_item_name(item_name)
        if pack_size <= 0:
            return Decimal("0")

        return (quantity / pack_size).quantize(Decimal("0.001"))

    @staticmethod
    def _pack_size_from_item_name(item_name: str) -> Decimal:
        match = re.search(r"(\d+(?:\.\d+)?)\s*(?:PCS?|PIECES?|BOTTLES?|BTL)\b", item_name, re.IGNORECASE)
        if not match:
            return Decimal("0")
        return SapDispatchAdapter._to_decimal(match.group(1))

    @staticmethod
    def _to_decimal(value: Any) -> Decimal:
        try:
            return Decimal(str(value or "0"))
        except (InvalidOperation, ValueError, TypeError):
            return Decimal("0")


class BarcodeDispatchService:
    ACTIVE_STATUSES = {
        DispatchSessionStatus.DRAFT,
        DispatchSessionStatus.ACTIVE,
        DispatchSessionStatus.PARTIAL,
        DispatchSessionStatus.READY_TO_DISPATCH,
    }
    CLOSED_STATUSES = {
        DispatchSessionStatus.COMPLETED,
        DispatchSessionStatus.CLOSED,
        DispatchSessionStatus.CANCELLED,
        DispatchSessionStatus.SAP_SYNC_FAILED,
    }
    LOCAL_DISPATCHED_STATUSES = {
        DispatchSessionStatus.COMPLETED,
        DispatchSessionStatus.SAP_SYNC_FAILED,
    }
    CLOSED_OR_CANCELLED_STATUSES = {
        DispatchSessionStatus.CLOSED,
        DispatchSessionStatus.CANCELLED,
    }

    def __init__(self, company_code: str, sap_adapter: SapDispatchAdapter | None = None):
        self.company_code = company_code
        self.sap_adapter = sap_adapter or SapDispatchAdapter(company_code)
        self.scan_service = ScanService(company_code=company_code)
        self._company: Company | None = None
        self._settings: DispatchSettings | None = None

    @property
    def company(self) -> Company:
        if self._company is None:
            self._company = Company.objects.get(code=self.company_code)
        return self._company

    @property
    def settings(self) -> DispatchSettings:
        if self._settings is None:
            self._settings, _ = DispatchSettings.objects.get_or_create(company=self.company)
        return self._settings

    def lookup_bill(self, bill_number: str) -> dict[str, Any]:
        bill_number = self._clean_bill_number(bill_number)
        bill = self.sap_adapter.lookup_bill(bill_number)
        if not bill:
            raise DispatchValidationError("SAP_BILL_NOT_FOUND", "Bill not found in SAP.", 404)

        if DispatchSession.objects.filter(
            company=self.company,
            bill_number=bill_number,
            status__in=self.LOCAL_DISPATCHED_STATUSES,
        ).exists():
            raise DispatchValidationError(
                "BILL_ALREADY_DISPATCHED",
                "This bill is already dispatched locally.",
            )

        if not bill.get("lines"):
            raise DispatchValidationError(
                "SAP_BILL_HAS_NO_LINES",
                "SAP bill has no dispatchable item lines.",
            )

        return bill

    @transaction.atomic
    def create_session(self, bill_number: str, user) -> DispatchSession:
        bill_number = self._clean_bill_number(bill_number)
        existing = (
            DispatchSession.objects.select_for_update()
            .filter(company=self.company, bill_number=bill_number)
            .exclude(status__in=self.CLOSED_OR_CANCELLED_STATUSES)
            .first()
        )
        if existing:
            if existing.status in self.LOCAL_DISPATCHED_STATUSES:
                raise DispatchValidationError(
                    "BILL_ALREADY_DISPATCHED",
                    "This bill is already dispatched locally.",
                )
            return self.get_session(existing.id)

        bill = self.lookup_bill(bill_number)
        delivery_number = bill.get("reference_delivery_number") or ""
        session = DispatchSession.objects.create(
            company=self.company,
            bill_number=bill_number,
            sap_system_type=bill.get("source_system") or DispatchSapSystemType.BUSINESS_ONE,
            sap_object_type=bill.get("sap_object_type") or DispatchSapObjectType.AR_INVOICE,
            sap_doc_entry=bill.get("bill_internal_id") or "",
            sap_doc_num=bill.get("bill_number") or bill_number,
            delivery_number=delivery_number,
            reference_delivery_number=delivery_number,
            customer_code=(bill.get("customer") or {}).get("code", ""),
            customer_name=(bill.get("customer") or {}).get("name", ""),
            ship_to_code=(bill.get("customer") or {}).get("ship_to_code", ""),
            ship_to_name=(bill.get("customer") or {}).get("ship_to_name", ""),
            bill_date=self._parse_date(bill.get("bill_date")),
            sap_dispatch_status=bill.get("sap_dispatch_status") or "OPEN",
            sap_update_status=DispatchSapUpdateStatus.NOT_CONFIGURED,
            sap_snapshot=bill,
            created_by=user,
            updated_by=user,
        )

        lines = []
        seen_line_numbers: set[str] = set()
        total_expected_qty = Decimal("0")
        for index, line in enumerate(bill.get("lines") or []):
            sap_line_no = str(line.get("sap_line_no") or index + 1)
            if sap_line_no in seen_line_numbers:
                sap_line_no = f"{sap_line_no}-{index + 1}"
            seen_line_numbers.add(sap_line_no)
            bill_qty = self._to_decimal(line.get("quantity"))
            bill_boxes = self._to_decimal(line.get("total_boxes"))
            if bill_qty <= 0:
                raise DispatchValidationError(
                    "INVALID_BILL_QUANTITY",
                    f"SAP line {sap_line_no} has invalid quantity.",
                )
            total_expected_qty += bill_qty
            lines.append(
                DispatchSessionLine(
                    session=session,
                    sequence_no=int(line.get("sequence_no") or index + 1),
                    sap_line_no=sap_line_no,
                    material_code=line.get("material_code") or "",
                    material_description=line.get("material_description") or "",
                    bill_qty=bill_qty,
                    bill_boxes=bill_boxes,
                    scanned_qty=Decimal("0"),
                    uom=line.get("uom") or "",
                    batch_number=line.get("batch_number") or "",
                    warehouse_code=line.get("warehouse_code") or "",
                    serial_required=bool(line.get("serial_required")),
                    status="PENDING",
                )
            )

        DispatchSessionLine.objects.bulk_create(lines)
        session.total_expected_qty = total_expected_qty
        session.total_scanned_qty = Decimal("0")
        session.save(update_fields=["total_expected_qty", "total_scanned_qty", "updated_at"])
        return self.get_session(session.id)

    def get_session(self, session_id: int) -> DispatchSession:
        try:
            return (
                DispatchSession.objects
                .filter(company=self.company)
                .prefetch_related(
                    "lines",
                    "scan_logs",
                    "scanned_units",
                    "sap_sync_logs",
                    "dispatched_boxes",
                    "dispatched_pallets",
                )
                .select_related(
                    "created_by",
                    "updated_by",
                    "dispatched_by",
                    "closed_by",
                    "cancelled_by",
                )
                .get(id=session_id)
            )
        except DispatchSession.DoesNotExist:
            raise DispatchValidationError("SESSION_NOT_FOUND", "Dispatch session not found.", 404)

    def list_sessions(
        self,
        *,
        status_value: str = "",
        status_group: str = "",
        bill_number: str = "",
        customer: str = "",
        created_by: str = "",
        date_from: str = "",
        date_to: str = "",
        sap_sync_status: str = "",
    ):
        qs = DispatchSession.objects.filter(company=self.company).select_related(
            "created_by",
            "dispatched_by",
            "closed_by",
            "cancelled_by",
        )

        statuses = self._status_filter_values(status_value, status_group)
        if statuses:
            qs = qs.filter(status__in=statuses)
        if bill_number:
            qs = qs.filter(bill_number__icontains=bill_number.strip())
        if customer:
            term = customer.strip()
            qs = qs.filter(Q(customer_name__icontains=term) | Q(customer_code__icontains=term))
        if created_by:
            user_term = created_by.strip()
            if user_term.isdigit():
                qs = qs.filter(created_by_id=int(user_term))
            else:
                qs = qs.filter(
                    Q(created_by__username__icontains=user_term)
                    | Q(created_by__first_name__icontains=user_term)
                    | Q(created_by__last_name__icontains=user_term)
                )
        if date_from:
            parsed = self._parse_date(date_from)
            if parsed:
                qs = qs.filter(created_at__date__gte=parsed)
        if date_to:
            parsed = self._parse_date(date_to)
            if parsed:
                qs = qs.filter(created_at__date__lte=parsed)
        if sap_sync_status:
            qs = qs.filter(sap_update_status=sap_sync_status.strip())
        return qs

    @transaction.atomic
    def submit_scan(
        self,
        session_id: int,
        raw_barcode: str,
        user,
        device_id: str = "",
        request_id: str | None = None,
        ip_address: str | None = None,
        line_id: int | None = None,
    ) -> DispatchScanLog:
        parsed_request_id = self._parse_uuid(request_id)
        raw_barcode = str(raw_barcode or "").strip()
        try:
            session = DispatchSession.objects.select_for_update().get(
                id=session_id,
                company=self.company,
            )
        except DispatchSession.DoesNotExist:
            raise DispatchValidationError("SESSION_NOT_FOUND", "Dispatch session not found.", 404)

        if parsed_request_id:
            existing_log = DispatchScanLog.objects.filter(
                session=session,
                request_id=parsed_request_id,
            ).first()
            if existing_log:
                return existing_log

        active_line = self._get_active_line(session)
        if session.status in self.CLOSED_STATUSES:
            return self._log_rejected_scan(
                session=session,
                line=active_line,
                raw_barcode=raw_barcode,
                reject_code="SESSION_CLOSED",
                reject_message="Completed or closed dispatch cannot be scanned again.",
                user=user,
                device_id=device_id,
                request_id=parsed_request_id,
                ip_address=ip_address,
            )
        if not raw_barcode:
            return self._log_rejected_scan(
                session=session,
                line=active_line,
                raw_barcode=raw_barcode,
                reject_code="BARCODE_REQUIRED",
                reject_message="Barcode is required.",
                user=user,
                device_id=device_id,
                request_id=parsed_request_id,
                ip_address=ip_address,
            )
        if not active_line and not self.settings.allow_partial_dispatch:
            return self._log_rejected_scan(
                session=session,
                line=None,
                raw_barcode=raw_barcode,
                reject_code="SESSION_ALREADY_COMPLETE",
                reject_message="All bill items are already fully scanned.",
                user=user,
                device_id=device_id,
                request_id=parsed_request_id,
                ip_address=ip_address,
            )

        resolved = self._resolve_barcode(raw_barcode)
        if not resolved:
            return self._log_rejected_scan(
                session=session,
                line=active_line,
                raw_barcode=raw_barcode,
                reject_code="BARCODE_NOT_FOUND",
                reject_message="Barcode was not found in the barcode system.",
                user=user,
                device_id=device_id,
                request_id=parsed_request_id,
                ip_address=ip_address,
            )

        if resolved["entity_type"] == DispatchScanEntityType.PALLET:
            return self._scan_pallet(
                session=session,
                raw_barcode=raw_barcode,
                resolved=resolved,
                user=user,
                device_id=device_id,
                request_id=parsed_request_id,
                ip_address=ip_address,
                selected_line_id=line_id,
            )
        if resolved["entity_type"] == DispatchScanEntityType.BOX:
            return self._scan_box(
                session=session,
                raw_barcode=raw_barcode,
                resolved=resolved,
                user=user,
                device_id=device_id,
                request_id=parsed_request_id,
                ip_address=ip_address,
                selected_line_id=line_id,
            )
        return self._scan_item(
            session=session,
            raw_barcode=raw_barcode,
            resolved=resolved,
            user=user,
            device_id=device_id,
            request_id=parsed_request_id,
            ip_address=ip_address,
            selected_line_id=line_id,
        )

    @transaction.atomic
    def mark_dispatched(self, session_id: int, user) -> DispatchSession:
        return self.complete_session(session_id, user=user)

    @transaction.atomic
    def complete_session(self, session_id: int, user) -> DispatchSession:
        try:
            session = DispatchSession.objects.select_for_update().get(
                id=session_id,
                company=self.company,
            )
        except DispatchSession.DoesNotExist:
            raise DispatchValidationError("SESSION_NOT_FOUND", "Dispatch session not found.", 404)

        if session.status in (DispatchSessionStatus.CANCELLED, DispatchSessionStatus.CLOSED):
            raise DispatchValidationError("SESSION_CLOSED", "This dispatch session is closed.")
        if session.status == DispatchSessionStatus.COMPLETED:
            return self.get_session(session.id)
        if not self._all_lines_complete(session) and not self.settings.allow_partial_dispatch:
            raise DispatchValidationError(
                "DISPATCH_NOT_COMPLETE",
                "All bill items must be fully scanned before dispatch.",
            )

        result = self.sap_adapter.update_dispatch_status(session)
        success_statuses = {DispatchSapUpdateStatus.SUCCESS, DispatchSapUpdateStatus.NOT_CONFIGURED}
        sap_success = result.status in success_statuses
        if result.status == DispatchSapUpdateStatus.NOT_CONFIGURED and self.settings.require_sap_sync_on_completion:
            sap_success = False
            result = SapUpdateResult(
                status=DispatchSapUpdateStatus.FAILED,
                message="SAP sync is required, but SAP dispatch update is not configured.",
                request_payload=result.request_payload,
                response_payload=result.response_payload,
            )

        DispatchSapSyncLog.objects.create(
            session=session,
            operation="UPDATE_DISPATCH_STATUS",
            request_payload=result.request_payload or {},
            response_payload=result.response_payload or {},
            status="SUCCESS" if sap_success else "FAILED",
            error_message="" if sap_success else result.message,
            attempt_no=session.sap_sync_logs.count() + 1,
        )

        now = timezone.now()
        session.completed_at = session.completed_at or now
        session.dispatched_at = now
        session.dispatched_by = user
        session.updated_by = user
        session.sap_update_status = result.status
        session.sap_update_error = "" if sap_success else result.message
        session.status = DispatchSessionStatus.COMPLETED if sap_success else DispatchSessionStatus.SAP_SYNC_FAILED
        self._refresh_session_totals(session, save=False)
        session.save()
        return self.get_session(session.id)

    @transaction.atomic
    def close_session(self, session_id: int, reason: str, user) -> DispatchSession:
        if not self.settings.allow_manual_close:
            raise DispatchValidationError("MANUAL_CLOSE_DISABLED", "Manual close is disabled for dispatch.")
        try:
            session = DispatchSession.objects.select_for_update().get(
                id=session_id,
                company=self.company,
            )
        except DispatchSession.DoesNotExist:
            raise DispatchValidationError("SESSION_NOT_FOUND", "Dispatch session not found.", 404)
        if session.status in self.LOCAL_DISPATCHED_STATUSES:
            raise DispatchValidationError(
                "SESSION_ALREADY_DISPATCHED",
                "Completed dispatch sessions cannot be closed.",
            )
        session.status = DispatchSessionStatus.CLOSED
        session.closed_at = timezone.now()
        session.closed_by = user
        session.close_reason = reason.strip()
        session.updated_by = user
        session.save()
        return self.get_session(session.id)

    @transaction.atomic
    def cancel_session(self, session_id: int, reason: str, user) -> DispatchSession:
        try:
            session = DispatchSession.objects.select_for_update().get(
                id=session_id,
                company=self.company,
            )
        except DispatchSession.DoesNotExist:
            raise DispatchValidationError("SESSION_NOT_FOUND", "Dispatch session not found.", 404)
        if session.status in self.LOCAL_DISPATCHED_STATUSES:
            raise DispatchValidationError(
                "SESSION_ALREADY_DISPATCHED",
                "Completed dispatch sessions cannot be cancelled.",
            )
        session.status = DispatchSessionStatus.CANCELLED
        session.cancel_reason = reason.strip()
        session.cancelled_at = timezone.now()
        session.cancelled_by = user
        session.closed_at = session.cancelled_at
        session.closed_by = user
        session.close_reason = reason.strip()
        session.updated_by = user
        session.save()
        return self.get_session(session.id)

    @transaction.atomic
    def retry_sap_sync(self, session_id: int, user) -> DispatchSession:
        try:
            session = DispatchSession.objects.select_for_update().get(
                id=session_id,
                company=self.company,
            )
        except DispatchSession.DoesNotExist:
            raise DispatchValidationError("SESSION_NOT_FOUND", "Dispatch session not found.", 404)
        if session.status != DispatchSessionStatus.SAP_SYNC_FAILED:
            raise DispatchValidationError(
                "SAP_SYNC_RETRY_NOT_ALLOWED",
                "SAP sync can be retried only for failed dispatch sessions.",
            )

        result = self.sap_adapter.update_dispatch_status(session)
        success = result.status in {DispatchSapUpdateStatus.SUCCESS, DispatchSapUpdateStatus.NOT_CONFIGURED}
        DispatchSapSyncLog.objects.create(
            session=session,
            operation="RETRY_UPDATE_DISPATCH_STATUS",
            request_payload=result.request_payload or {},
            response_payload=result.response_payload or {},
            status="SUCCESS" if success else "FAILED",
            error_message="" if success else result.message,
            attempt_no=session.sap_sync_logs.count() + 1,
        )
        session.sap_update_status = result.status
        session.sap_update_error = "" if success else result.message
        session.status = DispatchSessionStatus.COMPLETED if success else DispatchSessionStatus.SAP_SYNC_FAILED
        session.updated_by = user
        session.save()
        return self.get_session(session.id)

    def get_settings(self) -> DispatchSettings:
        return self.settings

    @transaction.atomic
    def update_settings(self, data: dict[str, Any], user=None) -> DispatchSettings:
        settings_obj = self.settings
        editable_fields = [
            "allow_partial_dispatch",
            "allow_partial_pallet_dispatch",
            "allow_box_dispatch_from_pallet",
            "require_sequential_item_scanning",
            "require_sap_sync_on_completion",
            "allow_manual_close",
            "allow_admin_override",
        ]
        for field in editable_fields:
            if field in data:
                setattr(settings_obj, field, bool(data[field]))
        settings_obj.save(update_fields=[*editable_fields, "updated_at"])
        self._settings = settings_obj
        return settings_obj

    def dispatch_report(self, filters: dict[str, Any]) -> list[dict[str, Any]]:
        sessions = self._filtered_report_sessions(filters)
        rows = []
        for session in sessions:
            expected_boxes = sum((line.bill_boxes or Decimal("0")) for line in session.lines.all())
            dispatched_boxes = DispatchScannedUnit.objects.filter(
                session=session,
                entity_type=DispatchScanEntityType.BOX,
            ).count()
            rows.append({
                "session_id": session.id,
                "bill_number": session.bill_number,
                "delivery_number": session.delivery_number or session.reference_delivery_number,
                "customer_code": session.customer_code,
                "customer_name": session.customer_name,
                "status": session.status,
                "created_by": self._display_user(session.created_by),
                "completed_by": self._display_user(session.dispatched_by),
                "started_at": session.started_at,
                "completed_at": session.completed_at or session.dispatched_at,
                "total_expected_qty": str(session.total_expected_qty),
                "total_dispatched_qty": str(session.total_scanned_qty),
                "pending_qty": str(max(session.total_expected_qty - session.total_scanned_qty, Decimal("0"))),
                "total_expected_boxes": str(expected_boxes),
                "total_dispatched_boxes": str(dispatched_boxes),
                "pending_boxes": str(max(expected_boxes - dispatched_boxes, Decimal("0"))),
                "sap_sync_status": session.sap_update_status,
                "sap_sync_error": session.sap_update_error,
            })
        return rows

    def dispatch_detail_report(self, session_id: int) -> dict[str, Any]:
        session = self.get_session(session_id)
        scans = (
            session.scan_logs
            .select_related("line", "scanned_by")
            .order_by("scanned_at", "id")
        )
        expected_boxes = sum((line.bill_boxes or Decimal("0")) for line in session.lines.all())
        dispatched_boxes = DispatchScannedUnit.objects.filter(
            session=session,
            entity_type=DispatchScanEntityType.BOX,
        ).count()
        return {
            "session": {
                "session_id": session.id,
                "bill_number": session.bill_number,
                "delivery_number": session.delivery_number or session.reference_delivery_number,
                "customer_code": session.customer_code,
                "customer_name": session.customer_name,
                "status": session.status,
                "total_expected_qty": str(session.total_expected_qty),
                "total_dispatched_qty": str(session.total_scanned_qty),
                "total_expected_boxes": str(expected_boxes),
                "total_dispatched_boxes": str(dispatched_boxes),
            },
            "lines": [
                {
                    "line_id": line.id,
                    "sap_line_no": line.sap_line_no,
                    "material_code": line.material_code,
                    "material_description": line.material_description,
                    "expected_qty": str(line.bill_qty),
                    "dispatched_qty": str(line.scanned_qty),
                    "pending_qty": str(max(line.bill_qty - line.scanned_qty, Decimal("0"))),
                    "expected_boxes": str(line.bill_boxes or Decimal("0")),
                    "dispatched_boxes": str(line.scanned_units.filter(entity_type=DispatchScanEntityType.BOX).count()),
                    "pending_boxes": str(max((line.bill_boxes or Decimal("0")) - line.scanned_units.filter(entity_type=DispatchScanEntityType.BOX).count(), Decimal("0"))),
                    "uom": line.uom,
                    "status": line.status,
                }
                for line in session.lines.all()
            ],
            "scans": [
                {
                    "scan_id": scan.id,
                    "barcode": scan.raw_barcode,
                    "scan_type": scan.entity_type,
                    "material_code": scan.material_code,
                    "qty": str(scan.qty or Decimal("0")),
                    "result": scan.result,
                    "rejection_reason": scan.reject_message,
                    "scanned_by": self._display_user(scan.scanned_by),
                    "scanned_at": scan.scanned_at,
                }
                for scan in scans
            ],
        }

    def pallet_report(self, filters: dict[str, Any]) -> list[dict[str, Any]]:
        qs = Pallet.objects.filter(company=self.company).select_related("dispatch_session")
        if filters.get("status"):
            qs = qs.filter(status=filters["status"])
        if filters.get("pallet_barcode"):
            qs = qs.filter(pallet_id__icontains=filters["pallet_barcode"])
        if filters.get("bill_number"):
            qs = qs.filter(dispatch_session__bill_number__icontains=filters["bill_number"])
        rows = []
        for pallet in qs.order_by("-updated_at")[:1000]:
            rows.append({
                "pallet_id": pallet.id,
                "pallet_barcode": pallet.pallet_id,
                "pallet_status": pallet.status,
                "total_boxes": pallet.total_boxes or pallet.box_count,
                "dispatched_boxes": pallet.dispatched_boxes,
                "remaining_boxes": pallet.available_boxes,
                "dispatch_session_id": pallet.dispatch_session_id,
                "bill_number": pallet.dispatch_session.bill_number if pallet.dispatch_session else "",
                "dispatched_time": pallet.dispatched_at,
            })
        return rows

    def box_report(self, filters: dict[str, Any]) -> list[dict[str, Any]]:
        qs = Box.objects.filter(company=self.company).select_related("pallet", "dispatch_session")
        if filters.get("status"):
            qs = qs.filter(status=filters["status"])
        if filters.get("box_barcode"):
            qs = qs.filter(box_barcode__icontains=filters["box_barcode"])
        if filters.get("material_code"):
            qs = qs.filter(item_code__icontains=filters["material_code"])
        if filters.get("pallet_barcode"):
            qs = qs.filter(pallet__pallet_id__icontains=filters["pallet_barcode"])
        if filters.get("bill_number"):
            qs = qs.filter(dispatch_session__bill_number__icontains=filters["bill_number"])
        rows = []
        for box in qs.order_by("-updated_at")[:1000]:
            rows.append({
                "box_id": box.id,
                "box_barcode": box.box_barcode,
                "material_code": box.item_code,
                "quantity": str(box.qty),
                "uom": box.uom,
                "pallet_barcode": box.pallet.pallet_id if box.pallet else "",
                "box_status": box.status,
                "dispatch_session_id": box.dispatch_session_id,
                "bill_number": box.dispatch_session.bill_number if box.dispatch_session else "",
                "dispatched_time": box.dispatched_at,
                "removed_from_pallet": bool(box.removed_from_pallet_at),
            })
        return rows

    def rejected_scan_report(self, filters: dict[str, Any]) -> list[dict[str, Any]]:
        qs = DispatchScanLog.objects.filter(
            session__company=self.company,
            result=DispatchScanResult.REJECTED,
        ).select_related("session", "scanned_by")
        qs = self._apply_scan_report_filters(qs, filters)
        return [
            {
                "scan_id": scan.id,
                "barcode": scan.raw_barcode,
                "scan_type": scan.entity_type,
                "rejection_reason": scan.reject_message,
                "rejection_code": scan.reject_code,
                "bill_number": scan.session.bill_number,
                "user": self._display_user(scan.scanned_by),
                "scan_time": scan.scanned_at,
            }
            for scan in qs.order_by("-scanned_at")[:1000]
        ]

    def _scan_item(
        self,
        *,
        session: DispatchSession,
        raw_barcode: str,
        resolved: dict[str, Any],
        user,
        device_id: str,
        request_id,
        ip_address: str | None,
        selected_line_id: int | None = None,
    ) -> DispatchScanLog:
        line, rejection = self._select_line_for_material(
            session=session,
            material_code=resolved["material_code"],
            batch_number=resolved.get("batch_number") or "",
            raw_barcode=raw_barcode,
            resolved=resolved,
            user=user,
            device_id=device_id,
            request_id=request_id,
            ip_address=ip_address,
            selected_line_id=selected_line_id,
        )
        if rejection:
            return rejection
        qty = resolved["qty"] or Decimal("1")
        if qty <= 0:
            return self._reject_quantity(session, line, raw_barcode, resolved, user, device_id, request_id, ip_address)
        if qty > line.bill_qty - line.scanned_qty:
            return self._reject_over_quantity(session, line, raw_barcode, resolved, user, device_id, request_id, ip_address)

        scan_log = self._create_accepted_scan_log(
            session=session,
            line=line,
            raw_barcode=raw_barcode,
            resolved=resolved,
            qty=qty,
            user=user,
            device_id=device_id,
            request_id=request_id,
            ip_address=ip_address,
        )
        self._create_scanned_unit(
            session=session,
            line=line,
            scan_log=scan_log,
            barcode_value=f"{raw_barcode}#{scan_log.id}",
            entity_type=DispatchScanEntityType.ITEM,
            qty=qty,
            material_code=resolved["material_code"],
            batch_number=resolved.get("batch_number") or "",
            uom=resolved.get("uom") or line.uom,
        )
        self._increment_line(line, qty)
        self._refresh_session_after_scan(session, user)
        return scan_log

    def _scan_box(
        self,
        *,
        session: DispatchSession,
        raw_barcode: str,
        resolved: dict[str, Any],
        user,
        device_id: str,
        request_id,
        ip_address: str | None,
        selected_line_id: int | None = None,
    ) -> DispatchScanLog:
        box = Box.objects.select_for_update().get(
            id=resolved["box"].id,
            company=self.company,
        )
        resolved = {**resolved, "box": box, "pallet": box.pallet, "qty": self._to_decimal(box.qty)}
        active_line = self._get_active_line(session)

        if box.status == BoxStatus.DISPATCHED or box.dispatch_session_id:
            through_pallet = DispatchScannedUnit.objects.filter(box=box, pallet__isnull=False).exists()
            message = (
                "This box is already dispatched through pallet dispatch."
                if through_pallet
                else "Box already dispatched."
            )
            return self._log_rejected_scan(
                session=session,
                line=active_line,
                raw_barcode=raw_barcode,
                resolved=resolved,
                reject_code="BOX_ALREADY_DISPATCHED",
                reject_message=message,
                user=user,
                device_id=device_id,
                request_id=request_id,
                ip_address=ip_address,
            )
        if box.status not in (BoxStatus.ACTIVE, BoxStatus.PARTIAL):
            return self._log_rejected_scan(
                session=session,
                line=active_line,
                raw_barcode=raw_barcode,
                resolved=resolved,
                reject_code="BOX_NOT_DISPATCHABLE",
                reject_message="This box is not in a dispatchable status.",
                user=user,
                device_id=device_id,
                request_id=request_id,
                ip_address=ip_address,
            )
        if box.pallet_id and not self.settings.allow_box_dispatch_from_pallet:
            return self._log_rejected_scan(
                session=session,
                line=active_line,
                raw_barcode=raw_barcode,
                resolved=resolved,
                reject_code="BOX_FROM_PALLET_NOT_ALLOWED",
                reject_message="Box dispatch from pallet is disabled.",
                user=user,
                device_id=device_id,
                request_id=request_id,
                ip_address=ip_address,
            )

        line, rejection = self._select_line_for_material(
            session=session,
            material_code=box.item_code,
            batch_number=box.batch_number,
            raw_barcode=raw_barcode,
            resolved=resolved,
            user=user,
            device_id=device_id,
            request_id=request_id,
            ip_address=ip_address,
            selected_line_id=selected_line_id,
        )
        if rejection:
            return rejection
        qty = self._to_decimal(box.qty)
        if qty <= 0:
            return self._reject_quantity(session, line, raw_barcode, resolved, user, device_id, request_id, ip_address)
        if qty > line.bill_qty - line.scanned_qty:
            return self._reject_over_quantity(session, line, raw_barcode, resolved, user, device_id, request_id, ip_address)

        old_pallet = box.pallet
        now = timezone.now()
        if old_pallet:
            old_pallet = Pallet.objects.select_for_update().get(id=old_pallet.id, company=self.company)

        scan_log = self._create_accepted_scan_log(
            session=session,
            line=line,
            raw_barcode=raw_barcode,
            resolved=resolved,
            qty=qty,
            user=user,
            device_id=device_id,
            request_id=request_id,
            ip_address=ip_address,
        )

        old_status = box.status
        if old_pallet:
            box.pallet = None
            box.removed_from_pallet_at = now
            box.removed_from_pallet_reason = "Dispatched separately from pallet."
            PalletBoxHistory.objects.create(
                company=self.company,
                pallet=old_pallet,
                box=box,
                action="BOX_DISPATCHED_SEPARATELY",
                old_status=old_status,
                new_status=BoxStatus.DISPATCHED,
                dispatch_session=session,
                remarks="Box removed from pallet because it was dispatched separately.",
                created_by=user,
            )
            BoxMovement.objects.create(
                company=self.company,
                box=box,
                movement_type=BoxMovementType.REMOVE_FOR_DISPATCH,
                from_warehouse=box.current_warehouse,
                from_pallet=old_pallet,
                performed_by=user,
            )

        box.status = BoxStatus.DISPATCHED
        box.dispatch_session = session
        box.dispatched_at = now
        box.save(update_fields=[
            "status",
            "pallet",
            "dispatch_session",
            "dispatched_at",
            "removed_from_pallet_at",
            "removed_from_pallet_reason",
            "updated_at",
        ])
        BoxMovement.objects.create(
            company=self.company,
            box=box,
            movement_type=BoxMovementType.DISPATCH,
            from_warehouse=box.current_warehouse,
            from_pallet=old_pallet,
            performed_by=user,
        )
        if old_pallet:
            self._recalculate_pallet_state(old_pallet)

        self._create_scanned_unit(
            session=session,
            line=line,
            scan_log=scan_log,
            barcode_value=box.box_barcode,
            entity_type=DispatchScanEntityType.BOX,
            box=box,
            pallet=old_pallet,
            qty=qty,
            material_code=box.item_code,
            batch_number=box.batch_number,
            uom=box.uom,
        )

        self._increment_line(line, qty)
        self._refresh_session_after_scan(session, user)
        return scan_log

    def _scan_pallet(
        self,
        *,
        session: DispatchSession,
        raw_barcode: str,
        resolved: dict[str, Any],
        user,
        device_id: str,
        request_id,
        ip_address: str | None,
        selected_line_id: int | None = None,
    ) -> DispatchScanLog:
        pallet = Pallet.objects.select_for_update().get(id=resolved["pallet"].id, company=self.company)
        resolved = {**resolved, "pallet": pallet}
        active_line = self._get_active_line(session)
        if pallet.status == PalletStatus.DISPATCHED or pallet.dispatch_session_id:
            return self._log_rejected_scan(
                session=session,
                line=active_line,
                raw_barcode=raw_barcode,
                resolved=resolved,
                reject_code="PALLET_ALREADY_DISPATCHED",
                reject_message="Pallet already dispatched.",
                user=user,
                device_id=device_id,
                request_id=request_id,
                ip_address=ip_address,
                selected_line_id=selected_line_id,
            )
        if pallet.status not in (PalletStatus.ACTIVE, PalletStatus.PARTIAL):
            return self._log_rejected_scan(
                session=session,
                line=active_line,
                raw_barcode=raw_barcode,
                resolved=resolved,
                reject_code="PALLET_NOT_DISPATCHABLE",
                reject_message="This pallet is not in a dispatchable status.",
                user=user,
                device_id=device_id,
                request_id=request_id,
                ip_address=ip_address,
            )

        boxes = list(
            Box.objects
            .select_for_update()
            .filter(company=self.company, pallet=pallet)
            .order_by("id")
        )
        if not boxes:
            return self._log_rejected_scan(
                session=session,
                line=active_line,
                raw_barcode=raw_barcode,
                resolved=resolved,
                reject_code="PALLET_EMPTY",
                reject_message="Pallet has no boxes to dispatch.",
                user=user,
                device_id=device_id,
                request_id=request_id,
                ip_address=ip_address,
            )

        dispatched_boxes = [
            box for box in boxes
            if box.status == BoxStatus.DISPATCHED or box.dispatch_session_id
        ]
        removed_box_count = PalletBoxHistory.objects.filter(
            company=self.company,
            pallet=pallet,
            action="BOX_DISPATCHED_SEPARATELY",
        ).count()
        if (dispatched_boxes or removed_box_count) and not self.settings.allow_partial_pallet_dispatch:
            return self._log_rejected_scan(
                session=session,
                line=active_line,
                raw_barcode=raw_barcode,
                resolved=resolved,
                reject_code="PALLET_HAS_DISPATCHED_BOXES",
                reject_message="Pallet contains boxes that are already removed or dispatched.",
                user=user,
                device_id=device_id,
                request_id=request_id,
                ip_address=ip_address,
            )
        dispatchable_boxes = [
            box for box in boxes
            if box.status in (BoxStatus.ACTIVE, BoxStatus.PARTIAL) and not box.dispatch_session_id
        ]
        if not dispatchable_boxes:
            return self._log_rejected_scan(
                session=session,
                line=active_line,
                raw_barcode=raw_barcode,
                resolved=resolved,
                reject_code="PALLET_ALREADY_DISPATCHED",
                reject_message="Pallet already dispatched.",
                user=user,
                device_id=device_id,
                request_id=request_id,
                ip_address=ip_address,
            )

        line_quantities: dict[int, Decimal] = defaultdict(lambda: Decimal("0"))
        line_by_id: dict[int, DispatchSessionLine] = {}
        box_line_map: dict[int, DispatchSessionLine] = {}
        for box in dispatchable_boxes:
            box_resolved = {
                **resolved,
                "entity_type": DispatchScanEntityType.BOX,
                "entity_id": str(box.id),
                "barcode_value": box.box_barcode,
                "material_code": box.item_code,
                "batch_number": box.batch_number,
                "qty": self._to_decimal(box.qty),
                "uom": box.uom,
                "box": box,
            }
            line, rejection = self._select_line_for_material(
                session=session,
                material_code=box.item_code,
                batch_number=box.batch_number,
                raw_barcode=raw_barcode,
                resolved=box_resolved,
                user=user,
                device_id=device_id,
                request_id=request_id,
                ip_address=ip_address,
            )
            if rejection:
                return rejection
            qty = self._to_decimal(box.qty)
            if qty <= 0:
                return self._reject_quantity(session, line, raw_barcode, box_resolved, user, device_id, request_id, ip_address)
            line_quantities[line.id] += qty
            line_by_id[line.id] = line
            box_line_map[box.id] = line

        for line_id, qty in line_quantities.items():
            line = line_by_id[line_id]
            if qty > line.bill_qty - line.scanned_qty:
                return self._log_rejected_scan(
                    session=session,
                    line=line,
                    raw_barcode=raw_barcode,
                    resolved=resolved,
                    reject_code="OVER_QUANTITY",
                    reject_message="Pallet quantity is greater than remaining bill quantity.",
                    user=user,
                    device_id=device_id,
                    request_id=request_id,
                    ip_address=ip_address,
                )

        warning = ""
        skipped_box_count = len(dispatched_boxes) + removed_box_count
        if skipped_box_count:
            warning = f"{skipped_box_count} boxes were already dispatched or removed; only remaining boxes were dispatched."
        resolved_with_warning = {
            **resolved,
            "parsed": {
                **(resolved.get("parsed") or {}),
                "warning": warning,
                "box_count_dispatched": len(dispatchable_boxes),
            },
            "qty": sum((self._to_decimal(box.qty) for box in dispatchable_boxes), Decimal("0")),
        }
        scan_log = self._create_accepted_scan_log(
            session=session,
            line=active_line or box_line_map[dispatchable_boxes[0].id],
            raw_barcode=raw_barcode,
            resolved=resolved_with_warning,
            qty=resolved_with_warning["qty"],
            user=user,
            device_id=device_id,
            request_id=request_id,
            ip_address=ip_address,
        )

        now = timezone.now()
        for box in dispatchable_boxes:
            old_status = box.status
            line = box_line_map[box.id]
            qty = self._to_decimal(box.qty)
            box.status = BoxStatus.DISPATCHED
            box.dispatch_session = session
            box.dispatched_at = now
            PalletBoxHistory.objects.create(
                company=self.company,
                pallet=pallet,
                box=box,
                action="PALLET_DISPATCHED",
                old_status=old_status,
                new_status=BoxStatus.DISPATCHED,
                dispatch_session=session,
                remarks="Box dispatched through pallet scan.",
                created_by=user,
            )
            BoxMovement.objects.create(
                company=self.company,
                box=box,
                movement_type=BoxMovementType.DISPATCH,
                from_warehouse=box.current_warehouse,
                from_pallet=pallet,
                performed_by=user,
            )
            self._create_scanned_unit(
                session=session,
                line=line,
                scan_log=scan_log,
                barcode_value=box.box_barcode,
                entity_type=DispatchScanEntityType.BOX,
                box=box,
                pallet=pallet,
                qty=qty,
                material_code=box.item_code,
                batch_number=box.batch_number,
                uom=box.uom,
            )
        Box.objects.bulk_update(dispatchable_boxes, ["status", "dispatch_session", "dispatched_at", "updated_at"])

        for line_id, qty in line_quantities.items():
            self._increment_line(line_by_id[line_id], qty)

        pallet.status = PalletStatus.DISPATCHED
        pallet.dispatch_session = session
        pallet.dispatched_at = now
        pallet.dispatched_boxes = len([box for box in boxes if box.status == BoxStatus.DISPATCHED]) or len(dispatchable_boxes)
        pallet.available_boxes = 0
        pallet.total_boxes = len(boxes)
        pallet.save(update_fields=[
            "status",
            "dispatch_session",
            "dispatched_at",
            "total_boxes",
            "available_boxes",
            "dispatched_boxes",
            "updated_at",
        ])
        PalletMovement.objects.create(
            company=self.company,
            pallet=pallet,
            movement_type=PalletMovementType.DISPATCH,
            from_warehouse=pallet.current_warehouse,
            quantity=resolved_with_warning["qty"],
            performed_by=user,
            notes=warning or "Pallet dispatched.",
        )
        self._refresh_session_after_scan(session, user)
        return scan_log

    def _resolve_barcode(self, raw_barcode: str) -> dict[str, Any] | None:
        parsed = self.scan_service._parse_barcode(raw_barcode)
        lookup = self.scan_service.lookup_barcode(raw_barcode)
        entity_type = lookup.get("entity_type")
        data = lookup.get("entity_data") or {}
        if data and entity_type == DispatchScanEntityType.BOX:
            box = Box.objects.select_for_update().get(id=data["id"], company=self.company)
            return {
                "entity_type": DispatchScanEntityType.BOX,
                "entity_id": str(box.id),
                "barcode_value": box.box_barcode,
                "material_code": box.item_code,
                "batch_number": box.batch_number,
                "qty": self._to_decimal(box.qty),
                "uom": box.uom,
                "box": box,
                "pallet": box.pallet,
                "serial_number": "",
                "parsed": parsed,
            }

        if data and entity_type == DispatchScanEntityType.PALLET:
            pallet = Pallet.objects.select_for_update().get(id=data["id"], company=self.company)
            return {
                "entity_type": DispatchScanEntityType.PALLET,
                "entity_id": str(pallet.id),
                "barcode_value": pallet.pallet_id,
                "material_code": pallet.item_code,
                "batch_number": pallet.batch_number,
                "qty": self._to_decimal(pallet.total_qty),
                "uom": pallet.uom,
                "box": None,
                "pallet": pallet,
                "serial_number": "",
                "parsed": parsed,
            }

        master = (
            BarcodeMaster.objects
            .select_for_update()
            .filter(company=self.company, barcode__iexact=raw_barcode.strip(), is_active=True)
            .first()
        )
        if master:
            if master.barcode_type == BarcodeMasterType.BOX and master.box_id:
                box = Box.objects.select_for_update().get(id=master.box_id, company=self.company)
                return {
                    "entity_type": DispatchScanEntityType.BOX,
                    "entity_id": str(box.id),
                    "barcode_value": box.box_barcode,
                    "material_code": box.item_code,
                    "batch_number": box.batch_number,
                    "qty": self._to_decimal(box.qty),
                    "uom": box.uom,
                    "box": box,
                    "pallet": box.pallet,
                    "serial_number": "",
                    "parsed": parsed,
                }
            if master.barcode_type == BarcodeMasterType.PALLET and master.pallet_id:
                pallet = Pallet.objects.select_for_update().get(id=master.pallet_id, company=self.company)
                return {
                    "entity_type": DispatchScanEntityType.PALLET,
                    "entity_id": str(pallet.id),
                    "barcode_value": pallet.pallet_id,
                    "material_code": pallet.item_code,
                    "batch_number": pallet.batch_number,
                    "qty": self._to_decimal(pallet.total_qty),
                    "uom": pallet.uom,
                    "box": None,
                    "pallet": pallet,
                    "serial_number": "",
                    "parsed": parsed,
                }
            return {
                "entity_type": DispatchScanEntityType.ITEM,
                "entity_id": master.barcode,
                "barcode_value": master.barcode,
                "material_code": master.material_code,
                "batch_number": "",
                "qty": self._to_decimal(master.quantity) or Decimal("1"),
                "uom": master.uom,
                "box": None,
                "pallet": None,
                "serial_number": "",
                "parsed": parsed,
            }

        material_code = raw_barcode.strip()
        if DispatchSessionLine.objects.filter(session__company=self.company, material_code=material_code).exists():
            return {
                "entity_type": DispatchScanEntityType.ITEM,
                "entity_id": material_code,
                "barcode_value": material_code,
                "material_code": material_code,
                "batch_number": "",
                "qty": Decimal("1"),
                "uom": "",
                "box": None,
                "pallet": None,
                "serial_number": "",
                "parsed": parsed,
            }
        return None

    def _select_line_for_material(
        self,
        *,
        session: DispatchSession,
        material_code: str,
        batch_number: str,
        raw_barcode: str,
        resolved: dict[str, Any],
        user,
        device_id: str,
        request_id,
        ip_address: str | None,
        selected_line_id: int | None = None,
    ) -> tuple[DispatchSessionLine | None, DispatchScanLog | None]:
        active_line = self._get_active_line(session)
        if self.settings.require_sequential_item_scanning:
            if not active_line:
                return None, self._log_rejected_scan(
                    session=session,
                    line=None,
                    raw_barcode=raw_barcode,
                    resolved=resolved,
                    reject_code="SESSION_ALREADY_COMPLETE",
                    reject_message="All bill items are already fully scanned.",
                    user=user,
                    device_id=device_id,
                    request_id=request_id,
                    ip_address=ip_address,
                )
            if material_code != active_line.material_code:
                later_match = DispatchSessionLine.objects.filter(
                    session=session,
                    material_code=material_code,
                    scanned_qty__lt=F("bill_qty"),
                ).exclude(id=active_line.id).exists()
                code = "LINE_SEQUENCE_VIOLATION" if later_match else "WRONG_MATERIAL"
                message = (
                    "Complete the current item before scanning the next item."
                    if later_match
                    else (
                        f"Scanned material {material_code} does not match "
                        f"current item {active_line.material_code}."
                    )
                )
                return None, self._log_rejected_scan(
                    session=session,
                    line=active_line,
                    raw_barcode=raw_barcode,
                    resolved=resolved,
                    reject_code=code,
                    reject_message=message,
                    user=user,
                    device_id=device_id,
                    request_id=request_id,
                    ip_address=ip_address,
                )
            line = active_line
        else:
            if selected_line_id:
                line = (
                    DispatchSessionLine.objects
                    .select_for_update()
                    .filter(session=session, id=selected_line_id)
                    .first()
                )
                if not line:
                    return None, self._log_rejected_scan(
                        session=session,
                        line=active_line,
                        raw_barcode=raw_barcode,
                        resolved=resolved,
                        reject_code="SELECTED_LINE_NOT_FOUND",
                        reject_message="Selected dispatch item was not found.",
                        user=user,
                        device_id=device_id,
                        request_id=request_id,
                        ip_address=ip_address,
                    )
                if line.scanned_qty >= line.bill_qty:
                    return None, self._log_rejected_scan(
                        session=session,
                        line=line,
                        raw_barcode=raw_barcode,
                        resolved=resolved,
                        reject_code="OVER_QUANTITY",
                        reject_message="Selected dispatch item is already fully scanned.",
                        user=user,
                        device_id=device_id,
                        request_id=request_id,
                        ip_address=ip_address,
                    )
                if material_code != line.material_code:
                    return None, self._log_rejected_scan(
                        session=session,
                        line=line,
                        raw_barcode=raw_barcode,
                        resolved=resolved,
                        reject_code="WRONG_MATERIAL",
                        reject_message=(
                            f"Scanned material {material_code} does not match "
                            f"selected item {line.material_code}."
                        ),
                        user=user,
                        device_id=device_id,
                        request_id=request_id,
                        ip_address=ip_address,
                    )
            else:
                line = (
                    DispatchSessionLine.objects
                    .select_for_update()
                    .filter(session=session, material_code=material_code, scanned_qty__lt=F("bill_qty"))
                    .order_by("sequence_no", "id")
                    .first()
                )
            if not line:
                bill_has_material = DispatchSessionLine.objects.filter(
                    session=session,
                    material_code=material_code,
                ).exists()
                return None, self._log_rejected_scan(
                    session=session,
                    line=active_line,
                    raw_barcode=raw_barcode,
                    resolved=resolved,
                    reject_code="OVER_QUANTITY" if bill_has_material else "WRONG_MATERIAL",
                    reject_message=(
                        "This material is already fully scanned for the bill."
                        if bill_has_material
                        else f"Scanned material {material_code} does not belong to this bill."
                    ),
                    user=user,
                    device_id=device_id,
                    request_id=request_id,
                    ip_address=ip_address,
                )

        if line.batch_number and batch_number and batch_number != line.batch_number:
            return None, self._log_rejected_scan(
                session=session,
                line=line,
                raw_barcode=raw_barcode,
                resolved=resolved,
                reject_code="WRONG_BATCH",
                reject_message="Scanned batch does not match the bill batch.",
                user=user,
                device_id=device_id,
                request_id=request_id,
                ip_address=ip_address,
            )
        return line, None

    def _create_accepted_scan_log(
        self,
        *,
        session: DispatchSession,
        line: DispatchSessionLine | None,
        raw_barcode: str,
        resolved: dict[str, Any],
        qty: Decimal,
        user,
        device_id: str,
        request_id,
        ip_address: str | None,
    ) -> DispatchScanLog:
        return DispatchScanLog.objects.create(
            session=session,
            line=line,
            raw_barcode=raw_barcode,
            parsed_barcode=resolved.get("parsed") or self.scan_service._parse_barcode(raw_barcode),
            entity_type=resolved["entity_type"],
            entity_id=resolved.get("entity_id") or "",
            material_code=resolved.get("material_code") or "",
            batch_number=resolved.get("batch_number") or "",
            qty=qty,
            uom=resolved.get("uom") or (line.uom if line else ""),
            result=DispatchScanResult.ACCEPTED,
            scanned_by=user,
            device_id=device_id,
            ip_address=ip_address,
            request_id=request_id,
        )

    def _create_scanned_unit(
        self,
        *,
        session: DispatchSession,
        line: DispatchSessionLine,
        scan_log: DispatchScanLog,
        barcode_value: str,
        entity_type: str,
        qty: Decimal,
        material_code: str,
        batch_number: str = "",
        uom: str = "",
        box: Box | None = None,
        pallet: Pallet | None = None,
        serial_number: str = "",
    ) -> DispatchScannedUnit:
        return DispatchScannedUnit.objects.create(
            session=session,
            line=line,
            scan_log=scan_log,
            barcode_value=barcode_value,
            entity_type=entity_type,
            box=box,
            pallet=pallet,
            serial_number=serial_number,
            material_code=material_code,
            batch_number=batch_number,
            qty=qty,
            uom=uom,
        )

    def _increment_line(self, line: DispatchSessionLine, qty: Decimal) -> None:
        line.scanned_qty += qty
        line.status = "COMPLETE" if line.scanned_qty >= line.bill_qty else "PARTIAL"
        line.save(update_fields=["scanned_qty", "status", "updated_at"])

    def _refresh_session_after_scan(self, session: DispatchSession, user) -> None:
        if session.started_at is None:
            session.started_at = timezone.now()
        self._refresh_session_totals(session, save=False)
        if self._all_lines_complete(session):
            session.status = DispatchSessionStatus.READY_TO_DISPATCH
            session.completed_at = session.completed_at or timezone.now()
        elif session.total_scanned_qty > 0:
            session.status = DispatchSessionStatus.PARTIAL
        else:
            session.status = DispatchSessionStatus.ACTIVE
        session.updated_by = user
        session.save(update_fields=[
            "status",
            "started_at",
            "completed_at",
            "total_expected_qty",
            "total_scanned_qty",
            "updated_by",
            "updated_at",
        ])

    def _refresh_session_totals(self, session: DispatchSession, *, save: bool = True) -> None:
        aggregates = DispatchSessionLine.objects.filter(session=session).aggregate(
            expected=Sum("bill_qty"),
            scanned=Sum("scanned_qty"),
        )
        session.total_expected_qty = aggregates["expected"] or Decimal("0")
        session.total_scanned_qty = aggregates["scanned"] or Decimal("0")
        if save:
            session.save(update_fields=["total_expected_qty", "total_scanned_qty", "updated_at"])

    def _recalculate_pallet_state(self, pallet: Pallet) -> None:
        boxes = list(Box.objects.filter(company=self.company, pallet=pallet))
        active_boxes = [box for box in boxes if box.status in (BoxStatus.ACTIVE, BoxStatus.PARTIAL)]
        dispatched_boxes = [box for box in boxes if box.status == BoxStatus.DISPATCHED]
        removed_box_count = PalletBoxHistory.objects.filter(
            company=self.company,
            pallet=pallet,
            action="BOX_DISPATCHED_SEPARATELY",
        ).values("box_id").distinct().count()
        pallet.total_boxes = len(boxes) + removed_box_count
        pallet.available_boxes = len(active_boxes)
        pallet.dispatched_boxes = len(dispatched_boxes) + removed_box_count
        pallet.box_count = len(active_boxes)
        pallet.total_qty = sum((box.qty for box in active_boxes), Decimal("0"))
        if pallet.status != PalletStatus.DISPATCHED:
            if active_boxes and (dispatched_boxes or removed_box_count):
                pallet.status = PalletStatus.PARTIAL
            elif not active_boxes:
                pallet.status = PalletStatus.EMPTY
            else:
                pallet.status = PalletStatus.ACTIVE
        pallet.save(update_fields=[
            "status",
            "box_count",
            "total_boxes",
            "available_boxes",
            "dispatched_boxes",
            "total_qty",
            "updated_at",
        ])

    def _get_active_line(self, session: DispatchSession) -> DispatchSessionLine | None:
        return (
            DispatchSessionLine.objects
            .select_for_update()
            .filter(session=session, scanned_qty__lt=F("bill_qty"))
            .order_by("sequence_no", "id")
            .first()
        )

    def _all_lines_complete(self, session: DispatchSession) -> bool:
        return not DispatchSessionLine.objects.filter(
            session=session,
            scanned_qty__lt=F("bill_qty"),
        ).exists()

    def _log_rejected_scan(
        self,
        *,
        session: DispatchSession,
        line: DispatchSessionLine | None,
        raw_barcode: str,
        reject_code: str,
        reject_message: str,
        user,
        device_id: str = "",
        request_id=None,
        ip_address: str | None = None,
        resolved: dict[str, Any] | None = None,
    ) -> DispatchScanLog:
        resolved = resolved or {}
        return DispatchScanLog.objects.create(
            session=session,
            line=line,
            raw_barcode=raw_barcode,
            parsed_barcode=resolved.get("parsed") or self.scan_service._parse_barcode(raw_barcode),
            entity_type=resolved.get("entity_type") or DispatchScanEntityType.UNKNOWN,
            entity_id=resolved.get("entity_id") or "",
            material_code=resolved.get("material_code") or "",
            batch_number=resolved.get("batch_number") or "",
            qty=resolved.get("qty"),
            uom=resolved.get("uom") or "",
            result=DispatchScanResult.REJECTED,
            reject_code=reject_code,
            reject_message=reject_message,
            scanned_by=user,
            device_id=device_id,
            ip_address=ip_address,
            request_id=request_id,
        )

    def _reject_quantity(self, session, line, raw_barcode, resolved, user, device_id, request_id, ip_address):
        return self._log_rejected_scan(
            session=session,
            line=line,
            raw_barcode=raw_barcode,
            resolved=resolved,
            reject_code="INVALID_QUANTITY",
            reject_message="Scanned quantity must be greater than zero.",
            user=user,
            device_id=device_id,
            request_id=request_id,
            ip_address=ip_address,
        )

    def _reject_over_quantity(self, session, line, raw_barcode, resolved, user, device_id, request_id, ip_address):
        return self._log_rejected_scan(
            session=session,
            line=line,
            raw_barcode=raw_barcode,
            resolved=resolved,
            reject_code="OVER_QUANTITY",
            reject_message="Scan quantity is greater than remaining bill quantity.",
            user=user,
            device_id=device_id,
            request_id=request_id,
            ip_address=ip_address,
        )

    def _filtered_report_sessions(self, filters: dict[str, Any]):
        return self.list_sessions(
            status_value=filters.get("status", ""),
            bill_number=filters.get("bill_number", ""),
            customer=filters.get("customer", ""),
            created_by=filters.get("user", ""),
            date_from=filters.get("from_date", ""),
            date_to=filters.get("to_date", ""),
            sap_sync_status=filters.get("sap_sync_status", ""),
        ).order_by("-created_at")[:1000]

    def _apply_scan_report_filters(self, qs, filters: dict[str, Any]):
        if filters.get("from_date"):
            parsed = self._parse_date(filters["from_date"])
            if parsed:
                qs = qs.filter(scanned_at__date__gte=parsed)
        if filters.get("to_date"):
            parsed = self._parse_date(filters["to_date"])
            if parsed:
                qs = qs.filter(scanned_at__date__lte=parsed)
        if filters.get("bill_number"):
            qs = qs.filter(session__bill_number__icontains=filters["bill_number"])
        if filters.get("customer"):
            qs = qs.filter(session__customer_name__icontains=filters["customer"])
        if filters.get("user") and str(filters["user"]).isdigit():
            qs = qs.filter(scanned_by_id=int(filters["user"]))
        if filters.get("material_code"):
            qs = qs.filter(material_code__icontains=filters["material_code"])
        if filters.get("pallet_barcode"):
            qs = qs.filter(raw_barcode__icontains=filters["pallet_barcode"])
        if filters.get("box_barcode"):
            qs = qs.filter(raw_barcode__icontains=filters["box_barcode"])
        return qs

    def _status_filter_values(self, status_value: str, status_group: str) -> list[str]:
        if status_value:
            return [part.strip() for part in status_value.split(",") if part.strip()]
        group = (status_group or "").strip().lower()
        if group == "active":
            return list(self.ACTIVE_STATUSES)
        if group == "completed":
            return [DispatchSessionStatus.COMPLETED, DispatchSessionStatus.SAP_SYNC_FAILED]
        if group == "closed":
            return [DispatchSessionStatus.CLOSED, DispatchSessionStatus.CANCELLED]
        return []

    @staticmethod
    def _display_user(user) -> str:
        if not user:
            return ""
        full_name = ""
        if hasattr(user, "get_full_name"):
            full_name = user.get_full_name()
        return full_name or getattr(user, "username", "") or str(user)

    @staticmethod
    def _clean_bill_number(value: str) -> str:
        cleaned = str(value or "").strip()
        if not cleaned:
            raise DispatchValidationError("BILL_NUMBER_REQUIRED", "Bill number is required.")
        return cleaned

    @staticmethod
    def _parse_date(value):
        if not value:
            return None
        if hasattr(value, "date"):
            return value.date()
        if hasattr(value, "year") and hasattr(value, "month") and hasattr(value, "day"):
            return value
        try:
            return datetime.strptime(str(value)[:10], "%Y-%m-%d").date()
        except ValueError:
            return None

    @staticmethod
    def _parse_uuid(value: str | None):
        if not value:
            return None
        try:
            return uuid.UUID(str(value))
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _to_decimal(value) -> Decimal:
        try:
            return Decimal(str(value or "0"))
        except (InvalidOperation, ValueError):
            return Decimal("0")
