import json
from datetime import date
from decimal import Decimal

from django.test import TestCase
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from accounts.models import User
from company.models import Company

from .models import (
    BarcodeSequence,
    Box,
    BoxMovement,
    BoxMovementType,
    BoxStatus,
    EntityType,
    LabelPrintLog,
    LooseStockStatus,
    PalletMovement,
    PalletStatus,
    ScanLog,
    ScanResult,
)
from .serializers import (
    BoxGenerateSerializer,
    BoxListSerializer,
    MAX_BOX_LABELS_PER_REQUEST,
    PalletCreateSerializer,
)
from .services.barcode_service import BarcodeService
from .services.label_service import LabelService
from .services.production_release_service import ProductionReleaseOilService
from .services.scan_service import ScanService
from .views import _list_response


class BarcodeWorkflowTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(
            name='Barcode Test Company',
            code='TESTCO',
        )
        self.user = User.objects.create_user(
            email='barcode@example.com',
            password='test-pass',
            full_name='Barcode Tester',
            employee_code='EMP-BC-001',
        )
        self.service = BarcodeService(company_code=self.company.code)
        self.label_service = LabelService(company_code=self.company.code)
        self.scan_service = ScanService(company_code=self.company.code)

    def _generate_boxes(self, count=3, qty='12.50', line='Line 1', batch='BATCH-001'):
        return self.service.generate_boxes(
            {
                'item_code': 'FG001',
                'item_name': 'Test Finished Good',
                'batch_number': batch,
                'qty': Decimal(qty),
                'box_count': count,
                'uom': 'PCS',
                'mfg_date': date(2026, 5, 7),
                'exp_date': date(2027, 5, 7),
                'warehouse': 'FG01',
                'production_line': line,
            },
            user=self.user,
        )

    def test_generate_boxes_reserves_unique_sequence_and_logs_movements(self):
        boxes = self._generate_boxes(count=3)

        self.assertEqual(
            [box.box_barcode for box in boxes],
            [
                'BOX-20260507-Line_1-0001',
                'BOX-20260507-Line_1-0002',
                'BOX-20260507-Line_1-0003',
            ],
        )
        self.assertEqual(Box.objects.count(), 3)
        self.assertEqual(
            BoxMovement.objects.filter(movement_type=BoxMovementType.CREATE).count(),
            3,
        )
        self.assertEqual(
            [box.barcode_data for box in boxes],
            [{'barcode': box.box_barcode} for box in boxes],
        )

        sequence = BarcodeSequence.objects.get(
            company=self.company,
            sequence_type='BOX',
            date_str='20260507',
            line_key='Line_1',
        )
        self.assertEqual(sequence.next_value, 4)

        more_boxes = self._generate_boxes(count=2)
        self.assertEqual(
            [box.box_barcode for box in more_boxes],
            [
                'BOX-20260507-Line_1-0004',
                'BOX-20260507-Line_1-0005',
            ],
        )

    def test_list_response_returns_page_metadata_when_requested(self):
        self._generate_boxes(count=3)
        request = Request(APIRequestFactory().get('/barcode/boxes/?page=1&page_size=2'))

        response = _list_response(request, self.service.list_boxes(), BoxListSerializer)

        self.assertEqual(response.data['count'], 3)
        self.assertEqual(response.data['page'], 1)
        self.assertEqual(response.data['page_size'], 2)
        self.assertEqual(response.data['total_pages'], 2)
        self.assertTrue(response.data['next'])
        self.assertFalse(response.data['previous'])
        self.assertEqual(len(response.data['results']), 2)

    def test_list_response_keeps_legacy_array_shape_without_page_params(self):
        self._generate_boxes(count=2)
        request = Request(APIRequestFactory().get('/barcode/boxes/'))

        response = _list_response(request, self.service.list_boxes(), BoxListSerializer)

        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 2)

    def test_create_pallet_creates_empty_pallet_then_adds_boxes(self):
        boxes = self._generate_boxes(count=3)

        pallet = self.service.create_pallet(
            {
                'box_ids': [],
                'warehouse': 'FG01',
                'production_line': 'Line 1',
                'mfg_date': date(2026, 5, 7),
            },
            user=self.user,
        )

        self.assertEqual(pallet.pallet_id, 'PLT-20260507-Line_1-001')
        self.assertEqual(pallet.box_count, 0)
        self.assertEqual(pallet.total_qty, Decimal('0'))
        self.assertEqual(PalletMovement.objects.count(), 1)

        pallet = self.service.add_boxes_to_pallet(
            pallet.id,
            [box.id for box in boxes],
            user=self.user,
        )
        self.assertEqual(pallet.box_count, 3)
        self.assertEqual(pallet.total_qty, Decimal('37.50'))
        self.assertEqual(pallet.item_code, 'FG001')
        self.assertEqual(pallet.item_name, 'Test Finished Good')
        self.assertEqual(pallet.batch_number, 'BATCH-001')
        self.assertEqual(pallet.uom, 'PCS')
        self.assertEqual(pallet.mfg_date, date(2026, 5, 7))
        self.assertEqual(pallet.exp_date, date(2027, 5, 7))
        self.assertEqual(
            Box.objects.filter(pallet=pallet, current_warehouse='FG01').count(),
            3,
        )
        self.assertEqual(pallet.barcode_data, {'barcode': pallet.pallet_id})

    def test_add_boxes_to_pallet_rejects_mismatched_item_context(self):
        boxes = self._generate_boxes(count=1)
        pallet = self.service.create_pallet(
            {
                'box_ids': [],
                'warehouse': 'FG01',
                'production_line': 'Line 1',
                'mfg_date': date(2026, 5, 7),
            },
            user=self.user,
        )
        self.service.add_boxes_to_pallet(pallet.id, [boxes[0].id], user=self.user)

        other_box = self.service.generate_boxes(
            {
                'item_code': 'FG002',
                'item_name': 'Other Finished Good',
                'batch_number': 'BATCH-002',
                'qty': Decimal('12.50'),
                'box_count': 1,
                'uom': 'PCS',
                'mfg_date': date(2026, 5, 7),
                'exp_date': date(2027, 5, 7),
                'warehouse': 'FG01',
                'production_line': 'Line 1',
            },
            user=self.user,
        )[0]

        with self.assertRaisesMessage(
            ValueError,
            "Box item, batch, or UOM does not match the target pallet.",
        ):
            self.service.add_boxes_to_pallet(pallet.id, [other_box.id], user=self.user)

        other_box.refresh_from_db()
        pallet.refresh_from_db()
        self.assertIsNone(other_box.pallet)
        self.assertEqual(pallet.box_count, 1)

    def test_add_boxes_to_pallet_enforces_capacity(self):
        boxes = self._generate_boxes(count=2)
        pallet = self.service.create_pallet(
            {
                'box_ids': [],
                'warehouse': 'FG01',
                'production_line': 'Line 1',
                'mfg_date': date(2026, 5, 7),
                'max_box_count': 1,
            },
            user=self.user,
        )

        with self.assertRaisesMessage(ValueError, "Pallet capacity exceeded."):
            self.service.add_boxes_to_pallet(
                pallet.id,
                [box.id for box in boxes],
                user=self.user,
            )

        self.assertEqual(Box.objects.filter(pallet=pallet).count(), 0)

    def test_clear_pallet_resets_context_and_allows_reuse(self):
        first_boxes = self._generate_boxes(count=2, qty='10.00', batch='BATCH-001')
        pallet = self.service.create_pallet(
            {
                'box_ids': [],
                'warehouse': 'FG01',
                'production_line': 'Line 1',
                'mfg_date': date(2026, 5, 7),
            },
            user=self.user,
        )
        pallet = self.service.add_boxes_to_pallet(
            pallet.id,
            [box.id for box in first_boxes],
            user=self.user,
        )

        cleared = self.service.clear_pallet(
            pallet.id,
            notes='Ready for reuse',
            user=self.user,
        )

        self.assertEqual(cleared.status, PalletStatus.CLEARED)
        self.assertEqual(cleared.box_count, 0)
        self.assertEqual(cleared.total_qty, Decimal('0'))
        self.assertEqual(cleared.item_code, '')
        self.assertEqual(cleared.batch_number, '')
        self.assertEqual(cleared.uom, '')
        self.assertEqual(cleared.max_box_count, 0)
        self.assertEqual(Box.objects.filter(pallet=cleared).count(), 0)

        new_box = self.service.generate_boxes(
            {
                'item_code': 'FG002',
                'item_name': 'Reusable Pallet Product',
                'batch_number': 'BATCH-REUSE',
                'qty': Decimal('7.50'),
                'box_count': 1,
                'uom': 'PCS',
                'mfg_date': date(2026, 6, 1),
                'exp_date': date(2027, 6, 1),
                'warehouse': 'FG01',
                'production_line': 'Line 2',
            },
            user=self.user,
        )[0]

        reused = self.service.add_boxes_to_pallet(cleared.id, [new_box.id], user=self.user)

        self.assertEqual(reused.status, PalletStatus.ACTIVE)
        self.assertEqual(reused.pallet_id, pallet.pallet_id)
        self.assertEqual(reused.box_count, 1)
        self.assertEqual(reused.total_qty, Decimal('7.50'))
        self.assertEqual(reused.item_code, 'FG002')
        self.assertEqual(reused.item_name, 'Reusable Pallet Product')
        self.assertEqual(reused.batch_number, 'BATCH-REUSE')
        self.assertEqual(reused.mfg_date, date(2026, 6, 1))
        self.assertEqual(reused.exp_date, date(2027, 6, 1))

    def test_split_into_cleared_pallet_reactivates_and_sets_context(self):
        boxes = self._generate_boxes(count=3, qty='5.00', batch='BATCH-SPLIT')
        source = self.service.create_pallet(
            {
                'box_ids': [],
                'warehouse': 'FG01',
                'production_line': 'Line 1',
                'mfg_date': date(2026, 5, 7),
            },
            user=self.user,
        )
        source = self.service.add_boxes_to_pallet(
            source.id,
            [box.id for box in boxes],
            user=self.user,
        )
        target = self.service.create_pallet(
            {
                'box_ids': [],
                'warehouse': 'FG02',
                'production_line': 'Line 1',
                'mfg_date': date(2026, 5, 7),
            },
            user=self.user,
        )
        target.status = PalletStatus.CLEARED
        target.save(update_fields=['status'])

        updated_target = self.service.split_pallet(
            source.id,
            [boxes[0].id],
            target.id,
            user=self.user,
        )

        self.assertEqual(updated_target.status, PalletStatus.ACTIVE)
        self.assertEqual(updated_target.box_count, 1)
        self.assertEqual(updated_target.total_qty, Decimal('5.00'))
        self.assertEqual(updated_target.item_code, 'FG001')
        self.assertEqual(updated_target.batch_number, 'BATCH-SPLIT')
        self.assertEqual(updated_target.uom, 'PCS')
        updated_target.refresh_from_db()
        self.assertEqual(updated_target.boxes.first().current_warehouse, 'FG02')

    def test_full_pallet_dismantle_clears_context_for_reuse(self):
        boxes = self._generate_boxes(count=1, qty='10.00', batch='BATCH-DISMANTLE')
        pallet = self.service.create_pallet(
            {
                'box_ids': [],
                'warehouse': 'FG01',
                'production_line': 'Line 1',
                'mfg_date': date(2026, 5, 7),
            },
            user=self.user,
        )
        pallet = self.service.add_boxes_to_pallet(
            pallet.id,
            [boxes[0].id],
            user=self.user,
        )

        dismantled = self.service.dismantle_pallet(
            pallet.id,
            box_ids=None,
            reason='REPACK',
            reason_notes='Production test',
            user=self.user,
        )

        self.assertEqual(dismantled.status, PalletStatus.CLEARED)
        self.assertEqual(dismantled.box_count, 0)
        self.assertEqual(dismantled.total_qty, Decimal('0'))
        self.assertEqual(dismantled.item_code, '')
        self.assertEqual(dismantled.batch_number, '')
        self.assertEqual(dismantled.uom, '')
        self.assertEqual(dismantled.max_box_count, 0)

    def test_box_transfer_to_pallet_rejects_mismatched_context(self):
        target_box = self._generate_boxes(count=1, batch='BATCH-TARGET')[0]
        pallet = self.service.create_pallet(
            {
                'box_ids': [],
                'warehouse': 'FG01',
                'production_line': 'Line 1',
                'mfg_date': date(2026, 5, 7),
            },
            user=self.user,
        )
        pallet = self.service.add_boxes_to_pallet(pallet.id, [target_box.id], user=self.user)
        other_box = self.service.generate_boxes(
            {
                'item_code': 'FG002',
                'item_name': 'Other Finished Good',
                'batch_number': 'BATCH-OTHER',
                'qty': Decimal('4.00'),
                'box_count': 1,
                'uom': 'PCS',
                'mfg_date': date(2026, 5, 7),
                'exp_date': date(2027, 5, 7),
                'warehouse': 'FG02',
                'production_line': 'Line 1',
            },
            user=self.user,
        )[0]

        with self.assertRaisesMessage(
            ValueError,
            "Box item, batch, or UOM does not match the target pallet.",
        ):
            self.service.transfer_boxes(
                [other_box.id],
                to_warehouse='FG01',
                to_pallet_id=pallet.id,
                user=self.user,
            )

        other_box.refresh_from_db()
        self.assertIsNone(other_box.pallet)

    def test_box_transfer_between_pallets_requires_available_target_space(self):
        source_boxes = self._generate_boxes(count=2, qty='5.00', batch='BATCH-MERGE')
        target_box = self._generate_boxes(count=1, qty='5.00', batch='BATCH-MERGE')[0]

        source = self.service.create_pallet(
            {
                'box_ids': [],
                'warehouse': 'FG01',
                'production_line': 'Line 1',
                'mfg_date': date(2026, 5, 7),
            },
            user=self.user,
        )
        source = self.service.add_boxes_to_pallet(
            source.id,
            [box.id for box in source_boxes],
            user=self.user,
        )
        target = self.service.create_pallet(
            {
                'box_ids': [],
                'warehouse': 'FG02',
                'production_line': 'Line 1',
                'mfg_date': date(2026, 5, 7),
                'max_box_count': 2,
            },
            user=self.user,
        )
        target = self.service.add_boxes_to_pallet(target.id, [target_box.id], user=self.user)

        transferred = self.service.transfer_boxes(
            [source_boxes[0].id],
            to_warehouse=target.current_warehouse,
            to_pallet_id=target.id,
            user=self.user,
        )

        self.assertEqual(transferred[0].pallet_id, target.id)
        self.assertEqual(transferred[0].current_warehouse, 'FG02')
        source.refresh_from_db()
        target.refresh_from_db()
        self.assertEqual(source.box_count, 1)
        self.assertEqual(target.box_count, 2)

        with self.assertRaisesMessage(ValueError, "Pallet capacity exceeded."):
            self.service.transfer_boxes(
                [source_boxes[1].id],
                to_warehouse=target.current_warehouse,
                to_pallet_id=target.id,
                user=self.user,
            )

        source_boxes[1].refresh_from_db()
        self.assertEqual(source_boxes[1].pallet_id, source.id)

    def test_pallet_sequence_uses_global_unique_namespace(self):
        first = self.service.create_pallet(
            {
                'box_ids': [],
                'warehouse': 'FG01',
                'production_line': '',
                'mfg_date': date(2026, 5, 7),
            },
            user=self.user,
        )
        other_company = Company.objects.create(
            name='Other Barcode Company',
            code='OTHERCO',
        )
        other_service = BarcodeService(company_code=other_company.code)

        second = other_service.create_pallet(
            {
                'box_ids': [],
                'warehouse': 'FG01',
                'production_line': '',
                'mfg_date': date(2026, 5, 7),
            },
            user=self.user,
        )

        self.assertEqual(first.pallet_id, 'PLT-20260507-XX-001')
        self.assertEqual(second.pallet_id, 'PLT-20260507-XX-002')

    def test_pallet_create_serializer_allows_blank_production_line(self):
        serializer = PalletCreateSerializer(
            data={
                'box_ids': [],
                'warehouse': 'FG01',
                'production_line': '',
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data['production_line'], '')

    def test_pallet_create_serializer_rejects_linked_boxes(self):
        serializer = PalletCreateSerializer(
            data={
                'box_ids': [1, 2, 3],
                'warehouse': 'FG01',
                'production_line': '',
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn('box_ids', serializer.errors)

    def test_box_generate_serializer_allows_large_label_batches(self):
        serializer = BoxGenerateSerializer(
            data={
                'item_code': 'FG001',
                'item_name': 'Test Finished Good',
                'batch_number': 'BATCH-001',
                'qty': '1.00',
                'box_count': MAX_BOX_LABELS_PER_REQUEST,
                'uom': 'PCS',
                'mfg_date': '2026-05-07',
                'warehouse': 'FG01',
                'production_line': 'Line 1',
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_box_generate_serializer_rejects_extreme_label_batches(self):
        serializer = BoxGenerateSerializer(
            data={
                'item_code': 'FG001',
                'item_name': 'Test Finished Good',
                'batch_number': 'BATCH-001',
                'qty': '1.00',
                'box_count': MAX_BOX_LABELS_PER_REQUEST + 1,
                'uom': 'PCS',
                'mfg_date': '2026-05-07',
                'warehouse': 'FG01',
                'production_line': 'Line 1',
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn('box_count', serializer.errors)

    def test_scan_service_handles_exact_qr_one_d_and_missing_barcodes(self):
        boxes = self._generate_boxes(count=3)
        pallet = self.service.create_pallet(
            {
                'box_ids': [],
                'warehouse': 'FG01',
                'production_line': 'Line 1',
            },
            user=self.user,
        )
        pallet = self.service.add_boxes_to_pallet(
            pallet.id,
            [box.id for box in boxes],
            user=self.user,
        )

        exact_box = self.scan_service.process_scan(boxes[0].box_barcode, 'LOOKUP')
        self.assertEqual(exact_box['result'], ScanResult.SUCCESS)
        self.assertEqual(exact_box['entity_type'], EntityType.BOX)
        self.assertEqual(exact_box['entity_data']['box_barcode'], boxes[0].box_barcode)

        qr_box = self.scan_service.process_scan(json.dumps(boxes[1].barcode_data), 'LOOKUP')
        self.assertEqual(qr_box['result'], ScanResult.SUCCESS)
        self.assertEqual(qr_box['entity_data']['box_barcode'], boxes[1].box_barcode)

        one_d_box = self.scan_service.lookup_barcode(
            'B' + boxes[2].box_barcode.replace('-', '')
        )
        self.assertEqual(one_d_box['entity_type'], EntityType.BOX)
        self.assertEqual(one_d_box['entity_data']['box_barcode'], boxes[2].box_barcode)

        qr_pallet_lookup = self.scan_service.lookup_barcode(json.dumps(pallet.barcode_data))
        self.assertEqual(qr_pallet_lookup['entity_type'], EntityType.PALLET)
        self.assertEqual(qr_pallet_lookup['entity_data']['pallet_id'], pallet.pallet_id)

        one_d_pallet = self.scan_service.process_scan(
            'P' + pallet.pallet_id.replace('-', ''),
            'LOOKUP',
        )
        self.assertEqual(one_d_pallet['result'], ScanResult.SUCCESS)
        self.assertEqual(one_d_pallet['entity_data']['pallet_id'], pallet.pallet_id)

        missing = self.scan_service.process_scan('NOT-A-REAL-BARCODE', 'LOOKUP')
        self.assertEqual(missing['result'], ScanResult.NOT_FOUND)
        self.assertEqual(missing['entity_type'], EntityType.UNKNOWN)
        self.assertEqual(ScanLog.objects.count(), 4)

    def test_void_dismantle_and_repack_flow(self):
        boxes = self._generate_boxes(count=2, qty='10.00')
        pallet = self.service.create_pallet(
            {
                'box_ids': [],
                'warehouse': 'FG01',
                'production_line': 'Line 1',
            },
            user=self.user,
        )
        pallet = self.service.add_boxes_to_pallet(
            pallet.id,
            [box.id for box in boxes],
            user=self.user,
        )

        voided_box = self.service.void_box(
            boxes[0].id,
            reason='Damaged label',
            user=self.user,
        )
        pallet.refresh_from_db()
        self.assertEqual(voided_box.status, BoxStatus.VOID)
        self.assertIsNone(voided_box.pallet)
        self.assertEqual(pallet.box_count, 1)
        self.assertEqual(pallet.total_qty, Decimal('10.00'))

        loose = self.service.dismantle_box(
            boxes[1].id,
            loose_qty=Decimal('4.00'),
            reason='REPACK',
            reason_notes='Pilot repack test',
            user=self.user,
        )
        boxes[1].refresh_from_db()
        pallet.refresh_from_db()
        self.assertEqual(boxes[1].status, BoxStatus.PARTIAL)
        self.assertEqual(boxes[1].qty, Decimal('6.00'))
        self.assertEqual(loose.status, LooseStockStatus.ACTIVE)
        self.assertEqual(loose.qty, Decimal('4.00'))
        self.assertEqual(pallet.total_qty, Decimal('6.00'))

        repacked_box = self.service.repack(
            loose_ids=[loose.id],
            qty_per_loose=None,
            warehouse='FG01',
            user=self.user,
        )
        loose.refresh_from_db()
        self.assertEqual(loose.status, LooseStockStatus.REPACKED)
        self.assertEqual(loose.qty, Decimal('0.00'))
        self.assertEqual(loose.repacked_into_box, repacked_box)
        self.assertTrue(repacked_box.box_barcode.startswith('BOX-'))

    def test_line_key_is_sanitized_to_fit_barcode_field(self):
        boxes = self._generate_boxes(
            count=1,
            line='Filler Line / East Wing / Extremely Long Name 1234567890',
        )

        self.assertLessEqual(len(boxes[0].box_barcode), 50)
        self.assertNotIn('/', boxes[0].box_barcode)

    def test_label_print_log_stores_tsc_printer_name(self):
        box = self._generate_boxes(count=1)[0]
        label_data = self.label_service.get_box_label_data(box.id)

        self.label_service.log_print(
            label_type='BOX',
            reference_id=box.id,
            reference_code=label_data['barcode'],
            print_type='ORIGINAL',
            user=self.user,
            printer_name='TSC DA310 - 100 x 40 mm',
        )

        log = LabelPrintLog.objects.get(reference_code=box.box_barcode)
        self.assertEqual(log.printer_name, 'TSC DA310 - 100 x 40 mm')

    def test_production_release_oil_row_normalizes_for_label_dropdown(self):
        row = ProductionReleaseOilService._normalize_row({
            'DocEntry': 9465,
            'DocNum': 226926733,
            'PostDate': date(2026, 2, 20),
            'ItemCode': 'FG0000003',
            'ItemName': 'COLD PRESS 5 LTR + EXTRA LIGHT OLIVE 1 LTR 4 PCS',
            'Liter Countable': 'Y',
            'ManBtchNum': 'Y',
            'PlannedQty': Decimal('336.00'),
            'Box': Decimal('84.00'),
            'Liter': Decimal('1680.00'),
            'Box Size': Decimal('4.00'),
            'Volume Per Pc': Decimal('5.00'),
            'Volume Per Box': Decimal('20.00'),
            'U_BATCH_NO': 'BATCH-001',
            'MFG Date': date(2026, 2, 20),
            'Expiry Date': date(2027, 2, 20),
            'Status': 'R',
        })

        self.assertEqual(row['doc_entry'], 9465)
        self.assertEqual(row['doc_num'], 226926733)
        self.assertEqual(row['post_date'], '2026-02-20')
        self.assertEqual(row['item_code'], 'FG0000003')
        self.assertEqual(row['batch_number'], 'BATCH-001')
        self.assertEqual(row['box_count'], '84')
        self.assertEqual(row['box_size'], '4')
        self.assertEqual(row['mfg_date'], '2026-02-20')
        self.assertEqual(row['exp_date'], '2027-02-20')
