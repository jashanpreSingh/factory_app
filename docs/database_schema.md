# Database Schema

Generated on: `2026-05-09 12:41:37`

Source: Django model metadata via `scripts/generate_er_docs.py`.

Scope: managed Django models plus implicit many-to-many join tables. Unmanaged permission-only sentinel models are listed separately because Django does not create database tables for them.

Related ER files:

- [er_model.md](er_model.md)
- [er_model.mmd](er_model.mmd)

## Summary

- Managed tables: `100`
- Relationships: `249`
- Apps with managed tables: `25`

## Unmanaged Permission Models

| App | Model | Declared table name | Note |
| --- | --- | --- | --- |
| inventory_age | InventoryAgePermission | inventory_age_inventoryagepermission | No table is created (`managed = False`) |
| non_moving_rm | NonMovingRMPermission | non_moving_rm_nonmovingrmpermission | No table is created (`managed = False`) |
| sap_plan_dashboard | PlanDashboardPermission | sap_plan_dashboard_plandashboardpermission | No table is created (`managed = False`) |
| stock_dashboard | StockDashboardPermission | stock_dashboard_stockdashboardpermission | No table is created (`managed = False`) |

## Tables And Columns

### accounts

#### `accounts_department`

Django model: `accounts.Department`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `name` | `name` | `CharField(max_length=100)` |  | NO |  |
| `description` | `description` | `TextField` |  | NO |  |

#### `accounts_user`

Django model: `accounts.User`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `password` | `password` | `CharField(max_length=128)` |  | NO |  |
| `last_login` | `last_login` | `DateTimeField` |  | YES |  |
| `is_superuser` | `is_superuser` | `BooleanField` |  | NO |  |
| `email` | `email` | `CharField(max_length=254)` | UNIQUE | NO |  |
| `full_name` | `full_name` | `CharField(max_length=150)` |  | NO |  |
| `employee_code` | `employee_code` | `CharField(max_length=50)` | UNIQUE | NO |  |
| `is_active` | `is_active` | `BooleanField` |  | NO |  |
| `is_staff` | `is_staff` | `BooleanField` |  | NO |  |
| `date_joined` | `date_joined` | `DateTimeField` |  | NO |  |

#### `accounts_user_groups` (implicit join table)

Django model: `accounts.User_groups`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `user_id` | `user` | `ForeignKey` | FK | NO | accounts_user.id |
| `group_id` | `group` | `ForeignKey` | FK | NO | auth_group.id |

#### `accounts_user_user_permissions` (implicit join table)

Django model: `accounts.User_user_permissions`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `user_id` | `user` | `ForeignKey` | FK | NO | accounts_user.id |
| `permission_id` | `permission` | `ForeignKey` | FK | NO | auth_permission.id |

### admin

#### `django_admin_log`

Django model: `admin.LogEntry`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `AutoField` | PK | NO |  |
| `action_time` | `action_time` | `DateTimeField` |  | NO |  |
| `user_id` | `user` | `ForeignKey` | FK | NO | accounts_user.id |
| `content_type_id` | `content_type` | `ForeignKey` | FK | YES | django_content_type.id |
| `object_id` | `object_id` | `TextField` |  | YES |  |
| `object_repr` | `object_repr` | `CharField(max_length=200)` |  | NO |  |
| `action_flag` | `action_flag` | `PositiveSmallIntegerField` |  | NO |  |
| `change_message` | `change_message` | `TextField` |  | NO |  |

### auth

#### `auth_group`

Django model: `auth.Group`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `AutoField` | PK | NO |  |
| `name` | `name` | `CharField(max_length=150)` | UNIQUE | NO |  |

#### `auth_group_permissions` (implicit join table)

Django model: `auth.Group_permissions`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `AutoField` | PK | NO |  |
| `group_id` | `group` | `ForeignKey` | FK | NO | auth_group.id |
| `permission_id` | `permission` | `ForeignKey` | FK | NO | auth_permission.id |

#### `auth_permission`

Django model: `auth.Permission`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `AutoField` | PK | NO |  |
| `name` | `name` | `CharField(max_length=255)` |  | NO |  |
| `content_type_id` | `content_type` | `ForeignKey` | FK | NO | django_content_type.id |
| `codename` | `codename` | `CharField(max_length=100)` |  | NO |  |

### company

#### `company_company`

Django model: `company.Company`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `name` | `name` | `CharField(max_length=200)` |  | NO |  |
| `code` | `code` | `CharField(max_length=50)` | UNIQUE | NO |  |
| `is_active` | `is_active` | `BooleanField` |  | NO |  |

#### `company_usercompany`

Django model: `company.UserCompany`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `user_id` | `user` | `ForeignKey` | FK | NO | accounts_user.id |
| `company_id` | `company` | `ForeignKey` | FK | NO | company_company.id |
| `role_id` | `role` | `ForeignKey` | FK | NO | company_userrole.id |
| `is_default` | `is_default` | `BooleanField` |  | NO |  |
| `is_active` | `is_active` | `BooleanField` |  | NO |  |

#### `company_userrole`

Django model: `company.UserRole`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `name` | `name` | `CharField(max_length=100)` |  | NO |  |
| `description` | `description` | `TextField` |  | NO |  |

### construction_gatein

#### `construction_gatein_constructiongateentry`

Django model: `construction_gatein.ConstructionGateEntry`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `vehicle_entry_id` | `vehicle_entry` | `OneToOneField` | FK, UNIQUE | NO | driver_management_vehicleentry.id |
| `project_name` | `project_name` | `CharField(max_length=200)` |  | YES |  |
| `work_order_number` | `work_order_number` | `CharField(max_length=20)` | UNIQUE | YES |  |
| `contractor_name` | `contractor_name` | `CharField(max_length=200)` |  | NO |  |
| `contractor_contact` | `contractor_contact` | `CharField(max_length=15)` |  | YES |  |
| `material_category_id` | `material_category` | `ForeignKey` | FK | YES | construction_gatein_constructionmaterialcategory.id |
| `material_description` | `material_description` | `TextField` |  | NO |  |
| `quantity` | `quantity` | `DecimalField(max_digits=10, decimal_places=2)` |  | NO |  |
| `unit_id` | `unit` | `ForeignKey` | FK | YES | gate_core_unitchoice.id |
| `challan_number` | `challan_number` | `CharField(max_length=100)` |  | YES |  |
| `invoice_number` | `invoice_number` | `CharField(max_length=100)` |  | YES |  |
| `site_engineer` | `site_engineer` | `CharField(max_length=100)` |  | YES |  |
| `security_approval` | `security_approval` | `CharField(max_length=10)` |  | NO |  |
| `remarks` | `remarks` | `TextField` |  | YES |  |
| `inward_time` | `inward_time` | `DateTimeField` |  | NO |  |
| `created_by_id` | `created_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `created_at` | `created_at` | `DateTimeField` |  | NO |  |
| `updated_at` | `updated_at` | `DateTimeField` |  | NO |  |

#### `construction_gatein_constructionmaterialcategory`

Django model: `construction_gatein.ConstructionMaterialCategory`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `category_name` | `category_name` | `CharField(max_length=100)` | UNIQUE | NO |  |
| `description` | `description` | `TextField` |  | YES |  |
| `is_active` | `is_active` | `BooleanField` |  | NO |  |

### contenttypes

#### `django_content_type`

Django model: `contenttypes.ContentType`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `AutoField` | PK | NO |  |
| `app_label` | `app_label` | `CharField(max_length=100)` |  | NO |  |
| `model` | `model` | `CharField(max_length=100)` |  | NO |  |

### daily_needs_gatein

#### `daily_needs_gatein_categorylist`

Django model: `daily_needs_gatein.CategoryList`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `category_name` | `category_name` | `CharField(max_length=50)` | UNIQUE | NO |  |

#### `daily_needs_gatein_dailyneedgateentry`

Django model: `daily_needs_gatein.DailyNeedGateEntry`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `vehicle_entry_id` | `vehicle_entry` | `OneToOneField` | FK, UNIQUE | NO | driver_management_vehicleentry.id |
| `item_category_id` | `item_category` | `ForeignKey` | FK | YES | daily_needs_gatein_categorylist.id |
| `supplier_name` | `supplier_name` | `CharField(max_length=200)` |  | NO |  |
| `material_name` | `material_name` | `CharField(max_length=200)` |  | NO |  |
| `quantity` | `quantity` | `DecimalField(max_digits=10, decimal_places=2)` |  | NO |  |
| `unit_id` | `unit` | `ForeignKey` | FK | YES | gate_core_unitchoice.id |
| `receiving_department_id` | `receiving_department` | `ForeignKey` | FK | YES | accounts_department.id |
| `bill_number` | `bill_number` | `CharField(max_length=100)` |  | YES |  |
| `delivery_challan_number` | `delivery_challan_number` | `CharField(max_length=100)` |  | YES |  |
| `canteen_supervisor` | `canteen_supervisor` | `CharField(max_length=100)` |  | YES |  |
| `vehicle_or_person_name` | `vehicle_or_person_name` | `CharField(max_length=100)` |  | YES |  |
| `contact_number` | `contact_number` | `CharField(max_length=15)` |  | YES |  |
| `remarks` | `remarks` | `TextField` |  | YES |  |
| `created_by_id` | `created_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `created_at` | `created_at` | `DateTimeField` |  | NO |  |
| `updated_at` | `updated_at` | `DateTimeField` |  | NO |  |

### dispatch_plans

#### `dispatch_plans_dispatchplan`

Django model: `dispatch_plans.DispatchPlan`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `created_at` | `created_at` | `DateTimeField` |  | NO |  |
| `updated_at` | `updated_at` | `DateTimeField` |  | NO |  |
| `created_by_id` | `created_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `updated_by_id` | `updated_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `is_active` | `is_active` | `BooleanField` |  | NO |  |
| `company_id` | `company` | `ForeignKey` | FK | NO | company_company.id |
| `sap_invoice_doc_entry` | `sap_invoice_doc_entry` | `IntegerField` |  | NO |  |
| `sap_invoice_doc_num` | `sap_invoice_doc_num` | `CharField(max_length=30)` |  | NO |  |
| `vehicle_id` | `vehicle` | `ForeignKey` | FK | YES | vehicle_management_vehicle.id |
| `transporter_id` | `transporter` | `ForeignKey` | FK | YES | vehicle_management_transporter.id |
| `driver_id` | `driver` | `ForeignKey` | FK | YES | driver_management_driver.id |
| `linked_vehicle_entry_id` | `linked_vehicle_entry` | `ForeignKey` | FK | YES | driver_management_vehicleentry.id |
| `booking_status` | `booking_status` | `CharField(max_length=20)` |  | NO |  |
| `dispatch_date` | `dispatch_date` | `DateField` |  | YES |  |
| `priority` | `priority` | `CharField(max_length=50)` |  | NO |  |
| `transporter_name` | `transporter_name` | `CharField(max_length=150)` |  | NO |  |
| `transporter_gstin` | `transporter_gstin` | `CharField(max_length=20)` |  | NO |  |
| `contact_person` | `contact_person` | `CharField(max_length=100)` |  | NO |  |
| `mobile_no` | `mobile_no` | `CharField(max_length=50)` |  | NO |  |
| `vehicle_no` | `vehicle_no` | `CharField(max_length=30)` |  | NO |  |
| `driver_name` | `driver_name` | `CharField(max_length=100)` |  | NO |  |
| `driver_mobile_no` | `driver_mobile_no` | `CharField(max_length=50)` |  | NO |  |
| `driver_license_no` | `driver_license_no` | `CharField(max_length=50)` |  | NO |  |
| `driver_id_proof_type` | `driver_id_proof_type` | `CharField(max_length=50)` |  | NO |  |
| `driver_id_proof_number` | `driver_id_proof_number` | `CharField(max_length=50)` |  | NO |  |
| `bilty_no` | `bilty_no` | `CharField(max_length=50)` |  | NO |  |
| `bilty_date` | `bilty_date` | `DateField` |  | YES |  |
| `freight` | `freight` | `DecimalField(max_digits=18, decimal_places=2)` |  | YES |  |
| `total_freight` | `total_freight` | `DecimalField(max_digits=18, decimal_places=2)` |  | YES |  |
| `kanta_weight` | `kanta_weight` | `DecimalField(max_digits=18, decimal_places=3)` |  | YES |  |
| `remarks` | `remarks` | `TextField` |  | NO |  |

### django_apscheduler

#### `django_apscheduler_djangojob`

Django model: `django_apscheduler.DjangoJob`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `CharField(max_length=255)` | PK | NO |  |
| `next_run_time` | `next_run_time` | `DateTimeField` |  | YES |  |
| `job_state` | `job_state` | `BinaryField` |  | NO |  |

#### `django_apscheduler_djangojobexecution`

Django model: `django_apscheduler.DjangoJobExecution`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `job_id` | `job` | `ForeignKey` | FK | NO | django_apscheduler_djangojob.id |
| `status` | `status` | `CharField(max_length=50)` |  | NO |  |
| `run_time` | `run_time` | `DateTimeField` |  | NO |  |
| `duration` | `duration` | `DecimalField(max_digits=15, decimal_places=2)` |  | YES |  |
| `finished` | `finished` | `DecimalField(max_digits=15, decimal_places=2)` |  | YES |  |
| `exception` | `exception` | `CharField(max_length=1000)` |  | YES |  |
| `traceback` | `traceback` | `TextField` |  | YES |  |

### driver_management

#### `driver_management_driver`

Django model: `driver_management.Driver`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `created_at` | `created_at` | `DateTimeField` |  | NO |  |
| `updated_at` | `updated_at` | `DateTimeField` |  | NO |  |
| `created_by_id` | `created_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `updated_by_id` | `updated_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `is_active` | `is_active` | `BooleanField` |  | NO |  |
| `name` | `name` | `CharField(max_length=100)` |  | NO |  |
| `mobile_no` | `mobile_no` | `CharField(max_length=15)` |  | NO |  |
| `license_no` | `license_no` | `CharField(max_length=50)` | UNIQUE | NO |  |
| `id_proof_type` | `id_proof_type` | `CharField(max_length=50)` |  | NO |  |
| `id_proof_number` | `id_proof_number` | `CharField(max_length=50)` |  | NO |  |
| `photo` | `photo` | `FileField(max_length=100)` |  | YES |  |

#### `driver_management_vehicleentry`

Django model: `driver_management.VehicleEntry`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `created_at` | `created_at` | `DateTimeField` |  | NO |  |
| `updated_at` | `updated_at` | `DateTimeField` |  | NO |  |
| `is_active` | `is_active` | `BooleanField` |  | NO |  |
| `entry_no` | `entry_no` | `CharField(max_length=30)` | UNIQUE | NO |  |
| `status` | `status` | `CharField(max_length=30)` |  | NO |  |
| `is_locked` | `is_locked` | `BooleanField` |  | NO |  |
| `company_id` | `company` | `ForeignKey` | FK | NO | company_company.id |
| `vehicle_id` | `vehicle` | `ForeignKey` | FK | NO | vehicle_management_vehicle.id |
| `driver_id` | `driver` | `ForeignKey` | FK | NO | driver_management_driver.id |
| `entry_type` | `entry_type` | `CharField(max_length=20)` |  | NO |  |
| `created_by_id` | `created_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `updated_by_id` | `updated_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `entry_time` | `entry_time` | `DateTimeField` |  | NO |  |
| `remarks` | `remarks` | `TextField` |  | NO |  |

### gate_core

#### `gate_core_bstgatein`

Django model: `gate_core.BSTGateIn`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `created_at` | `created_at` | `DateTimeField` |  | NO |  |
| `updated_at` | `updated_at` | `DateTimeField` |  | NO |  |
| `created_by_id` | `created_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `updated_by_id` | `updated_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `is_active` | `is_active` | `BooleanField` |  | NO |  |
| `company_id` | `company` | `ForeignKey` | FK | NO | company_company.id |
| `entry_no` | `entry_no` | `CharField(max_length=50)` | UNIQUE | NO |  |
| `vehicle_entry_id` | `vehicle_entry` | `ForeignKey` | FK | NO | driver_management_vehicleentry.id |
| `bst_gate_out_id` | `bst_gate_out` | `ForeignKey` | FK | NO | gate_core_bstgateout.id |
| `vehicle_id` | `vehicle` | `ForeignKey` | FK | NO | vehicle_management_vehicle.id |
| `driver_id` | `driver` | `ForeignKey` | FK | NO | driver_management_driver.id |
| `gate_in_date` | `gate_in_date` | `DateField` |  | NO |  |
| `in_time` | `in_time` | `TimeField` |  | NO |  |
| `security_name` | `security_name` | `CharField(max_length=100)` |  | NO |  |
| `remarks` | `remarks` | `TextField` |  | NO |  |
| `status` | `status` | `CharField(max_length=20)` |  | NO |  |

#### `gate_core_bstgateinitem`

Django model: `gate_core.BSTGateInItem`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `created_at` | `created_at` | `DateTimeField` |  | NO |  |
| `updated_at` | `updated_at` | `DateTimeField` |  | NO |  |
| `created_by_id` | `created_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `updated_by_id` | `updated_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `is_active` | `is_active` | `BooleanField` |  | NO |  |
| `bst_gate_in_id` | `bst_gate_in` | `ForeignKey` | FK | NO | gate_core_bstgatein.id |
| `bst_gate_out_item_id` | `bst_gate_out_item` | `ForeignKey` | FK | NO | gate_core_bstgateoutitem.id |
| `line_num` | `line_num` | `IntegerField` |  | NO |  |
| `item_code` | `item_code` | `CharField(max_length=100)` |  | NO |  |
| `item_name` | `item_name` | `CharField(max_length=255)` |  | NO |  |
| `quantity` | `quantity` | `DecimalField(max_digits=18, decimal_places=3)` |  | NO |  |
| `actual_quantity` | `actual_quantity` | `DecimalField(max_digits=18, decimal_places=3)` |  | NO |  |
| `receiving_quantity` | `receiving_quantity` | `DecimalField(max_digits=18, decimal_places=3)` |  | NO |  |
| `uom` | `uom` | `CharField(max_length=50)` |  | NO |  |
| `from_warehouse` | `from_warehouse` | `CharField(max_length=50)` |  | NO |  |
| `to_warehouse` | `to_warehouse` | `CharField(max_length=50)` |  | NO |  |

#### `gate_core_bstgateout`

Django model: `gate_core.BSTGateOut`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `created_at` | `created_at` | `DateTimeField` |  | NO |  |
| `updated_at` | `updated_at` | `DateTimeField` |  | NO |  |
| `created_by_id` | `created_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `updated_by_id` | `updated_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `is_active` | `is_active` | `BooleanField` |  | NO |  |
| `company_id` | `company` | `ForeignKey` | FK | NO | company_company.id |
| `entry_no` | `entry_no` | `CharField(max_length=50)` | UNIQUE | NO |  |
| `vehicle_entry_id` | `vehicle_entry` | `ForeignKey` | FK | NO | driver_management_vehicleentry.id |
| `empty_vehicle_gate_in_id` | `empty_vehicle_gate_in` | `ForeignKey` | FK | NO | gate_core_emptyvehiclegatein.id |
| `vehicle_id` | `vehicle` | `ForeignKey` | FK | NO | vehicle_management_vehicle.id |
| `driver_id` | `driver` | `ForeignKey` | FK | NO | driver_management_driver.id |
| `sap_doc_entry` | `sap_doc_entry` | `IntegerField` |  | NO |  |
| `sap_doc_num` | `sap_doc_num` | `CharField(max_length=50)` |  | NO |  |
| `sap_doc_date` | `sap_doc_date` | `DateField` |  | YES |  |
| `sap_from_warehouse` | `sap_from_warehouse` | `CharField(max_length=50)` |  | NO |  |
| `sap_to_warehouse` | `sap_to_warehouse` | `CharField(max_length=50)` |  | NO |  |
| `sap_reference` | `sap_reference` | `CharField(max_length=100)` |  | NO |  |
| `sap_comments` | `sap_comments` | `TextField` |  | NO |  |
| `gate_out_date` | `gate_out_date` | `DateField` |  | NO |  |
| `out_time` | `out_time` | `TimeField` |  | NO |  |
| `security_name` | `security_name` | `CharField(max_length=100)` |  | NO |  |
| `remarks` | `remarks` | `TextField` |  | NO |  |
| `status` | `status` | `CharField(max_length=20)` |  | NO |  |
| `cancel_reason` | `cancel_reason` | `TextField` |  | NO |  |
| `cancelled_at` | `cancelled_at` | `DateTimeField` |  | YES |  |
| `cancelled_by_id` | `cancelled_by` | `ForeignKey` | FK | YES | accounts_user.id |

#### `gate_core_bstgateoutitem`

Django model: `gate_core.BSTGateOutItem`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `created_at` | `created_at` | `DateTimeField` |  | NO |  |
| `updated_at` | `updated_at` | `DateTimeField` |  | NO |  |
| `created_by_id` | `created_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `updated_by_id` | `updated_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `is_active` | `is_active` | `BooleanField` |  | NO |  |
| `bst_gate_out_id` | `bst_gate_out` | `ForeignKey` | FK | NO | gate_core_bstgateout.id |
| `line_num` | `line_num` | `IntegerField` |  | NO |  |
| `item_code` | `item_code` | `CharField(max_length=100)` |  | NO |  |
| `item_name` | `item_name` | `CharField(max_length=255)` |  | NO |  |
| `quantity` | `quantity` | `DecimalField(max_digits=18, decimal_places=3)` |  | NO |  |
| `actual_quantity` | `actual_quantity` | `DecimalField(max_digits=18, decimal_places=3)` |  | NO |  |
| `uom` | `uom` | `CharField(max_length=50)` |  | NO |  |
| `from_warehouse` | `from_warehouse` | `CharField(max_length=50)` |  | NO |  |
| `to_warehouse` | `to_warehouse` | `CharField(max_length=50)` |  | NO |  |

#### `gate_core_bstgatereturn`

Django model: `gate_core.BSTGateReturn`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `created_at` | `created_at` | `DateTimeField` |  | NO |  |
| `updated_at` | `updated_at` | `DateTimeField` |  | NO |  |
| `created_by_id` | `created_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `updated_by_id` | `updated_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `is_active` | `is_active` | `BooleanField` |  | NO |  |
| `company_id` | `company` | `ForeignKey` | FK | NO | company_company.id |
| `entry_no` | `entry_no` | `CharField(max_length=50)` | UNIQUE | NO |  |
| `vehicle_entry_id` | `vehicle_entry` | `ForeignKey` | FK | NO | driver_management_vehicleentry.id |
| `bst_gate_out_id` | `bst_gate_out` | `ForeignKey` | FK | NO | gate_core_bstgateout.id |
| `vehicle_id` | `vehicle` | `ForeignKey` | FK | NO | vehicle_management_vehicle.id |
| `driver_id` | `driver` | `ForeignKey` | FK | NO | driver_management_driver.id |
| `gate_in_date` | `gate_in_date` | `DateField` |  | NO |  |
| `in_time` | `in_time` | `TimeField` |  | NO |  |
| `security_name` | `security_name` | `CharField(max_length=100)` |  | NO |  |
| `remarks` | `remarks` | `TextField` |  | NO |  |
| `status` | `status` | `CharField(max_length=20)` |  | NO |  |

#### `gate_core_emptyvehiclegatein`

Django model: `gate_core.EmptyVehicleGateIn`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `created_at` | `created_at` | `DateTimeField` |  | NO |  |
| `updated_at` | `updated_at` | `DateTimeField` |  | NO |  |
| `created_by_id` | `created_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `updated_by_id` | `updated_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `is_active` | `is_active` | `BooleanField` |  | NO |  |
| `company_id` | `company` | `ForeignKey` | FK | NO | company_company.id |
| `entry_no` | `entry_no` | `CharField(max_length=50)` | UNIQUE | NO |  |
| `vehicle_entry_id` | `vehicle_entry` | `OneToOneField` | FK, UNIQUE | NO | driver_management_vehicleentry.id |
| `vehicle_id` | `vehicle` | `ForeignKey` | FK | NO | vehicle_management_vehicle.id |
| `driver_id` | `driver` | `ForeignKey` | FK | NO | driver_management_driver.id |
| `reason` | `reason` | `CharField(max_length=30)` |  | NO |  |
| `gate_in_date` | `gate_in_date` | `DateField` |  | NO |  |
| `in_time` | `in_time` | `TimeField` |  | NO |  |
| `sap_doc_entry` | `sap_doc_entry` | `IntegerField` |  | YES |  |
| `sap_doc_num` | `sap_doc_num` | `CharField(max_length=50)` |  | NO |  |
| `sap_doc_date` | `sap_doc_date` | `DateField` |  | YES |  |
| `sap_from_warehouse` | `sap_from_warehouse` | `CharField(max_length=50)` |  | NO |  |
| `sap_to_warehouse` | `sap_to_warehouse` | `CharField(max_length=50)` |  | NO |  |
| `sap_reference` | `sap_reference` | `CharField(max_length=100)` |  | NO |  |
| `sap_comments` | `sap_comments` | `TextField` |  | NO |  |
| `sap_line_count` | `sap_line_count` | `PositiveIntegerField` |  | NO |  |
| `sap_total_quantity` | `sap_total_quantity` | `DecimalField(max_digits=18, decimal_places=3)` |  | NO |  |
| `document_reference` | `document_reference` | `CharField(max_length=255)` |  | NO |  |
| `document_notes` | `document_notes` | `TextField` |  | NO |  |
| `security_name` | `security_name` | `CharField(max_length=100)` |  | NO |  |
| `remarks` | `remarks` | `TextField` |  | NO |  |

#### `gate_core_emptyvehiclegateinitem`

Django model: `gate_core.EmptyVehicleGateInItem`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `created_at` | `created_at` | `DateTimeField` |  | NO |  |
| `updated_at` | `updated_at` | `DateTimeField` |  | NO |  |
| `created_by_id` | `created_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `updated_by_id` | `updated_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `is_active` | `is_active` | `BooleanField` |  | NO |  |
| `empty_vehicle_gate_in_id` | `empty_vehicle_gate_in` | `ForeignKey` | FK | NO | gate_core_emptyvehiclegatein.id |
| `line_num` | `line_num` | `IntegerField` |  | NO |  |
| `item_code` | `item_code` | `CharField(max_length=100)` |  | NO |  |
| `item_name` | `item_name` | `CharField(max_length=255)` |  | NO |  |
| `sap_quantity` | `sap_quantity` | `DecimalField(max_digits=18, decimal_places=3)` |  | NO |  |
| `actual_quantity` | `actual_quantity` | `DecimalField(max_digits=18, decimal_places=3)` |  | NO |  |
| `uom` | `uom` | `CharField(max_length=50)` |  | NO |  |
| `from_warehouse` | `from_warehouse` | `CharField(max_length=50)` |  | NO |  |
| `to_warehouse` | `to_warehouse` | `CharField(max_length=50)` |  | NO |  |

#### `gate_core_emptyvehiclegateout`

Django model: `gate_core.EmptyVehicleGateOut`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `created_at` | `created_at` | `DateTimeField` |  | NO |  |
| `updated_at` | `updated_at` | `DateTimeField` |  | NO |  |
| `created_by_id` | `created_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `updated_by_id` | `updated_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `is_active` | `is_active` | `BooleanField` |  | NO |  |
| `company_id` | `company` | `ForeignKey` | FK | NO | company_company.id |
| `entry_no` | `entry_no` | `CharField(max_length=50)` | UNIQUE | NO |  |
| `vehicle_entry_id` | `vehicle_entry` | `ForeignKey` | FK | NO | driver_management_vehicleentry.id |
| `vehicle_id` | `vehicle` | `ForeignKey` | FK | NO | vehicle_management_vehicle.id |
| `driver_id` | `driver` | `ForeignKey` | FK | NO | driver_management_driver.id |
| `gate_out_date` | `gate_out_date` | `DateField` |  | NO |  |
| `out_time` | `out_time` | `TimeField` |  | NO |  |
| `security_name` | `security_name` | `CharField(max_length=100)` |  | NO |  |
| `remarks` | `remarks` | `TextField` |  | NO |  |
| `status` | `status` | `CharField(max_length=20)` |  | NO |  |
| `cancel_reason` | `cancel_reason` | `TextField` |  | NO |  |
| `cancelled_at` | `cancelled_at` | `DateTimeField` |  | YES |  |
| `cancelled_by_id` | `cancelled_by` | `ForeignKey` | FK | YES | accounts_user.id |

#### `gate_core_gateattachment`

Django model: `gate_core.GateAttachment`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `gate_entry_id` | `gate_entry` | `ForeignKey` | FK | NO | driver_management_vehicleentry.id |
| `file` | `file` | `FileField(max_length=100)` |  | NO |  |
| `uploaded_at` | `uploaded_at` | `DateTimeField` |  | NO |  |

#### `gate_core_jobworkgatein`

Django model: `gate_core.JobWorkGateIn`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `created_at` | `created_at` | `DateTimeField` |  | NO |  |
| `updated_at` | `updated_at` | `DateTimeField` |  | NO |  |
| `created_by_id` | `created_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `updated_by_id` | `updated_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `is_active` | `is_active` | `BooleanField` |  | NO |  |
| `company_id` | `company` | `ForeignKey` | FK | NO | company_company.id |
| `entry_no` | `entry_no` | `CharField(max_length=50)` | UNIQUE | NO |  |
| `vehicle_entry_id` | `vehicle_entry` | `ForeignKey` | FK | NO | driver_management_vehicleentry.id |
| `vehicle_id` | `vehicle` | `ForeignKey` | FK | NO | vehicle_management_vehicle.id |
| `driver_id` | `driver` | `ForeignKey` | FK | NO | driver_management_driver.id |
| `sap_doc_entry` | `sap_doc_entry` | `IntegerField` |  | YES |  |
| `sap_doc_num` | `sap_doc_num` | `CharField(max_length=50)` |  | NO |  |
| `sap_doc_date` | `sap_doc_date` | `DateField` |  | YES |  |
| `sap_doc_time` | `sap_doc_time` | `TimeField` |  | YES |  |
| `sap_supplier_code` | `sap_supplier_code` | `CharField(max_length=50)` |  | NO |  |
| `sap_supplier_name` | `sap_supplier_name` | `CharField(max_length=255)` |  | NO |  |
| `sap_reference` | `sap_reference` | `CharField(max_length=100)` |  | NO |  |
| `sap_comments` | `sap_comments` | `TextField` |  | NO |  |
| `sap_branch_id` | `sap_branch_id` | `IntegerField` |  | YES |  |
| `production_order_doc_entry` | `production_order_doc_entry` | `IntegerField` |  | YES |  |
| `production_order_doc_num` | `production_order_doc_num` | `CharField(max_length=50)` |  | NO |  |
| `production_item_code` | `production_item_code` | `CharField(max_length=100)` |  | NO |  |
| `production_item_name` | `production_item_name` | `CharField(max_length=255)` |  | NO |  |
| `production_planned_qty` | `production_planned_qty` | `DecimalField(max_digits=18, decimal_places=3)` |  | YES |  |
| `production_completed_qty` | `production_completed_qty` | `DecimalField(max_digits=18, decimal_places=3)` |  | YES |  |
| `production_rejected_qty` | `production_rejected_qty` | `DecimalField(max_digits=18, decimal_places=3)` |  | YES |  |
| `production_remaining_qty` | `production_remaining_qty` | `DecimalField(max_digits=18, decimal_places=3)` |  | YES |  |
| `production_start_date` | `production_start_date` | `DateField` |  | YES |  |
| `production_due_date` | `production_due_date` | `DateField` |  | YES |  |
| `production_warehouse` | `production_warehouse` | `CharField(max_length=50)` |  | NO |  |
| `production_status` | `production_status` | `CharField(max_length=20)` |  | NO |  |
| `gate_in_date` | `gate_in_date` | `DateField` |  | NO |  |
| `in_time` | `in_time` | `TimeField` |  | NO |  |
| `security_name` | `security_name` | `CharField(max_length=100)` |  | NO |  |
| `remarks` | `remarks` | `TextField` |  | NO |  |
| `status` | `status` | `CharField(max_length=20)` |  | NO |  |

#### `gate_core_jobworkgateinitem`

Django model: `gate_core.JobWorkGateInItem`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `created_at` | `created_at` | `DateTimeField` |  | NO |  |
| `updated_at` | `updated_at` | `DateTimeField` |  | NO |  |
| `created_by_id` | `created_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `updated_by_id` | `updated_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `is_active` | `is_active` | `BooleanField` |  | NO |  |
| `job_work_gate_in_id` | `job_work_gate_in` | `ForeignKey` | FK | NO | gate_core_jobworkgatein.id |
| `line_num` | `line_num` | `IntegerField` |  | NO |  |
| `item_code` | `item_code` | `CharField(max_length=100)` |  | NO |  |
| `item_name` | `item_name` | `CharField(max_length=255)` |  | NO |  |
| `quantity` | `quantity` | `DecimalField(max_digits=18, decimal_places=3)` |  | NO |  |
| `uom` | `uom` | `CharField(max_length=50)` |  | NO |  |
| `warehouse_code` | `warehouse_code` | `CharField(max_length=50)` |  | NO |  |
| `base_type` | `base_type` | `IntegerField` |  | YES |  |
| `base_entry` | `base_entry` | `IntegerField` |  | YES |  |
| `base_line` | `base_line` | `IntegerField` |  | YES |  |

#### `gate_core_rejectedqcreturnentry`

Django model: `gate_core.RejectedQCReturnEntry`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `created_at` | `created_at` | `DateTimeField` |  | NO |  |
| `updated_at` | `updated_at` | `DateTimeField` |  | NO |  |
| `created_by_id` | `created_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `updated_by_id` | `updated_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `is_active` | `is_active` | `BooleanField` |  | NO |  |
| `company_id` | `company` | `ForeignKey` | FK | NO | company_company.id |
| `entry_no` | `entry_no` | `CharField(max_length=50)` | UNIQUE | NO |  |
| `vehicle_id` | `vehicle` | `ForeignKey` | FK | NO | vehicle_management_vehicle.id |
| `driver_id` | `driver` | `ForeignKey` | FK | NO | driver_management_driver.id |
| `gate_out_date` | `gate_out_date` | `DateField` |  | NO |  |
| `out_time` | `out_time` | `TimeField` |  | YES |  |
| `challan_no` | `challan_no` | `CharField(max_length=100)` |  | NO |  |
| `eway_bill_no` | `eway_bill_no` | `CharField(max_length=100)` |  | NO |  |
| `manual_sap_reference` | `manual_sap_reference` | `CharField(max_length=100)` |  | NO |  |
| `security_name` | `security_name` | `CharField(max_length=100)` |  | NO |  |
| `gross_weight` | `gross_weight` | `DecimalField(max_digits=12, decimal_places=3)` |  | YES |  |
| `tare_weight` | `tare_weight` | `DecimalField(max_digits=12, decimal_places=3)` |  | YES |  |
| `net_weight` | `net_weight` | `DecimalField(max_digits=12, decimal_places=3)` |  | YES |  |
| `weighbridge_slip_no` | `weighbridge_slip_no` | `CharField(max_length=50)` |  | NO |  |
| `first_weighment_time` | `first_weighment_time` | `DateTimeField` |  | YES |  |
| `second_weighment_time` | `second_weighment_time` | `DateTimeField` |  | YES |  |
| `gatepass_documents` | `gatepass_documents` | `JSONField` |  | NO |  |
| `remarks` | `remarks` | `TextField` |  | NO |  |
| `status` | `status` | `CharField(max_length=20)` |  | NO |  |

#### `gate_core_rejectedqcreturnitem`

Django model: `gate_core.RejectedQCReturnItem`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `created_at` | `created_at` | `DateTimeField` |  | NO |  |
| `updated_at` | `updated_at` | `DateTimeField` |  | NO |  |
| `created_by_id` | `created_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `updated_by_id` | `updated_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `is_active` | `is_active` | `BooleanField` |  | NO |  |
| `entry_id` | `entry` | `ForeignKey` | FK | NO | gate_core_rejectedqcreturnentry.id |
| `inspection_id` | `inspection` | `OneToOneField` | FK, UNIQUE | NO | quality_control_rawmaterialinspection.id |
| `gate_entry_no` | `gate_entry_no` | `CharField(max_length=50)` |  | NO |  |
| `report_no` | `report_no` | `CharField(max_length=50)` |  | NO |  |
| `internal_lot_no` | `internal_lot_no` | `CharField(max_length=50)` |  | NO |  |
| `item_name` | `item_name` | `CharField(max_length=255)` |  | NO |  |
| `supplier_name` | `supplier_name` | `CharField(max_length=200)` |  | NO |  |
| `quantity` | `quantity` | `DecimalField(max_digits=12, decimal_places=3)` |  | YES |  |
| `uom` | `uom` | `CharField(max_length=20)` |  | NO |  |

#### `gate_core_unitchoice`

Django model: `gate_core.UnitChoice`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `name` | `name` | `CharField(max_length=50)` | UNIQUE | NO |  |

### grpo

#### `grpo_grpoattachment`

Django model: `grpo.GRPOAttachment`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `grpo_posting_id` | `grpo_posting` | `ForeignKey` | FK | NO | grpo_grpoposting.id |
| `file` | `file` | `FileField(max_length=100)` |  | NO |  |
| `original_filename` | `original_filename` | `CharField(max_length=255)` |  | NO |  |
| `sap_attachment_status` | `sap_attachment_status` | `CharField(max_length=20)` |  | NO |  |
| `sap_absolute_entry` | `sap_absolute_entry` | `IntegerField` |  | YES |  |
| `sap_error_message` | `sap_error_message` | `TextField` |  | YES |  |
| `uploaded_at` | `uploaded_at` | `DateTimeField` |  | NO |  |
| `uploaded_by_id` | `uploaded_by` | `ForeignKey` | FK | YES | accounts_user.id |

#### `grpo_grpolineposting`

Django model: `grpo.GRPOLinePosting`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `grpo_posting_id` | `grpo_posting` | `ForeignKey` | FK | NO | grpo_grpoposting.id |
| `po_item_receipt_id` | `po_item_receipt` | `ForeignKey` | FK | NO | raw_material_gatein_poitemreceipt.id |
| `quantity_posted` | `quantity_posted` | `DecimalField(max_digits=12, decimal_places=3)` |  | NO |  |
| `base_entry` | `base_entry` | `IntegerField` |  | YES |  |
| `base_line` | `base_line` | `IntegerField` |  | YES |  |

#### `grpo_grpoposting`

Django model: `grpo.GRPOPosting`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `vehicle_entry_id` | `vehicle_entry` | `ForeignKey` | FK | NO | driver_management_vehicleentry.id |
| `po_receipt_id` | `po_receipt` | `ForeignKey` | FK | YES | raw_material_gatein_poreceipt.id |
| `sap_doc_entry` | `sap_doc_entry` | `IntegerField` |  | YES |  |
| `sap_doc_num` | `sap_doc_num` | `IntegerField` |  | YES |  |
| `sap_doc_total` | `sap_doc_total` | `DecimalField(max_digits=18, decimal_places=2)` |  | YES |  |
| `status` | `status` | `CharField(max_length=20)` |  | NO |  |
| `error_message` | `error_message` | `TextField` |  | YES |  |
| `posted_at` | `posted_at` | `DateTimeField` |  | YES |  |
| `posted_by_id` | `posted_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `created_at` | `created_at` | `DateTimeField` |  | NO |  |
| `updated_at` | `updated_at` | `DateTimeField` |  | NO |  |

#### `grpo_grpoposting_po_receipts` (implicit join table)

Django model: `grpo.GRPOPosting_po_receipts`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `grpoposting_id` | `grpoposting` | `ForeignKey` | FK | NO | grpo_grpoposting.id |
| `poreceipt_id` | `poreceipt` | `ForeignKey` | FK | NO | raw_material_gatein_poreceipt.id |

#### `grpo_servicegrpoattachment`

Django model: `grpo.ServiceGRPOAttachment`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `service_grpo_posting_id` | `service_grpo_posting` | `ForeignKey` | FK | NO | grpo_servicegrpoposting.id |
| `file` | `file` | `FileField(max_length=100)` |  | NO |  |
| `original_filename` | `original_filename` | `CharField(max_length=255)` |  | NO |  |
| `sap_attachment_status` | `sap_attachment_status` | `CharField(max_length=20)` |  | NO |  |
| `sap_absolute_entry` | `sap_absolute_entry` | `IntegerField` |  | YES |  |
| `sap_error_message` | `sap_error_message` | `TextField` |  | YES |  |
| `uploaded_at` | `uploaded_at` | `DateTimeField` |  | NO |  |
| `uploaded_by_id` | `uploaded_by` | `ForeignKey` | FK | YES | accounts_user.id |

#### `grpo_servicegrpolineposting`

Django model: `grpo.ServiceGRPOLinePosting`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `service_grpo_posting_id` | `service_grpo_posting` | `ForeignKey` | FK | NO | grpo_servicegrpoposting.id |
| `service_description` | `service_description` | `CharField(max_length=255)` |  | NO |  |
| `amount` | `amount` | `DecimalField(max_digits=18, decimal_places=2)` |  | NO |  |
| `tax_code` | `tax_code` | `CharField(max_length=50)` |  | NO |  |
| `gl_account` | `gl_account` | `CharField(max_length=50)` |  | NO |  |

#### `grpo_servicegrpoposting`

Django model: `grpo.ServiceGRPOPosting`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `dispatch_plan_id` | `dispatch_plan` | `ForeignKey` | FK | NO | dispatch_plans_dispatchplan.id |
| `vendor_code` | `vendor_code` | `CharField(max_length=50)` |  | NO |  |
| `vendor_name` | `vendor_name` | `CharField(max_length=150)` |  | NO |  |
| `sap_doc_entry` | `sap_doc_entry` | `IntegerField` |  | YES |  |
| `sap_doc_num` | `sap_doc_num` | `IntegerField` |  | YES |  |
| `sap_doc_total` | `sap_doc_total` | `DecimalField(max_digits=18, decimal_places=2)` |  | YES |  |
| `status` | `status` | `CharField(max_length=20)` |  | NO |  |
| `error_message` | `error_message` | `TextField` |  | YES |  |
| `posted_at` | `posted_at` | `DateTimeField` |  | YES |  |
| `posted_by_id` | `posted_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `created_at` | `created_at` | `DateTimeField` |  | NO |  |
| `updated_at` | `updated_at` | `DateTimeField` |  | NO |  |

### maintenance_gatein

#### `maintenance_gatein_maintenancegateentry`

Django model: `maintenance_gatein.MaintenanceGateEntry`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `vehicle_entry_id` | `vehicle_entry` | `OneToOneField` | FK, UNIQUE | NO | driver_management_vehicleentry.id |
| `maintenance_type_id` | `maintenance_type` | `ForeignKey` | FK | YES | maintenance_gatein_maintenancetype.id |
| `work_order_number` | `work_order_number` | `CharField(max_length=20)` | UNIQUE | YES |  |
| `supplier_name` | `supplier_name` | `CharField(max_length=200)` |  | NO |  |
| `material_description` | `material_description` | `TextField` |  | NO |  |
| `part_number` | `part_number` | `CharField(max_length=100)` |  | YES |  |
| `quantity` | `quantity` | `DecimalField(max_digits=10, decimal_places=2)` |  | NO |  |
| `unit_id` | `unit` | `ForeignKey` | FK | YES | gate_core_unitchoice.id |
| `invoice_number` | `invoice_number` | `CharField(max_length=100)` |  | YES |  |
| `equipment_id` | `equipment_id` | `CharField(max_length=100)` |  | YES |  |
| `receiving_department_id` | `receiving_department` | `ForeignKey` | FK | YES | accounts_department.id |
| `urgency_level` | `urgency_level` | `CharField(max_length=10)` |  | NO |  |
| `inward_time` | `inward_time` | `DateTimeField` |  | NO |  |
| `remarks` | `remarks` | `TextField` |  | YES |  |
| `created_by_id` | `created_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `created_at` | `created_at` | `DateTimeField` |  | NO |  |
| `updated_at` | `updated_at` | `DateTimeField` |  | NO |  |

#### `maintenance_gatein_maintenancetype`

Django model: `maintenance_gatein.MaintenanceType`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `type_name` | `type_name` | `CharField(max_length=100)` | UNIQUE | NO |  |
| `description` | `description` | `TextField` |  | YES |  |
| `is_active` | `is_active` | `BooleanField` |  | NO |  |

### notifications

#### `notifications_notification`

Django model: `notifications.Notification`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `recipient_id` | `recipient` | `ForeignKey` | FK | NO | accounts_user.id |
| `company_id` | `company` | `ForeignKey` | FK | YES | company_company.id |
| `title` | `title` | `CharField(max_length=255)` |  | NO |  |
| `body` | `body` | `TextField` |  | NO |  |
| `notification_type` | `notification_type` | `CharField(max_length=50)` |  | NO |  |
| `click_action_url` | `click_action_url` | `CharField(max_length=500)` |  | NO |  |
| `reference_type` | `reference_type` | `CharField(max_length=50)` |  | NO |  |
| `reference_id` | `reference_id` | `IntegerField` |  | YES |  |
| `is_read` | `is_read` | `BooleanField` |  | NO |  |
| `read_at` | `read_at` | `DateTimeField` |  | YES |  |
| `extra_data` | `extra_data` | `JSONField` |  | NO |  |
| `created_at` | `created_at` | `DateTimeField` |  | NO |  |
| `created_by_id` | `created_by` | `ForeignKey` | FK | YES | accounts_user.id |

#### `notifications_userdevice`

Django model: `notifications.UserDevice`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `user_id` | `user` | `ForeignKey` | FK | NO | accounts_user.id |
| `fcm_token` | `fcm_token` | `TextField` | UNIQUE | NO |  |
| `device_type` | `device_type` | `CharField(max_length=20)` |  | NO |  |
| `device_info` | `device_info` | `CharField(max_length=255)` |  | NO |  |
| `is_active` | `is_active` | `BooleanField` |  | NO |  |
| `created_at` | `created_at` | `DateTimeField` |  | NO |  |
| `last_used_at` | `last_used_at` | `DateTimeField` |  | NO |  |

### person_gatein

#### `person_gatein_contractor`

Django model: `person_gatein.Contractor`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `contractor_name` | `contractor_name` | `CharField(max_length=150)` |  | NO |  |
| `contact_person` | `contact_person` | `CharField(max_length=100)` |  | YES |  |
| `mobile` | `mobile` | `CharField(max_length=20)` |  | YES |  |
| `address` | `address` | `TextField` |  | YES |  |
| `contract_valid_till` | `contract_valid_till` | `DateField` |  | YES |  |
| `is_active` | `is_active` | `BooleanField` |  | NO |  |

#### `person_gatein_entrylog`

Django model: `person_gatein.EntryLog`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `person_type_id` | `person_type` | `ForeignKey` | FK | NO | person_gatein_persontype.id |
| `visitor_id` | `visitor` | `ForeignKey` | FK | YES | person_gatein_visitor.id |
| `labour_id` | `labour` | `ForeignKey` | FK | YES | person_gatein_labour.id |
| `name_snapshot` | `name_snapshot` | `CharField(max_length=150)` |  | NO |  |
| `photo_snapshot` | `photo_snapshot` | `FileField(max_length=100)` |  | YES |  |
| `gate_in_id` | `gate_in` | `ForeignKey` | FK | NO | person_gatein_gate.id |
| `gate_out_id` | `gate_out` | `ForeignKey` | FK | YES | person_gatein_gate.id |
| `entry_time` | `entry_time` | `DateTimeField` |  | NO |  |
| `actual_entry_time` | `actual_entry_time` | `DateTimeField` |  | YES |  |
| `exit_time` | `exit_time` | `DateTimeField` |  | YES |  |
| `purpose` | `purpose` | `CharField(max_length=255)` |  | YES |  |
| `approved_by_id` | `approved_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `vehicle_no` | `vehicle_no` | `CharField(max_length=50)` |  | YES |  |
| `remarks` | `remarks` | `TextField` |  | YES |  |
| `status` | `status` | `CharField(max_length=10)` |  | NO |  |
| `created_by_id` | `created_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `created_at` | `created_at` | `DateTimeField` |  | NO |  |
| `updated_at` | `updated_at` | `DateTimeField` |  | NO |  |

#### `person_gatein_gate`

Django model: `person_gatein.Gate`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `name` | `name` | `CharField(max_length=100)` |  | NO |  |
| `location` | `location` | `CharField(max_length=150)` |  | YES |  |
| `is_active` | `is_active` | `BooleanField` |  | NO |  |

#### `person_gatein_labour`

Django model: `person_gatein.Labour`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `name` | `name` | `CharField(max_length=150)` |  | NO |  |
| `contractor_id` | `contractor` | `ForeignKey` | FK | NO | person_gatein_contractor.id |
| `mobile` | `mobile` | `CharField(max_length=20)` |  | YES |  |
| `id_proof_no` | `id_proof_no` | `CharField(max_length=100)` |  | YES |  |
| `photo` | `photo` | `FileField(max_length=100)` |  | YES |  |
| `skill_type` | `skill_type` | `CharField(max_length=100)` |  | YES |  |
| `permit_valid_till` | `permit_valid_till` | `DateField` |  | YES |  |
| `is_active` | `is_active` | `BooleanField` |  | NO |  |

#### `person_gatein_persontype`

Django model: `person_gatein.PersonType`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `name` | `name` | `CharField(max_length=50)` | UNIQUE | NO |  |
| `is_active` | `is_active` | `BooleanField` |  | NO |  |

#### `person_gatein_visitor`

Django model: `person_gatein.Visitor`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `name` | `name` | `CharField(max_length=150)` |  | NO |  |
| `mobile` | `mobile` | `CharField(max_length=20)` |  | YES |  |
| `company_name` | `company_name` | `CharField(max_length=150)` |  | YES |  |
| `id_proof_type` | `id_proof_type` | `CharField(max_length=50)` |  | YES |  |
| `id_proof_no` | `id_proof_no` | `CharField(max_length=100)` |  | YES |  |
| `photo` | `photo` | `FileField(max_length=100)` |  | YES |  |
| `blacklisted` | `blacklisted` | `BooleanField` |  | NO |  |
| `created_at` | `created_at` | `DateTimeField` |  | NO |  |

### production_execution

#### `production_execution_breakdowncategory`

Django model: `production_execution.BreakdownCategory`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `company_id` | `company` | `ForeignKey` | FK | NO | company_company.id |
| `name` | `name` | `CharField(max_length=100)` |  | NO |  |
| `is_active` | `is_active` | `BooleanField` |  | NO |  |
| `created_at` | `created_at` | `DateTimeField` |  | NO |  |
| `updated_at` | `updated_at` | `DateTimeField` |  | NO |  |

#### `production_execution_finalqccheck`

Django model: `production_execution.FinalQCCheck`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `production_run_id` | `production_run` | `OneToOneField` | FK, UNIQUE | NO | production_execution_productionrun.id |
| `checked_at` | `checked_at` | `DateTimeField` |  | NO |  |
| `overall_result` | `overall_result` | `CharField(max_length=15)` |  | NO |  |
| `parameters` | `parameters` | `JSONField` |  | NO |  |
| `remarks` | `remarks` | `TextField` |  | NO |  |
| `checked_by_id` | `checked_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `created_at` | `created_at` | `DateTimeField` |  | NO |  |
| `updated_at` | `updated_at` | `DateTimeField` |  | NO |  |

#### `production_execution_inprocessqccheck`

Django model: `production_execution.InProcessQCCheck`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `production_run_id` | `production_run` | `ForeignKey` | FK | NO | production_execution_productionrun.id |
| `checked_at` | `checked_at` | `DateTimeField` |  | NO |  |
| `parameter` | `parameter` | `CharField(max_length=200)` |  | NO |  |
| `acceptable_min` | `acceptable_min` | `DecimalField(max_digits=10, decimal_places=3)` |  | YES |  |
| `acceptable_max` | `acceptable_max` | `DecimalField(max_digits=10, decimal_places=3)` |  | YES |  |
| `actual_value` | `actual_value` | `DecimalField(max_digits=10, decimal_places=3)` |  | YES |  |
| `result` | `result` | `CharField(max_length=10)` |  | NO |  |
| `remarks` | `remarks` | `TextField` |  | NO |  |
| `checked_by_id` | `checked_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `created_at` | `created_at` | `DateTimeField` |  | NO |  |
| `updated_at` | `updated_at` | `DateTimeField` |  | NO |  |

#### `production_execution_lineclearance`

Django model: `production_execution.LineClearance`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `company_id` | `company` | `ForeignKey` | FK | NO | company_company.id |
| `production_run_id` | `production_run` | `ForeignKey` | FK | YES | production_execution_productionrun.id |
| `date` | `date` | `DateField` |  | NO |  |
| `line_id` | `line` | `ForeignKey` | FK | NO | production_execution_productionline.id |
| `document_id` | `document_id` | `CharField(max_length=50)` |  | NO |  |
| `verified_by_id` | `verified_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `qa_approved` | `qa_approved` | `BooleanField` |  | NO |  |
| `qa_approved_by_id` | `qa_approved_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `qa_approved_at` | `qa_approved_at` | `DateTimeField` |  | YES |  |
| `production_supervisor_sign` | `production_supervisor_sign` | `CharField(max_length=200)` |  | NO |  |
| `production_incharge_sign` | `production_incharge_sign` | `CharField(max_length=200)` |  | NO |  |
| `status` | `status` | `CharField(max_length=20)` |  | NO |  |
| `created_by_id` | `created_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `created_at` | `created_at` | `DateTimeField` |  | NO |  |
| `updated_at` | `updated_at` | `DateTimeField` |  | NO |  |

#### `production_execution_lineclearanceitem`

Django model: `production_execution.LineClearanceItem`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `clearance_id` | `clearance` | `ForeignKey` | FK | NO | production_execution_lineclearance.id |
| `checkpoint` | `checkpoint` | `CharField(max_length=500)` |  | NO |  |
| `sort_order` | `sort_order` | `PositiveIntegerField` |  | NO |  |
| `result` | `result` | `CharField(max_length=5)` |  | NO |  |
| `remarks` | `remarks` | `TextField` |  | NO |  |

#### `production_execution_lineskuconfig`

Django model: `production_execution.LineSkuConfig`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `company_id` | `company` | `ForeignKey` | FK | NO | company_company.id |
| `line_id` | `line` | `ForeignKey` | FK | NO | production_execution_productionline.id |
| `config_name` | `config_name` | `CharField(max_length=300)` |  | NO |  |
| `sku_code` | `sku_code` | `CharField(max_length=100)` |  | NO |  |
| `sku_name` | `sku_name` | `CharField(max_length=300)` |  | NO |  |
| `rated_speed` | `rated_speed` | `DecimalField(max_digits=10, decimal_places=2)` |  | YES |  |
| `labour_count` | `labour_count` | `PositiveIntegerField` |  | NO |  |
| `other_manpower_count` | `other_manpower_count` | `PositiveIntegerField` |  | NO |  |
| `supervisor` | `supervisor` | `CharField(max_length=200)` |  | NO |  |
| `operators` | `operators` | `CharField(max_length=500)` |  | NO |  |
| `is_active` | `is_active` | `BooleanField` |  | NO |  |
| `created_at` | `created_at` | `DateTimeField` |  | NO |  |
| `updated_at` | `updated_at` | `DateTimeField` |  | NO |  |

#### `production_execution_machine`

Django model: `production_execution.Machine`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `company_id` | `company` | `ForeignKey` | FK | NO | company_company.id |
| `name` | `name` | `CharField(max_length=200)` |  | NO |  |
| `machine_type` | `machine_type` | `CharField(max_length=30)` |  | NO |  |
| `line_id` | `line` | `ForeignKey` | FK | NO | production_execution_productionline.id |
| `is_active` | `is_active` | `BooleanField` |  | NO |  |
| `created_at` | `created_at` | `DateTimeField` |  | NO |  |
| `updated_at` | `updated_at` | `DateTimeField` |  | NO |  |

#### `production_execution_machinebreakdown`

Django model: `production_execution.MachineBreakdown`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `production_run_id` | `production_run` | `ForeignKey` | FK | NO | production_execution_productionrun.id |
| `machine_id` | `machine` | `ForeignKey` | FK | NO | production_execution_machine.id |
| `start_time` | `start_time` | `DateTimeField` |  | NO |  |
| `end_time` | `end_time` | `DateTimeField` |  | YES |  |
| `breakdown_minutes` | `breakdown_minutes` | `PositiveIntegerField` |  | NO |  |
| `breakdown_category_id` | `breakdown_category` | `ForeignKey` | FK | YES | production_execution_breakdowncategory.id |
| `is_active` | `is_active` | `BooleanField` |  | NO |  |
| `is_unrecovered` | `is_unrecovered` | `BooleanField` |  | NO |  |
| `reason` | `reason` | `CharField(max_length=500)` |  | NO |  |
| `remarks` | `remarks` | `TextField` |  | NO |  |
| `created_at` | `created_at` | `DateTimeField` |  | NO |  |
| `updated_at` | `updated_at` | `DateTimeField` |  | NO |  |

#### `production_execution_machinechecklistentry`

Django model: `production_execution.MachineChecklistEntry`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `company_id` | `company` | `ForeignKey` | FK | NO | company_company.id |
| `machine_id` | `machine` | `ForeignKey` | FK | NO | production_execution_machine.id |
| `machine_type` | `machine_type` | `CharField(max_length=30)` |  | NO |  |
| `date` | `date` | `DateField` |  | NO |  |
| `month` | `month` | `PositiveSmallIntegerField` |  | NO |  |
| `year` | `year` | `PositiveSmallIntegerField` |  | NO |  |
| `template_id` | `template` | `ForeignKey` | FK | NO | production_execution_machinechecklisttemplate.id |
| `task_description` | `task_description` | `CharField(max_length=500)` |  | NO |  |
| `frequency` | `frequency` | `CharField(max_length=10)` |  | NO |  |
| `status` | `status` | `CharField(max_length=10)` |  | NO |  |
| `operator` | `operator` | `CharField(max_length=200)` |  | NO |  |
| `shift_incharge` | `shift_incharge` | `CharField(max_length=200)` |  | NO |  |
| `remarks` | `remarks` | `TextField` |  | NO |  |
| `created_at` | `created_at` | `DateTimeField` |  | NO |  |
| `updated_at` | `updated_at` | `DateTimeField` |  | NO |  |

#### `production_execution_machinechecklisttemplate`

Django model: `production_execution.MachineChecklistTemplate`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `company_id` | `company` | `ForeignKey` | FK | NO | company_company.id |
| `machine_type` | `machine_type` | `CharField(max_length=30)` |  | NO |  |
| `task` | `task` | `CharField(max_length=500)` |  | NO |  |
| `frequency` | `frequency` | `CharField(max_length=10)` |  | NO |  |
| `sort_order` | `sort_order` | `PositiveIntegerField` |  | NO |  |
| `is_active` | `is_active` | `BooleanField` |  | NO |  |
| `created_at` | `created_at` | `DateTimeField` |  | NO |  |
| `updated_at` | `updated_at` | `DateTimeField` |  | NO |  |

#### `production_execution_machineruntime`

Django model: `production_execution.MachineRuntime`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `production_run_id` | `production_run` | `ForeignKey` | FK | NO | production_execution_productionrun.id |
| `machine_id` | `machine` | `ForeignKey` | FK | YES | production_execution_machine.id |
| `machine_type` | `machine_type` | `CharField(max_length=30)` |  | NO |  |
| `runtime_minutes` | `runtime_minutes` | `PositiveIntegerField` |  | NO |  |
| `downtime_minutes` | `downtime_minutes` | `PositiveIntegerField` |  | NO |  |
| `remarks` | `remarks` | `TextField` |  | NO |  |
| `created_at` | `created_at` | `DateTimeField` |  | NO |  |
| `updated_at` | `updated_at` | `DateTimeField` |  | NO |  |

#### `production_execution_productionline`

Django model: `production_execution.ProductionLine`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `company_id` | `company` | `ForeignKey` | FK | NO | company_company.id |
| `name` | `name` | `CharField(max_length=100)` |  | NO |  |
| `description` | `description` | `TextField` |  | NO |  |
| `is_active` | `is_active` | `BooleanField` |  | NO |  |
| `created_at` | `created_at` | `DateTimeField` |  | NO |  |
| `updated_at` | `updated_at` | `DateTimeField` |  | NO |  |

#### `production_execution_productionmanpower`

Django model: `production_execution.ProductionManpower`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `production_run_id` | `production_run` | `ForeignKey` | FK | NO | production_execution_productionrun.id |
| `shift` | `shift` | `CharField(max_length=20)` |  | NO |  |
| `worker_count` | `worker_count` | `PositiveIntegerField` |  | NO |  |
| `supervisor` | `supervisor` | `CharField(max_length=200)` |  | NO |  |
| `engineer` | `engineer` | `CharField(max_length=200)` |  | NO |  |
| `remarks` | `remarks` | `TextField` |  | NO |  |
| `created_at` | `created_at` | `DateTimeField` |  | NO |  |
| `updated_at` | `updated_at` | `DateTimeField` |  | NO |  |

#### `production_execution_productionmaterialusage`

Django model: `production_execution.ProductionMaterialUsage`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `production_run_id` | `production_run` | `ForeignKey` | FK | NO | production_execution_productionrun.id |
| `material_code` | `material_code` | `CharField(max_length=50)` |  | NO |  |
| `material_name` | `material_name` | `CharField(max_length=255)` |  | NO |  |
| `opening_qty` | `opening_qty` | `DecimalField(max_digits=12, decimal_places=3)` |  | NO |  |
| `issued_qty` | `issued_qty` | `DecimalField(max_digits=12, decimal_places=3)` |  | NO |  |
| `closing_qty` | `closing_qty` | `DecimalField(max_digits=12, decimal_places=3)` |  | NO |  |
| `wastage_qty` | `wastage_qty` | `DecimalField(max_digits=12, decimal_places=3)` |  | NO |  |
| `uom` | `uom` | `CharField(max_length=20)` |  | NO |  |
| `created_at` | `created_at` | `DateTimeField` |  | NO |  |
| `updated_at` | `updated_at` | `DateTimeField` |  | NO |  |

#### `production_execution_productionrun`

Django model: `production_execution.ProductionRun`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `company_id` | `company` | `ForeignKey` | FK | NO | company_company.id |
| `sap_doc_entry` | `sap_doc_entry` | `IntegerField` |  | YES |  |
| `run_number` | `run_number` | `PositiveSmallIntegerField` |  | NO |  |
| `date` | `date` | `DateField` |  | NO |  |
| `line_id` | `line` | `ForeignKey` | FK | NO | production_execution_productionline.id |
| `product` | `product` | `CharField(max_length=200)` |  | NO |  |
| `required_qty` | `required_qty` | `DecimalField(max_digits=12, decimal_places=2)` |  | YES |  |
| `warehouse_approval_status` | `warehouse_approval_status` | `CharField(max_length=25)` |  | NO |  |
| `rated_speed` | `rated_speed` | `DecimalField(max_digits=10, decimal_places=2)` |  | YES |  |
| `labour_count` | `labour_count` | `PositiveIntegerField` |  | NO |  |
| `other_manpower_count` | `other_manpower_count` | `PositiveIntegerField` |  | NO |  |
| `supervisor` | `supervisor` | `CharField(max_length=200)` |  | NO |  |
| `operators` | `operators` | `CharField(max_length=500)` |  | NO |  |
| `total_production` | `total_production` | `DecimalField(max_digits=12, decimal_places=1)` |  | NO |  |
| `total_running_minutes` | `total_running_minutes` | `PositiveIntegerField` |  | NO |  |
| `total_breakdown_time` | `total_breakdown_time` | `PositiveIntegerField` |  | NO |  |
| `rejected_qty` | `rejected_qty` | `DecimalField(max_digits=12, decimal_places=1)` |  | NO |  |
| `reworked_qty` | `reworked_qty` | `DecimalField(max_digits=12, decimal_places=1)` |  | NO |  |
| `sap_receipt_doc_entry` | `sap_receipt_doc_entry` | `IntegerField` |  | YES |  |
| `sap_sync_status` | `sap_sync_status` | `CharField(max_length=20)` |  | NO |  |
| `sap_sync_error` | `sap_sync_error` | `TextField` |  | NO |  |
| `status` | `status` | `CharField(max_length=20)` |  | NO |  |
| `created_by_id` | `created_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `created_at` | `created_at` | `DateTimeField` |  | NO |  |
| `updated_at` | `updated_at` | `DateTimeField` |  | NO |  |

#### `production_execution_productionrun_machines` (implicit join table)

Django model: `production_execution.ProductionRun_machines`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `productionrun_id` | `productionrun` | `ForeignKey` | FK | NO | production_execution_productionrun.id |
| `machine_id` | `machine` | `ForeignKey` | FK | NO | production_execution_machine.id |

#### `production_execution_productionruncost`

Django model: `production_execution.ProductionRunCost`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `production_run_id` | `production_run` | `OneToOneField` | FK, UNIQUE | NO | production_execution_productionrun.id |
| `raw_material_cost` | `raw_material_cost` | `DecimalField(max_digits=15, decimal_places=2)` |  | NO |  |
| `labour_cost` | `labour_cost` | `DecimalField(max_digits=15, decimal_places=2)` |  | NO |  |
| `machine_cost` | `machine_cost` | `DecimalField(max_digits=15, decimal_places=2)` |  | NO |  |
| `electricity_cost` | `electricity_cost` | `DecimalField(max_digits=15, decimal_places=2)` |  | NO |  |
| `water_cost` | `water_cost` | `DecimalField(max_digits=15, decimal_places=2)` |  | NO |  |
| `gas_cost` | `gas_cost` | `DecimalField(max_digits=15, decimal_places=2)` |  | NO |  |
| `compressed_air_cost` | `compressed_air_cost` | `DecimalField(max_digits=15, decimal_places=2)` |  | NO |  |
| `overhead_cost` | `overhead_cost` | `DecimalField(max_digits=15, decimal_places=2)` |  | NO |  |
| `total_cost` | `total_cost` | `DecimalField(max_digits=15, decimal_places=2)` |  | NO |  |
| `produced_qty` | `produced_qty` | `DecimalField(max_digits=15, decimal_places=3)` |  | NO |  |
| `per_unit_cost` | `per_unit_cost` | `DecimalField(max_digits=15, decimal_places=4)` |  | NO |  |
| `calculated_at` | `calculated_at` | `DateTimeField` |  | NO |  |

#### `production_execution_productionsegment`

Django model: `production_execution.ProductionSegment`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `production_run_id` | `production_run` | `ForeignKey` | FK | NO | production_execution_productionrun.id |
| `start_time` | `start_time` | `DateTimeField` |  | NO |  |
| `end_time` | `end_time` | `DateTimeField` |  | YES |  |
| `produced_cases` | `produced_cases` | `DecimalField(max_digits=12, decimal_places=1)` |  | NO |  |
| `is_active` | `is_active` | `BooleanField` |  | NO |  |
| `remarks` | `remarks` | `TextField` |  | NO |  |
| `created_at` | `created_at` | `DateTimeField` |  | NO |  |
| `updated_at` | `updated_at` | `DateTimeField` |  | NO |  |

#### `production_execution_resourcecompressedair`

Django model: `production_execution.ResourceCompressedAir`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `production_run_id` | `production_run` | `ForeignKey` | FK | NO | production_execution_productionrun.id |
| `description` | `description` | `CharField(max_length=200)` |  | NO |  |
| `units_consumed` | `units_consumed` | `DecimalField(max_digits=12, decimal_places=3)` |  | NO |  |
| `rate_per_unit` | `rate_per_unit` | `DecimalField(max_digits=12, decimal_places=4)` |  | NO |  |
| `total_cost` | `total_cost` | `DecimalField(max_digits=15, decimal_places=2)` |  | NO |  |
| `created_by_id` | `created_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `created_at` | `created_at` | `DateTimeField` |  | NO |  |
| `updated_at` | `updated_at` | `DateTimeField` |  | NO |  |

#### `production_execution_resourceelectricity`

Django model: `production_execution.ResourceElectricity`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `production_run_id` | `production_run` | `ForeignKey` | FK | NO | production_execution_productionrun.id |
| `description` | `description` | `CharField(max_length=200)` |  | NO |  |
| `units_consumed` | `units_consumed` | `DecimalField(max_digits=12, decimal_places=3)` |  | NO |  |
| `rate_per_unit` | `rate_per_unit` | `DecimalField(max_digits=12, decimal_places=4)` |  | NO |  |
| `total_cost` | `total_cost` | `DecimalField(max_digits=15, decimal_places=2)` |  | NO |  |
| `created_by_id` | `created_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `created_at` | `created_at` | `DateTimeField` |  | NO |  |
| `updated_at` | `updated_at` | `DateTimeField` |  | NO |  |

#### `production_execution_resourcegas`

Django model: `production_execution.ResourceGas`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `production_run_id` | `production_run` | `ForeignKey` | FK | NO | production_execution_productionrun.id |
| `description` | `description` | `CharField(max_length=200)` |  | NO |  |
| `qty_consumed` | `qty_consumed` | `DecimalField(max_digits=12, decimal_places=3)` |  | NO |  |
| `rate_per_unit` | `rate_per_unit` | `DecimalField(max_digits=12, decimal_places=4)` |  | NO |  |
| `total_cost` | `total_cost` | `DecimalField(max_digits=15, decimal_places=2)` |  | NO |  |
| `created_by_id` | `created_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `created_at` | `created_at` | `DateTimeField` |  | NO |  |
| `updated_at` | `updated_at` | `DateTimeField` |  | NO |  |

#### `production_execution_resourcelabour`

Django model: `production_execution.ResourceLabour`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `production_run_id` | `production_run` | `ForeignKey` | FK | NO | production_execution_productionrun.id |
| `description` | `description` | `CharField(max_length=200)` |  | NO |  |
| `worker_count` | `worker_count` | `PositiveIntegerField` |  | NO |  |
| `hours_worked` | `hours_worked` | `DecimalField(max_digits=8, decimal_places=2)` |  | NO |  |
| `rate_per_hour` | `rate_per_hour` | `DecimalField(max_digits=12, decimal_places=4)` |  | NO |  |
| `total_cost` | `total_cost` | `DecimalField(max_digits=15, decimal_places=2)` |  | NO |  |
| `created_by_id` | `created_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `created_at` | `created_at` | `DateTimeField` |  | NO |  |
| `updated_at` | `updated_at` | `DateTimeField` |  | NO |  |

#### `production_execution_resourcemachinecost`

Django model: `production_execution.ResourceMachineCost`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `production_run_id` | `production_run` | `ForeignKey` | FK | NO | production_execution_productionrun.id |
| `machine_name` | `machine_name` | `CharField(max_length=200)` |  | NO |  |
| `hours_used` | `hours_used` | `DecimalField(max_digits=8, decimal_places=2)` |  | NO |  |
| `rate_per_hour` | `rate_per_hour` | `DecimalField(max_digits=12, decimal_places=4)` |  | NO |  |
| `total_cost` | `total_cost` | `DecimalField(max_digits=15, decimal_places=2)` |  | NO |  |
| `created_by_id` | `created_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `created_at` | `created_at` | `DateTimeField` |  | NO |  |
| `updated_at` | `updated_at` | `DateTimeField` |  | NO |  |

#### `production_execution_resourceoverhead`

Django model: `production_execution.ResourceOverhead`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `production_run_id` | `production_run` | `ForeignKey` | FK | NO | production_execution_productionrun.id |
| `expense_name` | `expense_name` | `CharField(max_length=200)` |  | NO |  |
| `amount` | `amount` | `DecimalField(max_digits=15, decimal_places=2)` |  | NO |  |
| `created_by_id` | `created_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `created_at` | `created_at` | `DateTimeField` |  | NO |  |
| `updated_at` | `updated_at` | `DateTimeField` |  | NO |  |

#### `production_execution_resourcewater`

Django model: `production_execution.ResourceWater`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `production_run_id` | `production_run` | `ForeignKey` | FK | NO | production_execution_productionrun.id |
| `description` | `description` | `CharField(max_length=200)` |  | NO |  |
| `volume_consumed` | `volume_consumed` | `DecimalField(max_digits=12, decimal_places=3)` |  | NO |  |
| `rate_per_unit` | `rate_per_unit` | `DecimalField(max_digits=12, decimal_places=4)` |  | NO |  |
| `total_cost` | `total_cost` | `DecimalField(max_digits=15, decimal_places=2)` |  | NO |  |
| `created_by_id` | `created_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `created_at` | `created_at` | `DateTimeField` |  | NO |  |
| `updated_at` | `updated_at` | `DateTimeField` |  | NO |  |

#### `production_execution_wastelog`

Django model: `production_execution.WasteLog`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `production_run_id` | `production_run` | `ForeignKey` | FK | NO | production_execution_productionrun.id |
| `material_code` | `material_code` | `CharField(max_length=50)` |  | NO |  |
| `material_name` | `material_name` | `CharField(max_length=255)` |  | NO |  |
| `wastage_qty` | `wastage_qty` | `DecimalField(max_digits=12, decimal_places=3)` |  | NO |  |
| `uom` | `uom` | `CharField(max_length=20)` |  | NO |  |
| `reason` | `reason` | `TextField` |  | NO |  |
| `engineer_sign` | `engineer_sign` | `CharField(max_length=200)` |  | NO |  |
| `engineer_signed_by_id` | `engineer_signed_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `engineer_signed_at` | `engineer_signed_at` | `DateTimeField` |  | YES |  |
| `am_sign` | `am_sign` | `CharField(max_length=200)` |  | NO |  |
| `am_signed_by_id` | `am_signed_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `am_signed_at` | `am_signed_at` | `DateTimeField` |  | YES |  |
| `store_sign` | `store_sign` | `CharField(max_length=200)` |  | NO |  |
| `store_signed_by_id` | `store_signed_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `store_signed_at` | `store_signed_at` | `DateTimeField` |  | YES |  |
| `hod_sign` | `hod_sign` | `CharField(max_length=200)` |  | NO |  |
| `hod_signed_by_id` | `hod_signed_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `hod_signed_at` | `hod_signed_at` | `DateTimeField` |  | YES |  |
| `wastage_approval_status` | `wastage_approval_status` | `CharField(max_length=20)` |  | NO |  |
| `created_at` | `created_at` | `DateTimeField` |  | NO |  |
| `updated_at` | `updated_at` | `DateTimeField` |  | NO |  |

### quality_control

#### `quality_control_arrivalslipattachment`

Django model: `quality_control.ArrivalSlipAttachment`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `arrival_slip_id` | `arrival_slip` | `ForeignKey` | FK | NO | quality_control_materialarrivalslip.id |
| `file` | `file` | `FileField(max_length=100)` |  | NO |  |
| `attachment_type` | `attachment_type` | `CharField(max_length=30)` |  | NO |  |
| `uploaded_at` | `uploaded_at` | `DateTimeField` |  | NO |  |

#### `quality_control_inspectionparameterresult`

Django model: `quality_control.InspectionParameterResult`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `created_at` | `created_at` | `DateTimeField` |  | NO |  |
| `updated_at` | `updated_at` | `DateTimeField` |  | NO |  |
| `created_by_id` | `created_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `updated_by_id` | `updated_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `is_active` | `is_active` | `BooleanField` |  | NO |  |
| `inspection_id` | `inspection` | `ForeignKey` | FK | NO | quality_control_rawmaterialinspection.id |
| `parameter_master_id` | `parameter_master` | `ForeignKey` | FK | NO | quality_control_qcparametermaster.id |
| `parameter_name` | `parameter_name` | `CharField(max_length=200)` |  | NO |  |
| `standard_value` | `standard_value` | `CharField(max_length=200)` |  | NO |  |
| `result_value` | `result_value` | `CharField(max_length=200)` |  | NO |  |
| `result_numeric` | `result_numeric` | `DecimalField(max_digits=12, decimal_places=4)` |  | YES |  |
| `is_within_spec` | `is_within_spec` | `BooleanField` |  | YES |  |
| `remarks` | `remarks` | `TextField` |  | NO |  |

#### `quality_control_materialarrivalslip`

Django model: `quality_control.MaterialArrivalSlip`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `created_at` | `created_at` | `DateTimeField` |  | NO |  |
| `updated_at` | `updated_at` | `DateTimeField` |  | NO |  |
| `created_by_id` | `created_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `updated_by_id` | `updated_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `is_active` | `is_active` | `BooleanField` |  | NO |  |
| `po_item_receipt_id` | `po_item_receipt` | `OneToOneField` | FK, UNIQUE | YES | raw_material_gatein_poitemreceipt.id |
| `particulars` | `particulars` | `TextField` |  | NO |  |
| `arrival_datetime` | `arrival_datetime` | `DateTimeField` |  | NO |  |
| `weighing_required` | `weighing_required` | `BooleanField` |  | NO |  |
| `party_name` | `party_name` | `CharField(max_length=200)` |  | NO |  |
| `billing_qty` | `billing_qty` | `DecimalField(max_digits=12, decimal_places=3)` |  | NO |  |
| `billing_uom` | `billing_uom` | `CharField(max_length=20)` |  | NO |  |
| `in_time_to_qa` | `in_time_to_qa` | `DateTimeField` |  | YES |  |
| `truck_no_as_per_bill` | `truck_no_as_per_bill` | `CharField(max_length=50)` |  | NO |  |
| `commercial_invoice_no` | `commercial_invoice_no` | `CharField(max_length=100)` |  | NO |  |
| `eway_bill_no` | `eway_bill_no` | `CharField(max_length=100)` |  | NO |  |
| `bilty_no` | `bilty_no` | `CharField(max_length=100)` |  | NO |  |
| `has_certificate_of_analysis` | `has_certificate_of_analysis` | `BooleanField` |  | NO |  |
| `has_certificate_of_quantity` | `has_certificate_of_quantity` | `BooleanField` |  | NO |  |
| `status` | `status` | `CharField(max_length=20)` |  | NO |  |
| `is_submitted` | `is_submitted` | `BooleanField` |  | NO |  |
| `submitted_at` | `submitted_at` | `DateTimeField` |  | YES |  |
| `submitted_by_id` | `submitted_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `remarks` | `remarks` | `TextField` |  | NO |  |
| `sent_back_by_id` | `sent_back_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `sent_back_at` | `sent_back_at` | `DateTimeField` |  | YES |  |

#### `quality_control_materialtype`

Django model: `quality_control.MaterialType`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `created_at` | `created_at` | `DateTimeField` |  | NO |  |
| `updated_at` | `updated_at` | `DateTimeField` |  | NO |  |
| `created_by_id` | `created_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `updated_by_id` | `updated_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `is_active` | `is_active` | `BooleanField` |  | NO |  |
| `code` | `code` | `CharField(max_length=50)` |  | NO |  |
| `name` | `name` | `CharField(max_length=200)` |  | NO |  |
| `description` | `description` | `TextField` |  | NO |  |
| `company_id` | `company` | `ForeignKey` | FK | NO | company_company.id |

#### `quality_control_productionqcresult`

Django model: `quality_control.ProductionQCResult`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `created_at` | `created_at` | `DateTimeField` |  | NO |  |
| `updated_at` | `updated_at` | `DateTimeField` |  | NO |  |
| `created_by_id` | `created_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `updated_by_id` | `updated_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `is_active` | `is_active` | `BooleanField` |  | NO |  |
| `session_id` | `session` | `ForeignKey` | FK | NO | quality_control_productionqcsession.id |
| `parameter_master_id` | `parameter_master` | `ForeignKey` | FK | NO | quality_control_qcparametermaster.id |
| `parameter_name` | `parameter_name` | `CharField(max_length=200)` |  | NO |  |
| `standard_value` | `standard_value` | `CharField(max_length=200)` |  | NO |  |
| `result_value` | `result_value` | `CharField(max_length=200)` |  | NO |  |
| `result_numeric` | `result_numeric` | `DecimalField(max_digits=12, decimal_places=4)` |  | YES |  |
| `is_within_spec` | `is_within_spec` | `BooleanField` |  | YES |  |
| `remarks` | `remarks` | `TextField` |  | NO |  |

#### `quality_control_productionqcsession`

Django model: `quality_control.ProductionQCSession`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `created_at` | `created_at` | `DateTimeField` |  | NO |  |
| `updated_at` | `updated_at` | `DateTimeField` |  | NO |  |
| `created_by_id` | `created_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `updated_by_id` | `updated_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `is_active` | `is_active` | `BooleanField` |  | NO |  |
| `production_run_id` | `production_run` | `ForeignKey` | FK | NO | production_execution_productionrun.id |
| `material_type_id` | `material_type` | `ForeignKey` | FK | NO | quality_control_materialtype.id |
| `session_number` | `session_number` | `PositiveSmallIntegerField` |  | NO |  |
| `session_type` | `session_type` | `CharField(max_length=15)` |  | NO |  |
| `checked_at` | `checked_at` | `DateTimeField` |  | NO |  |
| `checked_by_id` | `checked_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `overall_result` | `overall_result` | `CharField(max_length=10)` |  | NO |  |
| `workflow_status` | `workflow_status` | `CharField(max_length=15)` |  | NO |  |
| `submitted_by_id` | `submitted_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `submitted_at` | `submitted_at` | `DateTimeField` |  | YES |  |
| `remarks` | `remarks` | `TextField` |  | NO |  |

#### `quality_control_qcparametermaster`

Django model: `quality_control.QCParameterMaster`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `created_at` | `created_at` | `DateTimeField` |  | NO |  |
| `updated_at` | `updated_at` | `DateTimeField` |  | NO |  |
| `created_by_id` | `created_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `updated_by_id` | `updated_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `is_active` | `is_active` | `BooleanField` |  | NO |  |
| `material_type_id` | `material_type` | `ForeignKey` | FK | NO | quality_control_materialtype.id |
| `parameter_name` | `parameter_name` | `CharField(max_length=200)` |  | NO |  |
| `parameter_code` | `parameter_code` | `CharField(max_length=50)` |  | NO |  |
| `standard_value` | `standard_value` | `CharField(max_length=200)` |  | NO |  |
| `parameter_type` | `parameter_type` | `CharField(max_length=20)` |  | NO |  |
| `min_value` | `min_value` | `DecimalField(max_digits=12, decimal_places=4)` |  | YES |  |
| `max_value` | `max_value` | `DecimalField(max_digits=12, decimal_places=4)` |  | YES |  |
| `uom` | `uom` | `CharField(max_length=50)` |  | NO |  |
| `sequence` | `sequence` | `PositiveIntegerField` |  | NO |  |
| `is_mandatory` | `is_mandatory` | `BooleanField` |  | NO |  |

#### `quality_control_rawmaterialinspection`

Django model: `quality_control.RawMaterialInspection`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `created_at` | `created_at` | `DateTimeField` |  | NO |  |
| `updated_at` | `updated_at` | `DateTimeField` |  | NO |  |
| `created_by_id` | `created_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `updated_by_id` | `updated_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `is_active` | `is_active` | `BooleanField` |  | NO |  |
| `arrival_slip_id` | `arrival_slip` | `OneToOneField` | FK, UNIQUE | YES | quality_control_materialarrivalslip.id |
| `report_no` | `report_no` | `CharField(max_length=50)` | UNIQUE | NO |  |
| `internal_lot_no` | `internal_lot_no` | `CharField(max_length=50)` |  | NO |  |
| `inspection_date` | `inspection_date` | `DateField` |  | NO |  |
| `description_of_material` | `description_of_material` | `TextField` |  | NO |  |
| `sap_code` | `sap_code` | `CharField(max_length=50)` |  | NO |  |
| `supplier_name` | `supplier_name` | `CharField(max_length=200)` |  | NO |  |
| `manufacturer_name` | `manufacturer_name` | `CharField(max_length=200)` |  | NO |  |
| `supplier_batch_lot_no` | `supplier_batch_lot_no` | `CharField(max_length=100)` |  | NO |  |
| `unit_packing` | `unit_packing` | `CharField(max_length=100)` |  | NO |  |
| `purchase_order_no` | `purchase_order_no` | `CharField(max_length=50)` |  | NO |  |
| `internal_report_no` | `internal_report_no` | `CharField(max_length=100)` |  | NO |  |
| `invoice_bill_no` | `invoice_bill_no` | `CharField(max_length=100)` |  | NO |  |
| `vehicle_no` | `vehicle_no` | `CharField(max_length=50)` |  | NO |  |
| `material_type_id` | `material_type` | `ForeignKey` | FK | YES | quality_control_materialtype.id |
| `final_status` | `final_status` | `CharField(max_length=20)` |  | NO |  |
| `qa_chemist_id` | `qa_chemist` | `ForeignKey` | FK | YES | accounts_user.id |
| `qa_chemist_approved_at` | `qa_chemist_approved_at` | `DateTimeField` |  | YES |  |
| `qa_chemist_remarks` | `qa_chemist_remarks` | `TextField` |  | NO |  |
| `qam_id` | `qam` | `ForeignKey` | FK | YES | accounts_user.id |
| `qam_approved_at` | `qam_approved_at` | `DateTimeField` |  | YES |  |
| `qam_remarks` | `qam_remarks` | `TextField` |  | NO |  |
| `rejected_by_id` | `rejected_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `rejected_at` | `rejected_at` | `DateTimeField` |  | YES |  |
| `factory_head_id` | `factory_head` | `ForeignKey` | FK | YES | accounts_user.id |
| `factory_head_decision` | `factory_head_decision` | `CharField(max_length=30)` |  | NO |  |
| `factory_head_remarks` | `factory_head_remarks` | `TextField` |  | NO |  |
| `factory_head_decided_at` | `factory_head_decided_at` | `DateTimeField` |  | YES |  |
| `workflow_status` | `workflow_status` | `CharField(max_length=30)` |  | NO |  |
| `is_locked` | `is_locked` | `BooleanField` |  | NO |  |
| `remarks` | `remarks` | `TextField` |  | NO |  |

### raw_material_gatein

#### `raw_material_gatein_poitemreceipt`

Django model: `raw_material_gatein.POItemReceipt`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `created_at` | `created_at` | `DateTimeField` |  | NO |  |
| `updated_at` | `updated_at` | `DateTimeField` |  | NO |  |
| `created_by_id` | `created_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `updated_by_id` | `updated_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `is_active` | `is_active` | `BooleanField` |  | NO |  |
| `po_receipt_id` | `po_receipt` | `ForeignKey` | FK | NO | raw_material_gatein_poreceipt.id |
| `po_item_code` | `po_item_code` | `CharField(max_length=50)` |  | NO |  |
| `item_name` | `item_name` | `CharField(max_length=200)` |  | NO |  |
| `sap_line_num` | `sap_line_num` | `IntegerField` |  | YES |  |
| `unit_price` | `unit_price` | `DecimalField(max_digits=18, decimal_places=6)` |  | YES |  |
| `tax_code` | `tax_code` | `CharField(max_length=20)` |  | NO |  |
| `warehouse_code` | `warehouse_code` | `CharField(max_length=20)` |  | NO |  |
| `gl_account` | `gl_account` | `CharField(max_length=30)` |  | NO |  |
| `variety` | `variety` | `CharField(max_length=100)` |  | NO |  |
| `ordered_qty` | `ordered_qty` | `DecimalField(max_digits=12, decimal_places=3)` |  | NO |  |
| `received_qty` | `received_qty` | `DecimalField(max_digits=12, decimal_places=3)` |  | NO |  |
| `accepted_qty` | `accepted_qty` | `DecimalField(max_digits=12, decimal_places=3)` |  | NO |  |
| `rejected_qty` | `rejected_qty` | `DecimalField(max_digits=12, decimal_places=3)` |  | NO |  |
| `short_qty` | `short_qty` | `DecimalField(max_digits=12, decimal_places=3)` |  | NO |  |
| `uom` | `uom` | `CharField(max_length=20)` |  | NO |  |

#### `raw_material_gatein_poreceipt`

Django model: `raw_material_gatein.POReceipt`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `created_at` | `created_at` | `DateTimeField` |  | NO |  |
| `updated_at` | `updated_at` | `DateTimeField` |  | NO |  |
| `created_by_id` | `created_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `updated_by_id` | `updated_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `is_active` | `is_active` | `BooleanField` |  | NO |  |
| `vehicle_entry_id` | `vehicle_entry` | `ForeignKey` | FK | NO | driver_management_vehicleentry.id |
| `po_number` | `po_number` | `CharField(max_length=30)` |  | NO |  |
| `supplier_code` | `supplier_code` | `CharField(max_length=30)` |  | NO |  |
| `supplier_name` | `supplier_name` | `CharField(max_length=150)` |  | NO |  |
| `sap_doc_entry` | `sap_doc_entry` | `IntegerField` |  | YES |  |
| `branch_id` | `branch_id` | `IntegerField` |  | YES |  |
| `vendor_ref` | `vendor_ref` | `CharField(max_length=100)` |  | NO |  |
| `po_date` | `po_date` | `DateField` |  | YES |  |
| `invoice_no` | `invoice_no` | `CharField(max_length=50)` |  | NO |  |
| `invoice_date` | `invoice_date` | `DateField` |  | YES |  |
| `challan_no` | `challan_no` | `CharField(max_length=50)` |  | NO |  |

### security_checks

#### `security_checks_securitycheck`

Django model: `security_checks.SecurityCheck`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `created_at` | `created_at` | `DateTimeField` |  | NO |  |
| `updated_at` | `updated_at` | `DateTimeField` |  | NO |  |
| `created_by_id` | `created_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `updated_by_id` | `updated_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `is_active` | `is_active` | `BooleanField` |  | NO |  |
| `vehicle_entry_id` | `vehicle_entry` | `OneToOneField` | FK, UNIQUE | NO | driver_management_vehicleentry.id |
| `vehicle_condition_ok` | `vehicle_condition_ok` | `BooleanField` |  | NO |  |
| `tyre_condition_ok` | `tyre_condition_ok` | `BooleanField` |  | NO |  |
| `fire_extinguisher_available` | `fire_extinguisher_available` | `BooleanField` |  | NO |  |
| `seal_no_before` | `seal_no_before` | `CharField(max_length=50)` |  | NO |  |
| `seal_no_after` | `seal_no_after` | `CharField(max_length=50)` |  | NO |  |
| `alcohol_test_done` | `alcohol_test_done` | `BooleanField` |  | NO |  |
| `alcohol_test_passed` | `alcohol_test_passed` | `BooleanField` |  | NO |  |
| `inspected_by_name` | `inspected_by_name` | `CharField(max_length=100)` |  | NO |  |
| `inspection_time` | `inspection_time` | `DateTimeField` |  | NO |  |
| `remarks` | `remarks` | `TextField` |  | NO |  |
| `is_submitted` | `is_submitted` | `BooleanField` |  | NO |  |

### sessions

#### `django_session`

Django model: `sessions.Session`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `session_key` | `session_key` | `CharField(max_length=40)` | PK | NO |  |
| `session_data` | `session_data` | `TextField` |  | NO |  |
| `expire_date` | `expire_date` | `DateTimeField` |  | NO |  |

### stock_dashboard

#### `stock_dashboard_stockalertlog`

Django model: `stock_dashboard.StockAlertLog`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `company_code` | `company_code` | `CharField(max_length=50)` |  | NO |  |
| `item_code` | `item_code` | `CharField(max_length=50)` |  | NO |  |
| `warehouse` | `warehouse` | `CharField(max_length=20)` |  | NO |  |
| `stock_status` | `stock_status` | `CharField(max_length=10)` |  | NO |  |
| `on_hand` | `on_hand` | `FloatField` |  | NO |  |
| `min_stock` | `min_stock` | `FloatField` |  | NO |  |
| `notified_at` | `notified_at` | `DateTimeField` |  | NO |  |
| `cooldown_until` | `cooldown_until` | `DateTimeField` |  | NO |  |

### token_blacklist

#### `token_blacklist_blacklistedtoken`

Django model: `token_blacklist.BlacklistedToken`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `token_id` | `token` | `OneToOneField` | FK, UNIQUE | NO | token_blacklist_outstandingtoken.id |
| `blacklisted_at` | `blacklisted_at` | `DateTimeField` |  | NO |  |

#### `token_blacklist_outstandingtoken`

Django model: `token_blacklist.OutstandingToken`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `user_id` | `user` | `ForeignKey` | FK | YES | accounts_user.id |
| `jti` | `jti` | `CharField(max_length=255)` | UNIQUE | NO |  |
| `token` | `token` | `TextField` |  | NO |  |
| `created_at` | `created_at` | `DateTimeField` |  | YES |  |
| `expires_at` | `expires_at` | `DateTimeField` |  | NO |  |

### vehicle_management

#### `vehicle_management_transporter`

Django model: `vehicle_management.Transporter`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `created_at` | `created_at` | `DateTimeField` |  | NO |  |
| `updated_at` | `updated_at` | `DateTimeField` |  | NO |  |
| `created_by_id` | `created_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `updated_by_id` | `updated_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `is_active` | `is_active` | `BooleanField` |  | NO |  |
| `name` | `name` | `CharField(max_length=150)` | UNIQUE | NO |  |
| `contact_person` | `contact_person` | `CharField(max_length=100)` |  | NO |  |
| `mobile_no` | `mobile_no` | `CharField(max_length=15)` |  | NO |  |
| `gstin` | `gstin` | `CharField(max_length=20)` |  | NO |  |

#### `vehicle_management_vehicle`

Django model: `vehicle_management.Vehicle`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `created_at` | `created_at` | `DateTimeField` |  | NO |  |
| `updated_at` | `updated_at` | `DateTimeField` |  | NO |  |
| `created_by_id` | `created_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `updated_by_id` | `updated_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `is_active` | `is_active` | `BooleanField` |  | NO |  |
| `vehicle_number` | `vehicle_number` | `CharField(max_length=20)` | UNIQUE | NO |  |
| `vehicle_type_id` | `vehicle_type` | `ForeignKey` | FK | YES | vehicle_management_vehicletype.id |
| `transporter_id` | `transporter` | `ForeignKey` | FK | YES | vehicle_management_transporter.id |
| `capacity_ton` | `capacity_ton` | `DecimalField(max_digits=8, decimal_places=2)` |  | YES |  |

#### `vehicle_management_vehicletype`

Django model: `vehicle_management.VehicleType`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `created_at` | `created_at` | `DateTimeField` |  | NO |  |
| `updated_at` | `updated_at` | `DateTimeField` |  | NO |  |
| `created_by_id` | `created_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `updated_by_id` | `updated_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `is_active` | `is_active` | `BooleanField` |  | NO |  |
| `name` | `name` | `CharField(max_length=50)` | UNIQUE | NO |  |

### warehouse

#### `warehouse_bomrequest`

Django model: `warehouse.BOMRequest`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `company_id` | `company` | `ForeignKey` | FK | NO | company_company.id |
| `production_run_id` | `production_run` | `ForeignKey` | FK | NO | production_execution_productionrun.id |
| `sap_doc_entry` | `sap_doc_entry` | `IntegerField` |  | YES |  |
| `required_qty` | `required_qty` | `DecimalField(max_digits=12, decimal_places=2)` |  | NO |  |
| `status` | `status` | `CharField(max_length=25)` |  | NO |  |
| `remarks` | `remarks` | `TextField` |  | NO |  |
| `rejection_reason` | `rejection_reason` | `TextField` |  | NO |  |
| `material_issue_status` | `material_issue_status` | `CharField(max_length=25)` |  | NO |  |
| `sap_issue_doc_entries` | `sap_issue_doc_entries` | `JSONField` |  | NO |  |
| `requested_by_id` | `requested_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `reviewed_by_id` | `reviewed_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `reviewed_at` | `reviewed_at` | `DateTimeField` |  | YES |  |
| `created_at` | `created_at` | `DateTimeField` |  | NO |  |
| `updated_at` | `updated_at` | `DateTimeField` |  | NO |  |

#### `warehouse_bomrequestline`

Django model: `warehouse.BOMRequestLine`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `bom_request_id` | `bom_request` | `ForeignKey` | FK | NO | warehouse_bomrequest.id |
| `item_code` | `item_code` | `CharField(max_length=50)` |  | NO |  |
| `item_name` | `item_name` | `CharField(max_length=255)` |  | NO |  |
| `per_unit_qty` | `per_unit_qty` | `DecimalField(max_digits=12, decimal_places=4)` |  | NO |  |
| `required_qty` | `required_qty` | `DecimalField(max_digits=12, decimal_places=3)` |  | NO |  |
| `available_stock` | `available_stock` | `DecimalField(max_digits=12, decimal_places=3)` |  | NO |  |
| `approved_qty` | `approved_qty` | `DecimalField(max_digits=12, decimal_places=3)` |  | NO |  |
| `issued_qty` | `issued_qty` | `DecimalField(max_digits=12, decimal_places=3)` |  | NO |  |
| `warehouse` | `warehouse` | `CharField(max_length=20)` |  | NO |  |
| `uom` | `uom` | `CharField(max_length=20)` |  | NO |  |
| `base_line` | `base_line` | `IntegerField` |  | NO |  |
| `status` | `status` | `CharField(max_length=20)` |  | NO |  |
| `remarks` | `remarks` | `TextField` |  | NO |  |
| `created_at` | `created_at` | `DateTimeField` |  | NO |  |
| `updated_at` | `updated_at` | `DateTimeField` |  | NO |  |

#### `warehouse_finishedgoodsreceipt`

Django model: `warehouse.FinishedGoodsReceipt`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `company_id` | `company` | `ForeignKey` | FK | NO | company_company.id |
| `production_run_id` | `production_run` | `ForeignKey` | FK | NO | production_execution_productionrun.id |
| `sap_doc_entry` | `sap_doc_entry` | `IntegerField` |  | YES |  |
| `item_code` | `item_code` | `CharField(max_length=50)` |  | NO |  |
| `item_name` | `item_name` | `CharField(max_length=255)` |  | NO |  |
| `produced_qty` | `produced_qty` | `DecimalField(max_digits=12, decimal_places=2)` |  | NO |  |
| `good_qty` | `good_qty` | `DecimalField(max_digits=12, decimal_places=2)` |  | NO |  |
| `rejected_qty` | `rejected_qty` | `DecimalField(max_digits=12, decimal_places=2)` |  | NO |  |
| `warehouse` | `warehouse` | `CharField(max_length=20)` |  | NO |  |
| `uom` | `uom` | `CharField(max_length=20)` |  | NO |  |
| `posting_date` | `posting_date` | `DateField` |  | NO |  |
| `status` | `status` | `CharField(max_length=20)` |  | NO |  |
| `sap_receipt_doc_entry` | `sap_receipt_doc_entry` | `IntegerField` |  | YES |  |
| `sap_error` | `sap_error` | `TextField` |  | NO |  |
| `received_by_id` | `received_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `received_at` | `received_at` | `DateTimeField` |  | YES |  |
| `created_at` | `created_at` | `DateTimeField` |  | NO |  |
| `updated_at` | `updated_at` | `DateTimeField` |  | NO |  |

### weighment

#### `weighment_weighment`

Django model: `weighment.Weighment`

| Column | Model field | Type | Key | Null | Relation |
| --- | --- | --- | --- | --- | --- |
| `id` | `id` | `BigAutoField` | PK | NO |  |
| `created_at` | `created_at` | `DateTimeField` |  | NO |  |
| `updated_at` | `updated_at` | `DateTimeField` |  | NO |  |
| `created_by_id` | `created_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `updated_by_id` | `updated_by` | `ForeignKey` | FK | YES | accounts_user.id |
| `is_active` | `is_active` | `BooleanField` |  | NO |  |
| `vehicle_entry_id` | `vehicle_entry` | `OneToOneField` | FK, UNIQUE | NO | driver_management_vehicleentry.id |
| `gross_weight` | `gross_weight` | `DecimalField(max_digits=12, decimal_places=3)` |  | YES |  |
| `tare_weight` | `tare_weight` | `DecimalField(max_digits=12, decimal_places=3)` |  | YES |  |
| `net_weight` | `net_weight` | `DecimalField(max_digits=12, decimal_places=3)` |  | NO |  |
| `weighbridge_slip_no` | `weighbridge_slip_no` | `CharField(max_length=50)` |  | NO |  |
| `first_weighment_time` | `first_weighment_time` | `DateTimeField` |  | YES |  |
| `second_weighment_time` | `second_weighment_time` | `DateTimeField` |  | YES |  |
| `remarks` | `remarks` | `TextField` |  | NO |  |
