from datetime import date
from decimal import Decimal
from unittest.mock import Mock, patch

import requests
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
from .models import AIAssistantInteraction
from .services import FactoryAssistantService


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

    @override_settings(GEMINI_API_KEY='test-key', GEMINI_MODEL='test-model')
    @patch('ai_assistant.services.requests.post')
    def test_chat_can_answer_deep_question_with_read_only_sql(self, mock_post):
        self.user.user_permissions.add(Permission.objects.get(codename='can_query_factory_database'))
        planner_response = Mock()
        planner_response.status_code = 200
        planner_response.json.return_value = {
            'candidates': [
                {
                    'content': {
                        'parts': [
                            {
                                'text': (
                                    '{"sql": "SELECT status, COUNT(*) AS total '
                                    'FROM barcode_box '
                                    f'WHERE company_id = {self.company.id} '
                                    'GROUP BY status", '
                                    '"reason": "Counts boxes by status for the current company."}'
                                ),
                            }
                        ],
                    },
                },
            ],
        }
        summary_response = Mock()
        summary_response.status_code = 200
        summary_response.json.return_value = {
            'candidates': [
                {
                    'content': {
                        'parts': [{'text': 'Inventory insight: there is 1 active box.'}],
                    },
                },
            ],
        }
        mock_post.side_effect = [planner_response, summary_response]

        response = self.client.post(
            '/api/v1/ai/assistant/chat/',
            {'question': 'Give deep inventory insight by box status', 'page': '/barcode/boxes'},
            format='json',
            HTTP_COMPANY_CODE=self.company.code,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['provider'], 'gemini')
        self.assertEqual(response.data['mode'], 'read_only_sql')
        self.assertEqual(response.data['answer'], 'Inventory insight: there is 1 active box.')
        self.assertEqual(response.data['context_summary']['database_query']['row_count'], 1)
        self.assertTrue(
            any(source['type'] == 'factory_database_sql' for source in response.data['sources'])
        )
        self.assertEqual(mock_post.call_count, 2)

    @override_settings(GEMINI_API_KEY='test-key', GEMINI_MODEL='test-model')
    @patch('ai_assistant.services.requests.post')
    def test_chat_does_not_use_sql_without_ai_database_permission(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'candidates': [
                {
                    'content': {
                        'parts': [{'text': 'Inventory context answer without SQL.'}],
                    },
                },
            ],
        }
        mock_post.return_value = mock_response

        response = self.client.post(
            '/api/v1/ai/assistant/chat/',
            {'question': 'Give deep inventory insight by box status', 'page': '/barcode/boxes'},
            format='json',
            HTTP_COMPANY_CODE=self.company.code,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['mode'], 'read_only')
        self.assertEqual(response.data['answer'], 'Inventory context answer without SQL.')
        self.assertFalse(
            any(source['type'] == 'factory_database_sql' for source in response.data['sources'])
        )
        self.assertEqual(mock_post.call_count, 1)
        interaction = AIAssistantInteraction.objects.latest('created_at')
        self.assertEqual(interaction.validation_status, 'permission_denied')

    def test_read_only_sql_rejects_write_queries(self):
        service = FactoryAssistantService(
            company=self.company,
            company_code=self.company.code,
            user=self.user,
        )
        schema = service._database_schema_context()

        with self.assertRaises(ValueError):
            service._validate_read_only_sql(
                f"UPDATE barcode_box SET status = 'BROKEN' WHERE company_id = {self.company.id}",
                schema=schema,
            )

    def test_database_schema_includes_full_business_tables_but_not_sensitive_fields(self):
        service = FactoryAssistantService(
            company=self.company,
            company_code=self.company.code,
            user=self.user,
        )

        schema = service._database_schema_context()
        table_names = schema['allowed_table_names']

        self.assertIn('accounts_user', table_names)
        self.assertIn('company_usercompany', table_names)
        self.assertIn('notifications_notification', table_names)
        self.assertNotIn('auth_permission', table_names)
        self.assertNotIn('django_session', table_names)
        self.assertNotIn('token_blacklist_outstandingtoken', table_names)

        user_table = next(table for table in schema['tables'] if table['table'] == 'accounts_user')
        user_columns = ' '.join(user_table['columns']).lower()
        self.assertIn('email', user_columns)
        self.assertIn('full_name', user_columns)
        self.assertNotIn('password', user_columns)
        self.assertTrue(user_table['company_scoped'])
        self.assertTrue(
            any('company_usercompany.user_id' in reference for reference in user_table['referenced_by'])
        )

    def test_read_only_sql_allows_broad_company_scoped_account_query(self):
        service = FactoryAssistantService(
            company=self.company,
            company_code=self.company.code,
            user=self.user,
        )
        schema = service._database_schema_context()
        sql = (
            'SELECT u.email, u.full_name '
            'FROM accounts_user u '
            'JOIN company_usercompany uc ON uc.user_id = u.id '
            f'WHERE uc.company_id = {self.company.id}'
        )

        safe_sql = service._validate_read_only_sql(sql, schema=schema)
        result = service._execute_read_only_sql(safe_sql)

        self.assertEqual(result['row_count'], 1)
        self.assertEqual(result['rows'][0]['email'], self.user.email)
        self.assertEqual(result['rows'][0]['full_name'], self.user.full_name)

    def test_read_only_sql_rejects_sensitive_columns_even_in_allowed_tables(self):
        service = FactoryAssistantService(
            company=self.company,
            company_code=self.company.code,
            user=self.user,
        )
        schema = service._database_schema_context()

        with self.assertRaises(ValueError):
            service._validate_read_only_sql(
                (
                    'SELECT u.password '
                    'FROM accounts_user u '
                    'JOIN company_usercompany uc ON uc.user_id = u.id '
                    f'WHERE uc.company_id = {self.company.id}'
                ),
                schema=schema,
            )

    @override_settings(GEMINI_API_KEY='test-key', GEMINI_MODEL='test-model')
    @patch('ai_assistant.services.requests.post')
    def test_chat_returns_clear_dns_error_when_gemini_host_cannot_resolve(self, mock_post):
        mock_post.side_effect = requests.exceptions.ConnectionError(
            "Failed to resolve 'generativelanguage.googleapis.com' ([Errno 11001] getaddrinfo failed)"
        )

        response = self.client.post(
            '/api/v1/ai/assistant/chat/',
            {'question': 'Explain this app data', 'page': '/dashboard'},
            format='json',
            HTTP_COMPANY_CODE=self.company.code,
        )

        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.data['code'], 'ai_provider_error')
        self.assertIn('DNS/network resolution is failing', response.data['error'])
