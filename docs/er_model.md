# ER Model

Generated on: `2026-05-09 12:41:37`

Source: Django model metadata via `scripts/generate_er_docs.py`.

- Managed tables: `100`
- Relationships: `249`
- Full column inventory: [database_schema.md](database_schema.md)
- Raw Mermaid source: [er_model.mmd](er_model.mmd)

```mermaid
erDiagram
    accounts_department {
        bigint id PK
        varchar name
        text description
    }
    accounts_user {
        bigint id PK
        varchar password
        datetime last_login
        boolean is_superuser
        varchar email UK
        varchar full_name
        varchar employee_code UK
        boolean is_active
        boolean is_staff
        datetime date_joined
    }
    accounts_user_groups {
        bigint id PK
        bigint user_id FK
        bigint group_id FK
    }
    accounts_user_user_permissions {
        bigint id PK
        bigint user_id FK
        bigint permission_id FK
    }
    django_admin_log {
        int id PK
        datetime action_time
        bigint user_id FK
        bigint content_type_id FK
        text object_id
        varchar object_repr
        smallint action_flag
        text change_message
    }
    auth_group {
        int id PK
        varchar name UK
    }
    auth_group_permissions {
        int id PK
        bigint group_id FK
        bigint permission_id FK
    }
    auth_permission {
        int id PK
        varchar name
        bigint content_type_id FK
        varchar codename
    }
    company_company {
        bigint id PK
        varchar name
        varchar code UK
        boolean is_active
    }
    company_usercompany {
        bigint id PK
        bigint user_id FK
        bigint company_id FK
        bigint role_id FK
        boolean is_default
        boolean is_active
    }
    company_userrole {
        bigint id PK
        varchar name
        text description
    }
    construction_gatein_constructiongateentry {
        bigint id PK
        bigint vehicle_entry_id FK
        varchar project_name
        varchar work_order_number UK
        varchar contractor_name
        varchar contractor_contact
        bigint material_category_id FK
        text material_description
        decimal quantity
        bigint unit_id FK
        varchar challan_number
        varchar invoice_number
        varchar site_engineer
        varchar security_approval
        text remarks
        datetime inward_time
        bigint created_by_id FK
        datetime created_at
        datetime updated_at
    }
    construction_gatein_constructionmaterialcategory {
        bigint id PK
        varchar category_name UK
        text description
        boolean is_active
    }
    django_content_type {
        int id PK
        varchar app_label
        varchar model
    }
    daily_needs_gatein_categorylist {
        bigint id PK
        varchar category_name UK
    }
    daily_needs_gatein_dailyneedgateentry {
        bigint id PK
        bigint vehicle_entry_id FK
        bigint item_category_id FK
        varchar supplier_name
        varchar material_name
        decimal quantity
        bigint unit_id FK
        bigint receiving_department_id FK
        varchar bill_number
        varchar delivery_challan_number
        varchar canteen_supervisor
        varchar vehicle_or_person_name
        varchar contact_number
        text remarks
        bigint created_by_id FK
        datetime created_at
        datetime updated_at
    }
    dispatch_plans_dispatchplan {
        bigint id PK
        datetime created_at
        datetime updated_at
        bigint created_by_id FK
        bigint updated_by_id FK
        boolean is_active
        bigint company_id FK
        int sap_invoice_doc_entry
        varchar sap_invoice_doc_num
        bigint vehicle_id FK
        bigint transporter_id FK
        bigint driver_id FK
        bigint linked_vehicle_entry_id FK
        varchar booking_status
        date dispatch_date
        varchar priority
        varchar transporter_name
        varchar transporter_gstin
        varchar contact_person
        varchar mobile_no
        varchar vehicle_no
        varchar driver_name
        varchar driver_mobile_no
        varchar driver_license_no
        varchar driver_id_proof_type
        varchar driver_id_proof_number
        varchar bilty_no
        date bilty_date
        decimal freight
        decimal total_freight
        decimal kanta_weight
        text remarks
    }
    django_apscheduler_djangojob {
        varchar id PK
        datetime next_run_time
        binaryfield job_state
    }
    django_apscheduler_djangojobexecution {
        bigint id PK
        bigint job_id FK
        varchar status
        datetime run_time
        decimal duration
        decimal finished
        varchar exception
        text traceback
    }
    driver_management_driver {
        bigint id PK
        datetime created_at
        datetime updated_at
        bigint created_by_id FK
        bigint updated_by_id FK
        boolean is_active
        varchar name
        varchar mobile_no
        varchar license_no UK
        varchar id_proof_type
        varchar id_proof_number
        varchar photo
    }
    driver_management_vehicleentry {
        bigint id PK
        datetime created_at
        datetime updated_at
        boolean is_active
        varchar entry_no UK
        varchar status
        boolean is_locked
        bigint company_id FK
        bigint vehicle_id FK
        bigint driver_id FK
        varchar entry_type
        bigint created_by_id FK
        bigint updated_by_id FK
        datetime entry_time
        text remarks
    }
    gate_core_bstgatein {
        bigint id PK
        datetime created_at
        datetime updated_at
        bigint created_by_id FK
        bigint updated_by_id FK
        boolean is_active
        bigint company_id FK
        varchar entry_no UK
        bigint vehicle_entry_id FK
        bigint bst_gate_out_id FK
        bigint vehicle_id FK
        bigint driver_id FK
        date gate_in_date
        time in_time
        varchar security_name
        text remarks
        varchar status
    }
    gate_core_bstgateinitem {
        bigint id PK
        datetime created_at
        datetime updated_at
        bigint created_by_id FK
        bigint updated_by_id FK
        boolean is_active
        bigint bst_gate_in_id FK
        bigint bst_gate_out_item_id FK
        int line_num
        varchar item_code
        varchar item_name
        decimal quantity
        decimal actual_quantity
        decimal receiving_quantity
        varchar uom
        varchar from_warehouse
        varchar to_warehouse
    }
    gate_core_bstgateout {
        bigint id PK
        datetime created_at
        datetime updated_at
        bigint created_by_id FK
        bigint updated_by_id FK
        boolean is_active
        bigint company_id FK
        varchar entry_no UK
        bigint vehicle_entry_id FK
        bigint empty_vehicle_gate_in_id FK
        bigint vehicle_id FK
        bigint driver_id FK
        int sap_doc_entry
        varchar sap_doc_num
        date sap_doc_date
        varchar sap_from_warehouse
        varchar sap_to_warehouse
        varchar sap_reference
        text sap_comments
        date gate_out_date
        time out_time
        varchar security_name
        text remarks
        varchar status
        text cancel_reason
        datetime cancelled_at
        bigint cancelled_by_id FK
    }
    gate_core_bstgateoutitem {
        bigint id PK
        datetime created_at
        datetime updated_at
        bigint created_by_id FK
        bigint updated_by_id FK
        boolean is_active
        bigint bst_gate_out_id FK
        int line_num
        varchar item_code
        varchar item_name
        decimal quantity
        decimal actual_quantity
        varchar uom
        varchar from_warehouse
        varchar to_warehouse
    }
    gate_core_bstgatereturn {
        bigint id PK
        datetime created_at
        datetime updated_at
        bigint created_by_id FK
        bigint updated_by_id FK
        boolean is_active
        bigint company_id FK
        varchar entry_no UK
        bigint vehicle_entry_id FK
        bigint bst_gate_out_id FK
        bigint vehicle_id FK
        bigint driver_id FK
        date gate_in_date
        time in_time
        varchar security_name
        text remarks
        varchar status
    }
    gate_core_emptyvehiclegatein {
        bigint id PK
        datetime created_at
        datetime updated_at
        bigint created_by_id FK
        bigint updated_by_id FK
        boolean is_active
        bigint company_id FK
        varchar entry_no UK
        bigint vehicle_entry_id FK
        bigint vehicle_id FK
        bigint driver_id FK
        varchar reason
        date gate_in_date
        time in_time
        int sap_doc_entry
        varchar sap_doc_num
        date sap_doc_date
        varchar sap_from_warehouse
        varchar sap_to_warehouse
        varchar sap_reference
        text sap_comments
        int sap_line_count
        decimal sap_total_quantity
        varchar document_reference
        text document_notes
        varchar security_name
        text remarks
    }
    gate_core_emptyvehiclegateinitem {
        bigint id PK
        datetime created_at
        datetime updated_at
        bigint created_by_id FK
        bigint updated_by_id FK
        boolean is_active
        bigint empty_vehicle_gate_in_id FK
        int line_num
        varchar item_code
        varchar item_name
        decimal sap_quantity
        decimal actual_quantity
        varchar uom
        varchar from_warehouse
        varchar to_warehouse
    }
    gate_core_emptyvehiclegateout {
        bigint id PK
        datetime created_at
        datetime updated_at
        bigint created_by_id FK
        bigint updated_by_id FK
        boolean is_active
        bigint company_id FK
        varchar entry_no UK
        bigint vehicle_entry_id FK
        bigint vehicle_id FK
        bigint driver_id FK
        date gate_out_date
        time out_time
        varchar security_name
        text remarks
        varchar status
        text cancel_reason
        datetime cancelled_at
        bigint cancelled_by_id FK
    }
    gate_core_gateattachment {
        bigint id PK
        bigint gate_entry_id FK
        varchar file
        datetime uploaded_at
    }
    gate_core_jobworkgatein {
        bigint id PK
        datetime created_at
        datetime updated_at
        bigint created_by_id FK
        bigint updated_by_id FK
        boolean is_active
        bigint company_id FK
        varchar entry_no UK
        bigint vehicle_entry_id FK
        bigint vehicle_id FK
        bigint driver_id FK
        int sap_doc_entry
        varchar sap_doc_num
        date sap_doc_date
        time sap_doc_time
        varchar sap_supplier_code
        varchar sap_supplier_name
        varchar sap_reference
        text sap_comments
        int sap_branch_id
        int production_order_doc_entry
        varchar production_order_doc_num
        varchar production_item_code
        varchar production_item_name
        decimal production_planned_qty
        decimal production_completed_qty
        decimal production_rejected_qty
        decimal production_remaining_qty
        date production_start_date
        date production_due_date
        varchar production_warehouse
        varchar production_status
        date gate_in_date
        time in_time
        varchar security_name
        text remarks
        varchar status
    }
    gate_core_jobworkgateinitem {
        bigint id PK
        datetime created_at
        datetime updated_at
        bigint created_by_id FK
        bigint updated_by_id FK
        boolean is_active
        bigint job_work_gate_in_id FK
        int line_num
        varchar item_code
        varchar item_name
        decimal quantity
        varchar uom
        varchar warehouse_code
        int base_type
        int base_entry
        int base_line
    }
    gate_core_rejectedqcreturnentry {
        bigint id PK
        datetime created_at
        datetime updated_at
        bigint created_by_id FK
        bigint updated_by_id FK
        boolean is_active
        bigint company_id FK
        varchar entry_no UK
        bigint vehicle_id FK
        bigint driver_id FK
        date gate_out_date
        time out_time
        varchar challan_no
        varchar eway_bill_no
        varchar manual_sap_reference
        varchar security_name
        decimal gross_weight
        decimal tare_weight
        decimal net_weight
        varchar weighbridge_slip_no
        datetime first_weighment_time
        datetime second_weighment_time
        json gatepass_documents
        text remarks
        varchar status
    }
    gate_core_rejectedqcreturnitem {
        bigint id PK
        datetime created_at
        datetime updated_at
        bigint created_by_id FK
        bigint updated_by_id FK
        boolean is_active
        bigint entry_id FK
        bigint inspection_id FK
        varchar gate_entry_no
        varchar report_no
        varchar internal_lot_no
        varchar item_name
        varchar supplier_name
        decimal quantity
        varchar uom
    }
    gate_core_unitchoice {
        bigint id PK
        varchar name UK
    }
    grpo_grpoattachment {
        bigint id PK
        bigint grpo_posting_id FK
        varchar file
        varchar original_filename
        varchar sap_attachment_status
        int sap_absolute_entry
        text sap_error_message
        datetime uploaded_at
        bigint uploaded_by_id FK
    }
    grpo_grpolineposting {
        bigint id PK
        bigint grpo_posting_id FK
        bigint po_item_receipt_id FK
        decimal quantity_posted
        int base_entry
        int base_line
    }
    grpo_grpoposting {
        bigint id PK
        bigint vehicle_entry_id FK
        bigint po_receipt_id FK
        int sap_doc_entry
        int sap_doc_num
        decimal sap_doc_total
        varchar status
        text error_message
        datetime posted_at
        bigint posted_by_id FK
        datetime created_at
        datetime updated_at
    }
    grpo_grpoposting_po_receipts {
        bigint id PK
        bigint grpoposting_id FK
        bigint poreceipt_id FK
    }
    grpo_servicegrpoattachment {
        bigint id PK
        bigint service_grpo_posting_id FK
        varchar file
        varchar original_filename
        varchar sap_attachment_status
        int sap_absolute_entry
        text sap_error_message
        datetime uploaded_at
        bigint uploaded_by_id FK
    }
    grpo_servicegrpolineposting {
        bigint id PK
        bigint service_grpo_posting_id FK
        varchar service_description
        decimal amount
        varchar tax_code
        varchar gl_account
    }
    grpo_servicegrpoposting {
        bigint id PK
        bigint dispatch_plan_id FK
        varchar vendor_code
        varchar vendor_name
        int sap_doc_entry
        int sap_doc_num
        decimal sap_doc_total
        varchar status
        text error_message
        datetime posted_at
        bigint posted_by_id FK
        datetime created_at
        datetime updated_at
    }
    maintenance_gatein_maintenancegateentry {
        bigint id PK
        bigint vehicle_entry_id FK
        bigint maintenance_type_id FK
        varchar work_order_number UK
        varchar supplier_name
        text material_description
        varchar part_number
        decimal quantity
        bigint unit_id FK
        varchar invoice_number
        varchar equipment_id
        bigint receiving_department_id FK
        varchar urgency_level
        datetime inward_time
        text remarks
        bigint created_by_id FK
        datetime created_at
        datetime updated_at
    }
    maintenance_gatein_maintenancetype {
        bigint id PK
        varchar type_name UK
        text description
        boolean is_active
    }
    notifications_notification {
        bigint id PK
        bigint recipient_id FK
        bigint company_id FK
        varchar title
        text body
        varchar notification_type
        varchar click_action_url
        varchar reference_type
        int reference_id
        boolean is_read
        datetime read_at
        json extra_data
        datetime created_at
        bigint created_by_id FK
    }
    notifications_userdevice {
        bigint id PK
        bigint user_id FK
        text fcm_token UK
        varchar device_type
        varchar device_info
        boolean is_active
        datetime created_at
        datetime last_used_at
    }
    person_gatein_contractor {
        bigint id PK
        varchar contractor_name
        varchar contact_person
        varchar mobile
        text address
        date contract_valid_till
        boolean is_active
    }
    person_gatein_entrylog {
        bigint id PK
        bigint person_type_id FK
        bigint visitor_id FK
        bigint labour_id FK
        varchar name_snapshot
        varchar photo_snapshot
        bigint gate_in_id FK
        bigint gate_out_id FK
        datetime entry_time
        datetime actual_entry_time
        datetime exit_time
        varchar purpose
        bigint approved_by_id FK
        varchar vehicle_no
        text remarks
        varchar status
        bigint created_by_id FK
        datetime created_at
        datetime updated_at
    }
    person_gatein_gate {
        bigint id PK
        varchar name
        varchar location
        boolean is_active
    }
    person_gatein_labour {
        bigint id PK
        varchar name
        bigint contractor_id FK
        varchar mobile
        varchar id_proof_no
        varchar photo
        varchar skill_type
        date permit_valid_till
        boolean is_active
    }
    person_gatein_persontype {
        bigint id PK
        varchar name UK
        boolean is_active
    }
    person_gatein_visitor {
        bigint id PK
        varchar name
        varchar mobile
        varchar company_name
        varchar id_proof_type
        varchar id_proof_no
        varchar photo
        boolean blacklisted
        datetime created_at
    }
    production_execution_breakdowncategory {
        bigint id PK
        bigint company_id FK
        varchar name
        boolean is_active
        datetime created_at
        datetime updated_at
    }
    production_execution_finalqccheck {
        bigint id PK
        bigint production_run_id FK
        datetime checked_at
        varchar overall_result
        json parameters
        text remarks
        bigint checked_by_id FK
        datetime created_at
        datetime updated_at
    }
    production_execution_inprocessqccheck {
        bigint id PK
        bigint production_run_id FK
        datetime checked_at
        varchar parameter
        decimal acceptable_min
        decimal acceptable_max
        decimal actual_value
        varchar result
        text remarks
        bigint checked_by_id FK
        datetime created_at
        datetime updated_at
    }
    production_execution_lineclearance {
        bigint id PK
        bigint company_id FK
        bigint production_run_id FK
        date date
        bigint line_id FK
        varchar document_id
        bigint verified_by_id FK
        boolean qa_approved
        bigint qa_approved_by_id FK
        datetime qa_approved_at
        varchar production_supervisor_sign
        varchar production_incharge_sign
        varchar status
        bigint created_by_id FK
        datetime created_at
        datetime updated_at
    }
    production_execution_lineclearanceitem {
        bigint id PK
        bigint clearance_id FK
        varchar checkpoint
        int sort_order
        varchar result
        text remarks
    }
    production_execution_lineskuconfig {
        bigint id PK
        bigint company_id FK
        bigint line_id FK
        varchar config_name
        varchar sku_code
        varchar sku_name
        decimal rated_speed
        int labour_count
        int other_manpower_count
        varchar supervisor
        varchar operators
        boolean is_active
        datetime created_at
        datetime updated_at
    }
    production_execution_machine {
        bigint id PK
        bigint company_id FK
        varchar name
        varchar machine_type
        bigint line_id FK
        boolean is_active
        datetime created_at
        datetime updated_at
    }
    production_execution_machinebreakdown {
        bigint id PK
        bigint production_run_id FK
        bigint machine_id FK
        datetime start_time
        datetime end_time
        int breakdown_minutes
        bigint breakdown_category_id FK
        boolean is_active
        boolean is_unrecovered
        varchar reason
        text remarks
        datetime created_at
        datetime updated_at
    }
    production_execution_machinechecklistentry {
        bigint id PK
        bigint company_id FK
        bigint machine_id FK
        varchar machine_type
        date date
        smallint month
        smallint year
        bigint template_id FK
        varchar task_description
        varchar frequency
        varchar status
        varchar operator
        varchar shift_incharge
        text remarks
        datetime created_at
        datetime updated_at
    }
    production_execution_machinechecklisttemplate {
        bigint id PK
        bigint company_id FK
        varchar machine_type
        varchar task
        varchar frequency
        int sort_order
        boolean is_active
        datetime created_at
        datetime updated_at
    }
    production_execution_machineruntime {
        bigint id PK
        bigint production_run_id FK
        bigint machine_id FK
        varchar machine_type
        int runtime_minutes
        int downtime_minutes
        text remarks
        datetime created_at
        datetime updated_at
    }
    production_execution_productionline {
        bigint id PK
        bigint company_id FK
        varchar name
        text description
        boolean is_active
        datetime created_at
        datetime updated_at
    }
    production_execution_productionmanpower {
        bigint id PK
        bigint production_run_id FK
        varchar shift
        int worker_count
        varchar supervisor
        varchar engineer
        text remarks
        datetime created_at
        datetime updated_at
    }
    production_execution_productionmaterialusage {
        bigint id PK
        bigint production_run_id FK
        varchar material_code
        varchar material_name
        decimal opening_qty
        decimal issued_qty
        decimal closing_qty
        decimal wastage_qty
        varchar uom
        datetime created_at
        datetime updated_at
    }
    production_execution_productionrun {
        bigint id PK
        bigint company_id FK
        int sap_doc_entry
        smallint run_number
        date date
        bigint line_id FK
        varchar product
        decimal required_qty
        varchar warehouse_approval_status
        decimal rated_speed
        int labour_count
        int other_manpower_count
        varchar supervisor
        varchar operators
        decimal total_production
        int total_running_minutes
        int total_breakdown_time
        decimal rejected_qty
        decimal reworked_qty
        int sap_receipt_doc_entry
        varchar sap_sync_status
        text sap_sync_error
        varchar status
        bigint created_by_id FK
        datetime created_at
        datetime updated_at
    }
    production_execution_productionrun_machines {
        bigint id PK
        bigint productionrun_id FK
        bigint machine_id FK
    }
    production_execution_productionruncost {
        bigint id PK
        bigint production_run_id FK
        decimal raw_material_cost
        decimal labour_cost
        decimal machine_cost
        decimal electricity_cost
        decimal water_cost
        decimal gas_cost
        decimal compressed_air_cost
        decimal overhead_cost
        decimal total_cost
        decimal produced_qty
        decimal per_unit_cost
        datetime calculated_at
    }
    production_execution_productionsegment {
        bigint id PK
        bigint production_run_id FK
        datetime start_time
        datetime end_time
        decimal produced_cases
        boolean is_active
        text remarks
        datetime created_at
        datetime updated_at
    }
    production_execution_resourcecompressedair {
        bigint id PK
        bigint production_run_id FK
        varchar description
        decimal units_consumed
        decimal rate_per_unit
        decimal total_cost
        bigint created_by_id FK
        datetime created_at
        datetime updated_at
    }
    production_execution_resourceelectricity {
        bigint id PK
        bigint production_run_id FK
        varchar description
        decimal units_consumed
        decimal rate_per_unit
        decimal total_cost
        bigint created_by_id FK
        datetime created_at
        datetime updated_at
    }
    production_execution_resourcegas {
        bigint id PK
        bigint production_run_id FK
        varchar description
        decimal qty_consumed
        decimal rate_per_unit
        decimal total_cost
        bigint created_by_id FK
        datetime created_at
        datetime updated_at
    }
    production_execution_resourcelabour {
        bigint id PK
        bigint production_run_id FK
        varchar description
        int worker_count
        decimal hours_worked
        decimal rate_per_hour
        decimal total_cost
        bigint created_by_id FK
        datetime created_at
        datetime updated_at
    }
    production_execution_resourcemachinecost {
        bigint id PK
        bigint production_run_id FK
        varchar machine_name
        decimal hours_used
        decimal rate_per_hour
        decimal total_cost
        bigint created_by_id FK
        datetime created_at
        datetime updated_at
    }
    production_execution_resourceoverhead {
        bigint id PK
        bigint production_run_id FK
        varchar expense_name
        decimal amount
        bigint created_by_id FK
        datetime created_at
        datetime updated_at
    }
    production_execution_resourcewater {
        bigint id PK
        bigint production_run_id FK
        varchar description
        decimal volume_consumed
        decimal rate_per_unit
        decimal total_cost
        bigint created_by_id FK
        datetime created_at
        datetime updated_at
    }
    production_execution_wastelog {
        bigint id PK
        bigint production_run_id FK
        varchar material_code
        varchar material_name
        decimal wastage_qty
        varchar uom
        text reason
        varchar engineer_sign
        bigint engineer_signed_by_id FK
        datetime engineer_signed_at
        varchar am_sign
        bigint am_signed_by_id FK
        datetime am_signed_at
        varchar store_sign
        bigint store_signed_by_id FK
        datetime store_signed_at
        varchar hod_sign
        bigint hod_signed_by_id FK
        datetime hod_signed_at
        varchar wastage_approval_status
        datetime created_at
        datetime updated_at
    }
    quality_control_arrivalslipattachment {
        bigint id PK
        bigint arrival_slip_id FK
        varchar file
        varchar attachment_type
        datetime uploaded_at
    }
    quality_control_inspectionparameterresult {
        bigint id PK
        datetime created_at
        datetime updated_at
        bigint created_by_id FK
        bigint updated_by_id FK
        boolean is_active
        bigint inspection_id FK
        bigint parameter_master_id FK
        varchar parameter_name
        varchar standard_value
        varchar result_value
        decimal result_numeric
        boolean is_within_spec
        text remarks
    }
    quality_control_materialarrivalslip {
        bigint id PK
        datetime created_at
        datetime updated_at
        bigint created_by_id FK
        bigint updated_by_id FK
        boolean is_active
        bigint po_item_receipt_id FK
        text particulars
        datetime arrival_datetime
        boolean weighing_required
        varchar party_name
        decimal billing_qty
        varchar billing_uom
        datetime in_time_to_qa
        varchar truck_no_as_per_bill
        varchar commercial_invoice_no
        varchar eway_bill_no
        varchar bilty_no
        boolean has_certificate_of_analysis
        boolean has_certificate_of_quantity
        varchar status
        boolean is_submitted
        datetime submitted_at
        bigint submitted_by_id FK
        text remarks
        bigint sent_back_by_id FK
        datetime sent_back_at
    }
    quality_control_materialtype {
        bigint id PK
        datetime created_at
        datetime updated_at
        bigint created_by_id FK
        bigint updated_by_id FK
        boolean is_active
        varchar code
        varchar name
        text description
        bigint company_id FK
    }
    quality_control_productionqcresult {
        bigint id PK
        datetime created_at
        datetime updated_at
        bigint created_by_id FK
        bigint updated_by_id FK
        boolean is_active
        bigint session_id FK
        bigint parameter_master_id FK
        varchar parameter_name
        varchar standard_value
        varchar result_value
        decimal result_numeric
        boolean is_within_spec
        text remarks
    }
    quality_control_productionqcsession {
        bigint id PK
        datetime created_at
        datetime updated_at
        bigint created_by_id FK
        bigint updated_by_id FK
        boolean is_active
        bigint production_run_id FK
        bigint material_type_id FK
        smallint session_number
        varchar session_type
        datetime checked_at
        bigint checked_by_id FK
        varchar overall_result
        varchar workflow_status
        bigint submitted_by_id FK
        datetime submitted_at
        text remarks
    }
    quality_control_qcparametermaster {
        bigint id PK
        datetime created_at
        datetime updated_at
        bigint created_by_id FK
        bigint updated_by_id FK
        boolean is_active
        bigint material_type_id FK
        varchar parameter_name
        varchar parameter_code
        varchar standard_value
        varchar parameter_type
        decimal min_value
        decimal max_value
        varchar uom
        int sequence
        boolean is_mandatory
    }
    quality_control_rawmaterialinspection {
        bigint id PK
        datetime created_at
        datetime updated_at
        bigint created_by_id FK
        bigint updated_by_id FK
        boolean is_active
        bigint arrival_slip_id FK
        varchar report_no UK
        varchar internal_lot_no
        date inspection_date
        text description_of_material
        varchar sap_code
        varchar supplier_name
        varchar manufacturer_name
        varchar supplier_batch_lot_no
        varchar unit_packing
        varchar purchase_order_no
        varchar internal_report_no
        varchar invoice_bill_no
        varchar vehicle_no
        bigint material_type_id FK
        varchar final_status
        bigint qa_chemist_id FK
        datetime qa_chemist_approved_at
        text qa_chemist_remarks
        bigint qam_id FK
        datetime qam_approved_at
        text qam_remarks
        bigint rejected_by_id FK
        datetime rejected_at
        bigint factory_head_id FK
        varchar factory_head_decision
        text factory_head_remarks
        datetime factory_head_decided_at
        varchar workflow_status
        boolean is_locked
        text remarks
    }
    raw_material_gatein_poitemreceipt {
        bigint id PK
        datetime created_at
        datetime updated_at
        bigint created_by_id FK
        bigint updated_by_id FK
        boolean is_active
        bigint po_receipt_id FK
        varchar po_item_code
        varchar item_name
        int sap_line_num
        decimal unit_price
        varchar tax_code
        varchar warehouse_code
        varchar gl_account
        varchar variety
        decimal ordered_qty
        decimal received_qty
        decimal accepted_qty
        decimal rejected_qty
        decimal short_qty
        varchar uom
    }
    raw_material_gatein_poreceipt {
        bigint id PK
        datetime created_at
        datetime updated_at
        bigint created_by_id FK
        bigint updated_by_id FK
        boolean is_active
        bigint vehicle_entry_id FK
        varchar po_number
        varchar supplier_code
        varchar supplier_name
        int sap_doc_entry
        int branch_id
        varchar vendor_ref
        date po_date
        varchar invoice_no
        date invoice_date
        varchar challan_no
    }
    security_checks_securitycheck {
        bigint id PK
        datetime created_at
        datetime updated_at
        bigint created_by_id FK
        bigint updated_by_id FK
        boolean is_active
        bigint vehicle_entry_id FK
        boolean vehicle_condition_ok
        boolean tyre_condition_ok
        boolean fire_extinguisher_available
        varchar seal_no_before
        varchar seal_no_after
        boolean alcohol_test_done
        boolean alcohol_test_passed
        varchar inspected_by_name
        datetime inspection_time
        text remarks
        boolean is_submitted
    }
    django_session {
        varchar session_key PK
        text session_data
        datetime expire_date
    }
    stock_dashboard_stockalertlog {
        bigint id PK
        varchar company_code
        varchar item_code
        varchar warehouse
        varchar stock_status
        float on_hand
        float min_stock
        datetime notified_at
        datetime cooldown_until
    }
    token_blacklist_blacklistedtoken {
        bigint id PK
        bigint token_id FK
        datetime blacklisted_at
    }
    token_blacklist_outstandingtoken {
        bigint id PK
        bigint user_id FK
        varchar jti UK
        text token
        datetime created_at
        datetime expires_at
    }
    vehicle_management_transporter {
        bigint id PK
        datetime created_at
        datetime updated_at
        bigint created_by_id FK
        bigint updated_by_id FK
        boolean is_active
        varchar name UK
        varchar contact_person
        varchar mobile_no
        varchar gstin
    }
    vehicle_management_vehicle {
        bigint id PK
        datetime created_at
        datetime updated_at
        bigint created_by_id FK
        bigint updated_by_id FK
        boolean is_active
        varchar vehicle_number UK
        bigint vehicle_type_id FK
        bigint transporter_id FK
        decimal capacity_ton
    }
    vehicle_management_vehicletype {
        bigint id PK
        datetime created_at
        datetime updated_at
        bigint created_by_id FK
        bigint updated_by_id FK
        boolean is_active
        varchar name UK
    }
    warehouse_bomrequest {
        bigint id PK
        bigint company_id FK
        bigint production_run_id FK
        int sap_doc_entry
        decimal required_qty
        varchar status
        text remarks
        text rejection_reason
        varchar material_issue_status
        json sap_issue_doc_entries
        bigint requested_by_id FK
        bigint reviewed_by_id FK
        datetime reviewed_at
        datetime created_at
        datetime updated_at
    }
    warehouse_bomrequestline {
        bigint id PK
        bigint bom_request_id FK
        varchar item_code
        varchar item_name
        decimal per_unit_qty
        decimal required_qty
        decimal available_stock
        decimal approved_qty
        decimal issued_qty
        varchar warehouse
        varchar uom
        int base_line
        varchar status
        text remarks
        datetime created_at
        datetime updated_at
    }
    warehouse_finishedgoodsreceipt {
        bigint id PK
        bigint company_id FK
        bigint production_run_id FK
        int sap_doc_entry
        varchar item_code
        varchar item_name
        decimal produced_qty
        decimal good_qty
        decimal rejected_qty
        varchar warehouse
        varchar uom
        date posting_date
        varchar status
        int sap_receipt_doc_entry
        text sap_error
        bigint received_by_id FK
        datetime received_at
        datetime created_at
        datetime updated_at
    }
    weighment_weighment {
        bigint id PK
        datetime created_at
        datetime updated_at
        bigint created_by_id FK
        bigint updated_by_id FK
        boolean is_active
        bigint vehicle_entry_id FK
        decimal gross_weight
        decimal tare_weight
        decimal net_weight
        varchar weighbridge_slip_no
        datetime first_weighment_time
        datetime second_weighment_time
        text remarks
    }
    accounts_department ||--o{ daily_needs_gatein_dailyneedgateentry : "receiving_department_id"
    accounts_department ||--o{ maintenance_gatein_maintenancegateentry : "receiving_department_id"
    accounts_user ||--o{ accounts_user_groups : "user_id"
    accounts_user ||--o{ accounts_user_user_permissions : "user_id"
    accounts_user ||--o{ company_usercompany : "user_id"
    accounts_user ||--o{ construction_gatein_constructiongateentry : "created_by_id"
    accounts_user ||--o{ daily_needs_gatein_dailyneedgateentry : "created_by_id"
    accounts_user ||--o{ dispatch_plans_dispatchplan : "created_by_id"
    accounts_user ||--o{ dispatch_plans_dispatchplan : "updated_by_id"
    accounts_user ||--o{ django_admin_log : "user_id"
    accounts_user ||--o{ driver_management_driver : "created_by_id"
    accounts_user ||--o{ driver_management_driver : "updated_by_id"
    accounts_user ||--o{ driver_management_vehicleentry : "created_by_id"
    accounts_user ||--o{ driver_management_vehicleentry : "updated_by_id"
    accounts_user ||--o{ gate_core_bstgatein : "created_by_id"
    accounts_user ||--o{ gate_core_bstgatein : "updated_by_id"
    accounts_user ||--o{ gate_core_bstgateinitem : "created_by_id"
    accounts_user ||--o{ gate_core_bstgateinitem : "updated_by_id"
    accounts_user ||--o{ gate_core_bstgateout : "cancelled_by_id"
    accounts_user ||--o{ gate_core_bstgateout : "created_by_id"
    accounts_user ||--o{ gate_core_bstgateout : "updated_by_id"
    accounts_user ||--o{ gate_core_bstgateoutitem : "created_by_id"
    accounts_user ||--o{ gate_core_bstgateoutitem : "updated_by_id"
    accounts_user ||--o{ gate_core_bstgatereturn : "created_by_id"
    accounts_user ||--o{ gate_core_bstgatereturn : "updated_by_id"
    accounts_user ||--o{ gate_core_emptyvehiclegatein : "created_by_id"
    accounts_user ||--o{ gate_core_emptyvehiclegatein : "updated_by_id"
    accounts_user ||--o{ gate_core_emptyvehiclegateinitem : "created_by_id"
    accounts_user ||--o{ gate_core_emptyvehiclegateinitem : "updated_by_id"
    accounts_user ||--o{ gate_core_emptyvehiclegateout : "cancelled_by_id"
    accounts_user ||--o{ gate_core_emptyvehiclegateout : "created_by_id"
    accounts_user ||--o{ gate_core_emptyvehiclegateout : "updated_by_id"
    accounts_user ||--o{ gate_core_jobworkgatein : "created_by_id"
    accounts_user ||--o{ gate_core_jobworkgatein : "updated_by_id"
    accounts_user ||--o{ gate_core_jobworkgateinitem : "created_by_id"
    accounts_user ||--o{ gate_core_jobworkgateinitem : "updated_by_id"
    accounts_user ||--o{ gate_core_rejectedqcreturnentry : "created_by_id"
    accounts_user ||--o{ gate_core_rejectedqcreturnentry : "updated_by_id"
    accounts_user ||--o{ gate_core_rejectedqcreturnitem : "created_by_id"
    accounts_user ||--o{ gate_core_rejectedqcreturnitem : "updated_by_id"
    accounts_user ||--o{ grpo_grpoattachment : "uploaded_by_id"
    accounts_user ||--o{ grpo_grpoposting : "posted_by_id"
    accounts_user ||--o{ grpo_servicegrpoattachment : "uploaded_by_id"
    accounts_user ||--o{ grpo_servicegrpoposting : "posted_by_id"
    accounts_user ||--o{ maintenance_gatein_maintenancegateentry : "created_by_id"
    accounts_user ||--o{ notifications_notification : "created_by_id"
    accounts_user ||--o{ notifications_notification : "recipient_id"
    accounts_user ||--o{ notifications_userdevice : "user_id"
    accounts_user ||--o{ person_gatein_entrylog : "approved_by_id"
    accounts_user ||--o{ person_gatein_entrylog : "created_by_id"
    accounts_user ||--o{ production_execution_finalqccheck : "checked_by_id"
    accounts_user ||--o{ production_execution_inprocessqccheck : "checked_by_id"
    accounts_user ||--o{ production_execution_lineclearance : "created_by_id"
    accounts_user ||--o{ production_execution_lineclearance : "qa_approved_by_id"
    accounts_user ||--o{ production_execution_lineclearance : "verified_by_id"
    accounts_user ||--o{ production_execution_productionrun : "created_by_id"
    accounts_user ||--o{ production_execution_resourcecompressedair : "created_by_id"
    accounts_user ||--o{ production_execution_resourceelectricity : "created_by_id"
    accounts_user ||--o{ production_execution_resourcegas : "created_by_id"
    accounts_user ||--o{ production_execution_resourcelabour : "created_by_id"
    accounts_user ||--o{ production_execution_resourcemachinecost : "created_by_id"
    accounts_user ||--o{ production_execution_resourceoverhead : "created_by_id"
    accounts_user ||--o{ production_execution_resourcewater : "created_by_id"
    accounts_user ||--o{ production_execution_wastelog : "am_signed_by_id"
    accounts_user ||--o{ production_execution_wastelog : "engineer_signed_by_id"
    accounts_user ||--o{ production_execution_wastelog : "hod_signed_by_id"
    accounts_user ||--o{ production_execution_wastelog : "store_signed_by_id"
    accounts_user ||--o{ quality_control_inspectionparameterresult : "created_by_id"
    accounts_user ||--o{ quality_control_inspectionparameterresult : "updated_by_id"
    accounts_user ||--o{ quality_control_materialarrivalslip : "created_by_id"
    accounts_user ||--o{ quality_control_materialarrivalslip : "sent_back_by_id"
    accounts_user ||--o{ quality_control_materialarrivalslip : "submitted_by_id"
    accounts_user ||--o{ quality_control_materialarrivalslip : "updated_by_id"
    accounts_user ||--o{ quality_control_materialtype : "created_by_id"
    accounts_user ||--o{ quality_control_materialtype : "updated_by_id"
    accounts_user ||--o{ quality_control_productionqcresult : "created_by_id"
    accounts_user ||--o{ quality_control_productionqcresult : "updated_by_id"
    accounts_user ||--o{ quality_control_productionqcsession : "checked_by_id"
    accounts_user ||--o{ quality_control_productionqcsession : "created_by_id"
    accounts_user ||--o{ quality_control_productionqcsession : "submitted_by_id"
    accounts_user ||--o{ quality_control_productionqcsession : "updated_by_id"
    accounts_user ||--o{ quality_control_qcparametermaster : "created_by_id"
    accounts_user ||--o{ quality_control_qcparametermaster : "updated_by_id"
    accounts_user ||--o{ quality_control_rawmaterialinspection : "created_by_id"
    accounts_user ||--o{ quality_control_rawmaterialinspection : "factory_head_id"
    accounts_user ||--o{ quality_control_rawmaterialinspection : "qa_chemist_id"
    accounts_user ||--o{ quality_control_rawmaterialinspection : "qam_id"
    accounts_user ||--o{ quality_control_rawmaterialinspection : "rejected_by_id"
    accounts_user ||--o{ quality_control_rawmaterialinspection : "updated_by_id"
    accounts_user ||--o{ raw_material_gatein_poitemreceipt : "created_by_id"
    accounts_user ||--o{ raw_material_gatein_poitemreceipt : "updated_by_id"
    accounts_user ||--o{ raw_material_gatein_poreceipt : "created_by_id"
    accounts_user ||--o{ raw_material_gatein_poreceipt : "updated_by_id"
    accounts_user ||--o{ security_checks_securitycheck : "created_by_id"
    accounts_user ||--o{ security_checks_securitycheck : "updated_by_id"
    accounts_user ||--o{ token_blacklist_outstandingtoken : "user_id"
    accounts_user ||--o{ vehicle_management_transporter : "created_by_id"
    accounts_user ||--o{ vehicle_management_transporter : "updated_by_id"
    accounts_user ||--o{ vehicle_management_vehicle : "created_by_id"
    accounts_user ||--o{ vehicle_management_vehicle : "updated_by_id"
    accounts_user ||--o{ vehicle_management_vehicletype : "created_by_id"
    accounts_user ||--o{ vehicle_management_vehicletype : "updated_by_id"
    accounts_user ||--o{ warehouse_bomrequest : "requested_by_id"
    accounts_user ||--o{ warehouse_bomrequest : "reviewed_by_id"
    accounts_user ||--o{ warehouse_finishedgoodsreceipt : "received_by_id"
    accounts_user ||--o{ weighment_weighment : "created_by_id"
    accounts_user ||--o{ weighment_weighment : "updated_by_id"
    auth_group ||--o{ accounts_user_groups : "group_id"
    auth_group ||--o{ auth_group_permissions : "group_id"
    auth_permission ||--o{ accounts_user_user_permissions : "permission_id"
    auth_permission ||--o{ auth_group_permissions : "permission_id"
    company_company ||--o{ company_usercompany : "company_id"
    company_company ||--o{ dispatch_plans_dispatchplan : "company_id"
    company_company ||--o{ driver_management_vehicleentry : "company_id"
    company_company ||--o{ gate_core_bstgatein : "company_id"
    company_company ||--o{ gate_core_bstgateout : "company_id"
    company_company ||--o{ gate_core_bstgatereturn : "company_id"
    company_company ||--o{ gate_core_emptyvehiclegatein : "company_id"
    company_company ||--o{ gate_core_emptyvehiclegateout : "company_id"
    company_company ||--o{ gate_core_jobworkgatein : "company_id"
    company_company ||--o{ gate_core_rejectedqcreturnentry : "company_id"
    company_company ||--o{ notifications_notification : "company_id"
    company_company ||--o{ production_execution_breakdowncategory : "company_id"
    company_company ||--o{ production_execution_lineclearance : "company_id"
    company_company ||--o{ production_execution_lineskuconfig : "company_id"
    company_company ||--o{ production_execution_machine : "company_id"
    company_company ||--o{ production_execution_machinechecklistentry : "company_id"
    company_company ||--o{ production_execution_machinechecklisttemplate : "company_id"
    company_company ||--o{ production_execution_productionline : "company_id"
    company_company ||--o{ production_execution_productionrun : "company_id"
    company_company ||--o{ quality_control_materialtype : "company_id"
    company_company ||--o{ warehouse_bomrequest : "company_id"
    company_company ||--o{ warehouse_finishedgoodsreceipt : "company_id"
    company_userrole ||--o{ company_usercompany : "role_id"
    construction_gatein_constructionmaterialcategory ||--o{ construction_gatein_constructiongateentry : "material_category_id"
    daily_needs_gatein_categorylist ||--o{ daily_needs_gatein_dailyneedgateentry : "item_category_id"
    dispatch_plans_dispatchplan ||--o{ grpo_servicegrpoposting : "dispatch_plan_id"
    django_apscheduler_djangojob ||--o{ django_apscheduler_djangojobexecution : "job_id"
    django_content_type ||--o{ auth_permission : "content_type_id"
    django_content_type ||--o{ django_admin_log : "content_type_id"
    driver_management_driver ||--o{ dispatch_plans_dispatchplan : "driver_id"
    driver_management_driver ||--o{ driver_management_vehicleentry : "driver_id"
    driver_management_driver ||--o{ gate_core_bstgatein : "driver_id"
    driver_management_driver ||--o{ gate_core_bstgateout : "driver_id"
    driver_management_driver ||--o{ gate_core_bstgatereturn : "driver_id"
    driver_management_driver ||--o{ gate_core_emptyvehiclegatein : "driver_id"
    driver_management_driver ||--o{ gate_core_emptyvehiclegateout : "driver_id"
    driver_management_driver ||--o{ gate_core_jobworkgatein : "driver_id"
    driver_management_driver ||--o{ gate_core_rejectedqcreturnentry : "driver_id"
    driver_management_vehicleentry ||--o{ dispatch_plans_dispatchplan : "linked_vehicle_entry_id"
    driver_management_vehicleentry ||--o{ gate_core_bstgatein : "vehicle_entry_id"
    driver_management_vehicleentry ||--o{ gate_core_bstgateout : "vehicle_entry_id"
    driver_management_vehicleentry ||--o{ gate_core_bstgatereturn : "vehicle_entry_id"
    driver_management_vehicleentry ||--o{ gate_core_emptyvehiclegateout : "vehicle_entry_id"
    driver_management_vehicleentry ||--o{ gate_core_gateattachment : "gate_entry_id"
    driver_management_vehicleentry ||--o{ gate_core_jobworkgatein : "vehicle_entry_id"
    driver_management_vehicleentry ||--o{ grpo_grpoposting : "vehicle_entry_id"
    driver_management_vehicleentry ||--o{ raw_material_gatein_poreceipt : "vehicle_entry_id"
    driver_management_vehicleentry ||--|| construction_gatein_constructiongateentry : "vehicle_entry_id"
    driver_management_vehicleentry ||--|| daily_needs_gatein_dailyneedgateentry : "vehicle_entry_id"
    driver_management_vehicleentry ||--|| gate_core_emptyvehiclegatein : "vehicle_entry_id"
    driver_management_vehicleentry ||--|| maintenance_gatein_maintenancegateentry : "vehicle_entry_id"
    driver_management_vehicleentry ||--|| security_checks_securitycheck : "vehicle_entry_id"
    driver_management_vehicleentry ||--|| weighment_weighment : "vehicle_entry_id"
    gate_core_bstgatein ||--o{ gate_core_bstgateinitem : "bst_gate_in_id"
    gate_core_bstgateout ||--o{ gate_core_bstgatein : "bst_gate_out_id"
    gate_core_bstgateout ||--o{ gate_core_bstgateoutitem : "bst_gate_out_id"
    gate_core_bstgateout ||--o{ gate_core_bstgatereturn : "bst_gate_out_id"
    gate_core_bstgateoutitem ||--o{ gate_core_bstgateinitem : "bst_gate_out_item_id"
    gate_core_emptyvehiclegatein ||--o{ gate_core_bstgateout : "empty_vehicle_gate_in_id"
    gate_core_emptyvehiclegatein ||--o{ gate_core_emptyvehiclegateinitem : "empty_vehicle_gate_in_id"
    gate_core_jobworkgatein ||--o{ gate_core_jobworkgateinitem : "job_work_gate_in_id"
    gate_core_rejectedqcreturnentry ||--o{ gate_core_rejectedqcreturnitem : "entry_id"
    gate_core_unitchoice ||--o{ construction_gatein_constructiongateentry : "unit_id"
    gate_core_unitchoice ||--o{ daily_needs_gatein_dailyneedgateentry : "unit_id"
    gate_core_unitchoice ||--o{ maintenance_gatein_maintenancegateentry : "unit_id"
    grpo_grpoposting ||--o{ grpo_grpoattachment : "grpo_posting_id"
    grpo_grpoposting ||--o{ grpo_grpolineposting : "grpo_posting_id"
    grpo_grpoposting ||--o{ grpo_grpoposting_po_receipts : "grpoposting_id"
    grpo_servicegrpoposting ||--o{ grpo_servicegrpoattachment : "service_grpo_posting_id"
    grpo_servicegrpoposting ||--o{ grpo_servicegrpolineposting : "service_grpo_posting_id"
    maintenance_gatein_maintenancetype ||--o{ maintenance_gatein_maintenancegateentry : "maintenance_type_id"
    person_gatein_contractor ||--o{ person_gatein_labour : "contractor_id"
    person_gatein_gate ||--o{ person_gatein_entrylog : "gate_in_id"
    person_gatein_gate ||--o{ person_gatein_entrylog : "gate_out_id"
    person_gatein_labour ||--o{ person_gatein_entrylog : "labour_id"
    person_gatein_persontype ||--o{ person_gatein_entrylog : "person_type_id"
    person_gatein_visitor ||--o{ person_gatein_entrylog : "visitor_id"
    production_execution_breakdowncategory ||--o{ production_execution_machinebreakdown : "breakdown_category_id"
    production_execution_lineclearance ||--o{ production_execution_lineclearanceitem : "clearance_id"
    production_execution_machine ||--o{ production_execution_machinebreakdown : "machine_id"
    production_execution_machine ||--o{ production_execution_machinechecklistentry : "machine_id"
    production_execution_machine ||--o{ production_execution_machineruntime : "machine_id"
    production_execution_machine ||--o{ production_execution_productionrun_machines : "machine_id"
    production_execution_machinechecklisttemplate ||--o{ production_execution_machinechecklistentry : "template_id"
    production_execution_productionline ||--o{ production_execution_lineclearance : "line_id"
    production_execution_productionline ||--o{ production_execution_lineskuconfig : "line_id"
    production_execution_productionline ||--o{ production_execution_machine : "line_id"
    production_execution_productionline ||--o{ production_execution_productionrun : "line_id"
    production_execution_productionrun ||--o{ production_execution_inprocessqccheck : "production_run_id"
    production_execution_productionrun ||--o{ production_execution_lineclearance : "production_run_id"
    production_execution_productionrun ||--o{ production_execution_machinebreakdown : "production_run_id"
    production_execution_productionrun ||--o{ production_execution_machineruntime : "production_run_id"
    production_execution_productionrun ||--o{ production_execution_productionmanpower : "production_run_id"
    production_execution_productionrun ||--o{ production_execution_productionmaterialusage : "production_run_id"
    production_execution_productionrun ||--o{ production_execution_productionrun_machines : "productionrun_id"
    production_execution_productionrun ||--o{ production_execution_productionsegment : "production_run_id"
    production_execution_productionrun ||--o{ production_execution_resourcecompressedair : "production_run_id"
    production_execution_productionrun ||--o{ production_execution_resourceelectricity : "production_run_id"
    production_execution_productionrun ||--o{ production_execution_resourcegas : "production_run_id"
    production_execution_productionrun ||--o{ production_execution_resourcelabour : "production_run_id"
    production_execution_productionrun ||--o{ production_execution_resourcemachinecost : "production_run_id"
    production_execution_productionrun ||--o{ production_execution_resourceoverhead : "production_run_id"
    production_execution_productionrun ||--o{ production_execution_resourcewater : "production_run_id"
    production_execution_productionrun ||--o{ production_execution_wastelog : "production_run_id"
    production_execution_productionrun ||--o{ quality_control_productionqcsession : "production_run_id"
    production_execution_productionrun ||--o{ warehouse_bomrequest : "production_run_id"
    production_execution_productionrun ||--o{ warehouse_finishedgoodsreceipt : "production_run_id"
    production_execution_productionrun ||--|| production_execution_finalqccheck : "production_run_id"
    production_execution_productionrun ||--|| production_execution_productionruncost : "production_run_id"
    quality_control_materialarrivalslip ||--o{ quality_control_arrivalslipattachment : "arrival_slip_id"
    quality_control_materialarrivalslip ||--o| quality_control_rawmaterialinspection : "arrival_slip_id"
    quality_control_materialtype ||--o{ quality_control_productionqcsession : "material_type_id"
    quality_control_materialtype ||--o{ quality_control_qcparametermaster : "material_type_id"
    quality_control_materialtype ||--o{ quality_control_rawmaterialinspection : "material_type_id"
    quality_control_productionqcsession ||--o{ quality_control_productionqcresult : "session_id"
    quality_control_qcparametermaster ||--o{ quality_control_inspectionparameterresult : "parameter_master_id"
    quality_control_qcparametermaster ||--o{ quality_control_productionqcresult : "parameter_master_id"
    quality_control_rawmaterialinspection ||--o{ quality_control_inspectionparameterresult : "inspection_id"
    quality_control_rawmaterialinspection ||--|| gate_core_rejectedqcreturnitem : "inspection_id"
    raw_material_gatein_poitemreceipt ||--o{ grpo_grpolineposting : "po_item_receipt_id"
    raw_material_gatein_poitemreceipt ||--o| quality_control_materialarrivalslip : "po_item_receipt_id"
    raw_material_gatein_poreceipt ||--o{ grpo_grpoposting : "po_receipt_id"
    raw_material_gatein_poreceipt ||--o{ grpo_grpoposting_po_receipts : "poreceipt_id"
    raw_material_gatein_poreceipt ||--o{ raw_material_gatein_poitemreceipt : "po_receipt_id"
    token_blacklist_outstandingtoken ||--|| token_blacklist_blacklistedtoken : "token_id"
    vehicle_management_transporter ||--o{ dispatch_plans_dispatchplan : "transporter_id"
    vehicle_management_transporter ||--o{ vehicle_management_vehicle : "transporter_id"
    vehicle_management_vehicle ||--o{ dispatch_plans_dispatchplan : "vehicle_id"
    vehicle_management_vehicle ||--o{ driver_management_vehicleentry : "vehicle_id"
    vehicle_management_vehicle ||--o{ gate_core_bstgatein : "vehicle_id"
    vehicle_management_vehicle ||--o{ gate_core_bstgateout : "vehicle_id"
    vehicle_management_vehicle ||--o{ gate_core_bstgatereturn : "vehicle_id"
    vehicle_management_vehicle ||--o{ gate_core_emptyvehiclegatein : "vehicle_id"
    vehicle_management_vehicle ||--o{ gate_core_emptyvehiclegateout : "vehicle_id"
    vehicle_management_vehicle ||--o{ gate_core_jobworkgatein : "vehicle_id"
    vehicle_management_vehicle ||--o{ gate_core_rejectedqcreturnentry : "vehicle_id"
    vehicle_management_vehicletype ||--o{ vehicle_management_vehicle : "vehicle_type_id"
    warehouse_bomrequest ||--o{ warehouse_bomrequestline : "bom_request_id"
```
