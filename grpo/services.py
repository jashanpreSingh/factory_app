import logging
import os
import tempfile
from typing import List, Dict, Any, Optional
from decimal import Decimal
from datetime import date
from django.utils import timezone
from django.db import transaction

from gate_core.enums import GateEntryStatus
from dispatch_plans.hana_reader import HanaDispatchBillReader
from dispatch_plans.models import DispatchPlan, DispatchPlanStatus
from driver_management.models import VehicleEntry
from raw_material_gatein.models import POReceipt, POItemReceipt
from quality_control.enums import InspectionStatus
from sap_client.client import SAPClient
from sap_client.context import CompanyContext
from sap_client.exceptions import SAPConnectionError, SAPDataError, SAPValidationError

from .models import (
    GRPOPosting,
    GRPOLinePosting,
    GRPOStatus,
    GRPOAttachment,
    SAPAttachmentStatus,
    ServiceGRPOPosting,
    ServiceGRPOLinePosting,
    ServiceGRPOAttachment,
)

logger = logging.getLogger(__name__)


class GRPOService:
    """
    Service for handling GRPO operations.
    """
    SAP_DOCUMENT_COMMENTS_MAX_LENGTH = 254

    def __init__(self, company_code: str):
        self.company_code = company_code

    @classmethod
    def _truncate_sap_document_comments(cls, comments: str) -> str:
        """Keep SAP document comments within the Service Layer field limit."""
        comments = (comments or "").strip()
        if len(comments) <= cls.SAP_DOCUMENT_COMMENTS_MAX_LENGTH:
            return comments
        suffix = "..."
        max_body_length = cls.SAP_DOCUMENT_COMMENTS_MAX_LENGTH - len(suffix)
        return comments[:max_body_length].rstrip(" |,") + suffix

    @staticmethod
    def _decimal_or_none(value, decimal_places: str = "0.001") -> Optional[Decimal]:
        if value in (None, ""):
            return None
        decimal_value = Decimal(str(value))
        return decimal_value.quantize(Decimal(decimal_places))

    @staticmethod
    def _first_day_of_month(value) -> Optional[date]:
        if not value:
            return None
        if isinstance(value, str):
            try:
                value = date.fromisoformat(value)
            except ValueError:
                return None
        if not hasattr(value, "year") or not hasattr(value, "month"):
            return None
        return date(value.year, value.month, 1)

    @staticmethod
    def _infer_product_variety(item_summary: str) -> str:
        summary = (item_summary or "").lower()
        if any(token in summary for token in ("water", "drink", "beverage", "juice")):
            return "Beverage"
        if summary:
            return "Oil"
        return ""

    def _get_dispatch_bill_snapshot(self, dispatch_plan: DispatchPlan) -> Dict[str, Any]:
        doc_num = (dispatch_plan.sap_invoice_doc_num or "").strip()
        if not doc_num:
            return {}
        try:
            reader = HanaDispatchBillReader(CompanyContext(self.company_code))
            return reader.get_bill_by_number(doc_num) or {}
        except Exception as exc:
            logger.warning(
                "Could not fetch dispatch SAP bill snapshot for service GRPO plan %s: %s",
                dispatch_plan.id,
                exc,
            )
            return {}

    def get_pending_grpo_entries(self) -> List[VehicleEntry]:
        """
        Get all completed gate entries that are ready for GRPO posting.
        Returns entries with status COMPLETED or QC_COMPLETED.
        """
        return VehicleEntry.objects.filter(
            company__code=self.company_code,
            entry_type="RAW_MATERIAL",
            status__in=[GateEntryStatus.COMPLETED, GateEntryStatus.QC_COMPLETED]
        ).prefetch_related(
            "po_receipts",
            "po_receipts__items",
            "grpo_postings"
        ).order_by("-entry_time")

    def get_all_grpo_visible_entries(self) -> List[VehicleEntry]:
        """
        Get all RAW_MATERIAL gate entries the GRPO operator may want to see —
        including in-flight ones still at gate or QC. Cancelled entries are
        excluded; the GRPO operator has no action on them.
        """
        return VehicleEntry.objects.filter(
            company__code=self.company_code,
            entry_type="RAW_MATERIAL",
        ).exclude(
            status=GateEntryStatus.CANCELLED,
        ).prefetch_related(
            "po_receipts",
            "po_receipts__items",
            "grpo_postings",
        ).order_by("-entry_time")

    def get_grpo_preview_data(
        self,
        vehicle_entry_id: int,
        po_receipt_ids: Optional[List[int]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all data required for GRPO posting for a specific gate entry.
        Optionally filter by specific PO receipt IDs (for merged preview).
        Returns list of PO receipts with their items and QC status.
        """
        try:
            vehicle_entry = VehicleEntry.objects.prefetch_related(
                "po_receipts",
                "po_receipts__items",
                "po_receipts__items__arrival_slip",
                "po_receipts__items__arrival_slip__inspection",
                "grpo_postings"
            ).get(id=vehicle_entry_id)
        except VehicleEntry.DoesNotExist:
            raise ValueError(f"Vehicle entry {vehicle_entry_id} not found")

        is_ready = vehicle_entry.status in [
            GateEntryStatus.COMPLETED,
            GateEntryStatus.QC_COMPLETED
        ]

        po_receipts_qs = vehicle_entry.po_receipts.all()
        if po_receipt_ids:
            po_receipts_qs = po_receipts_qs.filter(id__in=po_receipt_ids)

        result = []
        for po_receipt in po_receipts_qs:
            # Check if GRPO already posted for this PO (M2M or legacy FK)
            existing_grpo = GRPOPosting.objects.filter(
                po_receipts=po_receipt,
                status=GRPOStatus.POSTED
            ).first()
            if not existing_grpo:
                existing_grpo = vehicle_entry.grpo_postings.filter(
                    po_receipt=po_receipt,
                    status=GRPOStatus.POSTED
                ).first()

            items_data = []
            for item in po_receipt.items.all():
                qc_status = self._get_item_qc_status(item)
                items_data.append({
                    "po_item_receipt_id": item.id,
                    "item_code": item.po_item_code,
                    "item_name": item.item_name,
                    "ordered_qty": item.ordered_qty,
                    "received_qty": item.received_qty,
                    "accepted_qty": item.accepted_qty,
                    "rejected_qty": item.rejected_qty,
                    "uom": item.uom,
                    "qc_status": qc_status,
                    "unit_price": item.unit_price,
                    "tax_code": item.tax_code or "",
                    "warehouse_code": item.warehouse_code or "",
                    "gl_account": item.gl_account or "",
                    "variety": item.variety or "",
                    "sap_line_num": item.sap_line_num,
                })

            result.append({
                "vehicle_entry_id": vehicle_entry.id,
                "entry_no": vehicle_entry.entry_no,
                "entry_status": vehicle_entry.status,
                "entry_date": vehicle_entry.entry_time.date() if vehicle_entry.entry_time else None,
                "is_ready_for_grpo": is_ready,
                "po_receipt_id": po_receipt.id,
                "po_number": po_receipt.po_number,
                "supplier_code": po_receipt.supplier_code,
                "supplier_name": po_receipt.supplier_name,
                "sap_doc_entry": po_receipt.sap_doc_entry,
                "branch_id": po_receipt.branch_id,
                "vendor_ref": po_receipt.vendor_ref or "",
                "invoice_no": po_receipt.invoice_no or "",
                "invoice_date": po_receipt.invoice_date,
                "challan_no": po_receipt.challan_no or "",
                "items": items_data,
                "grpo_status": existing_grpo.status if existing_grpo else None,
                "sap_doc_num": existing_grpo.sap_doc_num if existing_grpo else None,
                "total_amount": existing_grpo.sap_doc_total if existing_grpo else None
            })

        return result

    def _get_item_qc_status(self, po_item_receipt: POItemReceipt) -> str:
        """Get QC status for a PO item receipt."""
        if not hasattr(po_item_receipt, "arrival_slip"):
            return "NO_ARRIVAL_SLIP"

        arrival_slip = po_item_receipt.arrival_slip
        if not arrival_slip.is_submitted:
            return "ARRIVAL_SLIP_PENDING"

        if not hasattr(arrival_slip, "inspection"):
            return "INSPECTION_PENDING"

        inspection = arrival_slip.inspection
        return inspection.final_status

    def _build_structured_comments(
        self,
        user,
        po_receipts: List[POReceipt],
        vehicle_entry: VehicleEntry,
        user_comments: Optional[str] = None
    ) -> str:
        """Build structured comments string for SAP GRPO."""
        full_name = user.get_full_name() if hasattr(user, 'get_full_name') else str(user)
        username = getattr(user, 'username', getattr(user, 'email', str(user)))

        po_numbers = ", ".join(po.po_number for po in po_receipts)
        parts = [
            f"App: FactoryApp v2",
            f"User: {full_name} ({username})",
            f"PO: {po_numbers}",
            f"Gate Entry: {vehicle_entry.entry_no}",
        ]

        if len(po_receipts) > 1:
            parts.append(f"Merged: {len(po_receipts)} POs")

        if user_comments:
            parts.append(user_comments)

        return self._truncate_sap_document_comments(" | ".join(parts))

    @transaction.atomic
    def post_grpo(
        self,
        vehicle_entry_id: int,
        po_receipt_ids: List[int],
        user,
        items: List[Dict[str, Any]],
        branch_id: int,
        warehouse_code: Optional[str] = None,
        comments: Optional[str] = None,
        vendor_ref: Optional[str] = None,
        extra_charges: Optional[List[Dict[str, Any]]] = None,
        attachments: Optional[list] = None,
        doc_date: Optional[str] = None,
        doc_due_date: Optional[str] = None,
        tax_date: Optional[str] = None,
        should_roundoff: bool = False,
    ) -> GRPOPosting:
        """
        Post GRPO to SAP for one or more PO receipts (merged GRPO).
        All PO receipts must belong to the same supplier and vehicle entry.

        Args:
            vehicle_entry_id: ID of the vehicle entry
            po_receipt_ids: List of PO receipt IDs to merge into single GRPO
            user: User posting the GRPO
            items: List of dicts with po_item_receipt_id, accepted_qty, and optional fields
            branch_id: SAP Branch/Business Place ID (BPLId)
            warehouse_code: Optional warehouse code for SAP
            comments: Optional user comments for SAP document
            vendor_ref: Optional vendor reference number (NumAtCard)
            extra_charges: Optional list of additional expense dicts
            attachments: Optional list of Django UploadedFile objects to attach
            doc_date: Optional posting date (DocDate), ISO format YYYY-MM-DD
            doc_due_date: Optional due date (DocDueDate), ISO format YYYY-MM-DD
            tax_date: Optional document date (TaxDate), ISO format YYYY-MM-DD
            should_roundoff: If True, auto-calculates RoundDif to round the subtotal to the nearest integer
        """
        # Get vehicle entry
        try:
            vehicle_entry = VehicleEntry.objects.get(id=vehicle_entry_id)
        except VehicleEntry.DoesNotExist:
            raise ValueError(f"Vehicle entry {vehicle_entry_id} not found")

        # Get all PO receipts
        po_receipts = list(
            POReceipt.objects.prefetch_related(
                "items",
                "items__arrival_slip",
                "items__arrival_slip__inspection"
            ).filter(id__in=po_receipt_ids, vehicle_entry=vehicle_entry)
        )

        if len(po_receipts) != len(po_receipt_ids):
            found_ids = {po.id for po in po_receipts}
            missing_ids = set(po_receipt_ids) - found_ids
            raise ValueError(f"PO receipt(s) not found for this vehicle entry: {missing_ids}")

        # Validate all POs have the same supplier
        supplier_codes = set(po.supplier_code for po in po_receipts)
        if len(supplier_codes) > 1:
            raise ValueError(
                f"Cannot merge POs from different suppliers. "
                f"Found suppliers: {supplier_codes}"
            )

        # Validate all POs have the same branch_id
        branch_ids = set(po.branch_id for po in po_receipts if po.branch_id is not None)
        if len(branch_ids) > 1:
            raise ValueError(
                f"Cannot merge POs with different branch IDs. "
                f"Found branch IDs: {branch_ids}"
            )

        # Validate gate entry status
        if vehicle_entry.status not in [
            GateEntryStatus.COMPLETED,
            GateEntryStatus.QC_COMPLETED
        ]:
            raise ValueError(
                f"Gate entry is not completed. Current status: {vehicle_entry.status}"
            )

        # Check if any PO already has a POSTED GRPO
        for po_receipt in po_receipts:
            existing = GRPOPosting.objects.filter(
                po_receipts=po_receipt,
                status=GRPOStatus.POSTED
            ).first()
            if not existing:
                # Also check legacy po_receipt FK
                existing = GRPOPosting.objects.filter(
                    vehicle_entry=vehicle_entry,
                    po_receipt=po_receipt,
                    status=GRPOStatus.POSTED
                ).first()
            if existing:
                raise ValueError(
                    f"GRPO already posted for PO {po_receipt.po_number}. "
                    f"SAP Doc Num: {existing.sap_doc_num}"
                )

        # Collect all item IDs across all PO receipts
        all_po_item_ids = set()
        for po_receipt in po_receipts:
            all_po_item_ids.update(po_receipt.items.values_list("id", flat=True))

        # Create a mapping of item IDs to input data
        items_input_map = {item["po_item_receipt_id"]: item for item in items}

        # Validate all item IDs belong to one of the selected PO receipts
        invalid_ids = set(items_input_map.keys()) - all_po_item_ids
        if invalid_ids:
            raise ValueError(f"Invalid PO item receipt IDs: {invalid_ids}")

        # Update accepted and rejected quantities in POItemReceipt
        for po_receipt in po_receipts:
            for item in po_receipt.items.all():
                if item.id in items_input_map:
                    accepted_qty = items_input_map[item.id]["accepted_qty"]
                    item.accepted_qty = accepted_qty
                    item.rejected_qty = max(item.received_qty - accepted_qty, Decimal("0"))
                    item.save()

        # Create GRPO posting record (use first PO as legacy po_receipt)
        grpo_posting = GRPOPosting.objects.create(
            vehicle_entry=vehicle_entry,
            po_receipt=po_receipts[0],
            status=GRPOStatus.PENDING,
            posted_by=user
        )
        # Link all PO receipts via M2M
        grpo_posting.po_receipts.set(po_receipts)

        # Build GRPO document lines from ALL PO receipts
        document_lines = []
        grpo_lines_data = []

        for po_receipt in po_receipts:
            for item in po_receipt.items.all():
                if item.accepted_qty <= 0:
                    continue

                item_input = items_input_map.get(item.id, {})

                line_data = {
                    "ItemCode": item.po_item_code,
                    "Quantity": str(item.accepted_qty),
                }

                # PO Linking — each line references its own PO's BaseEntry
                if po_receipt.sap_doc_entry and item.sap_line_num is not None:
                    line_data["BaseEntry"] = po_receipt.sap_doc_entry
                    line_data["BaseLine"] = item.sap_line_num
                    line_data["BaseType"] = 22  # Purchase Order

                if warehouse_code:
                    line_data["WarehouseCode"] = warehouse_code

                unit_price = item_input.get("unit_price")
                if unit_price is not None:
                    line_data["UnitPrice"] = float(unit_price)

                tax_code = item_input.get("tax_code")
                if tax_code:
                    line_data["TaxCode"] = tax_code

                gl_account = item_input.get("gl_account")
                if gl_account:
                    line_data["AccountCode"] = gl_account

                variety = item_input.get("variety")
                if variety:
                    line_data["CostingCode"] = variety

                document_lines.append(line_data)
                grpo_lines_data.append({
                    "po_item_receipt": item,
                    "quantity_posted": item.accepted_qty,
                    "base_entry": po_receipt.sap_doc_entry,
                    "base_line": item.sap_line_num,
                })

        if not document_lines:
            grpo_posting.status = GRPOStatus.FAILED
            grpo_posting.error_message = "No accepted quantities to post"
            grpo_posting.save()
            raise ValueError("No accepted quantities to post")

        # Build structured comments
        structured_comments = self._build_structured_comments(
            user, po_receipts, vehicle_entry, comments
        )

        # Build full SAP payload — CardCode from any PO (all same supplier)
        grpo_payload = {
            "CardCode": po_receipts[0].supplier_code,
            "BPL_IDAssignedToInvoice": branch_id,
            "Comments": structured_comments,
            "DocumentLines": document_lines
        }

        # Optional date fields
        if doc_date:
            grpo_payload["DocDate"] = str(doc_date)
        if doc_due_date:
            grpo_payload["DocDueDate"] = str(doc_due_date)
        if tax_date:
            grpo_payload["TaxDate"] = str(tax_date)

        # Auto round-off
        if should_roundoff:
            subtotal = Decimal('0')
            for line in document_lines:
                qty = Decimal(str(line.get("Quantity", 0)))
                price = Decimal(str(line.get("UnitPrice", 0)))
                subtotal += qty * price
            if subtotal > 0:
                rounded = subtotal.quantize(Decimal('1'), rounding='ROUND_HALF_UP')
                round_dif = float(rounded - subtotal)
                if round_dif != 0:
                    grpo_payload["RoundDif"] = round_dif

        if vendor_ref:
            grpo_payload["NumAtCard"] = vendor_ref

        # Extra charges (DocumentAdditionalExpenses)
        if extra_charges:
            additional_expenses = []
            for charge in extra_charges:
                expense = {
                    "ExpenseCode": charge["expense_code"],
                    "LineTotal": float(charge["amount"]),
                }
                if charge.get("remarks"):
                    expense["Remarks"] = charge["remarks"]
                if charge.get("tax_code"):
                    expense["TaxCode"] = charge["tax_code"]
                additional_expenses.append(expense)
            grpo_payload["DocumentAdditionalExpenses"] = additional_expenses

        # Upload attachments to SAP BEFORE creating GRPO
        sap_client = SAPClient(company_code=self.company_code)
        attachment_records = []
        sap_absolute_entry = None

        if attachments:
            for uploaded_file in attachments:
                suffix = os.path.splitext(uploaded_file.name)[1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    for chunk in uploaded_file.chunks():
                        tmp.write(chunk)
                    tmp_path = tmp.name

                try:
                    sap_result = sap_client.upload_attachment(
                        file_path=tmp_path,
                        filename=uploaded_file.name
                    )
                    abs_entry = sap_result.get("AbsoluteEntry")
                    if abs_entry:
                        sap_absolute_entry = abs_entry
                        attachment_records.append({
                            "file": uploaded_file,
                            "filename": uploaded_file.name,
                            "sap_absolute_entry": abs_entry,
                        })
                        logger.info(
                            f"Attachment '{uploaded_file.name}' uploaded to SAP. "
                            f"AbsoluteEntry: {abs_entry}"
                        )
                finally:
                    os.unlink(tmp_path)

            if sap_absolute_entry:
                grpo_payload["AttachmentEntry"] = sap_absolute_entry

        po_numbers_str = ", ".join(po.po_number for po in po_receipts)
        logger.info(f"GRPO Payload for PO(s) {po_numbers_str}: {grpo_payload}")

        # Post to SAP
        try:
            result = sap_client.create_grpo(grpo_payload)

            grpo_posting.sap_doc_entry = result.get("DocEntry")
            grpo_posting.sap_doc_num = result.get("DocNum")
            grpo_posting.sap_doc_total = Decimal(str(result.get("DocTotal", 0)))
            grpo_posting.status = GRPOStatus.POSTED
            grpo_posting.posted_at = timezone.now()
            grpo_posting.posted_by = user
            grpo_posting.save()

            for line_data in grpo_lines_data:
                GRPOLinePosting.objects.create(
                    grpo_posting=grpo_posting,
                    po_item_receipt=line_data["po_item_receipt"],
                    quantity_posted=line_data["quantity_posted"],
                    base_entry=line_data["base_entry"],
                    base_line=line_data["base_line"],
                )

            for att_data in attachment_records:
                GRPOAttachment.objects.create(
                    grpo_posting=grpo_posting,
                    file=att_data["file"],
                    original_filename=att_data["filename"],
                    sap_attachment_status=SAPAttachmentStatus.LINKED,
                    sap_absolute_entry=att_data["sap_absolute_entry"],
                    uploaded_by=user,
                )

            logger.info(
                f"GRPO posted successfully for PO(s) {po_numbers_str}. "
                f"SAP DocNum: {grpo_posting.sap_doc_num}"
            )

            return grpo_posting

        except SAPValidationError as e:
            grpo_posting.status = GRPOStatus.FAILED
            grpo_posting.error_message = str(e)
            grpo_posting.save()
            logger.error(f"SAP validation error posting GRPO: {e}")
            raise

        except SAPConnectionError as e:
            grpo_posting.status = GRPOStatus.FAILED
            grpo_posting.error_message = "SAP system unavailable"
            grpo_posting.save()
            logger.error(f"SAP connection error posting GRPO: {e}")
            raise

        except SAPDataError as e:
            grpo_posting.status = GRPOStatus.FAILED
            grpo_posting.error_message = str(e)
            grpo_posting.save()
            logger.error(f"SAP data error posting GRPO: {e}")
            raise

    def get_pending_service_grpo_entries(self) -> List[DispatchPlan]:
        """
        Get booked dispatch plans pending transport service GRPO posting.
        A plan appears here only after the transport booking is marked BOOKED.
        """
        return (
            DispatchPlan.objects.filter(
                company__code=self.company_code,
                booking_status=DispatchPlanStatus.BOOKED,
                is_active=True,
            )
            .exclude(service_grpo_postings__status=GRPOStatus.POSTED)
            .select_related(
                "company",
                "vehicle",
                "transporter",
                "driver",
                "linked_vehicle_entry",
            )
            .prefetch_related("service_grpo_postings")
            .distinct()
            .order_by("-updated_at", "-created_at")
        )

    def get_service_grpo_preview_data(self, dispatch_plan_id: int) -> Dict[str, Any]:
        """Get dispatch booking data required for service GRPO posting."""
        try:
            dispatch_plan = (
                DispatchPlan.objects.select_related(
                    "company",
                    "vehicle",
                    "transporter",
                    "driver",
                    "linked_vehicle_entry",
                )
                .prefetch_related("service_grpo_postings")
                .get(
                    id=dispatch_plan_id,
                    company__code=self.company_code,
                    is_active=True,
                )
            )
        except DispatchPlan.DoesNotExist:
            raise ValueError(f"Dispatch plan {dispatch_plan_id} not found")

        existing_grpo = dispatch_plan.service_grpo_postings.filter(
            status=GRPOStatus.POSTED
        ).first()
        is_ready = (
            dispatch_plan.booking_status == DispatchPlanStatus.BOOKED
            and existing_grpo is None
        )

        amount = dispatch_plan.total_freight
        if amount is None:
            amount = dispatch_plan.freight
        if amount is None:
            amount = Decimal("0")

        bill_no = dispatch_plan.sap_invoice_doc_num or str(
            dispatch_plan.sap_invoice_doc_entry
        )
        vehicle_no = dispatch_plan.vehicle_no or (
            dispatch_plan.vehicle.vehicle_number if dispatch_plan.vehicle_id else ""
        )
        service_description = f"Transport freight for dispatch bill {bill_no}"
        if vehicle_no:
            service_description = f"{service_description} - {vehicle_no}"

        latest_grpo = dispatch_plan.service_grpo_postings.order_by("-created_at").first()
        bill_snapshot = self._get_dispatch_bill_snapshot(dispatch_plan)
        item_summary = bill_snapshot.get("item_summary", "")
        product_variety = (
            dispatch_plan.product_variety
            or self._infer_product_variety(item_summary)
        )
        total_litres = dispatch_plan.total_litres
        if total_litres is None and bill_snapshot:
            total_litres = self._decimal_or_none(
                bill_snapshot.get("total_litres"), "0.001"
            )
        invoice_weight = dispatch_plan.invoice_weight
        invoice_amount = dispatch_plan.invoice_amount
        if invoice_amount is None and bill_snapshot:
            invoice_amount = self._decimal_or_none(
                bill_snapshot.get("doc_total"), "0.01"
            )
        effective_month = dispatch_plan.effective_month or self._first_day_of_month(
            dispatch_plan.dispatch_date or bill_snapshot.get("doc_date")
        )

        return {
            "dispatch_plan_id": dispatch_plan.id,
            "sap_invoice_doc_entry": dispatch_plan.sap_invoice_doc_entry,
            "sap_invoice_doc_num": dispatch_plan.sap_invoice_doc_num,
            "booking_status": dispatch_plan.booking_status,
            "dispatch_date": dispatch_plan.dispatch_date,
            "is_ready_for_grpo": is_ready,
            "vehicle_no": vehicle_no,
            "driver_name": dispatch_plan.driver_name,
            "transporter_name": dispatch_plan.transporter_name,
            "transporter_gstin": dispatch_plan.transporter_gstin,
            "bilty_no": dispatch_plan.bilty_no,
            "bilty_date": dispatch_plan.bilty_date,
            "freight": dispatch_plan.freight,
            "total_freight": dispatch_plan.total_freight,
            "created_at": dispatch_plan.created_at,
            "updated_at": dispatch_plan.updated_at,
            "default_amount": amount,
            "default_service_description": service_description[:255],
            "default_place_of_supply": dispatch_plan.place_of_supply or "HR",
            "default_effective_month": effective_month,
            "default_budget_delivery_point": dispatch_plan.budget_delivery_point,
            "default_location_code": dispatch_plan.service_location_code,
            "default_location_name": dispatch_plan.service_location_name,
            "default_sac_entry": dispatch_plan.sac_entry,
            "default_sac_code": dispatch_plan.sac_code,
            "default_product_variety": product_variety,
            "default_total_litres": total_litres,
            "invoice_number": dispatch_plan.invoice_number
            or str(bill_snapshot.get("doc_num") or ""),
            "eway_bill": dispatch_plan.eway_bill or bill_snapshot.get("sap_eway_bill", ""),
            "invoice_weight": invoice_weight,
            "invoice_amount": invoice_amount,
            "source_state": bill_snapshot.get("state", ""),
            "source_city": bill_snapshot.get("city", ""),
            "item_summary": item_summary,
            "grpo_status": existing_grpo.status if existing_grpo else (
                latest_grpo.status if latest_grpo else None
            ),
            "sap_doc_num": existing_grpo.sap_doc_num if existing_grpo else (
                latest_grpo.sap_doc_num if latest_grpo else None
            ),
            "total_amount": existing_grpo.sap_doc_total if existing_grpo else (
                latest_grpo.sap_doc_total if latest_grpo else None
            ),
        }

    def _build_service_structured_comments(
        self,
        user,
        dispatch_plan: DispatchPlan,
        user_comments: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Build structured comments string for SAP service GRPO."""
        full_name = user.get_full_name() if hasattr(user, "get_full_name") else str(user)
        username = getattr(user, "username", getattr(user, "email", str(user)))

        parts = [
            "App: JI",
            f"User: {full_name} ({username})",
        ]

        return " | ".join(parts)

    @transaction.atomic
    def post_service_grpo(
        self,
        dispatch_plan_id: int,
        user,
        vendor_code: str,
        branch_id: int,
        service_description: str,
        amount: Decimal,
        tax_code: Optional[str] = None,
        gl_account: Optional[str] = None,
        unit_price: Optional[Decimal] = None,
        place_of_supply: Optional[str] = None,
        effective_month: Optional[str] = None,
        budget_delivery_point: Optional[str] = None,
        location_code: Optional[int] = None,
        location_name: Optional[str] = None,
        sac_entry: Optional[int] = None,
        sac_code: Optional[str] = None,
        product_variety: Optional[str] = None,
        total_litres: Optional[Decimal] = None,
        invoice_number: Optional[str] = None,
        eway_bill: Optional[str] = None,
        invoice_weight: Optional[Decimal] = None,
        invoice_amount: Optional[Decimal] = None,
        comments: Optional[str] = None,
        vendor_ref: Optional[str] = None,
        extra_charges: Optional[List[Dict[str, Any]]] = None,
        attachments: Optional[list] = None,
        doc_date: Optional[str] = None,
        doc_due_date: Optional[str] = None,
        tax_date: Optional[str] = None,
        should_roundoff: bool = False,
    ) -> ServiceGRPOPosting:
        """
        Post a service-type GRPO to SAP for a booked dispatch transport plan.
        The SAP document is a PurchaseDeliveryNotes document with service lines.
        """
        try:
            dispatch_plan = DispatchPlan.objects.select_related(
                "company",
                "transporter",
            ).get(
                id=dispatch_plan_id,
                company__code=self.company_code,
                is_active=True,
            )
        except DispatchPlan.DoesNotExist:
            raise ValueError(f"Dispatch plan {dispatch_plan_id} not found")

        if dispatch_plan.booking_status != DispatchPlanStatus.BOOKED:
            raise ValueError(
                "Service GRPO can be posted only after the vehicle booking is Booked."
            )

        existing_grpo = dispatch_plan.service_grpo_postings.filter(
            status=GRPOStatus.POSTED
        ).first()
        if existing_grpo:
            raise ValueError(
                f"Service GRPO already posted for this dispatch plan. "
                f"SAP Doc Num: {existing_grpo.sap_doc_num}"
            )

        amount = Decimal(str(amount))
        if amount <= 0:
            raise ValueError("Service amount must be greater than zero.")

        vendor_code = (vendor_code or "").strip()
        if not vendor_code:
            raise ValueError("SAP vendor code is required.")

        service_description = (
            service_description
            or f"Transport freight for dispatch bill {dispatch_plan.sap_invoice_doc_num}"
        ).strip()[:255]
        if not service_description:
            raise ValueError("Service description is required.")

        unit_price = Decimal(str(unit_price)) if unit_price is not None else amount
        place_of_supply = (place_of_supply or "").strip()
        budget_delivery_point = (budget_delivery_point or "").strip()
        location_name = (location_name or "").strip()
        sac_code = (sac_code or "").strip()
        product_variety = (product_variety or "").strip()
        invoice_number = (invoice_number or "").strip()
        eway_bill = (eway_bill or "").strip()
        total_litres = (
            Decimal(str(total_litres)) if total_litres not in (None, "") else None
        )
        invoice_weight = (
            Decimal(str(invoice_weight)) if invoice_weight not in (None, "") else None
        )
        invoice_amount = (
            Decimal(str(invoice_amount)) if invoice_amount not in (None, "") else None
        )

        if effective_month:
            effective_month = self._first_day_of_month(effective_month)

        grpo_posting = ServiceGRPOPosting.objects.create(
            dispatch_plan=dispatch_plan,
            vendor_code=vendor_code,
            vendor_name=dispatch_plan.transporter_name,
            place_of_supply=place_of_supply,
            effective_month=effective_month,
            budget_delivery_point=budget_delivery_point,
            location_code=location_code,
            location_name=location_name,
            sac_entry=sac_entry,
            sac_code=sac_code,
            product_variety=product_variety,
            total_litres=total_litres,
            status=GRPOStatus.PENDING,
            posted_by=user,
        )

        document_line = {
            "ItemDescription": service_description,
            "LineTotal": float(amount),
        }
        if unit_price is not None:
            document_line["UnitPrice"] = float(unit_price)
        if gl_account:
            document_line["AccountCode"] = gl_account
        if tax_code:
            document_line["TaxCode"] = tax_code
        if sac_entry:
            document_line["SACEntry"] = int(sac_entry)
        if location_code:
            document_line["LocationCode"] = int(location_code)
        if budget_delivery_point:
            document_line["ProjectCode"] = budget_delivery_point
        if total_litres is not None:
            document_line["U_UNE_LTS"] = float(total_litres)
        if dispatch_plan.bilty_no:
            document_line["U_BilltyNumber"] = dispatch_plan.bilty_no
        if invoice_number:
            document_line["U_ARNO"] = invoice_number
        remarks = []
        if product_variety:
            remarks.append(f"Variety: {product_variety}")
        if eway_bill:
            remarks.append(f"E-way Bill: {eway_bill}")
        if invoice_weight is not None:
            remarks.append(f"Charged Weight: {invoice_weight}")
        if remarks:
            document_line["U_Remarks"] = " | ".join(remarks)[:254]

        structured_comments = self._build_service_structured_comments(user, dispatch_plan)

        grpo_payload = {
            "DocType": "dDocument_Service",
            "CardCode": vendor_code,
            "BPL_IDAssignedToInvoice": branch_id,
            "Comments": structured_comments,
            "DocumentLines": [document_line],
        }
        if place_of_supply:
            grpo_payload["ShipPlace"] = place_of_supply
        if budget_delivery_point:
            grpo_payload["Project"] = budget_delivery_point
        if dispatch_plan.bilty_no:
            grpo_payload["U_BilltyNumber"] = dispatch_plan.bilty_no
            grpo_payload["U_LRNUmber"] = dispatch_plan.bilty_no
        if dispatch_plan.bilty_date:
            grpo_payload["U_BiltyDate"] = dispatch_plan.bilty_date.isoformat()
        if dispatch_plan.transporter_name:
            grpo_payload["U_TransporterName"] = dispatch_plan.transporter_name
        if dispatch_plan.vehicle_no:
            grpo_payload["U_VehicleNoM"] = dispatch_plan.vehicle_no
        if invoice_number:
            grpo_payload["U_ARNO"] = invoice_number
            grpo_payload["U_TransporterInvoice"] = invoice_number
        if total_litres is not None:
            grpo_payload["U_UNE_TOTL"] = float(total_litres)
        if invoice_amount is not None:
            grpo_payload["U_TotalAmt"] = float(invoice_amount)

        if doc_date:
            grpo_payload["DocDate"] = str(doc_date)
        if doc_due_date:
            grpo_payload["DocDueDate"] = str(doc_due_date)
        if tax_date:
            grpo_payload["TaxDate"] = str(tax_date)
        if vendor_ref:
            grpo_payload["NumAtCard"] = vendor_ref

        subtotal = amount
        if extra_charges:
            additional_expenses = []
            for charge in extra_charges:
                charge_amount = Decimal(str(charge["amount"]))
                subtotal += charge_amount
                expense = {
                    "ExpenseCode": charge["expense_code"],
                    "LineTotal": float(charge_amount),
                }
                if charge.get("remarks"):
                    expense["Remarks"] = charge["remarks"]
                if charge.get("tax_code"):
                    expense["TaxCode"] = charge["tax_code"]
                additional_expenses.append(expense)
            grpo_payload["DocumentAdditionalExpenses"] = additional_expenses

        if should_roundoff and subtotal > 0:
            rounded = subtotal.quantize(Decimal("1"), rounding="ROUND_HALF_UP")
            round_dif = float(rounded - subtotal)
            if round_dif != 0:
                grpo_payload["RoundDif"] = round_dif

        sap_client = SAPClient(company_code=self.company_code)
        attachment_records = []
        sap_absolute_entry = None

        if attachments:
            for uploaded_file in attachments:
                suffix = os.path.splitext(uploaded_file.name)[1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    for chunk in uploaded_file.chunks():
                        tmp.write(chunk)
                    tmp_path = tmp.name

                try:
                    if sap_absolute_entry:
                        sap_client.add_line_to_existing_attachment(
                            absolute_entry=sap_absolute_entry,
                            file_path=tmp_path,
                            filename=uploaded_file.name,
                        )
                        abs_entry = sap_absolute_entry
                    else:
                        sap_result = sap_client.upload_attachment(
                            file_path=tmp_path,
                            filename=uploaded_file.name,
                        )
                        abs_entry = sap_result.get("AbsoluteEntry")
                    if abs_entry:
                        sap_absolute_entry = abs_entry
                        attachment_records.append({
                            "file": uploaded_file,
                            "filename": uploaded_file.name,
                            "sap_absolute_entry": abs_entry,
                        })
                finally:
                    os.unlink(tmp_path)

            if sap_absolute_entry:
                grpo_payload["AttachmentEntry"] = sap_absolute_entry

        logger.info(
            "Service GRPO payload for dispatch plan %s: %s",
            dispatch_plan.id,
            grpo_payload,
        )

        try:
            result = sap_client.create_grpo(grpo_payload)

            grpo_posting.sap_doc_entry = result.get("DocEntry")
            grpo_posting.sap_doc_num = result.get("DocNum")
            grpo_posting.sap_doc_total = Decimal(str(result.get("DocTotal", 0)))
            grpo_posting.status = GRPOStatus.POSTED
            grpo_posting.posted_at = timezone.now()
            grpo_posting.posted_by = user
            grpo_posting.save()

            ServiceGRPOLinePosting.objects.create(
                service_grpo_posting=grpo_posting,
                service_description=service_description,
                amount=amount,
                unit_price=unit_price,
                tax_code=tax_code or "",
                gl_account=gl_account or "",
                sac_entry=sac_entry,
                sac_code=sac_code,
                location_code=location_code,
                location_name=location_name,
                project_code=budget_delivery_point,
                product_variety=product_variety,
                total_litres=total_litres,
            )

            for att_data in attachment_records:
                uploaded_file = att_data["file"]
                if hasattr(uploaded_file, "seek"):
                    uploaded_file.seek(0)
                ServiceGRPOAttachment.objects.create(
                    service_grpo_posting=grpo_posting,
                    file=uploaded_file,
                    original_filename=att_data["filename"],
                    sap_attachment_status=SAPAttachmentStatus.LINKED,
                    sap_absolute_entry=att_data["sap_absolute_entry"],
                    uploaded_by=user,
                )

            logger.info(
                "Service GRPO posted for dispatch plan %s. SAP DocNum: %s",
                dispatch_plan.id,
                grpo_posting.sap_doc_num,
            )
            return grpo_posting

        except SAPValidationError as e:
            grpo_posting.status = GRPOStatus.FAILED
            grpo_posting.error_message = str(e)
            grpo_posting.save()
            logger.error(f"SAP validation error posting service GRPO: {e}")
            raise

        except SAPConnectionError as e:
            grpo_posting.status = GRPOStatus.FAILED
            grpo_posting.error_message = "SAP system unavailable"
            grpo_posting.save()
            logger.error(f"SAP connection error posting service GRPO: {e}")
            raise

        except SAPDataError as e:
            grpo_posting.status = GRPOStatus.FAILED
            grpo_posting.error_message = str(e)
            grpo_posting.save()
            logger.error(f"SAP data error posting service GRPO: {e}")
            raise

    def get_service_grpo_posting_history(
        self,
        dispatch_plan_id: Optional[int] = None,
    ) -> List[ServiceGRPOPosting]:
        """Get service GRPO posting history."""
        queryset = ServiceGRPOPosting.objects.select_related(
            "dispatch_plan",
            "posted_by",
        ).prefetch_related("lines", "attachments")

        if dispatch_plan_id:
            queryset = queryset.filter(dispatch_plan_id=dispatch_plan_id)

        return queryset.order_by("-created_at")

    def get_service_grpo_options(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get SAP master-data options used by the service GRPO form."""
        sap_client = SAPClient(company_code=self.company_code)
        return sap_client.get_service_grpo_options()

    def get_grpo_posting_history(
        self,
        vehicle_entry_id: Optional[int] = None
    ) -> List[GRPOPosting]:
        """Get GRPO posting history."""
        queryset = GRPOPosting.objects.select_related(
            "vehicle_entry",
            "po_receipt",
            "posted_by"
        ).prefetch_related("lines", "attachments", "po_receipts")

        if vehicle_entry_id:
            queryset = queryset.filter(vehicle_entry_id=vehicle_entry_id)

        return queryset.order_by("-created_at")

    def upload_grpo_attachment(
        self,
        grpo_posting_id: int,
        file,
        user
    ) -> GRPOAttachment:
        """
        Upload an attachment for a GRPO posting.
        1. Save file locally (via Django FileField)
        2. Upload to SAP Attachments2 endpoint
        3. Link to the GRPO document via PATCH
        4. Update local record with SAP response
        """
        # Validate GRPO posting exists and is POSTED
        try:
            grpo_posting = GRPOPosting.objects.get(id=grpo_posting_id)
        except GRPOPosting.DoesNotExist:
            raise ValueError(f"GRPO posting {grpo_posting_id} not found")

        if grpo_posting.status != GRPOStatus.POSTED:
            raise ValueError(
                f"Cannot attach files to GRPO with status '{grpo_posting.status}'. "
                f"Only POSTED GRPOs accept attachments."
            )

        if not grpo_posting.sap_doc_entry:
            raise ValueError("GRPO posting has no SAP DocEntry. Cannot upload attachment.")

        # Step 1: Save file locally
        attachment = GRPOAttachment.objects.create(
            grpo_posting=grpo_posting,
            file=file,
            original_filename=file.name,
            sap_attachment_status=SAPAttachmentStatus.PENDING,
            uploaded_by=user,
        )

        # Step 2: Upload to SAP
        try:
            sap_client = SAPClient(company_code=self.company_code)

            # Check if the GRPO already has an AttachmentEntry
            existing_abs_entry = sap_client.get_grpo_attachment_entry(
                grpo_posting.sap_doc_entry
            )

            if existing_abs_entry:
                # Add a new line to the existing Attachments2 entry.
                # This avoids PATCHing the GRPO document which triggers
                # SAP approval error (200039).
                sap_result = sap_client.add_line_to_existing_attachment(
                    absolute_entry=existing_abs_entry,
                    file_path=attachment.file.path,
                    filename=attachment.original_filename,
                )
                attachment.sap_absolute_entry = existing_abs_entry
                attachment.sap_attachment_status = SAPAttachmentStatus.LINKED
                attachment.save(update_fields=[
                    "sap_absolute_entry", "sap_attachment_status"
                ])
            else:
                # No existing attachment — upload and include in GRPO
                sap_result = sap_client.upload_attachment(
                    file_path=attachment.file.path,
                    filename=attachment.original_filename
                )
                absolute_entry = sap_result.get("AbsoluteEntry")
                if not absolute_entry:
                    raise SAPDataError("SAP did not return AbsoluteEntry")

                attachment.sap_absolute_entry = absolute_entry
                attachment.sap_attachment_status = SAPAttachmentStatus.UPLOADED
                attachment.save(update_fields=[
                    "sap_absolute_entry", "sap_attachment_status"
                ])

                # Link attachment to the GRPO document
                sap_client.link_attachment_to_grpo(
                    doc_entry=grpo_posting.sap_doc_entry,
                    absolute_entry=absolute_entry
                )
                attachment.sap_attachment_status = SAPAttachmentStatus.LINKED
                attachment.save(update_fields=["sap_attachment_status"])

            logger.info(
                f"Attachment '{attachment.original_filename}' uploaded and linked "
                f"to GRPO DocEntry {grpo_posting.sap_doc_entry}"
            )

            return attachment

        except (SAPValidationError, SAPConnectionError, SAPDataError) as e:
            attachment.sap_attachment_status = SAPAttachmentStatus.FAILED
            attachment.sap_error_message = str(e)
            attachment.save(update_fields=[
                "sap_attachment_status", "sap_error_message"
            ])
            logger.error(
                f"Failed to upload attachment for GRPO {grpo_posting_id}: {e}"
            )
            # Return attachment with FAILED status — file is saved locally
            return attachment

    def retry_attachment_upload(
        self,
        attachment_id: int,
    ) -> GRPOAttachment:
        """
        Retry uploading a FAILED attachment to SAP.
        If upload succeeded but link failed, skips re-upload.
        """
        try:
            attachment = GRPOAttachment.objects.select_related(
                "grpo_posting"
            ).get(id=attachment_id)
        except GRPOAttachment.DoesNotExist:
            raise ValueError(f"Attachment {attachment_id} not found")

        if attachment.sap_attachment_status not in [
            SAPAttachmentStatus.PENDING,
            SAPAttachmentStatus.FAILED
        ]:
            raise ValueError(
                f"Attachment is already '{attachment.sap_attachment_status}'. "
                f"Only PENDING or FAILED attachments can be retried."
            )

        grpo_posting = attachment.grpo_posting
        if not grpo_posting.sap_doc_entry:
            raise ValueError("GRPO posting has no SAP DocEntry.")

        try:
            sap_client = SAPClient(company_code=self.company_code)

            # Check if GRPO already has an AttachmentEntry
            existing_abs_entry = sap_client.get_grpo_attachment_entry(
                grpo_posting.sap_doc_entry
            )

            if existing_abs_entry:
                # Add line to existing Attachments2 entry (avoids approval error)
                sap_client.add_line_to_existing_attachment(
                    absolute_entry=existing_abs_entry,
                    file_path=attachment.file.path,
                    filename=attachment.original_filename,
                )
                attachment.sap_absolute_entry = existing_abs_entry
                attachment.sap_attachment_status = SAPAttachmentStatus.LINKED
                attachment.sap_error_message = None
                attachment.save(update_fields=[
                    "sap_absolute_entry", "sap_attachment_status",
                    "sap_error_message"
                ])
            else:
                # No existing attachment — upload and link
                if attachment.sap_absolute_entry:
                    absolute_entry = attachment.sap_absolute_entry
                else:
                    sap_result = sap_client.upload_attachment(
                        file_path=attachment.file.path,
                        filename=attachment.original_filename
                    )
                    absolute_entry = sap_result.get("AbsoluteEntry")
                    if not absolute_entry:
                        raise SAPDataError("SAP did not return AbsoluteEntry")

                    attachment.sap_absolute_entry = absolute_entry
                    attachment.sap_attachment_status = SAPAttachmentStatus.UPLOADED
                    attachment.save(update_fields=[
                        "sap_absolute_entry", "sap_attachment_status"
                    ])

                sap_client.link_attachment_to_grpo(
                    doc_entry=grpo_posting.sap_doc_entry,
                    absolute_entry=absolute_entry
                )
                attachment.sap_attachment_status = SAPAttachmentStatus.LINKED
                attachment.sap_error_message = None
                attachment.save(update_fields=[
                    "sap_attachment_status", "sap_error_message"
                ])

            return attachment

        except (SAPValidationError, SAPConnectionError, SAPDataError) as e:
            attachment.sap_attachment_status = SAPAttachmentStatus.FAILED
            attachment.sap_error_message = str(e)
            attachment.save(update_fields=[
                "sap_attachment_status", "sap_error_message"
            ])
            return attachment
