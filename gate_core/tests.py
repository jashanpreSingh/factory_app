from decimal import Decimal

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from company.models import Company, UserCompany, UserRole
from dispatch_plans.models import DispatchPlan, DispatchPlanStatus
from driver_management.models import Driver, VehicleEntry
from gate_core.models import (
    SalesDispatchDocumentType,
    SalesDispatchGateOut,
    SalesDispatchGateOutItem,
    SalesDispatchGateOutStatus,
    SalesDispatchLock,
)
from vehicle_management.models import Transporter, Vehicle
from weighment.models import Weighment


class SalesDispatchAPITests(APITestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            email="dock.test@example.com",
            password="testpass",
            full_name="Dock Test User",
            employee_code="DCK001",
        )
        self.company = Company.objects.create(name="Jivo Oil", code="JIVO_OIL")
        self.role = UserRole.objects.create(name="Admin")
        UserCompany.objects.create(
            user=self.user,
            company=self.company,
            role=self.role,
            is_default=True,
        )
        self.transporter = Transporter.objects.create(name="Test Transporter")
        self.vehicle = Vehicle.objects.create(
            vehicle_number="DL01AC0001",
            transporter=self.transporter,
        )
        self.driver = Driver.objects.create(
            name="Test Driver",
            mobile_no="9999999999",
            license_no="DL-TEST-001",
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        self.company_header = {"HTTP_COMPANY_CODE": self.company.code}

    def create_sales_dispatch(
        self,
        suffix,
        *,
        status_value=SalesDispatchGateOutStatus.DOCKED,
        document_type=SalesDispatchDocumentType.INVOICE,
        dispatch_plan=None,
        with_photo=False,
        with_item=False,
        with_weighment=False,
    ):
        vehicle_entry = VehicleEntry.objects.create(
            entry_no=f"DOCKV-TEST-{suffix}",
            company=self.company,
            vehicle=self.vehicle,
            driver=self.driver,
            entry_type="SALES_DISPATCH",
            status="IN_PROGRESS",
            created_by=self.user,
            updated_by=self.user,
        )
        entry = SalesDispatchGateOut.objects.create(
            company=self.company,
            entry_no=f"DOCK-TEST-{suffix}",
            vehicle_entry=vehicle_entry,
            dispatch_plan=dispatch_plan,
            vehicle=self.vehicle,
            transporter=self.transporter,
            driver=self.driver,
            document_type=document_type,
            sap_doc_entry=1000 + int(suffix),
            sap_doc_num=f"INV-{suffix}",
            customer_code=f"C{suffix}",
            customer_name=f"Customer {suffix}",
            vehicle_no=self.vehicle.vehicle_number,
            transporter_name=self.transporter.name,
            driver_name=self.driver.name,
            driver_mobile_no=self.driver.mobile_no,
            status=status_value,
            truck_photo=f"sales_dispatch/truck_photos/{suffix}.jpg" if with_photo else None,
            photo_latitude=Decimal("28.613900") if with_photo else None,
            photo_longitude=Decimal("77.209000") if with_photo else None,
            created_by=self.user,
            updated_by=self.user,
        )
        if with_item:
            SalesDispatchGateOutItem.objects.create(
                sales_dispatch=entry,
                line_num=0,
                item_code=f"ITEM-{suffix}",
                item_name="Test Item",
                quantity=Decimal("10.000"),
                uom="BOX",
                created_by=self.user,
                updated_by=self.user,
            )
        if with_weighment:
            Weighment.objects.create(
                vehicle_entry=vehicle_entry,
                gross_weight=Decimal("1000.000"),
                tare_weight=Decimal("250.000"),
                created_by=self.user,
                updated_by=self.user,
            )
        return entry

    def test_lock_endpoint_creates_default_unlocked_state(self):
        response = self.client.get(
            "/api/v1/gate-core/sales-dispatch/lock/",
            **self.company_header,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["is_locked"])
        self.assertEqual(response.data["reason"], "")
        self.assertTrue(SalesDispatchLock.objects.filter(company=self.company).exists())

    def test_lock_requires_reason_when_locking(self):
        response = self.client.patch(
            "/api/v1/gate-core/sales-dispatch/lock/",
            {"is_locked": True, "reason": ""},
            format="json",
            **self.company_header,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("reason", response.data)

    def test_locked_docking_blocks_gatepass_print_and_commit(self):
        print_entry = self.create_sales_dispatch(
            "1",
            status_value=SalesDispatchGateOutStatus.READY_FOR_GATEPASS,
        )
        commit_entry = self.create_sales_dispatch(
            "2",
            status_value=SalesDispatchGateOutStatus.GATEPASS_PRINTED,
        )
        commit_entry.gatepass_no = "DCK/JIVO_OIL/2026-27/000001"
        commit_entry.save(update_fields=["gatepass_no"])
        SalesDispatchLock.objects.create(
            company=self.company,
            is_locked=True,
            reason="Monthly close",
            changed_by=self.user,
        )

        print_response = self.client.post(
            f"/api/v1/gate-core/sales-dispatch/{print_entry.id}/gatepass/print/",
            {},
            format="json",
            **self.company_header,
        )
        commit_response = self.client.post(
            f"/api/v1/gate-core/sales-dispatch/{commit_entry.id}/commit-print/",
            {},
            format="json",
            **self.company_header,
        )

        self.assertEqual(print_response.status_code, 423)
        self.assertEqual(commit_response.status_code, 423)
        print_entry.refresh_from_db()
        commit_entry.refresh_from_db()
        self.assertIsNone(print_entry.gatepass_no)
        self.assertEqual(print_entry.status, SalesDispatchGateOutStatus.READY_FOR_GATEPASS)
        self.assertEqual(commit_entry.status, SalesDispatchGateOutStatus.GATEPASS_PRINTED)

    def test_reports_return_operational_counts(self):
        self.create_sales_dispatch("10", status_value=SalesDispatchGateOutStatus.DOCKED)
        self.create_sales_dispatch(
            "11",
            status_value=SalesDispatchGateOutStatus.READY_FOR_GATEPASS,
            with_photo=True,
        )
        self.create_sales_dispatch(
            "12",
            status_value=SalesDispatchGateOutStatus.GATEPASS_PRINTED,
            with_photo=True,
        )
        self.create_sales_dispatch(
            "13",
            status_value=SalesDispatchGateOutStatus.PRINT_COMMITTED,
            with_photo=True,
        )
        self.create_sales_dispatch("14", status_value=SalesDispatchGateOutStatus.DISPATCHED)
        self.create_sales_dispatch("15", status_value=SalesDispatchGateOutStatus.CANCELLED)
        self.create_sales_dispatch("16", status_value=SalesDispatchGateOutStatus.REJECTED)

        response = self.client.get(
            "/api/v1/gate-core/sales-dispatch/reports/",
            **self.company_header,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["counts"],
            {
                "total": 7,
                "waiting_inside": 4,
                "missing_photo": 1,
                "gatepass_pending": 2,
                "printed_not_committed": 1,
                "ready_for_dispatch": 1,
                "dispatched": 1,
                "rejected_cancelled": 2,
            },
        )
        self.assertEqual(len(response.data["waiting_inside"]), 4)
        self.assertEqual(len(response.data["missing_photo"]), 1)
        self.assertEqual(len(response.data["ready_for_dispatch"]), 1)
        self.assertEqual(len(response.data["rejected_cancelled"]), 2)

    def test_mark_dispatched_completes_vehicle_entry_and_dispatch_plan(self):
        plan = DispatchPlan.objects.create(
            company=self.company,
            sap_invoice_doc_entry=99001,
            sap_invoice_doc_num="99001",
            booking_status=DispatchPlanStatus.BOOKED,
            vehicle=self.vehicle,
            transporter=self.transporter,
            driver=self.driver,
            created_by=self.user,
            updated_by=self.user,
        )
        entry = self.create_sales_dispatch(
            "20",
            status_value=SalesDispatchGateOutStatus.PRINT_COMMITTED,
            dispatch_plan=plan,
            with_photo=True,
            with_item=True,
            with_weighment=True,
        )
        entry.gatepass_no = "DCK/JIVO_OIL/2026-27/000020"
        entry.print_committed_at = timezone.now()
        entry.save(update_fields=["gatepass_no", "print_committed_at"])

        response = self.client.post(
            f"/api/v1/gate-core/sales-dispatch/{entry.id}/dispatch/",
            {},
            format="json",
            **self.company_header,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        entry.refresh_from_db()
        entry.vehicle_entry.refresh_from_db()
        plan.refresh_from_db()
        self.assertEqual(entry.status, SalesDispatchGateOutStatus.DISPATCHED)
        self.assertEqual(entry.vehicle_entry.status, "COMPLETED")
        self.assertEqual(plan.booking_status, DispatchPlanStatus.DISPATCHED)

    def test_mark_dispatched_requires_committed_gatepass_audit(self):
        entry = self.create_sales_dispatch(
            "21",
            status_value=SalesDispatchGateOutStatus.PRINT_COMMITTED,
        )

        response = self.client.post(
            f"/api/v1/gate-core/sales-dispatch/{entry.id}/dispatch/",
            {},
            format="json",
            **self.company_header,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Gatepass number", response.data["detail"])
        entry.refresh_from_db()
        self.assertEqual(entry.status, SalesDispatchGateOutStatus.PRINT_COMMITTED)
