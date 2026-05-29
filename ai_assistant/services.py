import json
import logging
import re
import time
from datetime import timedelta
from pathlib import Path
from typing import Any

import requests
import sqlparse
from django.apps import apps
from django.conf import settings
from django.db import DatabaseError, connection, connections, transaction
from django.db.models import Count, Q
from django.utils import timezone

from barcode.models import Box, LabelPrintLog, Pallet
from construction_gatein.models import ConstructionGateEntry
from daily_needs_gatein.models import DailyNeedGateEntry
from barcode.services.production_release_service import (
    ProductionReleaseOilService,
    ProductionReleaseReadError,
)
from driver_management.models import VehicleEntry
from grpo.services import GRPOService
from grpo.models import GRPOPosting
from maintenance_gatein.models import MaintenanceGateEntry
from quality_control.models import MaterialArrivalSlip, RawMaterialInspection
from raw_material_gatein.models import POReceipt
from security_checks.models import SecurityCheck
from weighment.models import Weighment
from warehouse.models import BOMRequest, FinishedGoodsReceipt
from production_execution.models import (
    LineClearance,
    MachineBreakdown,
    ProductionRun,
    WasteLog,
)
from .models import AIAssistantInteraction

logger = logging.getLogger(__name__)


class AssistantConfigError(RuntimeError):
    """Raised when the assistant is not configured for model calls."""


class AssistantProviderError(RuntimeError):
    """Raised when the AI provider returns an unusable response."""


class FactoryAssistantService:
    """Read-only AI assistant with Factory data context and guarded SQL analysis."""

    GEMINI_GENERATE_CONTENT_BASE_URL = 'https://generativelanguage.googleapis.com/v1beta/models'
    SQL_RESULT_ROW_LIMIT = 50
    SQL_SCHEMA_COLUMN_LIMIT = 35
    SQL_EXCLUDED_APP_LABELS = {
        'admin',
        'auth',
        'contenttypes',
        'sessions',
        'token_blacklist',
    }
    SQL_EXCLUDED_TABLE_PATTERN = re.compile(
        r'(?:^auth_|^django_|^token_blacklist_|_groups|_permission|_permissions|_group_permissions|_user_permissions)',
        re.IGNORECASE,
    )
    SQL_SENSITIVE_COLUMN_PATTERN = re.compile(
        r'(?:password|token|secret|session|api_key|private_key|credential|firebase_private_key|otp)',
        re.IGNORECASE,
    )
    SQL_FORBIDDEN_PATTERN = re.compile(
        r'\b('
        r'alter|analyze|benchmark|call|comment|copy|create|delete|dblink|do|drop|'
        r'execute|explain|grant|insert|into|listen|lo_export|lo_import|lock|merge|'
        r'notify|pg_sleep|refresh|replace|reset|revoke|set|truncate|unlisten|update|'
        r'vacuum'
        r')\b',
        re.IGNORECASE,
    )
    SQL_SENSITIVE_PATTERN = re.compile(
        r'\b(password|token|secret|session|api_key|private_key|credential|firebase_private_key|otp)\b',
        re.IGNORECASE,
    )
    SQL_TABLE_REF_PATTERN = re.compile(
        r'\b(?:from|join)\s+([("]?[A-Za-z_][A-Za-z0-9_."()]*)',
        re.IGNORECASE,
    )
    SQL_CTE_PATTERN = re.compile(r'(?:with|,)\s+"?([A-Za-z_][A-Za-z0-9_]*)"?\s+as\s*\(', re.IGNORECASE)

    def __init__(self, *, company, company_code: str, user):
        self.company = company
        self.company_code = company_code
        self.user = user
        self.max_rows = settings.AI_ASSISTANT_MAX_CONTEXT_ROWS
        self._last_database_audit: dict[str, Any] = {}

    def answer(self, *, question: str, page: str = '') -> dict[str, Any]:
        started = time.monotonic()
        self._last_database_audit = {}
        try:
            context = self._build_context(question=question, page=page)
            direct_answer = self._direct_answer(question=question, context=context)
            if direct_answer:
                result = {
                    'answer': direct_answer,
                    'sources': context['sources'],
                    'context_summary': context['summary'],
                    'model': 'factory-context',
                    'provider': 'local',
                    'mode': 'read_only',
                }
                self._audit_interaction(
                    question=question,
                    page=page,
                    result=result,
                    started=started,
                )
                return result

            database_result = self._answer_from_database(question=question, page=page, context=context)
            if database_result:
                context_summary = {
                    **context['summary'],
                    'database_query': database_result['summary'],
                }
                result = {
                    'answer': database_result['answer'],
                    'sources': [*context['sources'], database_result['source']],
                    'context_summary': context_summary,
                    'model': database_result['model'],
                    'provider': 'gemini',
                    'mode': 'read_only_sql',
                }
                self._audit_interaction(
                    question=question,
                    page=page,
                    result=result,
                    started=started,
                )
                return result

            provider_result = self._call_gemini(question=question, page=page, context=context)
            result = {
                'answer': provider_result['text'],
                'sources': context['sources'],
                'context_summary': context['summary'],
                'model': provider_result['model'],
                'provider': 'gemini',
                'mode': 'read_only',
            }
            self._audit_interaction(
                question=question,
                page=page,
                result=result,
                started=started,
            )
            return result
        except (AssistantConfigError, AssistantProviderError) as exc:
            self._audit_interaction(
                question=question,
                page=page,
                result={},
                started=started,
                status=AIAssistantInteraction.STATUS_ERROR,
                error_code=exc.__class__.__name__,
                blocked_reason=str(exc),
            )
            raise

    def _build_context(self, *, question: str, page: str) -> dict[str, Any]:
        tokens = self._extract_search_terms(question)
        boxes = self._search_boxes(tokens)
        pallets = self._search_pallets(tokens)
        print_logs = self._search_print_logs(tokens)
        production_releases = self._search_production_releases(question, tokens)
        pending_grpos = self._search_pending_grpos(question=question, page=page)
        operations = self._build_operational_context(question=question, page=page, tokens=tokens)
        documents = self._search_documents(question, tokens) if self._should_search_documents(question) else []

        sources: list[dict[str, str]] = []
        if boxes:
            sources.append({'type': 'barcode_boxes', 'label': f'{len(boxes)} matching boxes'})
        if pallets:
            sources.append({'type': 'barcode_pallets', 'label': f'{len(pallets)} matching pallets'})
        if print_logs:
            sources.append({'type': 'print_history', 'label': f'{len(print_logs)} print records'})
        if production_releases:
            sources.append({
                'type': 'production_release_oil',
                'label': f'{len(production_releases)} SAP release rows',
            })
        if pending_grpos:
            if pending_grpos.get('error'):
                sources.append({'type': 'grpo_pending', 'label': 'GRPO pending data unavailable'})
            else:
                sources.append({
                    'type': 'grpo_pending',
                    'label': f"{pending_grpos['pending_entry_count']} pending GRPO entries",
                })
        sources.extend(
            {'type': section['source_type'], 'label': section['label']}
            for section in operations.get('sources', [])
        )
        sources.extend({'type': 'document', 'label': doc['title']} for doc in documents)

        return {
            'summary': {
                'company_code': self.company_code,
                'page': page,
                'date_context': self._date_context(),
                'tokens_used_for_lookup': tokens,
                'box_count': len(boxes),
                'pallet_count': len(pallets),
                'print_log_count': len(print_logs),
                'production_release_count': len(production_releases),
                'pending_grpo_entry_count': pending_grpos.get('pending_entry_count', 0),
                'pending_grpo_po_count': pending_grpos.get('pending_po_count', 0),
                'operations_sections': list(operations.get('data', {}).keys()),
                'document_count': len(documents),
            },
            'data': {
                'boxes': boxes,
                'pallets': pallets,
                'print_logs': print_logs,
                'production_releases': production_releases,
                'pending_grpos': pending_grpos,
                'operations': operations.get('data', {}),
                'documents': documents,
            },
            'sources': sources,
        }

    def _direct_answer(self, *, question: str, context: dict[str, Any]) -> str:
        lower_question = question.lower()
        if self._is_fg_receipt_question(lower_question):
            answer = self._fg_receipt_answer(question=question, context=context)
            if answer:
                return answer

        wants_pending_grpo_count = (
            'grpo' in lower_question
            and 'pending' in lower_question
            and any(word in lower_question for word in ['how many', 'count', 'number'])
        )
        if not wants_pending_grpo_count:
            return self._direct_count_answer(question=question, context=context)

        pending_grpos = context['data'].get('pending_grpos') or {}
        if pending_grpos.get('error'):
            return str(pending_grpos['error'])

        entry_count = pending_grpos.get('pending_entry_count', 0)
        po_count = pending_grpos.get('pending_po_count', 0)
        entry_label = 'entry' if entry_count == 1 else 'entries'
        po_label = 'PO' if po_count == 1 else 'POs'
        if entry_count == po_count:
            return f'There are {entry_count} pending GRPO {entry_label}.'
        return f'There are {entry_count} pending GRPO {entry_label}, covering {po_count} pending {po_label}.'

    def _direct_count_answer(self, *, question: str, context: dict[str, Any]) -> str:
        lower_question = question.lower()
        if not any(term in lower_question for term in ['how many', 'count', 'number of']):
            return ''

        operations = context['data'].get('operations') or {}

        if self._is_fg_receipt_question(lower_question):
            return self._fg_receipt_answer(question=question, context=context)

        if any(term in lower_question for term in ['gate entry', 'gate entries', 'vehicle entry', 'vehicle entries']):
            section = operations.get('gate_entries', {})
            count = self._matching_status_count(
                lower_question,
                section.get('status_counts', []),
                fallback=section.get('total_count'),
            )
            if count is not None:
                return f'There are {count} matching gate entries.'

        if any(term in lower_question for term in ['daily need', 'daily needs', 'canteen']):
            section = operations.get('daily_needs', {})
            count = self._matching_status_count(
                lower_question,
                section.get('vehicle_status_counts', []),
                fallback=section.get('total_count'),
            )
            if count is not None:
                return f'There are {count} matching daily needs gate entries.'

        if any(term in lower_question for term in ['maintenance', 'repair', 'work order']):
            section = operations.get('maintenance_gatein', {})
            urgency_count = self._matching_status_count(
                lower_question,
                section.get('urgency_counts', []),
            )
            if urgency_count is not None:
                return f'There are {urgency_count} matching maintenance gate entries.'
            count = self._matching_status_count(
                lower_question,
                section.get('vehicle_status_counts', []),
                fallback=section.get('total_count'),
            )
            if count is not None:
                return f'There are {count} matching maintenance gate entries.'

        if any(term in lower_question for term in ['construction', 'civil', 'contractor']):
            section = operations.get('construction_gatein', {})
            approval_count = self._matching_status_count(
                lower_question,
                section.get('security_approval_counts', []),
            )
            if approval_count is not None:
                return f'There are {approval_count} matching construction gate entries.'
            count = self._matching_status_count(
                lower_question,
                section.get('vehicle_status_counts', []),
                fallback=section.get('total_count'),
            )
            if count is not None:
                return f'There are {count} matching construction gate entries.'

        if 'grpo' in lower_question:
            section = operations.get('grpo_postings', {})
            count = self._matching_status_count(
                lower_question,
                section.get('status_counts', []),
                fallback=section.get('total_count'),
            )
            if count is not None:
                return f'There are {count} matching GRPO postings.'

        if 'production' in lower_question and 'run' in lower_question:
            section = operations.get('production', {})
            count = self._matching_status_count(
                lower_question,
                section.get('run_status_counts', []),
                fallback=section.get('run_total_count'),
            )
            if count is not None:
                return f'There are {count} matching production runs.'

        if 'weigh' in lower_question:
            section = operations.get('weighment', {})
            if 'complete' in lower_question or 'done' in lower_question:
                return f"There are {section.get('completed_count', 0)} completed weighments."
            if 'pending' in lower_question or 'incomplete' in lower_question:
                return f"There are {section.get('incomplete_count', 0)} incomplete weighments."
            if 'total_count' in section:
                return f"There are {section.get('total_count', 0)} weighment records."

        if 'bom' in lower_question:
            section = operations.get('warehouse', {})
            count = self._matching_status_count(
                lower_question,
                section.get('bom_request_status_counts', []),
            )
            if count is not None:
                return f'There are {count} matching BOM requests.'

        if any(term in lower_question for term in ['finished goods', 'fg receipt', 'fg receipts']):
            section = operations.get('warehouse', {})
            count = self._matching_status_count(
                lower_question,
                section.get('finished_goods_receipt_status_counts', []),
            )
            if count is not None:
                return f'There are {count} matching finished goods receipts.'

        if 'box' in lower_question or 'boxes' in lower_question:
            section = operations.get('barcode_inventory', {})
            count = self._matching_status_count(
                lower_question,
                section.get('box_status_counts', []),
                fallback=section.get('box_total_count'),
            )
            if count is not None:
                return f'There are {count} matching barcode boxes.'

        if 'pallet' in lower_question:
            section = operations.get('barcode_inventory', {})
            count = self._matching_status_count(
                lower_question,
                section.get('pallet_status_counts', []),
                fallback=section.get('pallet_total_count'),
            )
            if count is not None:
                return f'There are {count} matching pallets.'

        return ''

    def _fg_receipt_answer(self, *, question: str, context: dict[str, Any]) -> str:
        lower_question = question.lower()
        operations = context['data'].get('operations') or {}
        warehouse = operations.get('warehouse') or {}
        status_counts = warehouse.get('finished_goods_receipt_status_counts', [])

        if not status_counts:
            return 'There are 0 finished goods receipts.'

        if 'sap' in lower_question and 'post' in lower_question:
            count = self._count_for_status(status_counts, 'SAP_POSTED')
            return self._format_count(count, 'SAP-posted finished goods receipt')
        if 'pending' in lower_question:
            count = self._count_for_status(status_counts, 'PENDING')
            return self._format_count(count, 'pending finished goods receipt')
        if 'received' in lower_question or 'receive' in lower_question:
            count = self._count_for_status(status_counts, 'RECEIVED')
            return self._format_count(count, 'received finished goods receipt')
        if 'failed' in lower_question or 'fail' in lower_question:
            count = self._count_for_status(status_counts, 'FAILED')
            return self._format_count(count, 'failed finished goods receipt')
        if any(term in lower_question for term in ['how many', 'count', 'number of', 'total']):
            count = sum(int(item.get('count', 0)) for item in status_counts)
            return self._format_count(count, 'finished goods receipt')

        summary_parts = [
            f"{item.get('count', 0)} {self._status_label(str(item.get('value', '')))}"
            for item in status_counts
            if int(item.get('count', 0)) > 0
        ]
        if not summary_parts:
            return 'There are 0 finished goods receipts.'
        return f"Finished goods receipts: {', '.join(summary_parts)}."

    def _build_operational_context(
        self,
        *,
        question: str,
        page: str,
        tokens: list[str],
    ) -> dict[str, Any]:
        sections = {
            'gate_entries': self._gate_entry_context,
            'security_checks': self._security_check_context,
            'raw_material_pos': self._raw_material_po_context,
            'daily_needs': self._daily_needs_context,
            'maintenance_gatein': self._maintenance_gatein_context,
            'construction_gatein': self._construction_gatein_context,
            'grpo_postings': self._grpo_posting_context,
            'quality_control': self._quality_control_context,
            'weighment': self._weighment_context,
            'production': self._production_context,
            'warehouse': self._warehouse_context,
            'barcode_inventory': self._barcode_inventory_context,
        }
        selected_sections = self._selected_operation_sections(question=question, page=page)

        data: dict[str, Any] = {}
        for name, builder in sections.items():
            if name not in selected_sections:
                continue
            try:
                data[name] = builder(tokens=tokens)
            except Exception as exc:
                logger.info('AI assistant skipped %s context: %s', name, exc)
                data[name] = {'error': f'{name} data is unavailable.'}

        return {
            'data': data,
            'sources': [
                {
                    'source_type': 'factory_database',
                    'label': f"Factory database: {', '.join(data.keys())}",
                }
            ] if data else [],
        }

    @staticmethod
    def _selected_operation_sections(*, question: str, page: str) -> set[str]:
        text = f'{question} {page}'.lower()
        sections: set[str] = set()

        if FactoryAssistantService._is_fg_receipt_question(text):
            return {'warehouse'}
        if 'grpo' in text:
            return {'grpo_postings'}
        if 'bom' in text or 'warehouse' in text or 'material issue' in text:
            sections.add('warehouse')
        if any(term in text for term in ['gate entry', 'gate entries', 'vehicle entry', 'vehicle entries', '/gate']):
            sections.add('gate_entries')
        if 'security' in text:
            sections.add('security_checks')
        if any(term in text for term in ['raw material', 'po receipt', 'purchase order', 'supplier']):
            sections.add('raw_material_pos')
        if any(term in text for term in ['daily need', 'daily needs', 'canteen']):
            sections.add('daily_needs')
        if any(term in text for term in ['maintenance', 'repair', 'work order', 'equipment']):
            sections.add('maintenance_gatein')
        if any(term in text for term in ['construction', 'civil', 'contractor', 'project']):
            sections.add('construction_gatein')
        if any(term in text for term in ['quality', 'qc', 'inspection', 'arrival slip']):
            sections.add('quality_control')
        if 'weigh' in text:
            sections.add('weighment')
        if any(term in text for term in ['production', 'run', 'breakdown', 'waste', 'line clearance']):
            sections.add('production')
        if any(term in text for term in ['barcode', 'box', 'boxes', 'pallet', 'label']):
            sections.add('barcode_inventory')

        if sections:
            return sections
        return {
            'gate_entries',
            'security_checks',
            'raw_material_pos',
            'daily_needs',
            'maintenance_gatein',
            'construction_gatein',
            'grpo_postings',
            'quality_control',
            'weighment',
            'production',
            'warehouse',
            'barcode_inventory',
        }

    def _gate_entry_context(self, *, tokens: list[str]) -> dict[str, Any]:
        qs = VehicleEntry.objects.filter(company=self.company)
        matched = self._token_filter(
            qs,
            tokens,
            ['entry_no', 'status', 'entry_type', 'vehicle__vehicle_number', 'driver__name'],
        )
        recent = matched.select_related('vehicle', 'driver').order_by('-entry_time')[: self.max_rows]
        return {
            'total_count': qs.count(),
            'status_counts': self._counts_by(qs, 'status'),
            'entry_type_counts': self._counts_by(qs, 'entry_type'),
            'matching_records': [
                {
                    'id': entry.id,
                    'entry_no': entry.entry_no,
                    'entry_type': entry.entry_type,
                    'status': entry.status,
                    'vehicle_number': entry.vehicle.vehicle_number if entry.vehicle_id else '',
                    'driver_name': entry.driver.name if entry.driver_id else '',
                    'entry_time': entry.entry_time.isoformat() if entry.entry_time else '',
                }
                for entry in recent
            ],
        }

    def _security_check_context(self, *, tokens: list[str]) -> dict[str, Any]:
        qs = SecurityCheck.objects.filter(vehicle_entry__company=self.company)
        matched = self._token_filter(
            qs,
            tokens,
            ['vehicle_entry__entry_no', 'vehicle_entry__vehicle__vehicle_number', 'inspected_by_name'],
        )
        recent = matched.select_related('vehicle_entry', 'vehicle_entry__vehicle').order_by(
            '-inspection_time'
        )[: self.max_rows]
        submitted_count = qs.filter(is_submitted=True).count()
        failed_count = qs.filter(
            Q(vehicle_condition_ok=False)
            | Q(tyre_condition_ok=False)
            | Q(fire_extinguisher_available=False)
            | Q(alcohol_test_passed=False)
        ).count()
        return {
            'total_count': qs.count(),
            'submitted_count': submitted_count,
            'draft_count': qs.count() - submitted_count,
            'failed_or_not_ok_count': failed_count,
            'matching_records': [
                {
                    'id': check.id,
                    'entry_no': check.vehicle_entry.entry_no,
                    'vehicle_number': (
                        check.vehicle_entry.vehicle.vehicle_number
                        if check.vehicle_entry.vehicle_id
                        else ''
                    ),
                    'is_submitted': check.is_submitted,
                    'inspected_by_name': check.inspected_by_name,
                    'inspection_time': check.inspection_time.isoformat()
                    if check.inspection_time
                    else '',
                }
                for check in recent
            ],
        }

    def _raw_material_po_context(self, *, tokens: list[str]) -> dict[str, Any]:
        qs = POReceipt.objects.filter(vehicle_entry__company=self.company)
        matched = self._token_filter(
            qs,
            tokens,
            [
                'po_number',
                'supplier_code',
                'supplier_name',
                'invoice_no',
                'challan_no',
                'vehicle_entry__entry_no',
            ],
        )
        recent = matched.select_related('vehicle_entry').prefetch_related('items').order_by(
            '-created_at'
        )[: self.max_rows]
        return {
            'total_po_count': qs.count(),
            'total_item_count': self._safe_count_items(qs),
            'matching_records': [
                {
                    'id': po.id,
                    'po_number': po.po_number,
                    'supplier_code': po.supplier_code,
                    'supplier_name': po.supplier_name,
                    'entry_no': po.vehicle_entry.entry_no,
                    'item_count': po.items.count(),
                    'invoice_no': po.invoice_no,
                    'challan_no': po.challan_no,
                    'created_at': po.created_at.isoformat() if po.created_at else '',
                }
                for po in recent
            ],
        }

    def _daily_needs_context(self, *, tokens: list[str]) -> dict[str, Any]:
        qs = DailyNeedGateEntry.objects.filter(vehicle_entry__company=self.company)
        matched = self._token_filter(
            qs,
            tokens,
            [
                'vehicle_entry__entry_no',
                'vehicle_entry__status',
                'supplier_name',
                'material_name',
                'bill_number',
                'delivery_challan_number',
                'item_category__category_name',
                'receiving_department__name',
            ],
        )
        recent = matched.select_related(
            'vehicle_entry',
            'item_category',
            'unit',
            'receiving_department',
        ).order_by('-created_at')[: self.max_rows]
        return {
            'total_count': qs.count(),
            'vehicle_status_counts': self._counts_by(qs, 'vehicle_entry__status'),
            'category_counts': self._counts_by(qs, 'item_category__category_name'),
            'department_counts': self._counts_by(qs, 'receiving_department__name'),
            'matching_records': [
                {
                    'id': entry.id,
                    'entry_no': entry.vehicle_entry.entry_no,
                    'status': entry.vehicle_entry.status,
                    'category': entry.item_category.category_name if entry.item_category_id else '',
                    'supplier_name': entry.supplier_name,
                    'material_name': entry.material_name,
                    'quantity': str(entry.quantity),
                    'unit': str(entry.unit) if entry.unit_id else '',
                    'receiving_department': (
                        entry.receiving_department.name if entry.receiving_department_id else ''
                    ),
                    'bill_number': entry.bill_number or '',
                    'delivery_challan_number': entry.delivery_challan_number or '',
                    'created_at': entry.created_at.isoformat() if entry.created_at else '',
                }
                for entry in recent
            ],
        }

    def _maintenance_gatein_context(self, *, tokens: list[str]) -> dict[str, Any]:
        qs = MaintenanceGateEntry.objects.filter(vehicle_entry__company=self.company)
        matched = self._token_filter(
            qs,
            tokens,
            [
                'vehicle_entry__entry_no',
                'vehicle_entry__status',
                'work_order_number',
                'supplier_name',
                'material_description',
                'part_number',
                'equipment_id',
                'urgency_level',
                'maintenance_type__type_name',
                'receiving_department__name',
            ],
        )
        recent = matched.select_related(
            'vehicle_entry',
            'maintenance_type',
            'unit',
            'receiving_department',
        ).order_by('-created_at')[: self.max_rows]
        return {
            'total_count': qs.count(),
            'vehicle_status_counts': self._counts_by(qs, 'vehicle_entry__status'),
            'urgency_counts': self._counts_by(qs, 'urgency_level'),
            'maintenance_type_counts': self._counts_by(qs, 'maintenance_type__type_name'),
            'matching_records': [
                {
                    'id': entry.id,
                    'entry_no': entry.vehicle_entry.entry_no,
                    'status': entry.vehicle_entry.status,
                    'work_order_number': entry.work_order_number or '',
                    'maintenance_type': (
                        entry.maintenance_type.type_name if entry.maintenance_type_id else ''
                    ),
                    'supplier_name': entry.supplier_name,
                    'material_description': entry.material_description,
                    'equipment_id': entry.equipment_id or '',
                    'urgency_level': entry.urgency_level,
                    'quantity': str(entry.quantity),
                    'unit': str(entry.unit) if entry.unit_id else '',
                    'receiving_department': (
                        entry.receiving_department.name if entry.receiving_department_id else ''
                    ),
                    'created_at': entry.created_at.isoformat() if entry.created_at else '',
                }
                for entry in recent
            ],
        }

    def _construction_gatein_context(self, *, tokens: list[str]) -> dict[str, Any]:
        qs = ConstructionGateEntry.objects.filter(vehicle_entry__company=self.company)
        matched = self._token_filter(
            qs,
            tokens,
            [
                'vehicle_entry__entry_no',
                'vehicle_entry__status',
                'project_name',
                'work_order_number',
                'contractor_name',
                'material_description',
                'security_approval',
                'material_category__category_name',
                'challan_number',
                'invoice_number',
            ],
        )
        recent = matched.select_related(
            'vehicle_entry',
            'material_category',
            'unit',
        ).order_by('-created_at')[: self.max_rows]
        return {
            'total_count': qs.count(),
            'vehicle_status_counts': self._counts_by(qs, 'vehicle_entry__status'),
            'security_approval_counts': self._counts_by(qs, 'security_approval'),
            'material_category_counts': self._counts_by(qs, 'material_category__category_name'),
            'matching_records': [
                {
                    'id': entry.id,
                    'entry_no': entry.vehicle_entry.entry_no,
                    'status': entry.vehicle_entry.status,
                    'project_name': entry.project_name or '',
                    'work_order_number': entry.work_order_number or '',
                    'contractor_name': entry.contractor_name,
                    'material_category': (
                        entry.material_category.category_name if entry.material_category_id else ''
                    ),
                    'material_description': entry.material_description,
                    'security_approval': entry.security_approval,
                    'quantity': str(entry.quantity),
                    'unit': str(entry.unit) if entry.unit_id else '',
                    'challan_number': entry.challan_number or '',
                    'invoice_number': entry.invoice_number or '',
                    'created_at': entry.created_at.isoformat() if entry.created_at else '',
                }
                for entry in recent
            ],
        }

    def _grpo_posting_context(self, *, tokens: list[str]) -> dict[str, Any]:
        qs = GRPOPosting.objects.filter(vehicle_entry__company=self.company)
        matched = self._token_filter(
            qs,
            tokens,
            [
                'status',
                'vehicle_entry__entry_no',
                'po_receipt__po_number',
                'po_receipts__po_number',
                'error_message',
            ],
        )
        recent = matched.select_related('vehicle_entry', 'po_receipt').prefetch_related(
            'po_receipts'
        ).order_by('-created_at')[: self.max_rows]
        return {
            'total_count': qs.count(),
            'status_counts': self._counts_by(qs, 'status'),
            'matching_records': [
                {
                    'id': posting.id,
                    'entry_no': posting.vehicle_entry.entry_no,
                    'po_numbers': self._grpo_po_numbers(posting),
                    'status': posting.status,
                    'sap_doc_num': posting.sap_doc_num,
                    'sap_doc_total': str(posting.sap_doc_total)
                    if posting.sap_doc_total is not None
                    else '',
                    'error_message': posting.error_message or '',
                    'created_at': posting.created_at.isoformat() if posting.created_at else '',
                    'posted_at': posting.posted_at.isoformat() if posting.posted_at else '',
                }
                for posting in recent
            ],
        }

    def _quality_control_context(self, *, tokens: list[str]) -> dict[str, Any]:
        slip_qs = MaterialArrivalSlip.objects.filter(
            po_item_receipt__po_receipt__vehicle_entry__company=self.company
        )
        inspection_qs = RawMaterialInspection.objects.filter(
            arrival_slip__po_item_receipt__po_receipt__vehicle_entry__company=self.company,
            is_active=True,
        )
        matched = self._token_filter(
            inspection_qs,
            tokens,
            [
                'report_no',
                'internal_lot_no',
                'description_of_material',
                'sap_code',
                'supplier_name',
                'purchase_order_no',
                'final_status',
                'workflow_status',
                'arrival_slip__po_item_receipt__po_receipt__vehicle_entry__entry_no',
            ],
        )
        recent = matched.select_related(
            'arrival_slip',
            'arrival_slip__po_item_receipt',
            'arrival_slip__po_item_receipt__po_receipt',
            'arrival_slip__po_item_receipt__po_receipt__vehicle_entry',
        ).order_by('-created_at')[: self.max_rows]
        return {
            'arrival_slip_status_counts': self._counts_by(slip_qs, 'status'),
            'inspection_workflow_status_counts': self._counts_by(inspection_qs, 'workflow_status'),
            'inspection_final_status_counts': self._counts_by(inspection_qs, 'final_status'),
            'matching_inspections': [
                {
                    'id': inspection.id,
                    'report_no': inspection.report_no,
                    'entry_no': inspection.vehicle_entry.entry_no if inspection.arrival_slip_id else '',
                    'material': inspection.description_of_material,
                    'supplier_name': inspection.supplier_name,
                    'workflow_status': inspection.workflow_status,
                    'final_status': inspection.final_status,
                    'inspection_date': inspection.inspection_date.isoformat()
                    if inspection.inspection_date
                    else '',
                }
                for inspection in recent
            ],
        }

    def _weighment_context(self, *, tokens: list[str]) -> dict[str, Any]:
        qs = Weighment.objects.filter(vehicle_entry__company=self.company)
        matched = self._token_filter(
            qs,
            tokens,
            [
                'vehicle_entry__entry_no',
                'vehicle_entry__vehicle__vehicle_number',
                'weighbridge_slip_no',
            ],
        )
        recent = matched.select_related(
            'vehicle_entry',
            'vehicle_entry__vehicle',
        ).order_by('-created_at')[: self.max_rows]
        complete_qs = qs.filter(gross_weight__isnull=False, tare_weight__isnull=False)
        return {
            'total_count': qs.count(),
            'completed_count': complete_qs.count(),
            'incomplete_count': qs.exclude(gross_weight__isnull=False, tare_weight__isnull=False).count(),
            'matching_records': [
                {
                    'id': weighment.id,
                    'entry_no': weighment.vehicle_entry.entry_no,
                    'vehicle_number': (
                        weighment.vehicle_entry.vehicle.vehicle_number
                        if weighment.vehicle_entry.vehicle_id
                        else ''
                    ),
                    'gross_weight': str(weighment.gross_weight)
                    if weighment.gross_weight is not None
                    else '',
                    'tare_weight': str(weighment.tare_weight)
                    if weighment.tare_weight is not None
                    else '',
                    'net_weight': str(weighment.net_weight),
                    'weighbridge_slip_no': weighment.weighbridge_slip_no,
                }
                for weighment in recent
            ],
        }

    def _production_context(self, *, tokens: list[str]) -> dict[str, Any]:
        run_qs = ProductionRun.objects.filter(company=self.company)
        matched = self._token_filter(
            run_qs,
            tokens,
            ['status', 'product', 'line__name', 'supervisor', 'operators'],
        )
        recent = matched.select_related('line').order_by('-date', '-created_at')[: self.max_rows]
        breakdown_qs = MachineBreakdown.objects.filter(production_run__company=self.company)
        waste_qs = WasteLog.objects.filter(production_run__company=self.company)
        clearance_qs = LineClearance.objects.filter(company=self.company)
        return {
            'run_total_count': run_qs.count(),
            'run_status_counts': self._counts_by(run_qs, 'status'),
            'warehouse_approval_status_counts': self._counts_by(
                run_qs,
                'warehouse_approval_status',
            ),
            'active_breakdown_count': breakdown_qs.filter(is_active=True).count(),
            'waste_approval_status_counts': self._counts_by(
                waste_qs,
                'wastage_approval_status',
            ),
            'line_clearance_status_counts': self._counts_by(clearance_qs, 'status'),
            'matching_runs': [
                {
                    'id': run.id,
                    'run_number': run.run_number,
                    'date': run.date.isoformat() if run.date else '',
                    'line': run.line.name if run.line_id else '',
                    'product': run.product,
                    'status': run.status,
                    'required_qty': str(run.required_qty) if run.required_qty is not None else '',
                    'total_production': str(run.total_production),
                    'warehouse_approval_status': run.warehouse_approval_status,
                    'sap_sync_status': run.sap_sync_status,
                }
                for run in recent
            ],
        }

    def _warehouse_context(self, *, tokens: list[str]) -> dict[str, Any]:
        bom_qs = BOMRequest.objects.filter(company=self.company)
        fg_qs = FinishedGoodsReceipt.objects.filter(company=self.company)
        matched_bom = self._token_filter(
            bom_qs,
            tokens,
            ['status', 'material_issue_status', 'production_run__product', 'remarks'],
        ).select_related('production_run').order_by('-created_at')[: self.max_rows]
        matched_fg = self._token_filter(
            fg_qs,
            tokens,
            ['status', 'item_code', 'item_name', 'warehouse', 'production_run__product'],
        ).select_related('production_run').order_by('-created_at')[: self.max_rows]
        return {
            'bom_request_status_counts': self._counts_by(bom_qs, 'status'),
            'bom_material_issue_status_counts': self._counts_by(bom_qs, 'material_issue_status'),
            'finished_goods_receipt_status_counts': self._counts_by(fg_qs, 'status'),
            'matching_bom_requests': [
                {
                    'id': request.id,
                    'production_run_id': request.production_run_id,
                    'product': request.production_run.product if request.production_run_id else '',
                    'status': request.status,
                    'material_issue_status': request.material_issue_status,
                    'required_qty': str(request.required_qty),
                    'created_at': request.created_at.isoformat() if request.created_at else '',
                }
                for request in matched_bom
            ],
            'matching_finished_goods_receipts': [
                {
                    'id': receipt.id,
                    'production_run_id': receipt.production_run_id,
                    'item_code': receipt.item_code,
                    'item_name': receipt.item_name,
                    'good_qty': str(receipt.good_qty),
                    'rejected_qty': str(receipt.rejected_qty),
                    'warehouse': receipt.warehouse,
                    'status': receipt.status,
                    'posting_date': receipt.posting_date.isoformat()
                    if receipt.posting_date
                    else '',
                }
                for receipt in matched_fg
            ],
        }

    def _barcode_inventory_context(self, *, tokens: list[str]) -> dict[str, Any]:
        box_qs = Box.objects.filter(company=self.company)
        pallet_qs = Pallet.objects.filter(company=self.company)
        return {
            'box_total_count': box_qs.count(),
            'box_status_counts': self._counts_by(box_qs, 'status'),
            'pallet_total_count': pallet_qs.count(),
            'pallet_status_counts': self._counts_by(pallet_qs, 'status'),
            'print_log_count': LabelPrintLog.objects.filter(company=self.company).count(),
        }

    def _answer_from_database(
        self,
        *,
        question: str,
        page: str,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        if not self._should_use_database_query(question):
            return {}
        if not self.user.has_perm('ai_assistant.can_query_factory_database'):
            self._last_database_audit = {
                'validation_status': 'permission_denied',
                'blocked_reason': 'User lacks ai_assistant.can_query_factory_database.',
            }
            return {}

        schema = self._database_schema_context()
        if not schema['tables']:
            return {}

        plan = self._generate_database_sql(question=question, page=page, schema=schema)
        sql = str(plan.get('sql') or '').strip()
        self._last_database_audit = {
            'generated_sql': self._compact_sql(sql) if sql else '',
            'validation_status': 'planned' if sql else 'empty_plan',
        }
        if not sql:
            return {}

        try:
            safe_sql = self._validate_read_only_sql(sql, schema=schema)
            self._last_database_audit.update({
                'generated_sql': self._compact_sql(safe_sql),
                'validation_status': 'passed',
            })
            query_result = self._execute_read_only_sql(safe_sql)
        except (DatabaseError, ValueError) as exc:
            logger.info('AI assistant SQL path skipped: %s', exc)
            self._last_database_audit.update({
                'validation_status': 'blocked',
                'blocked_reason': str(exc),
            })
            return {}

        summary_result = self._summarize_database_answer(
            question=question,
            page=page,
            context=context,
            sql=safe_sql,
            query_result=query_result,
        )
        return {
            'answer': summary_result['text'],
            'model': summary_result['model'],
            'source': {
                'type': 'factory_database_sql',
                'label': f"Full read-only database query ({query_result['row_count']} rows)",
            },
            'summary': {
                'sql': self._compact_sql(safe_sql),
                'columns': query_result['columns'],
                'row_count': query_result['row_count'],
                'row_limit': self.SQL_RESULT_ROW_LIMIT,
            },
        }

    @staticmethod
    def _should_use_database_query(question: str) -> bool:
        lower_question = question.lower()
        documentation_terms = ['how to', 'guide', 'documentation', 'docs', 'manual', 'steps']
        data_terms = [
            'ageing',
            'aging',
            'analysis',
            'analyze',
            'average',
            'avg',
            'bottleneck',
            'compare',
            'comparison',
            'dashboard',
            'date wise',
            'day wise',
            'deep',
            'delay',
            'find out',
            'highest',
            'insight',
            'inventory',
            'issue',
            'last month',
            'last week',
            'lowest',
            'material',
            'monthly',
            'person',
            'performance',
            'quality',
            'reason',
            'reject',
            'report',
            'records',
            'risk',
            'root cause',
            'show',
            'stock',
            'supplier',
            'summary',
            'trend',
            'top',
            'total',
            'warehouse',
            'wastage',
            'weekly',
            'what',
            'when',
            'where',
            'which',
            'who',
            'why',
        ]
        if any(term in lower_question for term in documentation_terms):
            return any(term in lower_question for term in data_terms)
        return any(term in lower_question for term in data_terms)

    def _database_schema_context(self) -> dict[str, Any]:
        models = [
            model
            for model in apps.get_models(include_auto_created=True)
            if self._is_sql_model_allowed(model)
        ]
        scoped_tables = self._company_scoped_table_names(models)
        incoming_foreign_keys = self._incoming_foreign_keys(models)

        tables: list[dict[str, Any]] = []
        for model in sorted(models, key=lambda item: (item._meta.app_label, item._meta.model_name)):
            fields: list[str] = []
            foreign_keys: list[str] = []
            for field in model._meta.fields[: self.SQL_SCHEMA_COLUMN_LIMIT]:
                column_name = getattr(field, 'column', field.name)
                if self.SQL_SENSITIVE_COLUMN_PATTERN.search(column_name):
                    continue

                remote_model = getattr(getattr(field, 'remote_field', None), 'model', None)
                if remote_model and hasattr(remote_model, '_meta'):
                    target_table = remote_model._meta.db_table
                    fields.append(f'{column_name}:FK->{target_table}')
                    foreign_keys.append(f'{column_name}->{target_table}.id')
                else:
                    fields.append(f'{column_name}:{field.get_internal_type()}')

            if not fields:
                continue

            tables.append({
                'table': model._meta.db_table,
                'model': f'{model._meta.app_label}.{model.__name__}',
                'company_scoped': model._meta.db_table in scoped_tables,
                'columns': fields,
                'foreign_keys': foreign_keys[:12],
                'referenced_by': incoming_foreign_keys.get(model._meta.db_table, [])[:12],
            })

        return {
            'current_company': {
                'id': self.company.id,
                'code': self.company_code,
                'name': getattr(self.company, 'name', ''),
            },
            'tables': tables,
            'allowed_table_names': {table['table'] for table in tables},
            'company_scoped_table_names': scoped_tables,
        }

    @classmethod
    def _is_sql_model_allowed(cls, model) -> bool:
        opts = model._meta
        if opts.app_label in cls.SQL_EXCLUDED_APP_LABELS:
            return False
        if opts.proxy or not opts.managed:
            return False
        identifier = f'{opts.app_label}.{opts.model_name}.{opts.db_table}'
        if cls.SQL_EXCLUDED_TABLE_PATTERN.search(identifier):
            return False
        return True

    @staticmethod
    def _company_scoped_table_names(models: list[Any]) -> set[str]:
        company_model = apps.get_model('company', 'Company')
        candidate_models = set(models)
        candidate_models.add(company_model)
        scoped_models = {company_model}

        relations: list[tuple[Any, Any]] = []
        for model in candidate_models:
            for field in model._meta.fields:
                remote_model = getattr(getattr(field, 'remote_field', None), 'model', None)
                if remote_model in candidate_models:
                    relations.append((model, remote_model))

        changed = True
        while changed:
            changed = False
            for left_model, right_model in relations:
                if left_model in scoped_models and right_model not in scoped_models:
                    scoped_models.add(right_model)
                    changed = True
                if right_model in scoped_models and left_model not in scoped_models:
                    scoped_models.add(left_model)
                    changed = True

        return {
            model._meta.db_table
            for model in scoped_models
            if model in models or model is company_model
        }

    @staticmethod
    def _incoming_foreign_keys(models: list[Any]) -> dict[str, list[str]]:
        incoming: dict[str, list[str]] = {}
        model_set = set(models)
        for model in models:
            source_table = model._meta.db_table
            for field in model._meta.fields:
                remote_model = getattr(getattr(field, 'remote_field', None), 'model', None)
                if remote_model not in model_set:
                    continue
                target_table = remote_model._meta.db_table
                incoming.setdefault(target_table, []).append(
                    f'{source_table}.{field.column}->{target_table}.id'
                )
        return incoming

    def _generate_database_sql(
        self,
        *,
        question: str,
        page: str,
        schema: dict[str, Any],
    ) -> dict[str, str]:
        schema_prompt = {
            'dialect': connection.vendor,
            'current_company': schema['current_company'],
            'tables': schema['tables'],
        }
        system_prompt = (
            'You write safe read-only SQL for the full Factory business database schema provided. '
            'Return only JSON with keys "sql" and "reason". Use SELECT or WITH only. '
            'Use only the provided tables and columns. Never select password, token, '
            'secret, credential, session, or private key data. Never write data. '
            'Always filter company-scoped data to the current company. Prefer direct '
            'company_id filters when available. When a table is company-scoped but has '
            'no company_id column, use the foreign_keys and referenced_by hints to join '
            'through related tables until a company_id or company code filter is possible. '
            'For list queries, limit the result.'
        )
        user_prompt = (
            f'Current page: {page or "unknown"}\n'
            f'Question: {question}\n\n'
            'Date context JSON:\n'
            f'{json.dumps(self._date_context(), default=str, ensure_ascii=False)}\n\n'
            'Schema JSON:\n'
            f'{json.dumps(schema_prompt, default=str, ensure_ascii=False)}\n\n'
            'Return example: {"sql": "SELECT ...", "reason": "why this query answers it"}\n'
            'If the database cannot answer the question, return {"sql": null, "reason": "..."}'
        )
        result = self._call_gemini_text(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_output_tokens=1200,
            temperature=0.0,
        )
        return self._parse_database_sql_plan(result['text'])

    @staticmethod
    def _parse_database_sql_plan(text: str) -> dict[str, str]:
        cleaned = text.strip()
        if cleaned.startswith('```'):
            cleaned = re.sub(r'^```(?:json)?\s*', '', cleaned, flags=re.IGNORECASE)
            cleaned = re.sub(r'\s*```$', '', cleaned)

        match = re.search(r'\{.*\}', cleaned, flags=re.DOTALL)
        payload_text = match.group(0) if match else cleaned
        try:
            payload = json.loads(payload_text)
        except json.JSONDecodeError:
            logger.info('AI assistant SQL planner returned non-JSON text: %s', text[:300])
            return {}

        sql = payload.get('sql') if isinstance(payload, dict) else ''
        reason = payload.get('reason') if isinstance(payload, dict) else ''
        return {
            'sql': sql if isinstance(sql, str) else '',
            'reason': reason if isinstance(reason, str) else '',
        }

    def _validate_read_only_sql(self, sql: str, *, schema: dict[str, Any]) -> str:
        cleaned = sql.strip().rstrip(';').strip()
        if not cleaned:
            raise ValueError('SQL query is empty.')
        if ';' in cleaned:
            raise ValueError('Only one SQL statement is allowed.')
        if '--' in cleaned or '/*' in cleaned or '*/' in cleaned:
            raise ValueError('SQL comments are not allowed.')
        if self.SQL_FORBIDDEN_PATTERN.search(cleaned):
            raise ValueError('Only read-only SELECT queries are allowed.')
        if self.SQL_SENSITIVE_PATTERN.search(cleaned):
            raise ValueError('Sensitive columns are not allowed.')

        statements = sqlparse.parse(cleaned)
        if len(statements) != 1:
            raise ValueError('Only one SQL statement is allowed.')

        first_token = statements[0].token_first(skip_cm=True)
        first_value = first_token.normalized.upper() if first_token else ''
        if first_value not in {'SELECT', 'WITH'}:
            raise ValueError('Only SELECT or WITH queries are allowed.')

        table_refs = self._extract_sql_table_refs(cleaned)
        cte_names = self._extract_sql_cte_names(cleaned)
        unknown_tables = sorted(
            table
            for table in table_refs
            if table not in schema['allowed_table_names'] and table not in cte_names
        )
        if unknown_tables:
            raise ValueError(f'Query referenced unsupported tables: {", ".join(unknown_tables)}')

        scoped_refs = {
            table
            for table in table_refs
            if table in schema['company_scoped_table_names']
        }
        if scoped_refs and not self._sql_has_company_scope(cleaned):
            raise ValueError('Company-scoped queries must filter the current company.')

        return cleaned

    def _execute_read_only_sql(self, sql: str) -> dict[str, Any]:
        limited_sql = self._wrap_sql_with_limit(sql)
        alias = settings.AI_ASSISTANT_SQL_DATABASE_ALIAS
        db_connection = connections[alias]
        with transaction.atomic(using=alias):
            with db_connection.cursor() as cursor:
                if db_connection.vendor == 'postgresql':
                    cursor.execute('SET TRANSACTION READ ONLY')
                    cursor.execute('SET LOCAL statement_timeout = 10000')
                cursor.execute(limited_sql)
                if cursor.description is None:
                    raise ValueError('Query did not return rows.')
                columns = [column[0] for column in cursor.description]
                rows = [
                    {
                        column: self._json_safe_value(value)
                        for column, value in zip(columns, row)
                    }
                    for row in cursor.fetchall()
                ]

        return {
            'sql': limited_sql,
            'columns': columns,
            'rows': rows,
            'row_count': len(rows),
        }

    def _summarize_database_answer(
        self,
        *,
        question: str,
        page: str,
        context: dict[str, Any],
        sql: str,
        query_result: dict[str, Any],
    ) -> dict[str, str]:
        system_prompt = (
            'You are a Factory data analyst. Answer using only the read-only SQL result '
            'and the small context summary provided. Be direct and practical. For deep '
            'questions, give useful insights, risks, comparisons, or next checks when '
            'the data supports them. If rows are capped, say so for list-style answers. '
            'Do not claim you changed or posted any data.'
        )
        user_prompt = (
            f'Current page: {page or "unknown"}\n'
            f'Question: {question}\n\n'
            'Date context JSON:\n'
            f'{json.dumps(self._date_context(), default=str, ensure_ascii=False)}\n\n'
            f'SQL used:\n{sql}\n\n'
            f'Rows are capped at {self.SQL_RESULT_ROW_LIMIT}.\n'
            'SQL result JSON:\n'
            f'{json.dumps(query_result, default=str, ensure_ascii=False)}\n\n'
            'Existing context summary JSON:\n'
            f'{json.dumps(context.get("summary", {}), default=str, ensure_ascii=False)}'
        )
        return self._call_gemini_text(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_output_tokens=900,
            temperature=0.15,
        )

    @classmethod
    def _extract_sql_table_refs(cls, sql: str) -> set[str]:
        refs: set[str] = set()
        for match in cls.SQL_TABLE_REF_PATTERN.finditer(sql):
            raw_name = match.group(1).strip().strip(',')
            if raw_name.startswith('('):
                continue
            normalized = raw_name.split()[0].strip('"')
            if '.' in normalized:
                normalized = normalized.split('.')[-1].strip('"')
            normalized = normalized.strip('"').lower()
            if normalized and normalized not in {'select', 'lateral'}:
                refs.add(normalized)
        return refs

    @classmethod
    def _extract_sql_cte_names(cls, sql: str) -> set[str]:
        return {match.group(1).lower() for match in cls.SQL_CTE_PATTERN.finditer(sql)}

    def _sql_has_company_scope(self, sql: str) -> bool:
        normalized = re.sub(r'\s+', ' ', sql.lower())
        company_id = re.escape(str(self.company.id))
        company_code = re.escape(str(self.company_code).lower())
        return (
            re.search(rf'\bcompany_id\s*=\s*{company_id}\b', normalized) is not None
            or re.search(rf'\bcompany_id\s+in\s*\(\s*{company_id}\s*\)', normalized) is not None
            or re.search(
                rf'\b(?:code|company_code)\s*=\s*[\'"]{company_code}[\'"]',
                normalized,
            ) is not None
        )

    def _wrap_sql_with_limit(self, sql: str) -> str:
        return f'SELECT * FROM ({sql}) AS ai_readonly_query LIMIT {self.SQL_RESULT_ROW_LIMIT}'

    @staticmethod
    def _json_safe_value(value):
        if hasattr(value, 'isoformat'):
            return value.isoformat()
        try:
            json.dumps(value)
            return value
        except TypeError:
            return str(value)

    @staticmethod
    def _compact_sql(sql: str) -> str:
        compact = re.sub(r'\s+', ' ', sql).strip()
        return compact[:1000]

    def _call_gemini(self, *, question: str, page: str, context: dict[str, Any]) -> dict[str, str]:
        system_prompt = (
            'You are the Factory site AI assistant. Answer using only the provided '
            'Factory context and general troubleshooting knowledge. This is read-only: '
            'do not claim you generated labels, moved stock, posted SAP documents, '
            'approved QC, or changed records. If data is missing, say what the user '
            'should check in the app. Keep answers short, practical, and clear.'
        )
        user_prompt = (
            f'Current page: {page or "unknown"}\n'
            f'User question: {question}\n\n'
            'Date context JSON:\n'
            f'{json.dumps(self._date_context(), default=str, ensure_ascii=False)}\n\n'
            'Factory context JSON:\n'
            f'{json.dumps(context, default=str, ensure_ascii=False)}'
        )
        return self._call_gemini_text(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_output_tokens=700,
            temperature=0.2,
        )

    def _call_gemini_text(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        max_output_tokens: int,
        temperature: float,
    ) -> dict[str, str]:
        api_key = settings.GEMINI_API_KEY.strip()
        if not api_key:
            raise AssistantConfigError('Gemini API key is missing. Add GEMINI_API_KEY to backend .env.')

        payload = {
            'systemInstruction': {
                'parts': [{'text': system_prompt}],
            },
            'contents': [
                {
                    'role': 'user',
                    'parts': [{'text': user_prompt}],
                },
            ],
            'generationConfig': {
                'maxOutputTokens': max_output_tokens,
                'temperature': temperature,
            },
        }

        last_error = 'AI provider request failed. Please try again.'
        models = self._gemini_model_candidates()
        for index, model in enumerate(models):
            response = self._post_gemini(api_key=api_key, model=model, payload=payload)
            if response.status_code >= 400:
                provider_error = self._provider_error_message(response)
                last_error = provider_error
                logger.warning(
                    'AI assistant provider returned %s for %s: %s',
                    response.status_code,
                    model,
                    response.text[:500],
                )
                if self._should_try_next_model(response) and index < len(models) - 1:
                    continue
                raise AssistantProviderError(provider_error)

            return {
                'text': self._extract_gemini_text(response),
                'model': model,
            }

        raise AssistantProviderError(last_error)

    def _post_gemini(self, *, api_key: str, model: str, payload: dict[str, Any]):
        url = f'{self.GEMINI_GENERATE_CONTENT_BASE_URL}/{model}:generateContent'
        try:
            return requests.post(
                url,
                headers={
                    'x-goog-api-key': api_key,
                    'Content-Type': 'application/json',
                },
                json=payload,
                timeout=settings.AI_ASSISTANT_TIMEOUT_SECONDS,
            )
        except requests.exceptions.Timeout as exc:
            logger.exception('AI assistant provider request timed out')
            raise AssistantProviderError(
                'Gemini did not respond before the timeout. Please check internet connectivity and try again.'
            ) from exc
        except requests.exceptions.ConnectionError as exc:
            logger.exception('AI assistant provider connection failed')
            message = str(exc).lower()
            if any(term in message for term in ['getaddrinfo', 'name resolution', 'failed to resolve']):
                raise AssistantProviderError(
                    'Cannot reach Gemini because DNS/network resolution is failing for googleapis.com. '
                    'Please check internet, DNS, or proxy settings and try again.'
                ) from exc
            raise AssistantProviderError(
                'Cannot reach Gemini. Please check internet, firewall, or proxy settings and try again.'
            ) from exc
        except requests.RequestException as exc:
            logger.exception('AI assistant provider request failed')
            raise AssistantProviderError('AI provider request failed. Please try again.') from exc

    @staticmethod
    def _extract_gemini_text(response) -> str:
        try:
            data = response.json()
        except ValueError as exc:
            raise AssistantProviderError('AI provider did not return JSON.') from exc

        for candidate in data.get('candidates', []):
            content = candidate.get('content', {})
            for part in content.get('parts', []):
                text = part.get('text')
                if isinstance(text, str) and text.strip():
                    return text.strip()

        prompt_feedback = data.get('promptFeedback', {})
        block_reason = prompt_feedback.get('blockReason') if isinstance(prompt_feedback, dict) else ''
        if block_reason:
            raise AssistantProviderError(f'AI provider blocked the request: {block_reason}.')

        raise AssistantProviderError('AI provider did not return text.')

    @staticmethod
    def _gemini_model_candidates() -> list[str]:
        configured = [settings.GEMINI_MODEL, *settings.GEMINI_FALLBACK_MODELS]
        models: list[str] = []
        for model in configured:
            normalized = str(model).strip().removeprefix('models/')
            if normalized and normalized not in models:
                models.append(normalized)
        return models

    @staticmethod
    def _should_try_next_model(response) -> bool:
        if response.status_code in (429, 500, 502, 503, 504):
            return True
        try:
            payload = response.json()
        except ValueError:
            return False
        error = payload.get('error', {}) if isinstance(payload, dict) else {}
        status_text = error.get('status', '') if isinstance(error, dict) else ''
        message = error.get('message', '') if isinstance(error, dict) else ''
        return status_text == 'UNAVAILABLE' or 'high demand' in str(message).lower()

    @staticmethod
    def _provider_error_message(response) -> str:
        try:
            payload = response.json()
        except ValueError:
            return f'AI provider returned status {response.status_code}. Please try again.'

        error = payload.get('error', {}) if isinstance(payload, dict) else {}
        code = str(error.get('code', '')) if isinstance(error, dict) else ''
        message = error.get('message') if isinstance(error, dict) else ''

        if response.status_code in (401, 403):
            return 'Gemini API key was rejected. Please update GEMINI_API_KEY in backend .env.'
        if response.status_code == 429:
            return 'Gemini rate limit or quota was reached. Please try again later.'
        if code == 'RESOURCE_EXHAUSTED':
            return 'Gemini quota is exhausted. Please check billing or quota, then try again.'
        if message:
            return message
        return f'AI provider returned status {response.status_code}. Please try again.'

    def _search_boxes(self, tokens: list[str]) -> list[dict[str, Any]]:
        query = self._token_query(
            tokens,
            [
                'box_barcode',
                'item_code',
                'item_name',
                'batch_number',
                'current_warehouse',
                'production_line',
            ],
        )
        if query is None:
            qs = Box.objects.filter(company=self.company)
        else:
            qs = Box.objects.filter(company=self.company).filter(query)

        return [
            {
                'id': box.id,
                'box_barcode': box.box_barcode,
                'item_code': box.item_code,
                'item_name': box.item_name,
                'batch_number': box.batch_number,
                'qty': str(box.qty),
                'uom': box.uom,
                'warehouse': box.current_warehouse,
                'status': box.status,
                'pallet_id': box.pallet.pallet_id if box.pallet_id else '',
                'mfg_date': box.mfg_date.isoformat() if box.mfg_date else '',
                'exp_date': box.exp_date.isoformat() if box.exp_date else '',
                'created_at': box.created_at.isoformat(),
            }
            for box in qs.select_related('pallet').order_by('-created_at')[: self.max_rows]
        ]

    def _search_pallets(self, tokens: list[str]) -> list[dict[str, Any]]:
        query = self._token_query(
            tokens,
            [
                'pallet_id',
                'item_code',
                'item_name',
                'batch_number',
                'current_warehouse',
                'production_line',
            ],
        )
        if query is None:
            qs = Pallet.objects.filter(company=self.company)
        else:
            qs = Pallet.objects.filter(company=self.company).filter(query)

        return [
            {
                'id': pallet.id,
                'pallet_id': pallet.pallet_id,
                'item_code': pallet.item_code,
                'item_name': pallet.item_name,
                'batch_number': pallet.batch_number,
                'box_count': pallet.box_count,
                'total_qty': str(pallet.total_qty),
                'uom': pallet.uom,
                'warehouse': pallet.current_warehouse,
                'status': pallet.status,
                'created_at': pallet.created_at.isoformat(),
            }
            for pallet in qs.order_by('-created_at')[: self.max_rows]
        ]

    def _search_print_logs(self, tokens: list[str]) -> list[dict[str, Any]]:
        query = self._token_query(tokens, ['reference_code', 'label_type', 'print_type'])
        if query is None:
            qs = LabelPrintLog.objects.filter(company=self.company)
        else:
            qs = LabelPrintLog.objects.filter(company=self.company).filter(query)

        return [
            {
                'label_type': log.label_type,
                'reference_id': log.reference_id,
                'reference_code': log.reference_code,
                'print_type': log.print_type,
                'printed_at': log.printed_at.isoformat(),
                'printer_name': log.printer_name,
            }
            for log in qs.order_by('-printed_at')[: self.max_rows]
        ]

    def _search_production_releases(self, question: str, tokens: list[str]) -> list[dict[str, Any]]:
        lower_question = question.lower()
        likely_release_question = (
            'production' in lower_question
            or 'release' in lower_question
            or 'doc' in lower_question
            or any(token.upper().startswith('FG') for token in tokens)
        )
        if not likely_release_question:
            return []

        search = next((token for token in tokens if token.upper().startswith('FG')), '')
        if not search:
            search = tokens[0] if tokens else ''

        try:
            service = ProductionReleaseOilService(company_code=self.company_code)
            return service.list_releases(search=search, limit=self.max_rows)
        except ProductionReleaseReadError as exc:
            logger.info('Production release lookup skipped: %s', exc)
            return [{'error': str(exc)}]
        except Exception as exc:
            logger.info('Production release lookup unavailable: %s', exc)
            return [{'error': 'Production release data is unavailable for this company.'}]

    def _search_pending_grpos(self, *, question: str, page: str) -> dict[str, Any]:
        if not self._is_grpo_question(question=question, page=page):
            return {}

        if not self.user.has_perm('grpo.can_view_pending_grpo'):
            return {'error': 'You do not have permission to view pending GRPO entries.'}

        service = GRPOService(company_code=self.company_code)
        entries = service.get_pending_grpo_entries()
        pending_entries: list[dict[str, Any]] = []
        pending_entry_count = 0
        pending_po_count = 0

        for entry in entries:
            po_receipts = list(entry.po_receipts.all())
            if not po_receipts:
                continue

            posted_po_ids = set()
            for grpo in entry.grpo_postings.filter(status='POSTED'):
                posted_po_ids.update(grpo.po_receipts.values_list('id', flat=True))
                if grpo.po_receipt_id:
                    posted_po_ids.add(grpo.po_receipt_id)

            pending_pos = [po for po in po_receipts if po.id not in posted_po_ids]
            if not pending_pos:
                continue

            pending_entry_count += 1
            pending_po_count += len(pending_pos)
            if len(pending_entries) < self.max_rows:
                pending_entries.append({
                    'vehicle_entry_id': entry.id,
                    'entry_no': entry.entry_no,
                    'status': entry.status,
                    'entry_time': entry.entry_time.isoformat() if entry.entry_time else '',
                    'pending_po_count': len(pending_pos),
                    'total_po_count': len(po_receipts),
                    'pending_po_numbers': [po.po_number for po in pending_pos[: self.max_rows]],
                    'suppliers': sorted({po.supplier_name for po in pending_pos if po.supplier_name}),
                })

        return {
            'pending_entry_count': pending_entry_count,
            'pending_po_count': pending_po_count,
            'sample_entries': pending_entries,
        }

    @staticmethod
    def _is_grpo_question(*, question: str, page: str) -> bool:
        text = f'{question} {page}'.lower()
        return (
            'grpo' in text
            or 'goods receipt po' in text
            or 'goods receipt purchase' in text
            or '/grpo' in text
        )

    @staticmethod
    def _should_search_documents(question: str) -> bool:
        lower_question = question.lower()
        data_question_terms = ['how many', 'count', 'pending', 'status', 'find', 'show me']
        doc_question_terms = ['guide', 'documentation', 'docs', 'requirement', 'how to', 'explain']
        if any(term in lower_question for term in data_question_terms):
            return False
        return any(term in lower_question for term in doc_question_terms)

    def _search_documents(self, question: str, tokens: list[str]) -> list[dict[str, str]]:
        docs: list[dict[str, str]] = []
        paths = self._assistant_document_paths()
        terms = [token.lower() for token in tokens] + [
            word.lower()
            for word in re.findall(r'[A-Za-z]{4,}', question)
            if len(word) >= 4
        ]

        for path in paths:
            if not path.exists() or not path.is_file():
                continue
            snippet = self._document_snippet(path, terms)
            if snippet:
                try:
                    title = str(path.relative_to(settings.BASE_DIR))
                except ValueError:
                    title = path.name
                docs.append({'title': title, 'snippet': snippet})
            if len(docs) >= self.max_rows:
                break
        return docs

    @staticmethod
    def _assistant_document_paths() -> list[Path]:
        base_dir = settings.BASE_DIR
        ignored_parts = {
            '.git',
            '.venv',
            '__pycache__',
            'migrations',
            'node_modules',
            'staticfiles',
            'media',
        }
        paths: list[Path] = []
        for path in sorted(base_dir.rglob('*.md')):
            if any(part in ignored_parts for part in path.parts):
                continue
            paths.append(path)
            if len(paths) >= 250:
                break
        return paths

    @staticmethod
    def _document_snippet(path: Path, terms: list[str]) -> str:
        text = path.read_text(encoding='utf-8', errors='ignore')
        if not terms:
            return text[:1000]

        lower_text = text.lower()
        positions = [lower_text.find(term) for term in terms if term and lower_text.find(term) >= 0]
        if not positions:
            return ''
        start = max(min(positions) - 250, 0)
        end = min(start + 1200, len(text))
        return text[start:end].strip()

    def _audit_interaction(
        self,
        *,
        question: str,
        page: str,
        result: dict[str, Any],
        started: float,
        status: str = AIAssistantInteraction.STATUS_SUCCESS,
        error_code: str = '',
        blocked_reason: str = '',
    ) -> None:
        try:
            database_audit = self._last_database_audit or {}
            database_summary = (result.get('context_summary') or {}).get('database_query') or {}
            row_count = database_summary.get('row_count')
            AIAssistantInteraction.objects.create(
                user=self.user if getattr(self.user, 'is_authenticated', False) else None,
                company=self.company,
                question=question,
                page=page or '',
                mode=str(result.get('mode') or ''),
                provider=str(result.get('provider') or ''),
                model=str(result.get('model') or ''),
                status=status,
                generated_sql=str(database_audit.get('generated_sql') or ''),
                validation_status=str(database_audit.get('validation_status') or ''),
                blocked_reason=str(blocked_reason or database_audit.get('blocked_reason') or ''),
                row_count=int(row_count) if row_count is not None else None,
                latency_ms=max(int((time.monotonic() - started) * 1000), 0),
                error_code=error_code,
            )
        except Exception as exc:
            logger.info('AI assistant audit logging skipped: %s', exc)

    @staticmethod
    def _date_context() -> dict[str, str]:
        today = timezone.localdate()
        week_start = today - timedelta(days=today.weekday())
        return {
            'timezone': settings.TIME_ZONE,
            'today': today.isoformat(),
            'yesterday': (today - timedelta(days=1)).isoformat(),
            'this_week_start': week_start.isoformat(),
            'this_month_start': today.replace(day=1).isoformat(),
            'last_7_days_start': (today - timedelta(days=6)).isoformat(),
            'last_30_days_start': (today - timedelta(days=29)).isoformat(),
        }

    @staticmethod
    def _counts_by(queryset, field: str) -> list[dict[str, Any]]:
        return [
            {
                'value': row[field] or '',
                'count': row['count'],
            }
            for row in queryset.values(field).annotate(count=Count('id')).order_by(field)
        ]

    @staticmethod
    def _count_for_status(status_counts: list[dict[str, Any]], status_value: str) -> int:
        normalized_status = FactoryAssistantService._normalize_count_term(status_value)
        for item in status_counts:
            if FactoryAssistantService._normalize_count_term(str(item.get('value', ''))) == normalized_status:
                return int(item.get('count', 0))
        return 0

    @staticmethod
    def _format_count(count: int, singular_label: str) -> str:
        label = singular_label if count == 1 else f'{singular_label}s'
        return f'There are {count} {label}.'

    @staticmethod
    def _status_label(status_value: str) -> str:
        label = status_value.lower().replace('_', ' ').replace('-', ' ')
        return label or 'unknown'

    @staticmethod
    def _is_fg_receipt_question(text: str) -> bool:
        normalized = text.lower()
        return (
            'fg receipt' in normalized
            or 'fg receipts' in normalized
            or 'finished goods receipt' in normalized
            or 'finished goods receipts' in normalized
            or ('finished goods' in normalized and 'receipt' in normalized)
        )

    @staticmethod
    def _token_filter(queryset, tokens: list[str], fields: list[str]):
        if not tokens:
            return queryset

        query = Q()
        for token in tokens:
            field_query = Q()
            for field in fields:
                field_query |= Q(**{f'{field}__icontains': token})
            query |= field_query
        return queryset.filter(query).distinct()

    @staticmethod
    def _matching_status_count(
        question: str,
        status_counts: list[dict[str, Any]],
        fallback: int | None = None,
    ) -> int | None:
        normalized_question = FactoryAssistantService._normalize_count_term(question)
        normalized_counts = [
            {
                'value': FactoryAssistantService._normalize_count_term(str(item.get('value', ''))),
                'count': int(item.get('count', 0)),
            }
            for item in status_counts
        ]

        for item in status_counts:
            value = str(item.get('value', ''))
            if FactoryAssistantService._normalize_count_term(value) in normalized_question:
                return int(item.get('count', 0))

        status_terms = [
            'pending',
            'completed',
            'failed',
            'posted',
            'draft',
            'rejected',
            'approved',
            'submitted',
            'progress',
            'review',
            'hold',
            'cleared',
        ]
        for term in status_terms:
            if term in normalized_question:
                total = sum(
                    item['count']
                    for item in normalized_counts
                    if term in item['value']
                )
                if total:
                    return total
                return None

        if any(term in normalized_question for term in ['total', 'all', 'overall']) and fallback is not None:
            return int(fallback)
        if fallback is not None:
            return int(fallback)
        return None

    @staticmethod
    def _normalize_count_term(value: str) -> str:
        return re.sub(r'[^a-z0-9]+', '', value.lower())

    @staticmethod
    def _safe_count_items(queryset) -> int:
        return queryset.aggregate(count=Count('items'))['count'] or 0

    @staticmethod
    def _grpo_po_numbers(posting: GRPOPosting) -> list[str]:
        po_numbers = list(posting.po_receipts.values_list('po_number', flat=True))
        if not po_numbers and posting.po_receipt_id:
            po_numbers = [posting.po_receipt.po_number]
        return po_numbers

    @staticmethod
    def _extract_search_terms(question: str) -> list[str]:
        raw_terms = re.findall(r'[A-Za-z0-9][A-Za-z0-9_\-/.]{1,80}', question)
        priority = [
            term.strip('.,;:()[]{}')
            for term in raw_terms
            if len(term.strip('.,;:()[]{}')) >= 3
        ]
        seen = set()
        terms = []
        for term in priority:
            key = term.lower()
            if key not in seen:
                seen.add(key)
                terms.append(term)
        return terms[:8]

    @staticmethod
    def _token_query(tokens: list[str], fields: list[str]) -> Q | None:
        if not tokens:
            return None
        query = Q()
        for token in tokens:
            field_query = Q()
            for field in fields:
                field_query |= Q(**{f'{field}__icontains': token})
            query |= field_query
        return query
