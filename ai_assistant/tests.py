from datetime import date
from decimal import Decimal
from unittest.mock import Mock, patch

from django.contrib.auth.models import Permission
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from accounts.models import User
from barcode.models import Box
from company.models import Company, UserCompany, UserRole
from driver_management.models import Driver, VehicleEntry
from gate_core.enums import GateEntryStatus
from grpo.models import GRPOPosting, GRPOStatus
from production_execution.models import ProductionLine, ProductionRun
from raw_material_gatein.models import POReceipt
from vehicle_management.models import Vehicle
from warehouse.models import FGReceiptStatus, FinishedGoodsReceipt


class AssistantChatAPITests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='AI Test Company', code='AITEST')
        self.role = UserRole.objects.create(name='Barcode User')
        self.user = User.objects.create_user(
            email='ai@example.com',
            password='test-pass',
            full_name='AI Tester',
            employee_code='EMP-AI-001',
        )
        UserCompany.objects.create(
            user=self.user,
            company=self.company,
            role=self.role,
            is_default=True,
            is_active=True,
        )
        self.user.user_permissions.add(Permission.objects.get(codename='can_view_pending_grpo'))
        Box.objects.create(
            company=self.company,
            box_barcode='BOX-20260507-Water_Line-0001',
            item_code='FG0000004',
            item_name='COLD PRESS 5 LTR 4 PCS',
            batch_number='BATCH-AI-001',
            qty=Decimal('1.00'),
            uom='PCS',
            mfg_date=date(2026, 5, 7),
            exp_date=date(2027, 5, 7),
            current_warehouse='FG01',
            created_by=self.user,
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def _create_pending_grpo_entry(self):
        vehicle = Vehicle.objects.create(vehicle_number='AI-GRPO-001')
        driver = Driver.objects.create(
            name='AI Driver',
            mobile_no='9999999999',
            license_no='AI-LIC-001',
        )
        entry = VehicleEntry.objects.create(
            company=self.company,
            vehicle=vehicle,
            driver=driver,
            entry_no='GE-AI-GRPO-001',
            entry_type='RAW_MATERIAL',
            status=GateEntryStatus.COMPLETED,
            created_by=self.user,
        )
        POReceipt.objects.create(
            vehicle_entry=entry,
            po_number='PO-AI-001',
            supplier_code='SUP-AI',
            supplier_name='AI Supplier',
        )
        POReceipt.objects.create(
            vehicle_entry=entry,
            po_number='PO-AI-002',
            supplier_code='SUP-AI',
            supplier_name='AI Supplier',
        )
        return entry

    def _create_fg_receipts_and_posted_grpos(self):
        line = ProductionLine.objects.create(company=self.company, name='AI Line')
        run = ProductionRun.objects.create(
            company=self.company,
            run_number=1,
            date=date(2026, 5, 7),
            line=line,
            product='AI Finished Good',
        )
        FinishedGoodsReceipt.objects.create(
            company=self.company,
            production_run=run,
            item_code='FG-AI-001',
            item_name='AI Finished Good',
            produced_qty=Decimal('10.00'),
            good_qty=Decimal('10.00'),
            warehouse='FG01',
            posting_date=date(2026, 5, 7),
            status=FGReceiptStatus.SAP_POSTED,
        )
        FinishedGoodsReceipt.objects.create(
            company=self.company,
            production_run=run,
            item_code='FG-AI-002',
            item_name='AI Pending Finished Good',
            produced_qty=Decimal('5.00'),
            good_qty=Decimal('5.00'),
            warehouse='FG01',
            posting_date=date(2026, 5, 7),
            status=FGReceiptStatus.PENDING,
        )

        entry = self._create_pending_grpo_entry()
        for index, po_receipt in enumerate(entry.po_receipts.all(), start=1):
            GRPOPosting.objects.create(
                vehicle_entry=entry,
                po_receipt=po_receipt,
                status=GRPOStatus.POSTED,
                sap_doc_num=9000 + index,
            )

    @override_settings(GEMINI_API_KEY='test-key', GEMINI_MODEL='test-model')
    @patch('ai_assistant.services.requests.post')
    def test_chat_returns_answer_and_sources(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'candidates': [
                {
                    'content': {
                        'parts': [{'text': 'FG0000004 has one matching box.'}],
                    },
                },
            ],
        }
        mock_post.return_value = mock_response

        response = self.client.post(
            '/api/v1/ai/assistant/chat/',
            {'question': 'Find box for FG0000004', 'page': '/barcode/boxes'},
            format='json',
            HTTP_COMPANY_CODE=self.company.code,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['answer'], 'FG0000004 has one matching box.')
        self.assertEqual(response.data['mode'], 'read_only')
        self.assertTrue(
            any(source['type'] == 'barcode_boxes' for source in response.data['sources'])
        )
        payload = mock_post.call_args.kwargs['json']
        self.assertIn('/test-model:generateContent', mock_post.call_args.args[0])
        self.assertIn('FG0000004', payload['contents'][0]['parts'][0]['text'])

    @override_settings(GEMINI_API_KEY='')
    def test_chat_requires_gemini_key(self):
        response = self.client.post(
            '/api/v1/ai/assistant/chat/',
            {'question': 'Find box for FG0000004'},
            format='json',
            HTTP_COMPANY_CODE=self.company.code,
        )

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.data['code'], 'ai_not_configured')

    @patch('ai_assistant.services.requests.post')
    def test_chat_answers_pending_grpo_count_from_local_context(self, mock_post):
        self._create_pending_grpo_entry()

        response = self.client.post(
            '/api/v1/ai/assistant/chat/',
            {'question': 'how many grpos are pending', 'page': '/grpo/pending'},
            format='json',
            HTTP_COMPANY_CODE=self.company.code,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data['answer'],
            'There are 1 pending GRPO entry, covering 2 pending POs.',
        )
        self.assertEqual(response.data['provider'], 'local')
        self.assertEqual(response.data['context_summary']['pending_grpo_entry_count'], 1)
        self.assertEqual(response.data['context_summary']['pending_grpo_po_count'], 2)
        self.assertTrue(
            any(source['type'] == 'grpo_pending' for source in response.data['sources'])
        )
        self.assertFalse(
            any(source['type'] == 'document' for source in response.data['sources'])
        )
        mock_post.assert_not_called()

    @patch('ai_assistant.services.requests.post')
    def test_chat_answers_fg_receipts_posted_in_sap_not_grpo(self, mock_post):
        self._create_fg_receipts_and_posted_grpos()

        response = self.client.post(
            '/api/v1/ai/assistant/chat/',
            {'question': 'How many fg receipts are posted in sap', 'page': '/warehouse/fg-receipts'},
            format='json',
            HTTP_COMPANY_CODE=self.company.code,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data['answer'],
            'There are 1 SAP-posted finished goods receipt.',
        )
        self.assertEqual(response.data['provider'], 'local')
        self.assertIn('warehouse', response.data['context_summary']['operations_sections'])
        self.assertNotIn('grpo_postings', response.data['context_summary']['operations_sections'])
        mock_post.assert_not_called()
