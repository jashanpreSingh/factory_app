import json
import logging
import re
from pathlib import Path
from typing import Any

import requests
from django.conf import settings
from django.db.models import Count, Q

from barcode.models import Box, LabelPrintLog, Pallet
from barcode.services.production_release_service import (
    ProductionReleaseOilService,
    ProductionReleaseReadError,
)
from driver_management.models import VehicleEntry
from grpo.services import GRPOService
from grpo.models import GRPOPosting
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

logger = logging.getLogger(__name__)


class AssistantConfigError(RuntimeError):
    """Raised when the assistant is not configured for model calls."""


class AssistantProviderError(RuntimeError):
    """Raised when the AI provider returns an unusable response."""


class FactoryAssistantService:
    """Read-only AI assistant with a small Factory data context."""

    GEMINI_GENERATE_CONTENT_BASE_URL = 'https://generativelanguage.googleapis.com/v1beta/models'

    def __init__(self, *, company, company_code: str, user):
        self.company = company
        self.company_code = company_code
        self.user = user
        self.max_rows = settings.AI_ASSISTANT_MAX_CONTEXT_ROWS

    def answer(self, *, question: str, page: str = '') -> dict[str, Any]:
        context = self._build_context(question=question, page=page)
        direct_answer = self._direct_answer(question=question, context=context)
        if direct_answer:
            return {
                'answer': direct_answer,
                'sources': context['sources'],
                'context_summary': context['summary'],
                'model': 'factory-context',
                'provider': 'local',
                'mode': 'read_only',
            }

        provider_result = self._call_gemini(question=question, page=page, context=context)
        return {
            'answer': provider_result['text'],
            'sources': context['sources'],
            'context_summary': context['summary'],
            'model': provider_result['model'],
            'provider': 'gemini',
            'mode': 'read_only',
        }

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

    def _call_gemini(self, *, question: str, page: str, context: dict[str, Any]) -> dict[str, str]:
        api_key = settings.GEMINI_API_KEY.strip()
        if not api_key:
            raise AssistantConfigError('Gemini API key is missing. Add GEMINI_API_KEY to backend .env.')

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
            'Factory context JSON:\n'
            f'{json.dumps(context, default=str, ensure_ascii=False)}'
        )
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
                'maxOutputTokens': 700,
                'temperature': 0.2,
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
        root_dir = settings.BASE_DIR.parent
        paths = [
            root_dir / 'AI_INTEGRATION_GUIDE.md',
            root_dir / 'AI_ASSISTANT_REQUIREMENTS.md',
            root_dir / 'BARCODE_SYSTEM_TASKS.md',
            root_dir / 'FactoryFlow' / 'docs' / 'modules' / 'barcode-implementation.md',
        ]
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
                docs.append({'title': path.name, 'snippet': snippet})
            if len(docs) >= self.max_rows:
                break
        return docs

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
