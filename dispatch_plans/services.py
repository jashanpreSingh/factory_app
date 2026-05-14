from datetime import datetime, timezone
from typing import Any, Dict, List

from company.models import Company
from driver_management.models import Driver, VehicleEntry
from sap_client.context import CompanyContext
from vehicle_management.models import Transporter, Vehicle

from .hana_reader import HanaDispatchBillReader
from .models import DispatchPlan, DispatchPlanStatus
from .serializers import DispatchPlanSerializer


class DispatchPlansService:
    def __init__(self, company_code: str):
        self.company_code = company_code
        self.company = Company.objects.get(code=company_code)
        self.context = CompanyContext(company_code)
        self.reader = HanaDispatchBillReader(self.context)

    def get_bills(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        rows = self.reader.list_bills(filters)
        doc_entries = [row["doc_entry"] for row in rows]
        plans = {
            plan.sap_invoice_doc_entry: plan
            for plan in DispatchPlan.objects.filter(
                company=self.company,
                sap_invoice_doc_entry__in=doc_entries,
                is_active=True,
            )
        }

        data = []
        for row in rows:
            plan = plans.get(row["doc_entry"])
            row["plan"] = (
                DispatchPlanSerializer(plan).data
                if plan
                else self._empty_plan(row["doc_entry"], row["doc_num"])
            )
            data.append(row)

        booking_status = filters.get("booking_status") or "all"
        if booking_status != "all":
            data = [
                row
                for row in data
                if row["plan"]["booking_status"] == booking_status
            ]

        search = (filters.get("search") or "").strip().lower()
        if search:
            data = [row for row in data if self._matches_search(row, search)]

        return {
            "data": data,
            "meta": self._build_meta(data),
        }

    def get_bill_by_number(self, invoice_number: str) -> Dict[str, Any] | None:
        bill = self.reader.get_bill_by_number(invoice_number.strip())
        if not bill:
            return None

        plan = DispatchPlan.objects.filter(
            company=self.company,
            sap_invoice_doc_entry=bill["doc_entry"],
            is_active=True,
        ).first()
        bill["plan"] = (
            DispatchPlanSerializer(plan).data
            if plan
            else self._empty_plan(bill["doc_entry"], bill["doc_num"])
        )
        return bill

    def update_plan(
        self,
        sap_invoice_doc_entry: int,
        data: Dict[str, Any],
        user,
    ) -> DispatchPlan:
        doc_num = data.pop("sap_invoice_doc_num", "")
        bilty_attachment = data.get("bilty_attachment")
        self._validate_links(data)
        self._apply_master_data(data)
        plan, created = DispatchPlan.objects.get_or_create(
            company=self.company,
            sap_invoice_doc_entry=sap_invoice_doc_entry,
            defaults={
                "sap_invoice_doc_num": doc_num,
                "created_by": user,
                "updated_by": user,
            },
        )

        if doc_num:
            plan.sap_invoice_doc_num = doc_num

        for field, value in data.items():
            setattr(plan, field, value)

        if created and not plan.booking_status:
            plan.booking_status = DispatchPlanStatus.PENDING

        if bilty_attachment:
            plan.bilty_attachment_name = getattr(
                bilty_attachment,
                "name",
                plan.bilty_attachment_name,
            )

        if plan.booking_status == DispatchPlanStatus.BOOKED and not plan.bilty_no.strip():
            raise ValueError("Bilty number is required before booking the dispatch vehicle.")

        plan.updated_by = user
        plan.save()
        return plan

    def _empty_plan(self, doc_entry: int, doc_num: str) -> Dict[str, Any]:
        return {
            "id": None,
            "sap_invoice_doc_entry": doc_entry,
            "sap_invoice_doc_num": doc_num,
            "vehicle_id": None,
            "transporter_id": None,
            "driver_id": None,
            "linked_vehicle_entry_id": None,
            "booking_status": DispatchPlanStatus.PENDING,
            "dispatch_date": None,
            "priority": "",
            "transporter_name": "",
            "transporter_gstin": "",
            "contact_person": "",
            "mobile_no": "",
            "vehicle_no": "",
            "driver_name": "",
            "driver_mobile_no": "",
            "driver_license_no": "",
            "driver_id_proof_type": "",
            "driver_id_proof_number": "",
            "bilty_no": "",
            "bilty_date": None,
            "freight": None,
            "total_freight": None,
            "kanta_weight": None,
            "remarks": "",
            "created_at": None,
            "updated_at": None,
        }

    @staticmethod
    def _matches_search(row: Dict[str, Any], search: str) -> bool:
        plan = row.get("plan") or {}
        values = [
            row.get("doc_num"),
            row.get("card_code"),
            row.get("card_name"),
            row.get("ship_to_code"),
            row.get("ship_to_address"),
            row.get("state"),
            row.get("city"),
            row.get("bp_gstin"),
            row.get("sap_bilty_no"),
            row.get("sap_transporter_name"),
            row.get("sap_vehicle_no"),
            row.get("sap_transporter_invoice"),
            row.get("sap_lr_number"),
            row.get("gst_vehicle_no"),
            row.get("warehouses"),
            row.get("item_summary"),
            row.get("base_refs"),
            plan.get("transporter_name"),
            plan.get("transporter_gstin"),
            plan.get("contact_person"),
            plan.get("mobile_no"),
            plan.get("vehicle_no"),
            plan.get("driver_name"),
            plan.get("driver_mobile_no"),
            plan.get("driver_license_no"),
            plan.get("bilty_no"),
            plan.get("remarks"),
        ]
        return any(search in str(value or "").lower() for value in values)

    def _validate_links(self, data: Dict[str, Any]) -> None:
        vehicle_id = data.get("vehicle_id")
        if vehicle_id and not Vehicle.objects.filter(pk=vehicle_id, is_active=True).exists():
            raise ValueError("Selected vehicle does not exist.")

        transporter_id = data.get("transporter_id")
        if transporter_id and not Transporter.objects.filter(
            pk=transporter_id,
            is_active=True,
        ).exists():
            raise ValueError("Selected transporter does not exist.")

        driver_id = data.get("driver_id")
        if driver_id and not Driver.objects.filter(pk=driver_id, is_active=True).exists():
            raise ValueError("Selected driver does not exist.")

        linked_vehicle_entry_id = data.get("linked_vehicle_entry_id")
        if linked_vehicle_entry_id and not VehicleEntry.objects.filter(
            pk=linked_vehicle_entry_id,
            company=self.company,
        ).exists():
            raise ValueError("Selected gate vehicle entry does not exist for this company.")

    @staticmethod
    def _apply_master_data(data: Dict[str, Any]) -> None:
        vehicle = None
        vehicle_id = data.get("vehicle_id")
        if vehicle_id:
            vehicle = Vehicle.objects.select_related("transporter").get(pk=vehicle_id)
            data["vehicle_no"] = vehicle.vehicle_number
            if vehicle.transporter_id and not data.get("transporter_id"):
                data["transporter_id"] = vehicle.transporter_id
        elif "vehicle_id" in data:
            data["vehicle_no"] = ""

        transporter = None
        transporter_id = data.get("transporter_id")
        if transporter_id:
            transporter = Transporter.objects.get(pk=transporter_id)
        elif vehicle and vehicle.transporter_id:
            transporter = vehicle.transporter

        if transporter:
            data["transporter_name"] = transporter.name
            data["transporter_gstin"] = getattr(
                transporter,
                "gstin",
                data.get("transporter_gstin", ""),
            )
            data["contact_person"] = transporter.contact_person
            data["mobile_no"] = transporter.mobile_no
        elif "transporter_id" in data:
            data["transporter_name"] = ""
            data["transporter_gstin"] = ""
            data["contact_person"] = ""
            data["mobile_no"] = ""

        driver_id = data.get("driver_id")
        if driver_id:
            driver = Driver.objects.get(pk=driver_id)
            data["driver_name"] = driver.name
            data["driver_mobile_no"] = driver.mobile_no
            data["driver_license_no"] = driver.license_no
            data["driver_id_proof_type"] = driver.id_proof_type
            data["driver_id_proof_number"] = driver.id_proof_number
        elif "driver_id" in data:
            data["driver_name"] = ""
            data["driver_mobile_no"] = ""
            data["driver_license_no"] = ""
            data["driver_id_proof_type"] = ""
            data["driver_id_proof_number"] = ""

    @staticmethod
    def _build_meta(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
        statuses = [row["plan"]["booking_status"] for row in rows]
        return {
            "total_bills": len(rows),
            "pending_count": statuses.count(DispatchPlanStatus.PENDING),
            "booked_count": statuses.count(DispatchPlanStatus.BOOKED),
            "dispatched_count": statuses.count(DispatchPlanStatus.DISPATCHED),
            "cancelled_count": statuses.count(DispatchPlanStatus.CANCELLED),
            "total_doc_value": round(sum(row["doc_total"] for row in rows), 2),
            "total_litres": round(sum(row["total_litres"] for row in rows), 3),
            "total_boxes": round(sum(row["total_boxes"] for row in rows), 3),
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }
