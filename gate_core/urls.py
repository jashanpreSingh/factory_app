from django.urls import path
from .views import (
    BSTGateInByVehicleEntryView,
    BSTGateInCompleteView,
    BSTGateInDetailView,
    BSTGateInEligibleOutsView,
    BSTGateInListCreateView,
    BSTGateOutByVehicleEntryView,
    BSTGateOutCancelView,
    BSTGateOutCompleteView,
    BSTGateOutDetailView,
    BSTGateOutListCreateView,
    BSTGateReturnByVehicleEntryView,
    BSTGateReturnCompleteView,
    BSTGateReturnDetailView,
    BSTGateReturnEligibleOutsView,
    BSTGateReturnListCreateView,
    DispatchGateLockView,
    DispatchGateOutAttachmentView,
    DispatchGateOutCancelView,
    DispatchGateOutCommitPrintView,
    DispatchGateOutCompleteView,
    DispatchGateOutDetailView,
    DispatchGateOutListCreateView,
    DispatchGateOutRejectView,
    EmptyVehicleEligibleEntriesView,
    EmptyVehicleGateInDetailView,
    EmptyVehicleGateInEligibleView,
    EmptyVehicleGateInListCreateView,
    EmptyVehicleGateInReasonListView,
    EmptyVehicleGateOutCancelView,
    EmptyVehicleGateOutDetailView,
    EmptyVehicleGateOutListCreateView,
    JobWorkGateInByVehicleEntryView,
    JobWorkGateInCompleteView,
    JobWorkGateInDetailView,
    JobWorkGateInListCreateView,
    RawMaterialGateEntryFullView,
    DailyNeedGateEntryFullView,
    MaintenanceGateEntryFullView,
    ConstructionGateEntryFullView,
    UnitChoiceListView,
    GateAttachmentListCreateView,
    RejectedQCReturnDetailView,
    RejectedQCReturnListCreateView,
    SAPGRPODetailView,
    SAPGRPOListView,
    SAPProductionOrderDetailView,
    SAPProductionOrderListView,
    SAPStockTransferDetailView,
    SAPStockTransferListView,
)

urlpatterns = [
    # Unit Choice URLs
    path('unit-choices/', UnitChoiceListView.as_view(), name='unit_choice_list'),

    # Gate Attachment URLs
    path('gate-attachments/<int:gate_entry_id>/', GateAttachmentListCreateView.as_view(), name='gate_attachment_list_create'),

    # Rejected QC Return gate-out URLs
    path('rejected-qc-returns/', RejectedQCReturnListCreateView.as_view(), name='rejected_qc_return_list_create'),
    path('rejected-qc-returns/<int:entry_id>/', RejectedQCReturnDetailView.as_view(), name='rejected_qc_return_detail'),

    # Sales dispatch gate-out URLs
    path('dispatch-gate-lock/', DispatchGateLockView.as_view(), name='dispatch_gate_lock'),
    path('sales-dispatch-outs/', DispatchGateOutListCreateView.as_view(), name='dispatch_gate_out_list_create'),
    path('sales-dispatch-outs/<int:entry_id>/attachments/', DispatchGateOutAttachmentView.as_view(), name='dispatch_gate_out_attachments'),
    path('sales-dispatch-outs/<int:entry_id>/complete/', DispatchGateOutCompleteView.as_view(), name='dispatch_gate_out_complete'),
    path('sales-dispatch-outs/<int:entry_id>/commit-print/', DispatchGateOutCommitPrintView.as_view(), name='dispatch_gate_out_commit_print'),
    path('sales-dispatch-outs/<int:entry_id>/cancel/', DispatchGateOutCancelView.as_view(), name='dispatch_gate_out_cancel'),
    path('sales-dispatch-outs/<int:entry_id>/reject/', DispatchGateOutRejectView.as_view(), name='dispatch_gate_out_reject'),
    path('sales-dispatch-outs/<int:entry_id>/', DispatchGateOutDetailView.as_view(), name='dispatch_gate_out_detail'),

    # Empty Vehicle gate-in URLs
    path('empty-vehicle-ins/reasons/', EmptyVehicleGateInReasonListView.as_view(), name='empty_vehicle_gate_in_reasons'),
    path('empty-vehicle-ins/eligible/', EmptyVehicleGateInEligibleView.as_view(), name='empty_vehicle_gate_in_eligible'),
    path('empty-vehicle-ins/', EmptyVehicleGateInListCreateView.as_view(), name='empty_vehicle_gate_in_list_create'),
    path('empty-vehicle-ins/<int:entry_id>/', EmptyVehicleGateInDetailView.as_view(), name='empty_vehicle_gate_in_detail'),

    # Empty Vehicle gate-out URLs
    path('empty-vehicle-outs/eligible-entries/', EmptyVehicleEligibleEntriesView.as_view(), name='empty_vehicle_eligible_entries'),
    path('empty-vehicle-outs/', EmptyVehicleGateOutListCreateView.as_view(), name='empty_vehicle_gate_out_list_create'),
    path('empty-vehicle-outs/<int:entry_id>/cancel/', EmptyVehicleGateOutCancelView.as_view(), name='empty_vehicle_gate_out_cancel'),
    path('empty-vehicle-outs/<int:entry_id>/', EmptyVehicleGateOutDetailView.as_view(), name='empty_vehicle_gate_out_detail'),

    # BST gate-out URLs
    path('bst-outs/sap-transfers/', SAPStockTransferListView.as_view(), name='bst_out_sap_transfers'),
    path('bst-outs/sap-transfers/<int:doc_entry>/', SAPStockTransferDetailView.as_view(), name='bst_out_sap_transfer_detail'),
    path('bst-outs/by-vehicle-entry/<int:vehicle_entry_id>/', BSTGateOutByVehicleEntryView.as_view(), name='bst_gate_out_by_vehicle_entry'),
    path('bst-outs/by-vehicle-entry/<int:vehicle_entry_id>/complete/', BSTGateOutCompleteView.as_view(), name='bst_gate_out_complete'),
    path('bst-outs/', BSTGateOutListCreateView.as_view(), name='bst_gate_out_list_create'),
    path('bst-outs/<int:entry_id>/cancel/', BSTGateOutCancelView.as_view(), name='bst_gate_out_cancel'),
    path('bst-outs/<int:entry_id>/', BSTGateOutDetailView.as_view(), name='bst_gate_out_detail'),

    # BST gate-in URLs
    path('bst-ins/eligible-outs/', BSTGateInEligibleOutsView.as_view(), name='bst_gate_in_eligible_outs'),
    path('bst-ins/by-vehicle-entry/<int:vehicle_entry_id>/', BSTGateInByVehicleEntryView.as_view(), name='bst_gate_in_by_vehicle_entry'),
    path('bst-ins/by-vehicle-entry/<int:vehicle_entry_id>/complete/', BSTGateInCompleteView.as_view(), name='bst_gate_in_complete'),
    path('bst-ins/', BSTGateInListCreateView.as_view(), name='bst_gate_in_list_create'),
    path('bst-ins/<int:entry_id>/', BSTGateInDetailView.as_view(), name='bst_gate_in_detail'),

    # BST return URLs
    path('bst-returns/eligible-outs/', BSTGateReturnEligibleOutsView.as_view(), name='bst_gate_return_eligible_outs'),
    path('bst-returns/by-vehicle-entry/<int:vehicle_entry_id>/', BSTGateReturnByVehicleEntryView.as_view(), name='bst_gate_return_by_vehicle_entry'),
    path('bst-returns/by-vehicle-entry/<int:vehicle_entry_id>/complete/', BSTGateReturnCompleteView.as_view(), name='bst_gate_return_complete'),
    path('bst-returns/', BSTGateReturnListCreateView.as_view(), name='bst_gate_return_list_create'),
    path('bst-returns/<int:entry_id>/', BSTGateReturnDetailView.as_view(), name='bst_gate_return_detail'),

    # Job work gate-in URLs
    path('job-work/sap-grpos/', SAPGRPOListView.as_view(), name='job_work_sap_grpos'),
    path('job-work/sap-grpos/<int:doc_entry>/', SAPGRPODetailView.as_view(), name='job_work_sap_grpo_detail'),
    path('job-work/sap-production-orders/', SAPProductionOrderListView.as_view(), name='job_work_sap_production_orders'),
    path('job-work/sap-production-orders/<int:doc_entry>/', SAPProductionOrderDetailView.as_view(), name='job_work_sap_production_order_detail'),
    path('job-work/by-vehicle-entry/<int:vehicle_entry_id>/', JobWorkGateInByVehicleEntryView.as_view(), name='job_work_gate_in_by_vehicle_entry'),
    path('job-work/by-vehicle-entry/<int:vehicle_entry_id>/complete/', JobWorkGateInCompleteView.as_view(), name='job_work_gate_in_complete'),
    path('job-work/', JobWorkGateInListCreateView.as_view(), name='job_work_gate_in_list_create'),
    path('job-work/<int:entry_id>/', JobWorkGateInDetailView.as_view(), name='job_work_gate_in_detail'),

    # Gate Entry URLs
    path('raw-material-gate-entry/<int:gate_entry_id>/', RawMaterialGateEntryFullView.as_view(), name='raw_material_gate_entry_full_view'),
    path('daily-need-gate-entry/<int:gate_entry_id>/', DailyNeedGateEntryFullView.as_view(), name='daily_need_gate_entry_full_view'),
    path('maintenance-gate-entry/<int:gate_entry_id>/', MaintenanceGateEntryFullView.as_view(), name='maintenance_gate_entry_full_view'),
    path('construction-gate-entry/<int:gate_entry_id>/', ConstructionGateEntryFullView.as_view(), name='construction_gate_entry_full_view'),
]
