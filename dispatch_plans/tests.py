from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase
from django.http import QueryDict

from company.models import Company
from driver_management.models import Driver, VehicleEntry
from gate_core.enums import GateEntryStatus
from vehicle_management.models import Transporter, Vehicle, VehicleType

from .models import DispatchPlan
from .serializers import DispatchPlanUpdateSerializer
from .services import DispatchPlansService

User = get_user_model()


class DispatchPlanUpdateSerializerTests(SimpleTestCase):
    def test_linked_invoice_doc_entries_accepts_json_integer_list(self):
        serializer = DispatchPlanUpdateSerializer(
            data={"linked_invoice_doc_entries": [72826, 72815]},
            partial=True,
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(
            serializer.validated_data["linked_invoice_doc_entries"],
            [72826, 72815],
        )

    def test_linked_invoice_doc_entries_accepts_repeated_multipart_values(self):
        serializer = DispatchPlanUpdateSerializer(
            data={"linked_invoice_doc_entries": ["72826", "72815"]},
            partial=True,
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(
            serializer.validated_data["linked_invoice_doc_entries"],
            [72826, 72815],
        )

    def test_linked_invoice_doc_entries_accepts_comma_separated_multipart_value(self):
        serializer = DispatchPlanUpdateSerializer(
            data={"linked_invoice_doc_entries": "72826,72815"},
            partial=True,
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(
            serializer.validated_data["linked_invoice_doc_entries"],
            [72826, 72815],
        )

    def test_linked_invoice_doc_entries_accepts_querydict_comma_value(self):
        data = QueryDict("", mutable=True)
        data.update({"linked_invoice_doc_entries": "72826,72815"})

        serializer = DispatchPlanUpdateSerializer(data=data, partial=True)

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(
            serializer.validated_data["linked_invoice_doc_entries"],
            [72826, 72815],
        )

    def test_linked_invoice_doc_entries_rejects_non_integer_values(self):
        serializer = DispatchPlanUpdateSerializer(
            data={"linked_invoice_doc_entries": "72826,nope"},
            partial=True,
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("linked_invoice_doc_entries", serializer.errors)


class DispatchPlanInvoiceDefaultsTests(SimpleTestCase):
    def test_mineral_water_invoice_defaults_to_beverage_variety(self):
        self.assertEqual(
            DispatchPlansService._infer_product_variety(
                "FG0000324 - PET BOTTLE 500 ML JIVO NATURAL MINERAL SPECIAL EDITION"
            ),
            "Beverage",
        )


class DispatchPlanLinkedVehicleEntryTests(TestCase):
    def test_update_with_linked_vehicle_entry_hydrates_dispatch_snapshots(self):
        company = Company.objects.create(name="Test Company", code="JIVO_OIL")
        user = User.objects.create_user(
            email="dispatch-user@example.com",
            password="testpass123",
            full_name="Dispatch User",
        )
        transporter = Transporter.objects.create(
            name="Linked Transporter",
            contact_person="Transport Contact",
            mobile_no="9999999999",
            gstin="07ABCDE1234F1Z5",
        )
        vehicle_type = VehicleType.objects.create(name="Container")
        vehicle = Vehicle.objects.create(
            vehicle_number="DL01AB1234",
            vehicle_type=vehicle_type,
            transporter=transporter,
        )
        driver = Driver.objects.create(
            name="Linked Driver",
            mobile_no="8888888888",
            license_no="DL-LINK-123",
            id_proof_type="AADHAAR",
            id_proof_number="123412341234",
        )
        linked_entry = VehicleEntry.objects.create(
            entry_no="VE-DISP-001",
            company=company,
            vehicle=vehicle,
            driver=driver,
            entry_type="EMPTY_VEHICLE",
            status=GateEntryStatus.COMPLETED,
        )

        service = DispatchPlansService(company_code=company.code)
        plan = service._update_single_plan(
            sap_invoice_doc_entry=626050517,
            data={"linked_vehicle_entry_id": linked_entry.id},
            user=user,
        )

        plan = DispatchPlan.objects.get(pk=plan.pk)
        self.assertEqual(plan.linked_vehicle_entry_id, linked_entry.id)
        self.assertEqual(plan.vehicle_id, vehicle.id)
        self.assertEqual(plan.driver_id, driver.id)
        self.assertEqual(plan.transporter_id, transporter.id)
        self.assertEqual(plan.vehicle_no, "DL01AB1234")
        self.assertEqual(plan.driver_name, "Linked Driver")
        self.assertEqual(plan.driver_mobile_no, "8888888888")
        self.assertEqual(plan.driver_license_no, "DL-LINK-123")
        self.assertEqual(plan.driver_id_proof_type, "AADHAAR")
        self.assertEqual(plan.driver_id_proof_number, "123412341234")
        self.assertEqual(plan.transporter_name, "Linked Transporter")
        self.assertEqual(plan.transporter_gstin, "07ABCDE1234F1Z5")
        self.assertEqual(plan.contact_person, "Transport Contact")
        self.assertEqual(plan.mobile_no, "9999999999")
