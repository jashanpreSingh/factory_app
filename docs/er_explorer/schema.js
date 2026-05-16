window.ER_SCHEMA = {
  "source": "docs/db_er_diagram.mmd",
  "generatedAt": "2026-05-16T16:33:15",
  "stats": {
    "tables": 141,
    "relationships": 245,
    "apps": 31
  },
  "apps": [
    {
      "name": "accounts",
      "tableCount": 4,
      "relationshipCount": 51
    },
    {
      "name": "auth",
      "tableCount": 3,
      "relationshipCount": 7
    },
    {
      "name": "barcode",
      "tableCount": 8,
      "relationshipCount": 27
    },
    {
      "name": "company",
      "tableCount": 3,
      "relationshipCount": 39
    },
    {
      "name": "construction_gatein",
      "tableCount": 2,
      "relationshipCount": 4
    },
    {
      "name": "daily_needs_gatein",
      "tableCount": 3,
      "relationshipCount": 7
    },
    {
      "name": "database_connections",
      "tableCount": 1,
      "relationshipCount": 0
    },
    {
      "name": "dispatch_plans",
      "tableCount": 4,
      "relationshipCount": 22
    },
    {
      "name": "django",
      "tableCount": 4,
      "relationshipCount": 3
    },
    {
      "name": "django_apscheduler",
      "tableCount": 2,
      "relationshipCount": 2
    },
    {
      "name": "driver_management",
      "tableCount": 2,
      "relationshipCount": 31
    },
    {
      "name": "gate_core",
      "tableCount": 17,
      "relationshipCount": 92
    },
    {
      "name": "grpo",
      "tableCount": 7,
      "relationshipCount": 19
    },
    {
      "name": "inventory",
      "tableCount": 10,
      "relationshipCount": 18
    },
    {
      "name": "labour_verification",
      "tableCount": 2,
      "relationshipCount": 2
    },
    {
      "name": "mail",
      "tableCount": 1,
      "relationshipCount": 1
    },
    {
      "name": "maintenance_gatein",
      "tableCount": 2,
      "relationshipCount": 4
    },
    {
      "name": "notifications",
      "tableCount": 2,
      "relationshipCount": 1
    },
    {
      "name": "outbound_dispatch",
      "tableCount": 5,
      "relationshipCount": 10
    },
    {
      "name": "outbound_gatein",
      "tableCount": 2,
      "relationshipCount": 3
    },
    {
      "name": "person_gatein",
      "tableCount": 6,
      "relationshipCount": 12
    },
    {
      "name": "production_execution",
      "tableCount": 26,
      "relationshipCount": 71
    },
    {
      "name": "production_planning",
      "tableCount": 4,
      "relationshipCount": 7
    },
    {
      "name": "quality_control",
      "tableCount": 8,
      "relationshipCount": 25
    },
    {
      "name": "raw_material_gatein",
      "tableCount": 2,
      "relationshipCount": 7
    },
    {
      "name": "security_checks",
      "tableCount": 1,
      "relationshipCount": 1
    },
    {
      "name": "stock_dashboard",
      "tableCount": 1,
      "relationshipCount": 0
    },
    {
      "name": "token_blacklist",
      "tableCount": 2,
      "relationshipCount": 2
    },
    {
      "name": "vehicle_management",
      "tableCount": 3,
      "relationshipCount": 15
    },
    {
      "name": "warehouse",
      "tableCount": 3,
      "relationshipCount": 6
    },
    {
      "name": "weighment",
      "tableCount": 1,
      "relationshipCount": 1
    }
  ],
  "tables": [
    {
      "name": "accounts_department",
      "app": "accounts",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "description",
          "type": "text",
          "tags": [],
          "notes": []
        }
      ]
    },
    {
      "name": "accounts_user",
      "app": "accounts",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "password",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "last_login",
          "type": "datetime",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "is_superuser",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "email",
          "type": "varchar",
          "tags": [
            "UK"
          ],
          "notes": []
        },
        {
          "name": "full_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "employee_code",
          "type": "varchar",
          "tags": [
            "UK"
          ],
          "notes": []
        },
        {
          "name": "is_active",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "is_staff",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "date_joined",
          "type": "datetime",
          "tags": [],
          "notes": []
        }
      ]
    },
    {
      "name": "accounts_user_groups",
      "app": "accounts",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "user_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "group_id",
          "type": "int",
          "tags": [
            "FK"
          ],
          "notes": []
        }
      ]
    },
    {
      "name": "accounts_user_user_permissions",
      "app": "accounts",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "user_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "permission_id",
          "type": "int",
          "tags": [
            "FK"
          ],
          "notes": []
        }
      ]
    },
    {
      "name": "auth_group",
      "app": "auth",
      "fields": [
        {
          "name": "id",
          "type": "int",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "name",
          "type": "varchar",
          "tags": [
            "UK"
          ],
          "notes": []
        }
      ]
    },
    {
      "name": "auth_group_permissions",
      "app": "auth",
      "fields": [
        {
          "name": "id",
          "type": "int",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "group_id",
          "type": "int",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "permission_id",
          "type": "int",
          "tags": [
            "FK"
          ],
          "notes": []
        }
      ]
    },
    {
      "name": "auth_permission",
      "app": "auth",
      "fields": [
        {
          "name": "id",
          "type": "int",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "content_type_id",
          "type": "int",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "codename",
          "type": "varchar",
          "tags": [],
          "notes": []
        }
      ]
    },
    {
      "name": "barcode_barcodesequence",
      "app": "barcode",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "sequence_type",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "date_str",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "line_key",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "next_value",
          "type": "int",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "company_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        }
      ]
    },
    {
      "name": "barcode_box",
      "app": "barcode",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "company_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "box_barcode",
          "type": "varchar",
          "tags": [
            "UK"
          ],
          "notes": []
        },
        {
          "name": "barcode_data",
          "type": "json",
          "tags": [],
          "notes": []
        },
        {
          "name": "item_code",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "item_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "batch_number",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "qty",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "uom",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "g_weight",
          "type": "decimal",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "n_weight",
          "type": "decimal",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "mfg_date",
          "type": "date",
          "tags": [],
          "notes": []
        },
        {
          "name": "exp_date",
          "type": "date",
          "tags": [],
          "notes": []
        },
        {
          "name": "pallet_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "production_run_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "production_line",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "current_warehouse",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "current_bin",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "status",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "created_by_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        }
      ]
    },
    {
      "name": "barcode_boxmovement",
      "app": "barcode",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "movement_type",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "from_warehouse",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "to_warehouse",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "from_bin",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "to_bin",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "performed_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "box_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "company_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "performed_by_id",
          "type": "bigint",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "from_pallet_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "to_pallet_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        }
      ]
    },
    {
      "name": "barcode_labelprintlog",
      "app": "barcode",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "label_type",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "reference_id",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "reference_code",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "print_type",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "reprint_reason",
          "type": "text",
          "tags": [],
          "notes": []
        },
        {
          "name": "printed_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "printer_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "company_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "printed_by_id",
          "type": "bigint",
          "tags": [],
          "notes": [
            "nullable"
          ]
        }
      ]
    },
    {
      "name": "barcode_loosestock",
      "app": "barcode",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "item_code",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "item_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "batch_number",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "qty",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "original_qty",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "uom",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "reason",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "reason_notes",
          "type": "text",
          "tags": [],
          "notes": []
        },
        {
          "name": "current_warehouse",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "status",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "company_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "created_by_id",
          "type": "bigint",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "repacked_into_box_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "source_box_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "source_pallet_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        }
      ]
    },
    {
      "name": "barcode_pallet",
      "app": "barcode",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "pallet_id",
          "type": "varchar",
          "tags": [
            "UK"
          ],
          "notes": []
        },
        {
          "name": "barcode_data",
          "type": "json",
          "tags": [],
          "notes": []
        },
        {
          "name": "item_code",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "item_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "batch_number",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "box_count",
          "type": "int",
          "tags": [],
          "notes": []
        },
        {
          "name": "total_qty",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "uom",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "mfg_date",
          "type": "date",
          "tags": [],
          "notes": []
        },
        {
          "name": "exp_date",
          "type": "date",
          "tags": [],
          "notes": []
        },
        {
          "name": "production_line",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "current_warehouse",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "current_bin",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "status",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "company_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "created_by_id",
          "type": "bigint",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "production_run_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "max_box_count",
          "type": "int",
          "tags": [],
          "notes": []
        }
      ]
    },
    {
      "name": "barcode_palletmovement",
      "app": "barcode",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "movement_type",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "from_warehouse",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "to_warehouse",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "from_bin",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "to_bin",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "sap_transfer_doc_entry",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "quantity",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "performed_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "notes",
          "type": "text",
          "tags": [],
          "notes": []
        },
        {
          "name": "company_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "pallet_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "performed_by_id",
          "type": "bigint",
          "tags": [],
          "notes": [
            "nullable"
          ]
        }
      ]
    },
    {
      "name": "barcode_scanlog",
      "app": "barcode",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "scan_type",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "barcode_raw",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "barcode_parsed",
          "type": "json",
          "tags": [],
          "notes": []
        },
        {
          "name": "entity_type",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "entity_id",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "scan_result",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "context_ref_type",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "context_ref_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "scanned_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "device_info",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "company_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "scanned_by_id",
          "type": "bigint",
          "tags": [],
          "notes": [
            "nullable"
          ]
        }
      ]
    },
    {
      "name": "company_company",
      "app": "company",
      "fields": [
        {
          "name": "id",
          "type": "int",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "code",
          "type": "varchar",
          "tags": [
            "UK"
          ],
          "notes": []
        },
        {
          "name": "is_active",
          "type": "boolean",
          "tags": [],
          "notes": []
        }
      ]
    },
    {
      "name": "company_usercompany",
      "app": "company",
      "fields": [
        {
          "name": "id",
          "type": "int",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "role_id",
          "type": "int",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "is_default",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "is_active",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "company_id",
          "type": "int",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "user_id",
          "type": "int",
          "tags": [],
          "notes": []
        }
      ]
    },
    {
      "name": "company_userrole",
      "app": "company",
      "fields": [
        {
          "name": "id",
          "type": "int",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "description",
          "type": "text",
          "tags": [],
          "notes": []
        }
      ]
    },
    {
      "name": "construction_gatein_constructiongateentry",
      "app": "construction_gatein",
      "fields": [
        {
          "name": "id",
          "type": "int",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "project_name",
          "type": "varchar",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "work_order_number",
          "type": "varchar",
          "tags": [
            "UK"
          ],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "contractor_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "contractor_contact",
          "type": "varchar",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "material_description",
          "type": "text",
          "tags": [],
          "notes": []
        },
        {
          "name": "quantity",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "unit_id",
          "type": "int",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "challan_number",
          "type": "varchar",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "invoice_number",
          "type": "varchar",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "site_engineer",
          "type": "varchar",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "security_approval",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "remarks",
          "type": "text",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "inward_time",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "created_by_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "vehicle_entry_id",
          "type": "int",
          "tags": [
            "FK",
            "UK"
          ],
          "notes": []
        },
        {
          "name": "material_category_id",
          "type": "int",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        }
      ]
    },
    {
      "name": "construction_gatein_constructionmaterialcategory",
      "app": "construction_gatein",
      "fields": [
        {
          "name": "id",
          "type": "int",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "category_name",
          "type": "varchar",
          "tags": [
            "UK"
          ],
          "notes": []
        },
        {
          "name": "description",
          "type": "text",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "is_active",
          "type": "boolean",
          "tags": [],
          "notes": []
        }
      ]
    },
    {
      "name": "daily_needs_gatein_categorylist",
      "app": "daily_needs_gatein",
      "fields": [
        {
          "name": "id",
          "type": "int",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "category_name",
          "type": "varchar",
          "tags": [
            "UK"
          ],
          "notes": []
        }
      ]
    },
    {
      "name": "daily_needs_gatein_dailyneedgateentry",
      "app": "daily_needs_gatein",
      "fields": [
        {
          "name": "id",
          "type": "int",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "item_category_id",
          "type": "int",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "supplier_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "material_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "quantity",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "unit_id",
          "type": "int",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "receiving_department_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "bill_number",
          "type": "varchar",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "delivery_challan_number",
          "type": "varchar",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "canteen_supervisor",
          "type": "varchar",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "vehicle_or_person_name",
          "type": "varchar",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "contact_number",
          "type": "varchar",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "remarks",
          "type": "text",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "created_by_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "vehicle_entry_id",
          "type": "int",
          "tags": [
            "FK",
            "UK"
          ],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        }
      ]
    },
    {
      "name": "daily_needs_gatein_dailyneedgateentryitem",
      "app": "daily_needs_gatein",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "line_no",
          "type": "int",
          "tags": [],
          "notes": []
        },
        {
          "name": "material_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "quantity",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "daily_need_entry_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "unit_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        }
      ]
    },
    {
      "name": "database_connections_databaseconnection",
      "app": "database_connections",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "key",
          "type": "varchar",
          "tags": [
            "UK"
          ],
          "notes": []
        },
        {
          "name": "name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "database_type",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "environment",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "host",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "port",
          "type": "int",
          "tags": [],
          "notes": []
        },
        {
          "name": "database_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "schema_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "username",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "password_secret_key",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "pool_min_size",
          "type": "int",
          "tags": [],
          "notes": []
        },
        {
          "name": "pool_max_size",
          "type": "int",
          "tags": [],
          "notes": []
        },
        {
          "name": "connect_timeout_seconds",
          "type": "int",
          "tags": [],
          "notes": []
        },
        {
          "name": "options",
          "type": "json",
          "tags": [],
          "notes": []
        },
        {
          "name": "is_active",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "last_health_status",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "last_health_error",
          "type": "text",
          "tags": [],
          "notes": []
        },
        {
          "name": "last_checked_at",
          "type": "datetime",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        }
      ]
    },
    {
      "name": "dispatch_plans_dispatchplan",
      "app": "dispatch_plans",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "is_active",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "sap_invoice_doc_entry",
          "type": "int",
          "tags": [],
          "notes": []
        },
        {
          "name": "sap_invoice_doc_num",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "booking_status",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "dispatch_date",
          "type": "date",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "priority",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "transporter_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "transporter_gstin",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "contact_person",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "mobile_no",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "vehicle_no",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "bilty_no",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "bilty_date",
          "type": "date",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "freight",
          "type": "decimal",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "total_freight",
          "type": "decimal",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "kanta_weight",
          "type": "decimal",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "remarks",
          "type": "text",
          "tags": [],
          "notes": []
        },
        {
          "name": "company_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "created_by_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "updated_by_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "linked_vehicle_entry_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "transporter_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "vehicle_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "driver_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "driver_id_proof_number",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "driver_id_proof_type",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "driver_license_no",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "driver_mobile_no",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "driver_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "bilty_attachment",
          "type": "varchar",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "bilty_attachment_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "eway_bill",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "invoice_amount",
          "type": "decimal",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "invoice_number",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "invoice_weight",
          "type": "decimal",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "place_of_supply",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "budget_delivery_point",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "effective_month",
          "type": "date",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "product_variety",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "sac_code",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "sac_entry",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "service_location_code",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "service_location_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "total_litres",
          "type": "decimal",
          "tags": [],
          "notes": [
            "nullable"
          ]
        }
      ]
    },
    {
      "name": "dispatch_plans_transporterapinvoiceattachment",
      "app": "dispatch_plans",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "file",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "original_filename",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "sap_attachment_status",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "sap_absolute_entry",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "sap_error_message",
          "type": "text",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "uploaded_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "uploaded_by_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "transporter_ap_invoice_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        }
      ]
    },
    {
      "name": "dispatch_plans_transporterapinvoiceline",
      "app": "dispatch_plans",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "base_entry",
          "type": "int",
          "tags": [],
          "notes": []
        },
        {
          "name": "base_line",
          "type": "int",
          "tags": [],
          "notes": []
        },
        {
          "name": "base_doc_num",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "bilty_no",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "service_description",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "line_total",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "tax_code",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "gl_account",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "dispatch_plan_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "service_grpo_line_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "service_grpo_posting_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "transporter_ap_invoice_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        }
      ]
    },
    {
      "name": "dispatch_plans_transporterapinvoiceposting",
      "app": "dispatch_plans",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "is_active",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "vendor_code",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "vendor_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "invoice_number",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "invoice_date",
          "type": "date",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "invoice_amount",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "selected_grpo_total",
          "type": "decimal",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "amount_difference",
          "type": "decimal",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "branch_id",
          "type": "int",
          "tags": [],
          "notes": []
        },
        {
          "name": "sap_doc_entry",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "sap_doc_num",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "sap_doc_total",
          "type": "decimal",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "status",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "error_message",
          "type": "text",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "posted_at",
          "type": "datetime",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "comments",
          "type": "text",
          "tags": [],
          "notes": []
        },
        {
          "name": "company_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "created_by_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "posted_by_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "updated_by_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        }
      ]
    },
    {
      "name": "django_admin_log",
      "app": "django",
      "fields": [
        {
          "name": "id",
          "type": "int",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "action_time",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "object_id",
          "type": "text",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "object_repr",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "action_flag",
          "type": "int",
          "tags": [],
          "notes": []
        },
        {
          "name": "change_message",
          "type": "text",
          "tags": [],
          "notes": []
        },
        {
          "name": "content_type_id",
          "type": "int",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "user_id",
          "type": "int",
          "tags": [],
          "notes": []
        }
      ]
    },
    {
      "name": "django_apscheduler_djangojob",
      "app": "django_apscheduler",
      "fields": [
        {
          "name": "id",
          "type": "varchar",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "next_run_time",
          "type": "datetime",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "job_state",
          "type": "binary",
          "tags": [],
          "notes": []
        }
      ]
    },
    {
      "name": "django_apscheduler_djangojobexecution",
      "app": "django_apscheduler",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "status",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "run_time",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "duration",
          "type": "decimal",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "finished",
          "type": "decimal",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "exception",
          "type": "varchar",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "traceback",
          "type": "text",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "job_id",
          "type": "varchar",
          "tags": [
            "FK"
          ],
          "notes": []
        }
      ]
    },
    {
      "name": "django_content_type",
      "app": "django",
      "fields": [
        {
          "name": "id",
          "type": "int",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "app_label",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "model",
          "type": "varchar",
          "tags": [],
          "notes": []
        }
      ]
    },
    {
      "name": "django_migrations",
      "app": "django",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "app",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "applied",
          "type": "datetime",
          "tags": [],
          "notes": []
        }
      ]
    },
    {
      "name": "django_session",
      "app": "django",
      "fields": [
        {
          "name": "session_key",
          "type": "varchar",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "session_data",
          "type": "text",
          "tags": [],
          "notes": []
        },
        {
          "name": "expire_date",
          "type": "datetime",
          "tags": [],
          "notes": []
        }
      ]
    },
    {
      "name": "driver_management_driver",
      "app": "driver_management",
      "fields": [
        {
          "name": "id",
          "type": "int",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "is_active",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "mobile_no",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "license_no",
          "type": "varchar",
          "tags": [
            "UK"
          ],
          "notes": []
        },
        {
          "name": "id_proof_type",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "id_proof_number",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "photo",
          "type": "varchar",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "created_by_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "updated_by_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        }
      ]
    },
    {
      "name": "driver_management_vehicleentry",
      "app": "driver_management",
      "fields": [
        {
          "name": "id",
          "type": "int",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "is_active",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "entry_no",
          "type": "varchar",
          "tags": [
            "UK"
          ],
          "notes": []
        },
        {
          "name": "status",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "is_locked",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "entry_time",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "remarks",
          "type": "text",
          "tags": [],
          "notes": []
        },
        {
          "name": "created_by_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "driver_id",
          "type": "int",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "updated_by_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "vehicle_id",
          "type": "int",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "company_id",
          "type": "int",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "entry_type",
          "type": "varchar",
          "tags": [],
          "notes": []
        }
      ]
    },
    {
      "name": "gate_core_bstgatein",
      "app": "gate_core",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "is_active",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "entry_no",
          "type": "varchar",
          "tags": [
            "UK"
          ],
          "notes": []
        },
        {
          "name": "gate_in_date",
          "type": "date",
          "tags": [],
          "notes": []
        },
        {
          "name": "in_time",
          "type": "time",
          "tags": [],
          "notes": []
        },
        {
          "name": "security_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "remarks",
          "type": "text",
          "tags": [],
          "notes": []
        },
        {
          "name": "status",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "bst_gate_out_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "company_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "created_by_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "driver_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "updated_by_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "vehicle_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "vehicle_entry_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "sap_receipt_doc_num",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "sap_receipt_doc_date",
          "type": "date",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "sap_receipt_reference",
          "type": "varchar",
          "tags": [],
          "notes": []
        }
      ]
    },
    {
      "name": "gate_core_bstgateinitem",
      "app": "gate_core",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "is_active",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "line_num",
          "type": "int",
          "tags": [],
          "notes": []
        },
        {
          "name": "item_code",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "item_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "quantity",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "actual_quantity",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "receiving_quantity",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "uom",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "from_warehouse",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "to_warehouse",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "bst_gate_in_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "bst_gate_out_item_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "created_by_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "updated_by_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        }
      ]
    },
    {
      "name": "gate_core_bstgateout",
      "app": "gate_core",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "is_active",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "entry_no",
          "type": "varchar",
          "tags": [
            "UK"
          ],
          "notes": []
        },
        {
          "name": "sap_doc_entry",
          "type": "int",
          "tags": [],
          "notes": []
        },
        {
          "name": "sap_doc_num",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "sap_doc_date",
          "type": "date",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "sap_from_warehouse",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "sap_to_warehouse",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "sap_reference",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "sap_comments",
          "type": "text",
          "tags": [],
          "notes": []
        },
        {
          "name": "gate_out_date",
          "type": "date",
          "tags": [],
          "notes": []
        },
        {
          "name": "out_time",
          "type": "time",
          "tags": [],
          "notes": []
        },
        {
          "name": "security_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "remarks",
          "type": "text",
          "tags": [],
          "notes": []
        },
        {
          "name": "status",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "company_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "created_by_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "driver_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "empty_vehicle_gate_in_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "updated_by_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "vehicle_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "vehicle_entry_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "cancel_reason",
          "type": "text",
          "tags": [],
          "notes": []
        },
        {
          "name": "cancelled_at",
          "type": "datetime",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "cancelled_by_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        }
      ]
    },
    {
      "name": "gate_core_bstgateoutitem",
      "app": "gate_core",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "is_active",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "line_num",
          "type": "int",
          "tags": [],
          "notes": []
        },
        {
          "name": "item_code",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "item_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "quantity",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "uom",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "from_warehouse",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "to_warehouse",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "bst_gate_out_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "created_by_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "updated_by_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "actual_quantity",
          "type": "decimal",
          "tags": [],
          "notes": []
        }
      ]
    },
    {
      "name": "gate_core_bstgatereturn",
      "app": "gate_core",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "is_active",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "entry_no",
          "type": "varchar",
          "tags": [
            "UK"
          ],
          "notes": []
        },
        {
          "name": "gate_in_date",
          "type": "date",
          "tags": [],
          "notes": []
        },
        {
          "name": "in_time",
          "type": "time",
          "tags": [],
          "notes": []
        },
        {
          "name": "security_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "remarks",
          "type": "text",
          "tags": [],
          "notes": []
        },
        {
          "name": "status",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "bst_gate_out_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "company_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "created_by_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "driver_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "updated_by_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "vehicle_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "vehicle_entry_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "sap_return_doc_num",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "sap_return_doc_date",
          "type": "date",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "sap_return_reference",
          "type": "varchar",
          "tags": [],
          "notes": []
        }
      ]
    },
    {
      "name": "gate_core_dispatchgatelock",
      "app": "gate_core",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "is_active",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "locked",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "reason",
          "type": "text",
          "tags": [],
          "notes": []
        },
        {
          "name": "locked_at",
          "type": "datetime",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "unlocked_at",
          "type": "datetime",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "changed_by_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "company_id",
          "type": "bigint",
          "tags": [
            "FK",
            "UK"
          ],
          "notes": []
        },
        {
          "name": "created_by_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "updated_by_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        }
      ]
    },
    {
      "name": "gate_core_dispatchgateout",
      "app": "gate_core",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "is_active",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "entry_no",
          "type": "varchar",
          "tags": [
            "UK"
          ],
          "notes": []
        },
        {
          "name": "sap_invoice_doc_entry",
          "type": "int",
          "tags": [],
          "notes": []
        },
        {
          "name": "sap_invoice_doc_num",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "customer_code",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "customer_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "ship_to_address",
          "type": "text",
          "tags": [],
          "notes": []
        },
        {
          "name": "invoice_amount",
          "type": "decimal",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "sap_weight",
          "type": "decimal",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "gate_out_date",
          "type": "date",
          "tags": [],
          "notes": []
        },
        {
          "name": "out_time",
          "type": "time",
          "tags": [],
          "notes": []
        },
        {
          "name": "security_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "seal_no",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "pgi_document_no",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "goods_issue_posted",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "invoice_checked",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "delivery_note_checked",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "eway_bill_checked",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "lr_checked",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "physical_quantity",
          "type": "decimal",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "physical_uom",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "gross_weight",
          "type": "decimal",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "tare_weight",
          "type": "decimal",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "net_weight",
          "type": "decimal",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "weighbridge_slip_no",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "first_weighment_time",
          "type": "datetime",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "second_weighment_time",
          "type": "datetime",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "dock_photo",
          "type": "varchar",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "gatepass_document",
          "type": "varchar",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "attachment_notes",
          "type": "text",
          "tags": [],
          "notes": []
        },
        {
          "name": "remarks",
          "type": "text",
          "tags": [],
          "notes": []
        },
        {
          "name": "gatepass_no",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "gatepass_code",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "gate_printed",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "print_commit",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "printed_at",
          "type": "datetime",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "committed_at",
          "type": "datetime",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "status",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "cancel_reason",
          "type": "text",
          "tags": [],
          "notes": []
        },
        {
          "name": "cancelled_at",
          "type": "datetime",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "rejected_reason",
          "type": "text",
          "tags": [],
          "notes": []
        },
        {
          "name": "rejected_at",
          "type": "datetime",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "company_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "created_by_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "dispatch_plan_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "driver_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "updated_by_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "vehicle_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "vehicle_entry_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        }
      ]
    },
    {
      "name": "gate_core_dispatchgateoutline",
      "app": "gate_core",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "is_active",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "line_num",
          "type": "int",
          "tags": [],
          "notes": []
        },
        {
          "name": "item_code",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "item_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "order_qty",
          "type": "decimal",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "dispatched_qty",
          "type": "decimal",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "uom",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "warehouse",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "created_by_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "entry_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "updated_by_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        }
      ]
    },
    {
      "name": "gate_core_emptyvehiclegatein",
      "app": "gate_core",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "is_active",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "entry_no",
          "type": "varchar",
          "tags": [
            "UK"
          ],
          "notes": []
        },
        {
          "name": "reason",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "gate_in_date",
          "type": "date",
          "tags": [],
          "notes": []
        },
        {
          "name": "in_time",
          "type": "time",
          "tags": [],
          "notes": []
        },
        {
          "name": "security_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "remarks",
          "type": "text",
          "tags": [],
          "notes": []
        },
        {
          "name": "company_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "created_by_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "driver_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "updated_by_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "vehicle_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "vehicle_entry_id",
          "type": "bigint",
          "tags": [
            "FK",
            "UK"
          ],
          "notes": []
        },
        {
          "name": "document_notes",
          "type": "text",
          "tags": [],
          "notes": []
        },
        {
          "name": "document_reference",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "sap_comments",
          "type": "text",
          "tags": [],
          "notes": []
        },
        {
          "name": "sap_doc_date",
          "type": "date",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "sap_doc_entry",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "sap_doc_num",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "sap_from_warehouse",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "sap_line_count",
          "type": "int",
          "tags": [],
          "notes": []
        },
        {
          "name": "sap_reference",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "sap_to_warehouse",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "sap_total_quantity",
          "type": "decimal",
          "tags": [],
          "notes": []
        }
      ]
    },
    {
      "name": "gate_core_emptyvehiclegateinitem",
      "app": "gate_core",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "is_active",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "line_num",
          "type": "int",
          "tags": [],
          "notes": []
        },
        {
          "name": "item_code",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "item_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "sap_quantity",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "actual_quantity",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "uom",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "from_warehouse",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "to_warehouse",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "created_by_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "empty_vehicle_gate_in_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "updated_by_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        }
      ]
    },
    {
      "name": "gate_core_emptyvehiclegateout",
      "app": "gate_core",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "is_active",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "entry_no",
          "type": "varchar",
          "tags": [
            "UK"
          ],
          "notes": []
        },
        {
          "name": "gate_out_date",
          "type": "date",
          "tags": [],
          "notes": []
        },
        {
          "name": "out_time",
          "type": "time",
          "tags": [],
          "notes": []
        },
        {
          "name": "security_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "remarks",
          "type": "text",
          "tags": [],
          "notes": []
        },
        {
          "name": "status",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "company_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "created_by_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "driver_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "updated_by_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "vehicle_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "vehicle_entry_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "cancel_reason",
          "type": "text",
          "tags": [],
          "notes": []
        },
        {
          "name": "cancelled_at",
          "type": "datetime",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "cancelled_by_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        }
      ]
    },
    {
      "name": "gate_core_gateattachment",
      "app": "gate_core",
      "fields": [
        {
          "name": "id",
          "type": "int",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "file",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "uploaded_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "gate_entry_id",
          "type": "int",
          "tags": [
            "FK"
          ],
          "notes": []
        }
      ]
    },
    {
      "name": "gate_core_jobworkgatein",
      "app": "gate_core",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "is_active",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "entry_no",
          "type": "varchar",
          "tags": [
            "UK"
          ],
          "notes": []
        },
        {
          "name": "sap_doc_entry",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "sap_doc_num",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "sap_doc_date",
          "type": "date",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "sap_supplier_code",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "sap_supplier_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "sap_reference",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "sap_comments",
          "type": "text",
          "tags": [],
          "notes": []
        },
        {
          "name": "sap_branch_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "gate_in_date",
          "type": "date",
          "tags": [],
          "notes": []
        },
        {
          "name": "in_time",
          "type": "time",
          "tags": [],
          "notes": []
        },
        {
          "name": "security_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "remarks",
          "type": "text",
          "tags": [],
          "notes": []
        },
        {
          "name": "status",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "company_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "created_by_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "driver_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "updated_by_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "vehicle_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "vehicle_entry_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "sap_doc_time",
          "type": "time",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "production_order_doc_entry",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "production_order_doc_num",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "production_item_code",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "production_item_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "production_planned_qty",
          "type": "decimal",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "production_completed_qty",
          "type": "decimal",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "production_rejected_qty",
          "type": "decimal",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "production_remaining_qty",
          "type": "decimal",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "production_start_date",
          "type": "date",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "production_due_date",
          "type": "date",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "production_warehouse",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "production_status",
          "type": "varchar",
          "tags": [],
          "notes": []
        }
      ]
    },
    {
      "name": "gate_core_jobworkgateinitem",
      "app": "gate_core",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "is_active",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "line_num",
          "type": "int",
          "tags": [],
          "notes": []
        },
        {
          "name": "item_code",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "item_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "quantity",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "uom",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "warehouse_code",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "base_type",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "base_entry",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "base_line",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "created_by_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "job_work_gate_in_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "updated_by_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        }
      ]
    },
    {
      "name": "gate_core_rejectedqcreturnentry",
      "app": "gate_core",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "is_active",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "entry_no",
          "type": "varchar",
          "tags": [
            "UK"
          ],
          "notes": []
        },
        {
          "name": "gate_out_date",
          "type": "date",
          "tags": [],
          "notes": []
        },
        {
          "name": "out_time",
          "type": "time",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "challan_no",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "eway_bill_no",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "manual_sap_reference",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "security_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "remarks",
          "type": "text",
          "tags": [],
          "notes": []
        },
        {
          "name": "status",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "company_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "created_by_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "driver_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "updated_by_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "vehicle_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "gross_weight",
          "type": "decimal",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "tare_weight",
          "type": "decimal",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "net_weight",
          "type": "decimal",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "weighbridge_slip_no",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "first_weighment_time",
          "type": "datetime",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "second_weighment_time",
          "type": "datetime",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "gatepass_documents",
          "type": "json",
          "tags": [],
          "notes": []
        }
      ]
    },
    {
      "name": "gate_core_rejectedqcreturnitem",
      "app": "gate_core",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "is_active",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "gate_entry_no",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "report_no",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "internal_lot_no",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "item_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "supplier_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "quantity",
          "type": "decimal",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "uom",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "created_by_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "entry_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "inspection_id",
          "type": "bigint",
          "tags": [
            "FK",
            "UK"
          ],
          "notes": []
        },
        {
          "name": "updated_by_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        }
      ]
    },
    {
      "name": "gate_core_unitchoice",
      "app": "gate_core",
      "fields": [
        {
          "name": "id",
          "type": "int",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "name",
          "type": "varchar",
          "tags": [
            "UK"
          ],
          "notes": []
        }
      ]
    },
    {
      "name": "grpo_grpoattachment",
      "app": "grpo",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "file",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "original_filename",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "sap_attachment_status",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "sap_absolute_entry",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "sap_error_message",
          "type": "text",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "uploaded_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "grpo_posting_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "uploaded_by_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        }
      ]
    },
    {
      "name": "grpo_grpolineposting",
      "app": "grpo",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "quantity_posted",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "base_entry",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "base_line",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "po_item_receipt_id",
          "type": "int",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "grpo_posting_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        }
      ]
    },
    {
      "name": "grpo_grpoposting",
      "app": "grpo",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "sap_doc_entry",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "sap_doc_num",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "sap_doc_total",
          "type": "decimal",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "status",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "error_message",
          "type": "text",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "posted_at",
          "type": "datetime",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "po_receipt_id",
          "type": "int",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "posted_by_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "vehicle_entry_id",
          "type": "int",
          "tags": [
            "FK"
          ],
          "notes": []
        }
      ]
    },
    {
      "name": "grpo_grpoposting_po_receipts",
      "app": "grpo",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "grpoposting_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "poreceipt_id",
          "type": "int",
          "tags": [
            "FK"
          ],
          "notes": []
        }
      ]
    },
    {
      "name": "grpo_servicegrpoattachment",
      "app": "grpo",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "file",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "original_filename",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "sap_attachment_status",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "sap_absolute_entry",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "sap_error_message",
          "type": "text",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "uploaded_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "uploaded_by_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "service_grpo_posting_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        }
      ]
    },
    {
      "name": "grpo_servicegrpolineposting",
      "app": "grpo",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "service_description",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "amount",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "tax_code",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "gl_account",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "service_grpo_posting_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "location_code",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "location_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "product_variety",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "project_code",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "sac_code",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "sac_entry",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "total_litres",
          "type": "decimal",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "unit_price",
          "type": "decimal",
          "tags": [],
          "notes": [
            "nullable"
          ]
        }
      ]
    },
    {
      "name": "grpo_servicegrpoposting",
      "app": "grpo",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "vendor_code",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "vendor_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "sap_doc_entry",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "sap_doc_num",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "sap_doc_total",
          "type": "decimal",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "status",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "error_message",
          "type": "text",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "posted_at",
          "type": "datetime",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "dispatch_plan_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "posted_by_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "budget_delivery_point",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "effective_month",
          "type": "date",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "location_code",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "location_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "place_of_supply",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "product_variety",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "sac_code",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "sac_entry",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "total_litres",
          "type": "decimal",
          "tags": [],
          "notes": [
            "nullable"
          ]
        }
      ]
    },
    {
      "name": "inventory_sapbatchstock",
      "app": "inventory",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "item_code",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "item_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "system_number",
          "type": "int",
          "tags": [],
          "notes": []
        },
        {
          "name": "batch_number",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "warehouse_code",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "warehouse_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "manufacturing_date",
          "type": "date",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "expiry_date",
          "type": "date",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "admission_date",
          "type": "date",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "status",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "batch_quantity",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "batch_balance",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "warehouse_quantity",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "committed_quantity",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "last_synced_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "company_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        }
      ]
    },
    {
      "name": "inventory_sapcompany",
      "app": "inventory",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "key",
          "type": "varchar",
          "tags": [
            "UK"
          ],
          "notes": []
        },
        {
          "name": "env_key",
          "type": "varchar",
          "tags": [
            "UK"
          ],
          "notes": []
        },
        {
          "name": "label",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "database",
          "type": "varchar",
          "tags": [
            "UK"
          ],
          "notes": []
        },
        {
          "name": "hana_ok",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "last_seen_at",
          "type": "datetime",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        }
      ]
    },
    {
      "name": "inventory_sapinventoryagingsnapshot",
      "app": "inventory",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "item_code",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "item_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "warehouse_code",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "warehouse_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "on_hand",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "inventory_value",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "last_movement_date",
          "type": "date",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "days_since_movement",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "aging_bucket",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "last_synced_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "company_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        }
      ]
    },
    {
      "name": "inventory_sapinventorymovement",
      "app": "inventory",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "movement_type",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "doc_entry",
          "type": "int",
          "tags": [],
          "notes": []
        },
        {
          "name": "doc_num",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "doc_date",
          "type": "date",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "doc_status",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "card_code",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "card_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "journal_trans_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "comments",
          "type": "text",
          "tags": [],
          "notes": []
        },
        {
          "name": "line_num",
          "type": "int",
          "tags": [],
          "notes": []
        },
        {
          "name": "item_code",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "item_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "warehouse_code",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "from_warehouse_code",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "to_warehouse_code",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "quantity_in",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "quantity_out",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "unit_price",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "line_total",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "last_synced_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "company_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        }
      ]
    },
    {
      "name": "inventory_sapinventoryvaluation",
      "app": "inventory",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "trans_seq",
          "type": "int",
          "tags": [],
          "notes": []
        },
        {
          "name": "trans_type",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "created_by",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "base_ref",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "doc_line_num",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "doc_date",
          "type": "date",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "create_date",
          "type": "date",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "item_code",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "warehouse_code",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "in_qty",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "out_qty",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "price",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "currency",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "rate",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "open_stock",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "inventory_account",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "cost_account",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "cost_method",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "message_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "trans_num",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "layer_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "root_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "last_synced_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "company_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        }
      ]
    },
    {
      "name": "inventory_sapitem",
      "app": "inventory",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "item_code",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "item_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "foreign_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "item_group_code",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "item_group_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "barcode",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "default_warehouse",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "supplier_code",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "purchase_item",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "sales_item",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "inventory_item",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "valid_for",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "frozen_for",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "min_level",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "max_level",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "avg_price",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "last_purchase_price",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "last_purchase_date",
          "type": "date",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "warehouse_count",
          "type": "int",
          "tags": [],
          "notes": []
        },
        {
          "name": "on_hand",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "committed",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "ordered",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "available",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "projected_available",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "inventory_value",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "stock_status",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "last_synced_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "company_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        }
      ]
    },
    {
      "name": "inventory_sapitemgroup",
      "app": "inventory",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "group_code",
          "type": "int",
          "tags": [],
          "notes": []
        },
        {
          "name": "group_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "locked",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "last_synced_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "company_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        }
      ]
    },
    {
      "name": "inventory_sapitemwarehousestock",
      "app": "inventory",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "item_code",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "warehouse_code",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "item_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "item_group_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "warehouse_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "on_hand",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "committed",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "ordered",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "available",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "projected_available",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "min_stock",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "max_stock",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "min_order",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "avg_price",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "inventory_value",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "locked",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "stock_status",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "last_synced_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "company_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        }
      ]
    },
    {
      "name": "inventory_sapsyncrun",
      "app": "inventory",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "module",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "status",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "sections",
          "type": "json",
          "tags": [],
          "notes": []
        },
        {
          "name": "started_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "finished_at",
          "type": "datetime",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "records_read",
          "type": "int",
          "tags": [],
          "notes": []
        },
        {
          "name": "records_upserted",
          "type": "int",
          "tags": [],
          "notes": []
        },
        {
          "name": "errors",
          "type": "json",
          "tags": [],
          "notes": []
        },
        {
          "name": "company_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        }
      ]
    },
    {
      "name": "inventory_sapwarehouse",
      "app": "inventory",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "warehouse_code",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "warehouse_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "city",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "state",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "country",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "inactive",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "stock_rows",
          "type": "int",
          "tags": [],
          "notes": []
        },
        {
          "name": "sku_count",
          "type": "int",
          "tags": [],
          "notes": []
        },
        {
          "name": "on_hand",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "committed",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "ordered",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "inventory_value",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "low_stock_rows",
          "type": "int",
          "tags": [],
          "notes": []
        },
        {
          "name": "out_of_stock_rows",
          "type": "int",
          "tags": [],
          "notes": []
        },
        {
          "name": "last_synced_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "company_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        }
      ]
    },
    {
      "name": "labour_verification_departmentlabourresponse",
      "app": "labour_verification",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "labour_count",
          "type": "int",
          "tags": [],
          "notes": []
        },
        {
          "name": "labour_details",
          "type": "json",
          "tags": [],
          "notes": []
        },
        {
          "name": "remarks",
          "type": "text",
          "tags": [],
          "notes": []
        },
        {
          "name": "status",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "submitted_at",
          "type": "datetime",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "department_id",
          "type": "bigint",
          "tags": [],
          "notes": []
        },
        {
          "name": "submitted_by_id",
          "type": "bigint",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "verification_request_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        }
      ]
    },
    {
      "name": "labour_verification_labourverificationrequest",
      "app": "labour_verification",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "date",
          "type": "date",
          "tags": [
            "UK"
          ],
          "notes": []
        },
        {
          "name": "status",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "closed_at",
          "type": "datetime",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "remarks",
          "type": "text",
          "tags": [],
          "notes": []
        },
        {
          "name": "created_by_id",
          "type": "bigint",
          "tags": [],
          "notes": [
            "nullable"
          ]
        }
      ]
    },
    {
      "name": "mail_emaillog",
      "app": "mail",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "recipient_email",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "subject",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "body",
          "type": "text",
          "tags": [],
          "notes": []
        },
        {
          "name": "email_type",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "click_action_url",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "reference_type",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "reference_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "template_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "extra_data",
          "type": "json",
          "tags": [],
          "notes": []
        },
        {
          "name": "status",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "error_message",
          "type": "text",
          "tags": [],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "company_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "created_by_id",
          "type": "bigint",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "recipient_id",
          "type": "bigint",
          "tags": [],
          "notes": [
            "nullable"
          ]
        }
      ]
    },
    {
      "name": "maintenance_gatein_maintenancegateentry",
      "app": "maintenance_gatein",
      "fields": [
        {
          "name": "id",
          "type": "int",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "work_order_number",
          "type": "varchar",
          "tags": [
            "UK"
          ],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "supplier_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "material_description",
          "type": "text",
          "tags": [],
          "notes": []
        },
        {
          "name": "part_number",
          "type": "varchar",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "quantity",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "unit_id",
          "type": "int",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "invoice_number",
          "type": "varchar",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "equipment_id",
          "type": "varchar",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "urgency_level",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "inward_time",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "remarks",
          "type": "text",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "created_by_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "receiving_department_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "vehicle_entry_id",
          "type": "int",
          "tags": [
            "FK",
            "UK"
          ],
          "notes": []
        },
        {
          "name": "maintenance_type_id",
          "type": "int",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        }
      ]
    },
    {
      "name": "maintenance_gatein_maintenancetype",
      "app": "maintenance_gatein",
      "fields": [
        {
          "name": "id",
          "type": "int",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "type_name",
          "type": "varchar",
          "tags": [
            "UK"
          ],
          "notes": []
        },
        {
          "name": "description",
          "type": "text",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "is_active",
          "type": "boolean",
          "tags": [],
          "notes": []
        }
      ]
    },
    {
      "name": "notifications_notification",
      "app": "notifications",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "title",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "body",
          "type": "text",
          "tags": [],
          "notes": []
        },
        {
          "name": "notification_type",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "click_action_url",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "reference_type",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "reference_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "is_read",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "read_at",
          "type": "datetime",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "extra_data",
          "type": "json",
          "tags": [],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "company_id",
          "type": "int",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "created_by_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "recipient_id",
          "type": "int",
          "tags": [],
          "notes": []
        }
      ]
    },
    {
      "name": "notifications_userdevice",
      "app": "notifications",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "fcm_token",
          "type": "text",
          "tags": [
            "UK"
          ],
          "notes": []
        },
        {
          "name": "device_type",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "device_info",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "is_active",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "last_used_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "user_id",
          "type": "int",
          "tags": [],
          "notes": []
        }
      ]
    },
    {
      "name": "outbound_dispatch_goodsissueposting",
      "app": "outbound_dispatch",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "is_active",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "sap_doc_entry",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "sap_doc_num",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "status",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "posted_at",
          "type": "datetime",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "error_message",
          "type": "text",
          "tags": [],
          "notes": []
        },
        {
          "name": "retry_count",
          "type": "int",
          "tags": [],
          "notes": []
        },
        {
          "name": "created_by_id",
          "type": "bigint",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "posted_by_id",
          "type": "bigint",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "updated_by_id",
          "type": "bigint",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "shipment_order_id",
          "type": "bigint",
          "tags": [
            "FK",
            "UK"
          ],
          "notes": []
        }
      ]
    },
    {
      "name": "outbound_dispatch_outboundloadrecord",
      "app": "outbound_dispatch",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "is_active",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "trailer_condition",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "trailer_temp_ok",
          "type": "boolean",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "trailer_temp_reading",
          "type": "decimal",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "inspected_at",
          "type": "datetime",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "loading_started_at",
          "type": "datetime",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "loading_completed_at",
          "type": "datetime",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "supervisor_confirmed",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "confirmed_at",
          "type": "datetime",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "created_by_id",
          "type": "bigint",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "inspected_by_id",
          "type": "bigint",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "loaded_by_id",
          "type": "bigint",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "supervisor_id",
          "type": "bigint",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "updated_by_id",
          "type": "bigint",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "shipment_order_id",
          "type": "bigint",
          "tags": [
            "FK",
            "UK"
          ],
          "notes": []
        }
      ]
    },
    {
      "name": "outbound_dispatch_picktask",
      "app": "outbound_dispatch",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "is_active",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "pick_location",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "pick_qty",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "actual_qty",
          "type": "decimal",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "status",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "picked_at",
          "type": "datetime",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "scanned_barcode",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "assigned_to_id",
          "type": "bigint",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "created_by_id",
          "type": "bigint",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "updated_by_id",
          "type": "bigint",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "shipment_item_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        }
      ]
    },
    {
      "name": "outbound_dispatch_shipmentorder",
      "app": "outbound_dispatch",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "is_active",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "sap_doc_entry",
          "type": "int",
          "tags": [],
          "notes": []
        },
        {
          "name": "sap_doc_num",
          "type": "int",
          "tags": [],
          "notes": []
        },
        {
          "name": "customer_code",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "customer_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "ship_to_address",
          "type": "text",
          "tags": [],
          "notes": []
        },
        {
          "name": "carrier_code",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "carrier_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "scheduled_date",
          "type": "date",
          "tags": [],
          "notes": []
        },
        {
          "name": "dock_bay",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "dock_slot_start",
          "type": "datetime",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "dock_slot_end",
          "type": "datetime",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "status",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "bill_of_lading_no",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "seal_number",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "total_weight",
          "type": "decimal",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "notes",
          "type": "text",
          "tags": [],
          "notes": []
        },
        {
          "name": "company_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "created_by_id",
          "type": "bigint",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "updated_by_id",
          "type": "bigint",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "vehicle_entry_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        }
      ]
    },
    {
      "name": "outbound_dispatch_shipmentorderitem",
      "app": "outbound_dispatch",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "is_active",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "sap_line_num",
          "type": "int",
          "tags": [],
          "notes": []
        },
        {
          "name": "item_code",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "item_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "ordered_qty",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "picked_qty",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "packed_qty",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "loaded_qty",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "uom",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "warehouse_code",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "batch_number",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "weight",
          "type": "decimal",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "pick_status",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "created_by_id",
          "type": "bigint",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "shipment_order_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "updated_by_id",
          "type": "bigint",
          "tags": [],
          "notes": [
            "nullable"
          ]
        }
      ]
    },
    {
      "name": "outbound_gatein_outboundgateentry",
      "app": "outbound_gatein",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "sales_order_ref",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "customer_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "customer_code",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "transporter_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "transporter_contact",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "lr_number",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "vehicle_empty_confirmed",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "trailer_type",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "trailer_length_ft",
          "type": "decimal",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "assigned_zone",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "assigned_bay",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "expected_loading_time",
          "type": "datetime",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "arrival_time",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "released_for_loading_at",
          "type": "datetime",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "exit_time",
          "type": "datetime",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "remarks",
          "type": "text",
          "tags": [],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "created_by_id",
          "type": "bigint",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "vehicle_entry_id",
          "type": "bigint",
          "tags": [
            "FK",
            "UK"
          ],
          "notes": []
        },
        {
          "name": "purpose_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        }
      ]
    },
    {
      "name": "outbound_gatein_outboundpurpose",
      "app": "outbound_gatein",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "name",
          "type": "varchar",
          "tags": [
            "UK"
          ],
          "notes": []
        },
        {
          "name": "description",
          "type": "text",
          "tags": [],
          "notes": []
        },
        {
          "name": "is_active",
          "type": "boolean",
          "tags": [],
          "notes": []
        }
      ]
    },
    {
      "name": "person_gatein_contractor",
      "app": "person_gatein",
      "fields": [
        {
          "name": "id",
          "type": "int",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "contractor_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "contact_person",
          "type": "varchar",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "mobile",
          "type": "varchar",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "address",
          "type": "text",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "contract_valid_till",
          "type": "date",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "is_active",
          "type": "boolean",
          "tags": [],
          "notes": []
        }
      ]
    },
    {
      "name": "person_gatein_entrylog",
      "app": "person_gatein",
      "fields": [
        {
          "name": "id",
          "type": "int",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "name_snapshot",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "photo_snapshot",
          "type": "varchar",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "entry_time",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "exit_time",
          "type": "datetime",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "purpose",
          "type": "varchar",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "vehicle_no",
          "type": "varchar",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "remarks",
          "type": "text",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "status",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "approved_by_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "created_by_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "gate_in_id",
          "type": "int",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "gate_out_id",
          "type": "int",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "labour_id",
          "type": "int",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "person_type_id",
          "type": "int",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "visitor_id",
          "type": "int",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "actual_entry_time",
          "type": "datetime",
          "tags": [],
          "notes": [
            "nullable"
          ]
        }
      ]
    },
    {
      "name": "person_gatein_gate",
      "app": "person_gatein",
      "fields": [
        {
          "name": "id",
          "type": "int",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "location",
          "type": "varchar",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "is_active",
          "type": "boolean",
          "tags": [],
          "notes": []
        }
      ]
    },
    {
      "name": "person_gatein_labour",
      "app": "person_gatein",
      "fields": [
        {
          "name": "id",
          "type": "int",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "mobile",
          "type": "varchar",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "id_proof_no",
          "type": "varchar",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "photo",
          "type": "varchar",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "skill_type",
          "type": "varchar",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "permit_valid_till",
          "type": "date",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "is_active",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "contractor_id",
          "type": "int",
          "tags": [
            "FK"
          ],
          "notes": []
        }
      ]
    },
    {
      "name": "person_gatein_persontype",
      "app": "person_gatein",
      "fields": [
        {
          "name": "id",
          "type": "int",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "name",
          "type": "varchar",
          "tags": [
            "UK"
          ],
          "notes": []
        },
        {
          "name": "is_active",
          "type": "boolean",
          "tags": [],
          "notes": []
        }
      ]
    },
    {
      "name": "person_gatein_visitor",
      "app": "person_gatein",
      "fields": [
        {
          "name": "id",
          "type": "int",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "mobile",
          "type": "varchar",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "company_name",
          "type": "varchar",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "id_proof_type",
          "type": "varchar",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "id_proof_no",
          "type": "varchar",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "photo",
          "type": "varchar",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "blacklisted",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        }
      ]
    },
    {
      "name": "production_execution_breakdowncategory",
      "app": "production_execution",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "is_active",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "company_id",
          "type": "int",
          "tags": [
            "FK"
          ],
          "notes": []
        }
      ]
    },
    {
      "name": "production_execution_finalqccheck",
      "app": "production_execution",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "checked_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "overall_result",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "parameters",
          "type": "json",
          "tags": [],
          "notes": []
        },
        {
          "name": "remarks",
          "type": "text",
          "tags": [],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "checked_by_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "production_run_id",
          "type": "bigint",
          "tags": [
            "FK",
            "UK"
          ],
          "notes": []
        }
      ]
    },
    {
      "name": "production_execution_inprocessqccheck",
      "app": "production_execution",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "checked_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "parameter",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "acceptable_min",
          "type": "decimal",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "acceptable_max",
          "type": "decimal",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "actual_value",
          "type": "decimal",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "result",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "remarks",
          "type": "text",
          "tags": [],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "checked_by_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "production_run_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        }
      ]
    },
    {
      "name": "production_execution_lineclearance",
      "app": "production_execution",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "date",
          "type": "date",
          "tags": [],
          "notes": []
        },
        {
          "name": "document_id",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "qa_approved",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "qa_approved_at",
          "type": "datetime",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "production_supervisor_sign",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "status",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "company_id",
          "type": "int",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "created_by_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "qa_approved_by_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "verified_by_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "line_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "production_run_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "all_checks_passed",
          "type": "boolean",
          "tags": [],
          "notes": []
        }
      ]
    },
    {
      "name": "production_execution_lineclearanceitem",
      "app": "production_execution",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "checkpoint",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "sort_order",
          "type": "int",
          "tags": [],
          "notes": []
        },
        {
          "name": "result",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "remarks",
          "type": "text",
          "tags": [],
          "notes": []
        },
        {
          "name": "clearance_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        }
      ]
    },
    {
      "name": "production_execution_lineskuconfig",
      "app": "production_execution",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "sku_code",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "sku_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "rated_speed",
          "type": "decimal",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "labour_count",
          "type": "int",
          "tags": [],
          "notes": []
        },
        {
          "name": "other_manpower_count",
          "type": "int",
          "tags": [],
          "notes": []
        },
        {
          "name": "supervisor",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "operators",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "is_active",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "company_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "line_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "config_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "electricity_cost_per_unit",
          "type": "decimal",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "labour_cost_per_hour",
          "type": "decimal",
          "tags": [],
          "notes": [
            "nullable"
          ]
        }
      ]
    },
    {
      "name": "production_execution_machine",
      "app": "production_execution",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "machine_type",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "is_active",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "company_id",
          "type": "int",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "line_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        }
      ]
    },
    {
      "name": "production_execution_machinebreakdown",
      "app": "production_execution",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "start_time",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "end_time",
          "type": "datetime",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "breakdown_minutes",
          "type": "int",
          "tags": [],
          "notes": []
        },
        {
          "name": "is_unrecovered",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "reason",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "remarks",
          "type": "text",
          "tags": [],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "machine_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "production_run_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "is_active",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "breakdown_category_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        }
      ]
    },
    {
      "name": "production_execution_machinechecklistentry",
      "app": "production_execution",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "machine_type",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "date",
          "type": "date",
          "tags": [],
          "notes": []
        },
        {
          "name": "month",
          "type": "int",
          "tags": [],
          "notes": []
        },
        {
          "name": "year",
          "type": "int",
          "tags": [],
          "notes": []
        },
        {
          "name": "task_description",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "frequency",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "status",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "operator",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "shift_incharge",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "remarks",
          "type": "text",
          "tags": [],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "company_id",
          "type": "int",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "machine_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "template_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        }
      ]
    },
    {
      "name": "production_execution_machinechecklisttemplate",
      "app": "production_execution",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "machine_type",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "task",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "frequency",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "sort_order",
          "type": "int",
          "tags": [],
          "notes": []
        },
        {
          "name": "is_active",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "company_id",
          "type": "int",
          "tags": [
            "FK"
          ],
          "notes": []
        }
      ]
    },
    {
      "name": "production_execution_machineruntime",
      "app": "production_execution",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "machine_type",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "runtime_minutes",
          "type": "int",
          "tags": [],
          "notes": []
        },
        {
          "name": "downtime_minutes",
          "type": "int",
          "tags": [],
          "notes": []
        },
        {
          "name": "remarks",
          "type": "text",
          "tags": [],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "machine_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "production_run_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        }
      ]
    },
    {
      "name": "production_execution_productionline",
      "app": "production_execution",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "description",
          "type": "text",
          "tags": [],
          "notes": []
        },
        {
          "name": "is_active",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "company_id",
          "type": "int",
          "tags": [
            "FK"
          ],
          "notes": []
        }
      ]
    },
    {
      "name": "production_execution_productionmanpower",
      "app": "production_execution",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "shift",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "worker_count",
          "type": "int",
          "tags": [],
          "notes": []
        },
        {
          "name": "supervisor",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "engineer",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "remarks",
          "type": "text",
          "tags": [],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "production_run_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        }
      ]
    },
    {
      "name": "production_execution_productionmaterialusage",
      "app": "production_execution",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "material_code",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "material_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "opening_qty",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "issued_qty",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "closing_qty",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "wastage_qty",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "uom",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "production_run_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        }
      ]
    },
    {
      "name": "production_execution_productionrun",
      "app": "production_execution",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "run_number",
          "type": "int",
          "tags": [],
          "notes": []
        },
        {
          "name": "date",
          "type": "date",
          "tags": [],
          "notes": []
        },
        {
          "name": "rated_speed",
          "type": "decimal",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "total_production",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "total_breakdown_time",
          "type": "int",
          "tags": [],
          "notes": []
        },
        {
          "name": "status",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "company_id",
          "type": "int",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "created_by_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "line_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "sap_doc_entry",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "total_running_minutes",
          "type": "int",
          "tags": [],
          "notes": []
        },
        {
          "name": "labour_count",
          "type": "int",
          "tags": [],
          "notes": []
        },
        {
          "name": "operators",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "other_manpower_count",
          "type": "int",
          "tags": [],
          "notes": []
        },
        {
          "name": "product",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "supervisor",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "rejected_qty",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "reworked_qty",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "sap_receipt_doc_entry",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "sap_sync_error",
          "type": "text",
          "tags": [],
          "notes": []
        },
        {
          "name": "sap_sync_status",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "required_qty",
          "type": "decimal",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "warehouse_approval_status",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "electricity_cost_per_unit",
          "type": "decimal",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "labour_cost_per_hour",
          "type": "decimal",
          "tags": [],
          "notes": [
            "nullable"
          ]
        }
      ]
    },
    {
      "name": "production_execution_productionrun_machines",
      "app": "production_execution",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "productionrun_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "machine_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        }
      ]
    },
    {
      "name": "production_execution_productionruncost",
      "app": "production_execution",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "raw_material_cost",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "labour_cost",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "machine_cost",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "electricity_cost",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "water_cost",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "gas_cost",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "compressed_air_cost",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "overhead_cost",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "total_cost",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "produced_qty",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "per_unit_cost",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "calculated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "production_run_id",
          "type": "bigint",
          "tags": [
            "FK",
            "UK"
          ],
          "notes": []
        }
      ]
    },
    {
      "name": "production_execution_productionsegment",
      "app": "production_execution",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "start_time",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "end_time",
          "type": "datetime",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "produced_cases",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "is_active",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "production_run_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "remarks",
          "type": "text",
          "tags": [],
          "notes": []
        }
      ]
    },
    {
      "name": "production_execution_resourcecompressedair",
      "app": "production_execution",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "description",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "units_consumed",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "rate_per_unit",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "total_cost",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "created_by_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "production_run_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        }
      ]
    },
    {
      "name": "production_execution_resourceelectricity",
      "app": "production_execution",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "description",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "units_consumed",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "rate_per_unit",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "total_cost",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "created_by_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "production_run_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        }
      ]
    },
    {
      "name": "production_execution_resourcegas",
      "app": "production_execution",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "description",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "qty_consumed",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "rate_per_unit",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "total_cost",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "created_by_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "production_run_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        }
      ]
    },
    {
      "name": "production_execution_resourcelabour",
      "app": "production_execution",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "hours_worked",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "rate_per_hour",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "total_cost",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "created_by_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "production_run_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "description",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "worker_count",
          "type": "int",
          "tags": [],
          "notes": []
        }
      ]
    },
    {
      "name": "production_execution_resourcemachinecost",
      "app": "production_execution",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "machine_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "hours_used",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "rate_per_hour",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "total_cost",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "created_by_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "production_run_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        }
      ]
    },
    {
      "name": "production_execution_resourceoverhead",
      "app": "production_execution",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "expense_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "amount",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "created_by_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "production_run_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        }
      ]
    },
    {
      "name": "production_execution_resourcewater",
      "app": "production_execution",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "description",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "volume_consumed",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "rate_per_unit",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "total_cost",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "created_by_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "production_run_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        }
      ]
    },
    {
      "name": "production_execution_wastelog",
      "app": "production_execution",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "material_code",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "material_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "wastage_qty",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "uom",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "reason",
          "type": "text",
          "tags": [],
          "notes": []
        },
        {
          "name": "engineer_sign",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "engineer_signed_at",
          "type": "datetime",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "am_sign",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "am_signed_at",
          "type": "datetime",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "store_sign",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "store_signed_at",
          "type": "datetime",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "hod_sign",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "hod_signed_at",
          "type": "datetime",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "wastage_approval_status",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "am_signed_by_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "engineer_signed_by_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "hod_signed_by_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "production_run_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "store_signed_by_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        }
      ]
    },
    {
      "name": "production_planning_dailyproductionentry",
      "app": "production_planning",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "production_date",
          "type": "date",
          "tags": [],
          "notes": []
        },
        {
          "name": "produced_qty",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "shift",
          "type": "varchar",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "remarks",
          "type": "text",
          "tags": [],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "weekly_plan_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "recorded_by_id",
          "type": "bigint",
          "tags": [],
          "notes": [
            "nullable"
          ]
        }
      ]
    },
    {
      "name": "production_planning_planmaterialrequirement",
      "app": "production_planning",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "component_code",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "component_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "required_qty",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "uom",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "production_plan_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "warehouse_code",
          "type": "varchar",
          "tags": [],
          "notes": []
        }
      ]
    },
    {
      "name": "production_planning_productionplan",
      "app": "production_planning",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "sap_doc_entry",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "sap_doc_num",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "item_code",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "item_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "planned_qty",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "completed_qty",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "target_start_date",
          "type": "date",
          "tags": [],
          "notes": []
        },
        {
          "name": "due_date",
          "type": "date",
          "tags": [],
          "notes": []
        },
        {
          "name": "sap_status",
          "type": "varchar",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "status",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "branch_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "remarks",
          "type": "text",
          "tags": [],
          "notes": []
        },
        {
          "name": "closed_at",
          "type": "datetime",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "company_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "closed_by_id",
          "type": "bigint",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "sap_posting_status",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "sap_error_message",
          "type": "text",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "uom",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "warehouse_code",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "created_by_id",
          "type": "bigint",
          "tags": [],
          "notes": [
            "nullable"
          ]
        }
      ]
    },
    {
      "name": "production_planning_weeklyplan",
      "app": "production_planning",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "week_number",
          "type": "int",
          "tags": [],
          "notes": []
        },
        {
          "name": "week_label",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "start_date",
          "type": "date",
          "tags": [],
          "notes": []
        },
        {
          "name": "end_date",
          "type": "date",
          "tags": [],
          "notes": []
        },
        {
          "name": "target_qty",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "produced_qty",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "status",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "production_plan_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "created_by_id",
          "type": "bigint",
          "tags": [],
          "notes": [
            "nullable"
          ]
        }
      ]
    },
    {
      "name": "quality_control_arrivalslipattachment",
      "app": "quality_control",
      "fields": [
        {
          "name": "id",
          "type": "int",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "file",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "attachment_type",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "uploaded_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "arrival_slip_id",
          "type": "int",
          "tags": [
            "FK"
          ],
          "notes": []
        }
      ]
    },
    {
      "name": "quality_control_inspectionparameterresult",
      "app": "quality_control",
      "fields": [
        {
          "name": "id",
          "type": "int",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "is_active",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "parameter_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "standard_value",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "result_value",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "result_numeric",
          "type": "decimal",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "is_within_spec",
          "type": "boolean",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "remarks",
          "type": "text",
          "tags": [],
          "notes": []
        },
        {
          "name": "created_by_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "updated_by_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "parameter_master_id",
          "type": "int",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "inspection_id",
          "type": "int",
          "tags": [
            "FK"
          ],
          "notes": []
        }
      ]
    },
    {
      "name": "quality_control_materialarrivalslip",
      "app": "quality_control",
      "fields": [
        {
          "name": "id",
          "type": "int",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "is_active",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "particulars",
          "type": "text",
          "tags": [],
          "notes": []
        },
        {
          "name": "arrival_datetime",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "weighing_required",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "party_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "billing_qty",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "billing_uom",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "in_time_to_qa",
          "type": "datetime",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "truck_no_as_per_bill",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "commercial_invoice_no",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "eway_bill_no",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "bilty_no",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "has_certificate_of_analysis",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "has_certificate_of_quantity",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "status",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "is_submitted",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "submitted_at",
          "type": "datetime",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "remarks",
          "type": "text",
          "tags": [],
          "notes": []
        },
        {
          "name": "created_by_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "submitted_by_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "updated_by_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "po_item_receipt_id",
          "type": "int",
          "tags": [
            "FK",
            "UK"
          ],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "sent_back_at",
          "type": "datetime",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "sent_back_by_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        }
      ]
    },
    {
      "name": "quality_control_materialtype",
      "app": "quality_control",
      "fields": [
        {
          "name": "id",
          "type": "int",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "is_active",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "code",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "description",
          "type": "text",
          "tags": [],
          "notes": []
        },
        {
          "name": "company_id",
          "type": "int",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "created_by_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "updated_by_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        }
      ]
    },
    {
      "name": "quality_control_productionqcresult",
      "app": "quality_control",
      "fields": [
        {
          "name": "id",
          "type": "int",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "is_active",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "parameter_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "standard_value",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "result_value",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "result_numeric",
          "type": "decimal",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "is_within_spec",
          "type": "boolean",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "remarks",
          "type": "text",
          "tags": [],
          "notes": []
        },
        {
          "name": "created_by_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "parameter_master_id",
          "type": "int",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "updated_by_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "session_id",
          "type": "int",
          "tags": [
            "FK"
          ],
          "notes": []
        }
      ]
    },
    {
      "name": "quality_control_productionqcsession",
      "app": "quality_control",
      "fields": [
        {
          "name": "id",
          "type": "int",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "is_active",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "session_number",
          "type": "int",
          "tags": [],
          "notes": []
        },
        {
          "name": "session_type",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "checked_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "overall_result",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "workflow_status",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "remarks",
          "type": "text",
          "tags": [],
          "notes": []
        },
        {
          "name": "checked_by_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "created_by_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "material_type_id",
          "type": "int",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "production_run_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "updated_by_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "submitted_at",
          "type": "datetime",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "submitted_by_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "approval_remarks",
          "type": "text",
          "tags": [],
          "notes": []
        },
        {
          "name": "approved_at",
          "type": "datetime",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "approved_by_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "rejected_at",
          "type": "datetime",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "rejected_by_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "rejection_remarks",
          "type": "text",
          "tags": [],
          "notes": []
        }
      ]
    },
    {
      "name": "quality_control_qcparametermaster",
      "app": "quality_control",
      "fields": [
        {
          "name": "id",
          "type": "int",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "is_active",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "parameter_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "parameter_code",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "standard_value",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "parameter_type",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "min_value",
          "type": "decimal",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "max_value",
          "type": "decimal",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "uom",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "sequence",
          "type": "int",
          "tags": [],
          "notes": []
        },
        {
          "name": "is_mandatory",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "created_by_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "material_type_id",
          "type": "int",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "updated_by_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        }
      ]
    },
    {
      "name": "quality_control_rawmaterialinspection",
      "app": "quality_control",
      "fields": [
        {
          "name": "id",
          "type": "int",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "is_active",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "report_no",
          "type": "varchar",
          "tags": [
            "UK"
          ],
          "notes": []
        },
        {
          "name": "internal_lot_no",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "inspection_date",
          "type": "date",
          "tags": [],
          "notes": []
        },
        {
          "name": "description_of_material",
          "type": "text",
          "tags": [],
          "notes": []
        },
        {
          "name": "sap_code",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "supplier_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "manufacturer_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "supplier_batch_lot_no",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "unit_packing",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "purchase_order_no",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "invoice_bill_no",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "vehicle_no",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "final_status",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "qa_chemist_approved_at",
          "type": "datetime",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "qa_chemist_remarks",
          "type": "text",
          "tags": [],
          "notes": []
        },
        {
          "name": "qam_approved_at",
          "type": "datetime",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "qam_remarks",
          "type": "text",
          "tags": [],
          "notes": []
        },
        {
          "name": "workflow_status",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "is_locked",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "remarks",
          "type": "text",
          "tags": [],
          "notes": []
        },
        {
          "name": "created_by_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "material_type_id",
          "type": "int",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "qa_chemist_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "qam_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "updated_by_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "arrival_slip_id",
          "type": "int",
          "tags": [
            "FK",
            "UK"
          ],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "rejected_at",
          "type": "datetime",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "rejected_by_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "internal_report_no",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "factory_head_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "factory_head_decided_at",
          "type": "datetime",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "factory_head_decision",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "factory_head_remarks",
          "type": "text",
          "tags": [],
          "notes": []
        }
      ]
    },
    {
      "name": "raw_material_gatein_poitemreceipt",
      "app": "raw_material_gatein",
      "fields": [
        {
          "name": "id",
          "type": "int",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "is_active",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "po_item_code",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "item_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "ordered_qty",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "received_qty",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "accepted_qty",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "rejected_qty",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "short_qty",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "uom",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "created_by_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "updated_by_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "po_receipt_id",
          "type": "int",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "line_num",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "gl_account",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "tax_code",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "unit_price",
          "type": "decimal",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "warehouse_code",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "sap_line_num",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "variety",
          "type": "varchar",
          "tags": [],
          "notes": [
            "nullable"
          ]
        }
      ]
    },
    {
      "name": "raw_material_gatein_poreceipt",
      "app": "raw_material_gatein",
      "fields": [
        {
          "name": "id",
          "type": "int",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "is_active",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "po_number",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "supplier_code",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "supplier_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "invoice_no",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "invoice_date",
          "type": "date",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "challan_no",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "created_by_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "updated_by_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "vehicle_entry_id",
          "type": "int",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "sap_doc_entry",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "branch_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "vendor_ref",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "po_date",
          "type": "date",
          "tags": [],
          "notes": [
            "nullable"
          ]
        }
      ]
    },
    {
      "name": "security_checks_securitycheck",
      "app": "security_checks",
      "fields": [
        {
          "name": "id",
          "type": "int",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "is_active",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "vehicle_condition_ok",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "tyre_condition_ok",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "fire_extinguisher_available",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "seal_no_before",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "seal_no_after",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "alcohol_test_done",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "alcohol_test_passed",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "inspected_by_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "inspection_time",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "remarks",
          "type": "text",
          "tags": [],
          "notes": []
        },
        {
          "name": "is_submitted",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "created_by_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "updated_by_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "vehicle_entry_id",
          "type": "int",
          "tags": [
            "FK",
            "UK"
          ],
          "notes": []
        }
      ]
    },
    {
      "name": "stock_dashboard_stockalertlog",
      "app": "stock_dashboard",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "company_code",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "item_code",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "warehouse",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "stock_status",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "on_hand",
          "type": "float",
          "tags": [],
          "notes": []
        },
        {
          "name": "min_stock",
          "type": "float",
          "tags": [],
          "notes": []
        },
        {
          "name": "notified_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "cooldown_until",
          "type": "datetime",
          "tags": [],
          "notes": []
        }
      ]
    },
    {
      "name": "token_blacklist_blacklistedtoken",
      "app": "token_blacklist",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "blacklisted_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "token_id",
          "type": "bigint",
          "tags": [
            "FK",
            "UK"
          ],
          "notes": []
        }
      ]
    },
    {
      "name": "token_blacklist_outstandingtoken",
      "app": "token_blacklist",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "token",
          "type": "text",
          "tags": [],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "expires_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "user_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "jti",
          "type": "varchar",
          "tags": [
            "UK"
          ],
          "notes": []
        }
      ]
    },
    {
      "name": "vehicle_management_transporter",
      "app": "vehicle_management",
      "fields": [
        {
          "name": "id",
          "type": "int",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "is_active",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "name",
          "type": "varchar",
          "tags": [
            "UK"
          ],
          "notes": []
        },
        {
          "name": "contact_person",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "mobile_no",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "created_by_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "updated_by_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "gstin",
          "type": "varchar",
          "tags": [],
          "notes": []
        }
      ]
    },
    {
      "name": "vehicle_management_vehicle",
      "app": "vehicle_management",
      "fields": [
        {
          "name": "id",
          "type": "int",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "is_active",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "vehicle_number",
          "type": "varchar",
          "tags": [
            "UK"
          ],
          "notes": []
        },
        {
          "name": "vehicle_type_id",
          "type": "int",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "capacity_ton",
          "type": "decimal",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "created_by_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "transporter_id",
          "type": "int",
          "tags": [
            "FK"
          ],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "updated_by_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        }
      ]
    },
    {
      "name": "vehicle_management_vehicletype",
      "app": "vehicle_management",
      "fields": [
        {
          "name": "id",
          "type": "int",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "is_active",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "name",
          "type": "varchar",
          "tags": [
            "UK"
          ],
          "notes": []
        },
        {
          "name": "created_by_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "updated_by_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        }
      ]
    },
    {
      "name": "warehouse_bomrequest",
      "app": "warehouse",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "sap_doc_entry",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "required_qty",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "status",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "remarks",
          "type": "text",
          "tags": [],
          "notes": []
        },
        {
          "name": "rejection_reason",
          "type": "text",
          "tags": [],
          "notes": []
        },
        {
          "name": "material_issue_status",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "sap_issue_doc_entries",
          "type": "json",
          "tags": [],
          "notes": []
        },
        {
          "name": "reviewed_at",
          "type": "datetime",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "company_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "production_run_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "requested_by_id",
          "type": "bigint",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "reviewed_by_id",
          "type": "bigint",
          "tags": [],
          "notes": [
            "nullable"
          ]
        }
      ]
    },
    {
      "name": "warehouse_bomrequestline",
      "app": "warehouse",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "item_code",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "item_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "per_unit_qty",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "required_qty",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "available_stock",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "approved_qty",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "issued_qty",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "warehouse",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "uom",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "base_line",
          "type": "int",
          "tags": [],
          "notes": []
        },
        {
          "name": "status",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "remarks",
          "type": "text",
          "tags": [],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "bom_request_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        }
      ]
    },
    {
      "name": "warehouse_finishedgoodsreceipt",
      "app": "warehouse",
      "fields": [
        {
          "name": "id",
          "type": "bigint",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "sap_doc_entry",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "item_code",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "item_name",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "produced_qty",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "good_qty",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "rejected_qty",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "warehouse",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "uom",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "posting_date",
          "type": "date",
          "tags": [],
          "notes": []
        },
        {
          "name": "status",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "sap_receipt_doc_entry",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "sap_error",
          "type": "text",
          "tags": [],
          "notes": []
        },
        {
          "name": "received_at",
          "type": "datetime",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "company_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "production_run_id",
          "type": "bigint",
          "tags": [
            "FK"
          ],
          "notes": []
        },
        {
          "name": "received_by_id",
          "type": "bigint",
          "tags": [],
          "notes": [
            "nullable"
          ]
        }
      ]
    },
    {
      "name": "weighment_weighment",
      "app": "weighment",
      "fields": [
        {
          "name": "id",
          "type": "int",
          "tags": [
            "PK"
          ],
          "notes": []
        },
        {
          "name": "created_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "updated_at",
          "type": "datetime",
          "tags": [],
          "notes": []
        },
        {
          "name": "is_active",
          "type": "boolean",
          "tags": [],
          "notes": []
        },
        {
          "name": "gross_weight",
          "type": "decimal",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "tare_weight",
          "type": "decimal",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "net_weight",
          "type": "decimal",
          "tags": [],
          "notes": []
        },
        {
          "name": "weighbridge_slip_no",
          "type": "varchar",
          "tags": [],
          "notes": []
        },
        {
          "name": "first_weighment_time",
          "type": "datetime",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "second_weighment_time",
          "type": "datetime",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "remarks",
          "type": "text",
          "tags": [],
          "notes": []
        },
        {
          "name": "created_by_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "updated_by_id",
          "type": "int",
          "tags": [],
          "notes": [
            "nullable"
          ]
        },
        {
          "name": "vehicle_entry_id",
          "type": "int",
          "tags": [
            "FK",
            "UK"
          ],
          "notes": []
        }
      ]
    }
  ],
  "relationships": [
    {
      "src": "accounts_user",
      "dst": "accounts_user_groups",
      "left": "||",
      "right": "o{",
      "label": "user_id"
    },
    {
      "src": "accounts_user",
      "dst": "accounts_user_user_permissions",
      "left": "||",
      "right": "o{",
      "label": "user_id"
    },
    {
      "src": "accounts_user",
      "dst": "barcode_box",
      "left": "||",
      "right": "o{",
      "label": "created_by_id"
    },
    {
      "src": "accounts_user",
      "dst": "dispatch_plans_dispatchplan",
      "left": "||",
      "right": "o{",
      "label": "created_by_id"
    },
    {
      "src": "accounts_user",
      "dst": "dispatch_plans_dispatchplan",
      "left": "||",
      "right": "o{",
      "label": "updated_by_id"
    },
    {
      "src": "accounts_user",
      "dst": "dispatch_plans_transporterapinvoiceattachment",
      "left": "||",
      "right": "o{",
      "label": "uploaded_by_id"
    },
    {
      "src": "accounts_user",
      "dst": "dispatch_plans_transporterapinvoiceposting",
      "left": "||",
      "right": "o{",
      "label": "created_by_id"
    },
    {
      "src": "accounts_user",
      "dst": "dispatch_plans_transporterapinvoiceposting",
      "left": "||",
      "right": "o{",
      "label": "posted_by_id"
    },
    {
      "src": "accounts_user",
      "dst": "dispatch_plans_transporterapinvoiceposting",
      "left": "||",
      "right": "o{",
      "label": "updated_by_id"
    },
    {
      "src": "accounts_user",
      "dst": "gate_core_bstgatein",
      "left": "||",
      "right": "o{",
      "label": "created_by_id"
    },
    {
      "src": "accounts_user",
      "dst": "gate_core_bstgatein",
      "left": "||",
      "right": "o{",
      "label": "updated_by_id"
    },
    {
      "src": "accounts_user",
      "dst": "gate_core_bstgateinitem",
      "left": "||",
      "right": "o{",
      "label": "created_by_id"
    },
    {
      "src": "accounts_user",
      "dst": "gate_core_bstgateinitem",
      "left": "||",
      "right": "o{",
      "label": "updated_by_id"
    },
    {
      "src": "accounts_user",
      "dst": "gate_core_bstgateout",
      "left": "||",
      "right": "o{",
      "label": "cancelled_by_id"
    },
    {
      "src": "accounts_user",
      "dst": "gate_core_bstgateout",
      "left": "||",
      "right": "o{",
      "label": "created_by_id"
    },
    {
      "src": "accounts_user",
      "dst": "gate_core_bstgateout",
      "left": "||",
      "right": "o{",
      "label": "updated_by_id"
    },
    {
      "src": "accounts_user",
      "dst": "gate_core_bstgateoutitem",
      "left": "||",
      "right": "o{",
      "label": "created_by_id"
    },
    {
      "src": "accounts_user",
      "dst": "gate_core_bstgateoutitem",
      "left": "||",
      "right": "o{",
      "label": "updated_by_id"
    },
    {
      "src": "accounts_user",
      "dst": "gate_core_bstgatereturn",
      "left": "||",
      "right": "o{",
      "label": "created_by_id"
    },
    {
      "src": "accounts_user",
      "dst": "gate_core_bstgatereturn",
      "left": "||",
      "right": "o{",
      "label": "updated_by_id"
    },
    {
      "src": "accounts_user",
      "dst": "gate_core_dispatchgatelock",
      "left": "||",
      "right": "o{",
      "label": "changed_by_id"
    },
    {
      "src": "accounts_user",
      "dst": "gate_core_dispatchgatelock",
      "left": "||",
      "right": "o{",
      "label": "created_by_id"
    },
    {
      "src": "accounts_user",
      "dst": "gate_core_dispatchgatelock",
      "left": "||",
      "right": "o{",
      "label": "updated_by_id"
    },
    {
      "src": "accounts_user",
      "dst": "gate_core_dispatchgateout",
      "left": "||",
      "right": "o{",
      "label": "created_by_id"
    },
    {
      "src": "accounts_user",
      "dst": "gate_core_dispatchgateout",
      "left": "||",
      "right": "o{",
      "label": "updated_by_id"
    },
    {
      "src": "accounts_user",
      "dst": "gate_core_dispatchgateoutline",
      "left": "||",
      "right": "o{",
      "label": "created_by_id"
    },
    {
      "src": "accounts_user",
      "dst": "gate_core_dispatchgateoutline",
      "left": "||",
      "right": "o{",
      "label": "updated_by_id"
    },
    {
      "src": "accounts_user",
      "dst": "gate_core_emptyvehiclegatein",
      "left": "||",
      "right": "o{",
      "label": "created_by_id"
    },
    {
      "src": "accounts_user",
      "dst": "gate_core_emptyvehiclegatein",
      "left": "||",
      "right": "o{",
      "label": "updated_by_id"
    },
    {
      "src": "accounts_user",
      "dst": "gate_core_emptyvehiclegateinitem",
      "left": "||",
      "right": "o{",
      "label": "created_by_id"
    },
    {
      "src": "accounts_user",
      "dst": "gate_core_emptyvehiclegateinitem",
      "left": "||",
      "right": "o{",
      "label": "updated_by_id"
    },
    {
      "src": "accounts_user",
      "dst": "gate_core_emptyvehiclegateout",
      "left": "||",
      "right": "o{",
      "label": "cancelled_by_id"
    },
    {
      "src": "accounts_user",
      "dst": "gate_core_emptyvehiclegateout",
      "left": "||",
      "right": "o{",
      "label": "created_by_id"
    },
    {
      "src": "accounts_user",
      "dst": "gate_core_emptyvehiclegateout",
      "left": "||",
      "right": "o{",
      "label": "updated_by_id"
    },
    {
      "src": "accounts_user",
      "dst": "gate_core_jobworkgatein",
      "left": "||",
      "right": "o{",
      "label": "created_by_id"
    },
    {
      "src": "accounts_user",
      "dst": "gate_core_jobworkgatein",
      "left": "||",
      "right": "o{",
      "label": "updated_by_id"
    },
    {
      "src": "accounts_user",
      "dst": "gate_core_jobworkgateinitem",
      "left": "||",
      "right": "o{",
      "label": "created_by_id"
    },
    {
      "src": "accounts_user",
      "dst": "gate_core_jobworkgateinitem",
      "left": "||",
      "right": "o{",
      "label": "updated_by_id"
    },
    {
      "src": "accounts_user",
      "dst": "gate_core_rejectedqcreturnentry",
      "left": "||",
      "right": "o{",
      "label": "created_by_id"
    },
    {
      "src": "accounts_user",
      "dst": "gate_core_rejectedqcreturnentry",
      "left": "||",
      "right": "o{",
      "label": "updated_by_id"
    },
    {
      "src": "accounts_user",
      "dst": "gate_core_rejectedqcreturnitem",
      "left": "||",
      "right": "o{",
      "label": "created_by_id"
    },
    {
      "src": "accounts_user",
      "dst": "gate_core_rejectedqcreturnitem",
      "left": "||",
      "right": "o{",
      "label": "updated_by_id"
    },
    {
      "src": "accounts_user",
      "dst": "grpo_servicegrpoattachment",
      "left": "||",
      "right": "o{",
      "label": "uploaded_by_id"
    },
    {
      "src": "accounts_user",
      "dst": "grpo_servicegrpoposting",
      "left": "||",
      "right": "o{",
      "label": "posted_by_id"
    },
    {
      "src": "accounts_user",
      "dst": "quality_control_productionqcsession",
      "left": "||",
      "right": "o{",
      "label": "approved_by_id"
    },
    {
      "src": "accounts_user",
      "dst": "quality_control_productionqcsession",
      "left": "||",
      "right": "o{",
      "label": "rejected_by_id"
    },
    {
      "src": "accounts_user",
      "dst": "quality_control_rawmaterialinspection",
      "left": "||",
      "right": "o{",
      "label": "factory_head_id"
    },
    {
      "src": "auth_group",
      "dst": "accounts_user_groups",
      "left": "||",
      "right": "o{",
      "label": "group_id"
    },
    {
      "src": "auth_group",
      "dst": "auth_group_permissions",
      "left": "||",
      "right": "o{",
      "label": "group_id"
    },
    {
      "src": "auth_permission",
      "dst": "accounts_user_user_permissions",
      "left": "||",
      "right": "o{",
      "label": "permission_id"
    },
    {
      "src": "auth_permission",
      "dst": "auth_group_permissions",
      "left": "||",
      "right": "o{",
      "label": "permission_id"
    },
    {
      "src": "barcode_box",
      "dst": "barcode_boxmovement",
      "left": "||",
      "right": "o{",
      "label": "box_id"
    },
    {
      "src": "barcode_box",
      "dst": "barcode_loosestock",
      "left": "||",
      "right": "o{",
      "label": "repacked_into_box_id"
    },
    {
      "src": "barcode_box",
      "dst": "barcode_loosestock",
      "left": "||",
      "right": "o{",
      "label": "source_box_id"
    },
    {
      "src": "barcode_pallet",
      "dst": "barcode_box",
      "left": "||",
      "right": "o{",
      "label": "pallet_id"
    },
    {
      "src": "barcode_pallet",
      "dst": "barcode_boxmovement",
      "left": "||",
      "right": "o{",
      "label": "from_pallet_id"
    },
    {
      "src": "barcode_pallet",
      "dst": "barcode_boxmovement",
      "left": "||",
      "right": "o{",
      "label": "to_pallet_id"
    },
    {
      "src": "barcode_pallet",
      "dst": "barcode_loosestock",
      "left": "||",
      "right": "o{",
      "label": "source_pallet_id"
    },
    {
      "src": "barcode_pallet",
      "dst": "barcode_palletmovement",
      "left": "||",
      "right": "o{",
      "label": "pallet_id"
    },
    {
      "src": "company_company",
      "dst": "barcode_barcodesequence",
      "left": "||",
      "right": "o{",
      "label": "company_id"
    },
    {
      "src": "company_company",
      "dst": "barcode_box",
      "left": "||",
      "right": "o{",
      "label": "company_id"
    },
    {
      "src": "company_company",
      "dst": "barcode_boxmovement",
      "left": "||",
      "right": "o{",
      "label": "company_id"
    },
    {
      "src": "company_company",
      "dst": "barcode_labelprintlog",
      "left": "||",
      "right": "o{",
      "label": "company_id"
    },
    {
      "src": "company_company",
      "dst": "barcode_loosestock",
      "left": "||",
      "right": "o{",
      "label": "company_id"
    },
    {
      "src": "company_company",
      "dst": "barcode_pallet",
      "left": "||",
      "right": "o{",
      "label": "company_id"
    },
    {
      "src": "company_company",
      "dst": "barcode_palletmovement",
      "left": "||",
      "right": "o{",
      "label": "company_id"
    },
    {
      "src": "company_company",
      "dst": "barcode_scanlog",
      "left": "||",
      "right": "o{",
      "label": "company_id"
    },
    {
      "src": "company_company",
      "dst": "company_usercompany",
      "left": "||",
      "right": "o{",
      "label": "company_id"
    },
    {
      "src": "company_company",
      "dst": "dispatch_plans_dispatchplan",
      "left": "||",
      "right": "o{",
      "label": "company_id"
    },
    {
      "src": "company_company",
      "dst": "dispatch_plans_transporterapinvoiceposting",
      "left": "||",
      "right": "o{",
      "label": "company_id"
    },
    {
      "src": "company_company",
      "dst": "driver_management_vehicleentry",
      "left": "||",
      "right": "o{",
      "label": "company_id"
    },
    {
      "src": "company_company",
      "dst": "gate_core_bstgatein",
      "left": "||",
      "right": "o{",
      "label": "company_id"
    },
    {
      "src": "company_company",
      "dst": "gate_core_bstgateout",
      "left": "||",
      "right": "o{",
      "label": "company_id"
    },
    {
      "src": "company_company",
      "dst": "gate_core_bstgatereturn",
      "left": "||",
      "right": "o{",
      "label": "company_id"
    },
    {
      "src": "company_company",
      "dst": "gate_core_dispatchgatelock",
      "left": "||",
      "right": "o{",
      "label": "company_id"
    },
    {
      "src": "company_company",
      "dst": "gate_core_dispatchgateout",
      "left": "||",
      "right": "o{",
      "label": "company_id"
    },
    {
      "src": "company_company",
      "dst": "gate_core_emptyvehiclegatein",
      "left": "||",
      "right": "o{",
      "label": "company_id"
    },
    {
      "src": "company_company",
      "dst": "gate_core_emptyvehiclegateout",
      "left": "||",
      "right": "o{",
      "label": "company_id"
    },
    {
      "src": "company_company",
      "dst": "gate_core_jobworkgatein",
      "left": "||",
      "right": "o{",
      "label": "company_id"
    },
    {
      "src": "company_company",
      "dst": "gate_core_rejectedqcreturnentry",
      "left": "||",
      "right": "o{",
      "label": "company_id"
    },
    {
      "src": "company_company",
      "dst": "mail_emaillog",
      "left": "||",
      "right": "o{",
      "label": "company_id"
    },
    {
      "src": "company_company",
      "dst": "notifications_notification",
      "left": "||",
      "right": "o{",
      "label": "company_id"
    },
    {
      "src": "company_company",
      "dst": "outbound_dispatch_shipmentorder",
      "left": "||",
      "right": "o{",
      "label": "company_id"
    },
    {
      "src": "company_company",
      "dst": "production_execution_breakdowncategory",
      "left": "||",
      "right": "o{",
      "label": "company_id"
    },
    {
      "src": "company_company",
      "dst": "production_execution_lineclearance",
      "left": "||",
      "right": "o{",
      "label": "company_id"
    },
    {
      "src": "company_company",
      "dst": "production_execution_lineskuconfig",
      "left": "||",
      "right": "o{",
      "label": "company_id"
    },
    {
      "src": "company_company",
      "dst": "production_execution_machine",
      "left": "||",
      "right": "o{",
      "label": "company_id"
    },
    {
      "src": "company_company",
      "dst": "production_execution_machinechecklistentry",
      "left": "||",
      "right": "o{",
      "label": "company_id"
    },
    {
      "src": "company_company",
      "dst": "production_execution_machinechecklisttemplate",
      "left": "||",
      "right": "o{",
      "label": "company_id"
    },
    {
      "src": "company_company",
      "dst": "production_execution_productionline",
      "left": "||",
      "right": "o{",
      "label": "company_id"
    },
    {
      "src": "company_company",
      "dst": "production_execution_productionrun",
      "left": "||",
      "right": "o{",
      "label": "company_id"
    },
    {
      "src": "company_company",
      "dst": "production_planning_productionplan",
      "left": "||",
      "right": "o{",
      "label": "company_id"
    },
    {
      "src": "company_company",
      "dst": "quality_control_materialtype",
      "left": "||",
      "right": "o{",
      "label": "company_id"
    },
    {
      "src": "company_company",
      "dst": "warehouse_bomrequest",
      "left": "||",
      "right": "o{",
      "label": "company_id"
    },
    {
      "src": "company_company",
      "dst": "warehouse_finishedgoodsreceipt",
      "left": "||",
      "right": "o{",
      "label": "company_id"
    },
    {
      "src": "company_userrole",
      "dst": "company_usercompany",
      "left": "||",
      "right": "o{",
      "label": "role_id"
    },
    {
      "src": "construction_gatein_constructionmaterialcategory",
      "dst": "construction_gatein_constructiongateentry",
      "left": "||",
      "right": "o{",
      "label": "material_category_id"
    },
    {
      "src": "daily_needs_gatein_categorylist",
      "dst": "daily_needs_gatein_dailyneedgateentry",
      "left": "||",
      "right": "o{",
      "label": "item_category_id"
    },
    {
      "src": "daily_needs_gatein_dailyneedgateentry",
      "dst": "daily_needs_gatein_dailyneedgateentryitem",
      "left": "||",
      "right": "o{",
      "label": "daily_need_entry_id"
    },
    {
      "src": "dispatch_plans_dispatchplan",
      "dst": "dispatch_plans_transporterapinvoiceline",
      "left": "||",
      "right": "o{",
      "label": "dispatch_plan_id"
    },
    {
      "src": "dispatch_plans_dispatchplan",
      "dst": "gate_core_dispatchgateout",
      "left": "||",
      "right": "o{",
      "label": "dispatch_plan_id"
    },
    {
      "src": "dispatch_plans_dispatchplan",
      "dst": "grpo_servicegrpoposting",
      "left": "||",
      "right": "o{",
      "label": "dispatch_plan_id"
    },
    {
      "src": "dispatch_plans_transporterapinvoiceposting",
      "dst": "dispatch_plans_transporterapinvoiceattachment",
      "left": "||",
      "right": "o{",
      "label": "transporter_ap_invoice_id"
    },
    {
      "src": "dispatch_plans_transporterapinvoiceposting",
      "dst": "dispatch_plans_transporterapinvoiceline",
      "left": "||",
      "right": "o{",
      "label": "transporter_ap_invoice_id"
    },
    {
      "src": "django_apscheduler_djangojob",
      "dst": "django_apscheduler_djangojobexecution",
      "left": "||",
      "right": "o{",
      "label": "job_id"
    },
    {
      "src": "django_content_type",
      "dst": "auth_permission",
      "left": "||",
      "right": "o{",
      "label": "content_type_id"
    },
    {
      "src": "django_content_type",
      "dst": "django_admin_log",
      "left": "||",
      "right": "o{",
      "label": "content_type_id"
    },
    {
      "src": "driver_management_driver",
      "dst": "dispatch_plans_dispatchplan",
      "left": "||",
      "right": "o{",
      "label": "driver_id"
    },
    {
      "src": "driver_management_driver",
      "dst": "driver_management_vehicleentry",
      "left": "||",
      "right": "o{",
      "label": "driver_id"
    },
    {
      "src": "driver_management_driver",
      "dst": "gate_core_bstgatein",
      "left": "||",
      "right": "o{",
      "label": "driver_id"
    },
    {
      "src": "driver_management_driver",
      "dst": "gate_core_bstgateout",
      "left": "||",
      "right": "o{",
      "label": "driver_id"
    },
    {
      "src": "driver_management_driver",
      "dst": "gate_core_bstgatereturn",
      "left": "||",
      "right": "o{",
      "label": "driver_id"
    },
    {
      "src": "driver_management_driver",
      "dst": "gate_core_dispatchgateout",
      "left": "||",
      "right": "o{",
      "label": "driver_id"
    },
    {
      "src": "driver_management_driver",
      "dst": "gate_core_emptyvehiclegatein",
      "left": "||",
      "right": "o{",
      "label": "driver_id"
    },
    {
      "src": "driver_management_driver",
      "dst": "gate_core_emptyvehiclegateout",
      "left": "||",
      "right": "o{",
      "label": "driver_id"
    },
    {
      "src": "driver_management_driver",
      "dst": "gate_core_jobworkgatein",
      "left": "||",
      "right": "o{",
      "label": "driver_id"
    },
    {
      "src": "driver_management_driver",
      "dst": "gate_core_rejectedqcreturnentry",
      "left": "||",
      "right": "o{",
      "label": "driver_id"
    },
    {
      "src": "driver_management_vehicleentry",
      "dst": "construction_gatein_constructiongateentry",
      "left": "||",
      "right": "o{",
      "label": "vehicle_entry_id"
    },
    {
      "src": "driver_management_vehicleentry",
      "dst": "daily_needs_gatein_dailyneedgateentry",
      "left": "||",
      "right": "o{",
      "label": "vehicle_entry_id"
    },
    {
      "src": "driver_management_vehicleentry",
      "dst": "dispatch_plans_dispatchplan",
      "left": "||",
      "right": "o{",
      "label": "linked_vehicle_entry_id"
    },
    {
      "src": "driver_management_vehicleentry",
      "dst": "gate_core_bstgatein",
      "left": "||",
      "right": "o{",
      "label": "vehicle_entry_id"
    },
    {
      "src": "driver_management_vehicleentry",
      "dst": "gate_core_bstgateout",
      "left": "||",
      "right": "o{",
      "label": "vehicle_entry_id"
    },
    {
      "src": "driver_management_vehicleentry",
      "dst": "gate_core_bstgatereturn",
      "left": "||",
      "right": "o{",
      "label": "vehicle_entry_id"
    },
    {
      "src": "driver_management_vehicleentry",
      "dst": "gate_core_dispatchgateout",
      "left": "||",
      "right": "o{",
      "label": "vehicle_entry_id"
    },
    {
      "src": "driver_management_vehicleentry",
      "dst": "gate_core_emptyvehiclegatein",
      "left": "||",
      "right": "o{",
      "label": "vehicle_entry_id"
    },
    {
      "src": "driver_management_vehicleentry",
      "dst": "gate_core_emptyvehiclegateout",
      "left": "||",
      "right": "o{",
      "label": "vehicle_entry_id"
    },
    {
      "src": "driver_management_vehicleentry",
      "dst": "gate_core_gateattachment",
      "left": "||",
      "right": "o{",
      "label": "gate_entry_id"
    },
    {
      "src": "driver_management_vehicleentry",
      "dst": "gate_core_jobworkgatein",
      "left": "||",
      "right": "o{",
      "label": "vehicle_entry_id"
    },
    {
      "src": "driver_management_vehicleentry",
      "dst": "grpo_grpoposting",
      "left": "||",
      "right": "o{",
      "label": "vehicle_entry_id"
    },
    {
      "src": "driver_management_vehicleentry",
      "dst": "maintenance_gatein_maintenancegateentry",
      "left": "||",
      "right": "o{",
      "label": "vehicle_entry_id"
    },
    {
      "src": "driver_management_vehicleentry",
      "dst": "outbound_dispatch_shipmentorder",
      "left": "||",
      "right": "o{",
      "label": "vehicle_entry_id"
    },
    {
      "src": "driver_management_vehicleentry",
      "dst": "outbound_gatein_outboundgateentry",
      "left": "||",
      "right": "o{",
      "label": "vehicle_entry_id"
    },
    {
      "src": "driver_management_vehicleentry",
      "dst": "raw_material_gatein_poreceipt",
      "left": "||",
      "right": "o{",
      "label": "vehicle_entry_id"
    },
    {
      "src": "driver_management_vehicleentry",
      "dst": "security_checks_securitycheck",
      "left": "||",
      "right": "o{",
      "label": "vehicle_entry_id"
    },
    {
      "src": "driver_management_vehicleentry",
      "dst": "weighment_weighment",
      "left": "||",
      "right": "o{",
      "label": "vehicle_entry_id"
    },
    {
      "src": "gate_core_bstgatein",
      "dst": "gate_core_bstgateinitem",
      "left": "||",
      "right": "o{",
      "label": "bst_gate_in_id"
    },
    {
      "src": "gate_core_bstgateout",
      "dst": "gate_core_bstgatein",
      "left": "||",
      "right": "o{",
      "label": "bst_gate_out_id"
    },
    {
      "src": "gate_core_bstgateout",
      "dst": "gate_core_bstgateoutitem",
      "left": "||",
      "right": "o{",
      "label": "bst_gate_out_id"
    },
    {
      "src": "gate_core_bstgateout",
      "dst": "gate_core_bstgatereturn",
      "left": "||",
      "right": "o{",
      "label": "bst_gate_out_id"
    },
    {
      "src": "gate_core_bstgateoutitem",
      "dst": "gate_core_bstgateinitem",
      "left": "||",
      "right": "o{",
      "label": "bst_gate_out_item_id"
    },
    {
      "src": "gate_core_dispatchgateout",
      "dst": "gate_core_dispatchgateoutline",
      "left": "||",
      "right": "o{",
      "label": "entry_id"
    },
    {
      "src": "gate_core_emptyvehiclegatein",
      "dst": "gate_core_bstgateout",
      "left": "||",
      "right": "o{",
      "label": "empty_vehicle_gate_in_id"
    },
    {
      "src": "gate_core_emptyvehiclegatein",
      "dst": "gate_core_emptyvehiclegateinitem",
      "left": "||",
      "right": "o{",
      "label": "empty_vehicle_gate_in_id"
    },
    {
      "src": "gate_core_jobworkgatein",
      "dst": "gate_core_jobworkgateinitem",
      "left": "||",
      "right": "o{",
      "label": "job_work_gate_in_id"
    },
    {
      "src": "gate_core_rejectedqcreturnentry",
      "dst": "gate_core_rejectedqcreturnitem",
      "left": "||",
      "right": "o{",
      "label": "entry_id"
    },
    {
      "src": "gate_core_unitchoice",
      "dst": "construction_gatein_constructiongateentry",
      "left": "||",
      "right": "o{",
      "label": "unit_id"
    },
    {
      "src": "gate_core_unitchoice",
      "dst": "daily_needs_gatein_dailyneedgateentry",
      "left": "||",
      "right": "o{",
      "label": "unit_id"
    },
    {
      "src": "gate_core_unitchoice",
      "dst": "daily_needs_gatein_dailyneedgateentryitem",
      "left": "||",
      "right": "o{",
      "label": "unit_id"
    },
    {
      "src": "gate_core_unitchoice",
      "dst": "maintenance_gatein_maintenancegateentry",
      "left": "||",
      "right": "o{",
      "label": "unit_id"
    },
    {
      "src": "grpo_grpoposting",
      "dst": "grpo_grpoattachment",
      "left": "||",
      "right": "o{",
      "label": "grpo_posting_id"
    },
    {
      "src": "grpo_grpoposting",
      "dst": "grpo_grpolineposting",
      "left": "||",
      "right": "o{",
      "label": "grpo_posting_id"
    },
    {
      "src": "grpo_grpoposting",
      "dst": "grpo_grpoposting_po_receipts",
      "left": "||",
      "right": "o{",
      "label": "grpoposting_id"
    },
    {
      "src": "grpo_servicegrpolineposting",
      "dst": "dispatch_plans_transporterapinvoiceline",
      "left": "||",
      "right": "o{",
      "label": "service_grpo_line_id"
    },
    {
      "src": "grpo_servicegrpoposting",
      "dst": "dispatch_plans_transporterapinvoiceline",
      "left": "||",
      "right": "o{",
      "label": "service_grpo_posting_id"
    },
    {
      "src": "grpo_servicegrpoposting",
      "dst": "grpo_servicegrpoattachment",
      "left": "||",
      "right": "o{",
      "label": "service_grpo_posting_id"
    },
    {
      "src": "grpo_servicegrpoposting",
      "dst": "grpo_servicegrpolineposting",
      "left": "||",
      "right": "o{",
      "label": "service_grpo_posting_id"
    },
    {
      "src": "inventory_sapcompany",
      "dst": "inventory_sapbatchstock",
      "left": "||",
      "right": "o{",
      "label": "company_id"
    },
    {
      "src": "inventory_sapcompany",
      "dst": "inventory_sapinventoryagingsnapshot",
      "left": "||",
      "right": "o{",
      "label": "company_id"
    },
    {
      "src": "inventory_sapcompany",
      "dst": "inventory_sapinventorymovement",
      "left": "||",
      "right": "o{",
      "label": "company_id"
    },
    {
      "src": "inventory_sapcompany",
      "dst": "inventory_sapinventoryvaluation",
      "left": "||",
      "right": "o{",
      "label": "company_id"
    },
    {
      "src": "inventory_sapcompany",
      "dst": "inventory_sapitem",
      "left": "||",
      "right": "o{",
      "label": "company_id"
    },
    {
      "src": "inventory_sapcompany",
      "dst": "inventory_sapitemgroup",
      "left": "||",
      "right": "o{",
      "label": "company_id"
    },
    {
      "src": "inventory_sapcompany",
      "dst": "inventory_sapitemwarehousestock",
      "left": "||",
      "right": "o{",
      "label": "company_id"
    },
    {
      "src": "inventory_sapcompany",
      "dst": "inventory_sapsyncrun",
      "left": "||",
      "right": "o{",
      "label": "company_id"
    },
    {
      "src": "inventory_sapcompany",
      "dst": "inventory_sapwarehouse",
      "left": "||",
      "right": "o{",
      "label": "company_id"
    },
    {
      "src": "labour_verification_labourverificationrequest",
      "dst": "labour_verification_departmentlabourresponse",
      "left": "||",
      "right": "o{",
      "label": "verification_request_id"
    },
    {
      "src": "maintenance_gatein_maintenancetype",
      "dst": "maintenance_gatein_maintenancegateentry",
      "left": "||",
      "right": "o{",
      "label": "maintenance_type_id"
    },
    {
      "src": "outbound_dispatch_shipmentorder",
      "dst": "outbound_dispatch_goodsissueposting",
      "left": "||",
      "right": "o{",
      "label": "shipment_order_id"
    },
    {
      "src": "outbound_dispatch_shipmentorder",
      "dst": "outbound_dispatch_outboundloadrecord",
      "left": "||",
      "right": "o{",
      "label": "shipment_order_id"
    },
    {
      "src": "outbound_dispatch_shipmentorder",
      "dst": "outbound_dispatch_shipmentorderitem",
      "left": "||",
      "right": "o{",
      "label": "shipment_order_id"
    },
    {
      "src": "outbound_dispatch_shipmentorderitem",
      "dst": "outbound_dispatch_picktask",
      "left": "||",
      "right": "o{",
      "label": "shipment_item_id"
    },
    {
      "src": "outbound_gatein_outboundpurpose",
      "dst": "outbound_gatein_outboundgateentry",
      "left": "||",
      "right": "o{",
      "label": "purpose_id"
    },
    {
      "src": "person_gatein_contractor",
      "dst": "person_gatein_labour",
      "left": "||",
      "right": "o{",
      "label": "contractor_id"
    },
    {
      "src": "person_gatein_gate",
      "dst": "person_gatein_entrylog",
      "left": "||",
      "right": "o{",
      "label": "gate_in_id"
    },
    {
      "src": "person_gatein_gate",
      "dst": "person_gatein_entrylog",
      "left": "||",
      "right": "o{",
      "label": "gate_out_id"
    },
    {
      "src": "person_gatein_labour",
      "dst": "person_gatein_entrylog",
      "left": "||",
      "right": "o{",
      "label": "labour_id"
    },
    {
      "src": "person_gatein_persontype",
      "dst": "person_gatein_entrylog",
      "left": "||",
      "right": "o{",
      "label": "person_type_id"
    },
    {
      "src": "person_gatein_visitor",
      "dst": "person_gatein_entrylog",
      "left": "||",
      "right": "o{",
      "label": "visitor_id"
    },
    {
      "src": "production_execution_breakdowncategory",
      "dst": "production_execution_machinebreakdown",
      "left": "||",
      "right": "o{",
      "label": "breakdown_category_id"
    },
    {
      "src": "production_execution_lineclearance",
      "dst": "production_execution_lineclearanceitem",
      "left": "||",
      "right": "o{",
      "label": "clearance_id"
    },
    {
      "src": "production_execution_machine",
      "dst": "production_execution_machinebreakdown",
      "left": "||",
      "right": "o{",
      "label": "machine_id"
    },
    {
      "src": "production_execution_machine",
      "dst": "production_execution_machinechecklistentry",
      "left": "||",
      "right": "o{",
      "label": "machine_id"
    },
    {
      "src": "production_execution_machine",
      "dst": "production_execution_machineruntime",
      "left": "||",
      "right": "o{",
      "label": "machine_id"
    },
    {
      "src": "production_execution_machine",
      "dst": "production_execution_productionrun_machines",
      "left": "||",
      "right": "o{",
      "label": "machine_id"
    },
    {
      "src": "production_execution_machinechecklisttemplate",
      "dst": "production_execution_machinechecklistentry",
      "left": "||",
      "right": "o{",
      "label": "template_id"
    },
    {
      "src": "production_execution_productionline",
      "dst": "production_execution_lineclearance",
      "left": "||",
      "right": "o{",
      "label": "line_id"
    },
    {
      "src": "production_execution_productionline",
      "dst": "production_execution_lineskuconfig",
      "left": "||",
      "right": "o{",
      "label": "line_id"
    },
    {
      "src": "production_execution_productionline",
      "dst": "production_execution_machine",
      "left": "||",
      "right": "o{",
      "label": "line_id"
    },
    {
      "src": "production_execution_productionline",
      "dst": "production_execution_productionrun",
      "left": "||",
      "right": "o{",
      "label": "line_id"
    },
    {
      "src": "production_execution_productionrun",
      "dst": "barcode_box",
      "left": "||",
      "right": "o{",
      "label": "production_run_id"
    },
    {
      "src": "production_execution_productionrun",
      "dst": "barcode_pallet",
      "left": "||",
      "right": "o{",
      "label": "production_run_id"
    },
    {
      "src": "production_execution_productionrun",
      "dst": "production_execution_finalqccheck",
      "left": "||",
      "right": "o{",
      "label": "production_run_id"
    },
    {
      "src": "production_execution_productionrun",
      "dst": "production_execution_inprocessqccheck",
      "left": "||",
      "right": "o{",
      "label": "production_run_id"
    },
    {
      "src": "production_execution_productionrun",
      "dst": "production_execution_lineclearance",
      "left": "||",
      "right": "o{",
      "label": "production_run_id"
    },
    {
      "src": "production_execution_productionrun",
      "dst": "production_execution_machinebreakdown",
      "left": "||",
      "right": "o{",
      "label": "production_run_id"
    },
    {
      "src": "production_execution_productionrun",
      "dst": "production_execution_machineruntime",
      "left": "||",
      "right": "o{",
      "label": "production_run_id"
    },
    {
      "src": "production_execution_productionrun",
      "dst": "production_execution_productionmanpower",
      "left": "||",
      "right": "o{",
      "label": "production_run_id"
    },
    {
      "src": "production_execution_productionrun",
      "dst": "production_execution_productionmaterialusage",
      "left": "||",
      "right": "o{",
      "label": "production_run_id"
    },
    {
      "src": "production_execution_productionrun",
      "dst": "production_execution_productionrun_machines",
      "left": "||",
      "right": "o{",
      "label": "productionrun_id"
    },
    {
      "src": "production_execution_productionrun",
      "dst": "production_execution_productionruncost",
      "left": "||",
      "right": "o{",
      "label": "production_run_id"
    },
    {
      "src": "production_execution_productionrun",
      "dst": "production_execution_productionsegment",
      "left": "||",
      "right": "o{",
      "label": "production_run_id"
    },
    {
      "src": "production_execution_productionrun",
      "dst": "production_execution_resourcecompressedair",
      "left": "||",
      "right": "o{",
      "label": "production_run_id"
    },
    {
      "src": "production_execution_productionrun",
      "dst": "production_execution_resourceelectricity",
      "left": "||",
      "right": "o{",
      "label": "production_run_id"
    },
    {
      "src": "production_execution_productionrun",
      "dst": "production_execution_resourcegas",
      "left": "||",
      "right": "o{",
      "label": "production_run_id"
    },
    {
      "src": "production_execution_productionrun",
      "dst": "production_execution_resourcelabour",
      "left": "||",
      "right": "o{",
      "label": "production_run_id"
    },
    {
      "src": "production_execution_productionrun",
      "dst": "production_execution_resourcemachinecost",
      "left": "||",
      "right": "o{",
      "label": "production_run_id"
    },
    {
      "src": "production_execution_productionrun",
      "dst": "production_execution_resourceoverhead",
      "left": "||",
      "right": "o{",
      "label": "production_run_id"
    },
    {
      "src": "production_execution_productionrun",
      "dst": "production_execution_resourcewater",
      "left": "||",
      "right": "o{",
      "label": "production_run_id"
    },
    {
      "src": "production_execution_productionrun",
      "dst": "production_execution_wastelog",
      "left": "||",
      "right": "o{",
      "label": "production_run_id"
    },
    {
      "src": "production_execution_productionrun",
      "dst": "quality_control_productionqcsession",
      "left": "||",
      "right": "o{",
      "label": "production_run_id"
    },
    {
      "src": "production_execution_productionrun",
      "dst": "warehouse_bomrequest",
      "left": "||",
      "right": "o{",
      "label": "production_run_id"
    },
    {
      "src": "production_execution_productionrun",
      "dst": "warehouse_finishedgoodsreceipt",
      "left": "||",
      "right": "o{",
      "label": "production_run_id"
    },
    {
      "src": "production_planning_productionplan",
      "dst": "production_planning_planmaterialrequirement",
      "left": "||",
      "right": "o{",
      "label": "production_plan_id"
    },
    {
      "src": "production_planning_productionplan",
      "dst": "production_planning_weeklyplan",
      "left": "||",
      "right": "o{",
      "label": "production_plan_id"
    },
    {
      "src": "production_planning_weeklyplan",
      "dst": "production_planning_dailyproductionentry",
      "left": "||",
      "right": "o{",
      "label": "weekly_plan_id"
    },
    {
      "src": "quality_control_materialarrivalslip",
      "dst": "quality_control_arrivalslipattachment",
      "left": "||",
      "right": "o{",
      "label": "arrival_slip_id"
    },
    {
      "src": "quality_control_materialarrivalslip",
      "dst": "quality_control_rawmaterialinspection",
      "left": "||",
      "right": "o{",
      "label": "arrival_slip_id"
    },
    {
      "src": "quality_control_materialtype",
      "dst": "quality_control_productionqcsession",
      "left": "||",
      "right": "o{",
      "label": "material_type_id"
    },
    {
      "src": "quality_control_materialtype",
      "dst": "quality_control_qcparametermaster",
      "left": "||",
      "right": "o{",
      "label": "material_type_id"
    },
    {
      "src": "quality_control_materialtype",
      "dst": "quality_control_rawmaterialinspection",
      "left": "||",
      "right": "o{",
      "label": "material_type_id"
    },
    {
      "src": "quality_control_productionqcsession",
      "dst": "quality_control_productionqcresult",
      "left": "||",
      "right": "o{",
      "label": "session_id"
    },
    {
      "src": "quality_control_qcparametermaster",
      "dst": "quality_control_inspectionparameterresult",
      "left": "||",
      "right": "o{",
      "label": "parameter_master_id"
    },
    {
      "src": "quality_control_qcparametermaster",
      "dst": "quality_control_productionqcresult",
      "left": "||",
      "right": "o{",
      "label": "parameter_master_id"
    },
    {
      "src": "quality_control_rawmaterialinspection",
      "dst": "gate_core_rejectedqcreturnitem",
      "left": "||",
      "right": "o{",
      "label": "inspection_id"
    },
    {
      "src": "quality_control_rawmaterialinspection",
      "dst": "quality_control_inspectionparameterresult",
      "left": "||",
      "right": "o{",
      "label": "inspection_id"
    },
    {
      "src": "raw_material_gatein_poitemreceipt",
      "dst": "grpo_grpolineposting",
      "left": "||",
      "right": "o{",
      "label": "po_item_receipt_id"
    },
    {
      "src": "raw_material_gatein_poitemreceipt",
      "dst": "quality_control_materialarrivalslip",
      "left": "||",
      "right": "o{",
      "label": "po_item_receipt_id"
    },
    {
      "src": "raw_material_gatein_poreceipt",
      "dst": "grpo_grpoposting",
      "left": "||",
      "right": "o{",
      "label": "po_receipt_id"
    },
    {
      "src": "raw_material_gatein_poreceipt",
      "dst": "grpo_grpoposting_po_receipts",
      "left": "||",
      "right": "o{",
      "label": "poreceipt_id"
    },
    {
      "src": "raw_material_gatein_poreceipt",
      "dst": "raw_material_gatein_poitemreceipt",
      "left": "||",
      "right": "o{",
      "label": "po_receipt_id"
    },
    {
      "src": "token_blacklist_outstandingtoken",
      "dst": "token_blacklist_blacklistedtoken",
      "left": "||",
      "right": "o{",
      "label": "token_id"
    },
    {
      "src": "vehicle_management_transporter",
      "dst": "dispatch_plans_dispatchplan",
      "left": "||",
      "right": "o{",
      "label": "transporter_id"
    },
    {
      "src": "vehicle_management_transporter",
      "dst": "vehicle_management_vehicle",
      "left": "||",
      "right": "o{",
      "label": "transporter_id"
    },
    {
      "src": "vehicle_management_vehicle",
      "dst": "dispatch_plans_dispatchplan",
      "left": "||",
      "right": "o{",
      "label": "vehicle_id"
    },
    {
      "src": "vehicle_management_vehicle",
      "dst": "driver_management_vehicleentry",
      "left": "||",
      "right": "o{",
      "label": "vehicle_id"
    },
    {
      "src": "vehicle_management_vehicle",
      "dst": "gate_core_bstgatein",
      "left": "||",
      "right": "o{",
      "label": "vehicle_id"
    },
    {
      "src": "vehicle_management_vehicle",
      "dst": "gate_core_bstgateout",
      "left": "||",
      "right": "o{",
      "label": "vehicle_id"
    },
    {
      "src": "vehicle_management_vehicle",
      "dst": "gate_core_bstgatereturn",
      "left": "||",
      "right": "o{",
      "label": "vehicle_id"
    },
    {
      "src": "vehicle_management_vehicle",
      "dst": "gate_core_dispatchgateout",
      "left": "||",
      "right": "o{",
      "label": "vehicle_id"
    },
    {
      "src": "vehicle_management_vehicle",
      "dst": "gate_core_emptyvehiclegatein",
      "left": "||",
      "right": "o{",
      "label": "vehicle_id"
    },
    {
      "src": "vehicle_management_vehicle",
      "dst": "gate_core_emptyvehiclegateout",
      "left": "||",
      "right": "o{",
      "label": "vehicle_id"
    },
    {
      "src": "vehicle_management_vehicle",
      "dst": "gate_core_jobworkgatein",
      "left": "||",
      "right": "o{",
      "label": "vehicle_id"
    },
    {
      "src": "vehicle_management_vehicle",
      "dst": "gate_core_rejectedqcreturnentry",
      "left": "||",
      "right": "o{",
      "label": "vehicle_id"
    },
    {
      "src": "vehicle_management_vehicletype",
      "dst": "vehicle_management_vehicle",
      "left": "||",
      "right": "o{",
      "label": "vehicle_type_id"
    },
    {
      "src": "warehouse_bomrequest",
      "dst": "warehouse_bomrequestline",
      "left": "||",
      "right": "o{",
      "label": "bom_request_id"
    }
  ],
  "diagrams": {
    "overview": {
      "title": "Overview",
      "src": "overview.svg",
      "width": 1336,
      "height": 1494
    },
    "app:accounts": {
      "title": "Accounts",
      "src": "apps/accounts.svg",
      "width": 1664,
      "height": 6552
    },
    "app:auth": {
      "title": "Auth",
      "src": "apps/auth.svg",
      "width": 1310,
      "height": 720
    },
    "app:barcode": {
      "title": "Barcode",
      "src": "apps/barcode.svg",
      "width": 1406,
      "height": 3072
    },
    "app:company": {
      "title": "Company",
      "src": "apps/company.svg",
      "width": 1508,
      "height": 9264
    },
    "app:construction_gatein": {
      "title": "Construction Gatein",
      "src": "apps/construction_gatein.svg",
      "width": 1354,
      "height": 786
    },
    "app:daily_needs_gatein": {
      "title": "Daily Needs Gatein",
      "src": "apps/daily_needs_gatein.svg",
      "width": 1368,
      "height": 960
    },
    "app:database_connections": {
      "title": "Database Connections",
      "src": "apps/database_connections.svg",
      "width": 1100,
      "height": 720
    },
    "app:dispatch_plans": {
      "title": "Dispatch Plans",
      "src": "apps/dispatch_plans.svg",
      "width": 1409,
      "height": 2454
    },
    "app:django": {
      "title": "Django",
      "src": "apps/django.svg",
      "width": 1310,
      "height": 900
    },
    "app:django_apscheduler": {
      "title": "Django Apscheduler",
      "src": "apps/django_apscheduler.svg",
      "width": 1100,
      "height": 720
    },
    "app:driver_management": {
      "title": "Driver Management",
      "src": "apps/driver_management.svg",
      "width": 1437,
      "height": 5532
    },
    "app:gate_core": {
      "title": "Gate Core",
      "src": "apps/gate_core.svg",
      "width": 2121,
      "height": 7968
    },
    "app:grpo": {
      "title": "Grpo",
      "src": "apps/grpo.svg",
      "width": 1351,
      "height": 2232
    },
    "app:inventory": {
      "title": "Inventory",
      "src": "apps/inventory.svg",
      "width": 1100,
      "height": 4194
    },
    "app:labour_verification": {
      "title": "Labour Verification",
      "src": "apps/labour_verification.svg",
      "width": 1100,
      "height": 720
    },
    "app:mail": {
      "title": "Mail",
      "src": "apps/mail.svg",
      "width": 1310,
      "height": 720
    },
    "app:maintenance_gatein": {
      "title": "Maintenance Gatein",
      "src": "apps/maintenance_gatein.svg",
      "width": 1340,
      "height": 768
    },
    "app:notifications": {
      "title": "Notifications",
      "src": "apps/notifications.svg",
      "width": 1310,
      "height": 768
    },
    "app:outbound_dispatch": {
      "title": "Outbound Dispatch",
      "src": "apps/outbound_dispatch.svg",
      "width": 1354,
      "height": 2280
    },
    "app:outbound_gatein": {
      "title": "Outbound Gatein",
      "src": "apps/outbound_gatein.svg",
      "width": 1375,
      "height": 840
    },
    "app:person_gatein": {
      "title": "Person Gatein",
      "src": "apps/person_gatein.svg",
      "width": 1100,
      "height": 1698
    },
    "app:production_execution": {
      "title": "Production Execution",
      "src": "apps/production_execution.svg",
      "width": 1735,
      "height": 7950
    },
    "app:production_planning": {
      "title": "Production Planning",
      "src": "apps/production_planning.svg",
      "width": 1319,
      "height": 1494
    },
    "app:quality_control": {
      "title": "Quality Control",
      "src": "apps/quality_control.svg",
      "width": 1455,
      "height": 3612
    },
    "app:raw_material_gatein": {
      "title": "Raw Material Gatein",
      "src": "apps/raw_material_gatein.svg",
      "width": 1358,
      "height": 1326
    },
    "app:security_checks": {
      "title": "Security Checks",
      "src": "apps/security_checks.svg",
      "width": 1319,
      "height": 720
    },
    "app:stock_dashboard": {
      "title": "Stock Dashboard",
      "src": "apps/stock_dashboard.svg",
      "width": 1100,
      "height": 720
    },
    "app:token_blacklist": {
      "title": "Token Blacklist",
      "src": "apps/token_blacklist.svg",
      "width": 1100,
      "height": 720
    },
    "app:vehicle_management": {
      "title": "Vehicle Management",
      "src": "apps/vehicle_management.svg",
      "width": 1337,
      "height": 2808
    },
    "app:warehouse": {
      "title": "Warehouse",
      "src": "apps/warehouse.svg",
      "width": 1360,
      "height": 1374
    },
    "app:weighment": {
      "title": "Weighment",
      "src": "apps/weighment.svg",
      "width": 1361,
      "height": 720
    },
    "table:accounts_department": {
      "title": "accounts_department Neighborhood",
      "src": "neighborhoods/accounts_department.svg",
      "width": 1070,
      "height": 720
    },
    "table:accounts_user": {
      "title": "accounts_user Neighborhood",
      "src": "neighborhoods/accounts_user.svg",
      "width": 5017,
      "height": 744
    },
    "table:accounts_user_groups": {
      "title": "accounts_user_groups Neighborhood",
      "src": "neighborhoods/accounts_user_groups.svg",
      "width": 1104,
      "height": 720
    },
    "table:accounts_user_user_permissions": {
      "title": "accounts_user_user_permissions Neighborhood",
      "src": "neighborhoods/accounts_user_user_permissions.svg",
      "width": 1104,
      "height": 720
    },
    "table:auth_group": {
      "title": "auth_group Neighborhood",
      "src": "neighborhoods/auth_group.svg",
      "width": 1330,
      "height": 720
    },
    "table:auth_group_permissions": {
      "title": "auth_group_permissions Neighborhood",
      "src": "neighborhoods/auth_group_permissions.svg",
      "width": 1070,
      "height": 720
    },
    "table:auth_permission": {
      "title": "auth_permission Neighborhood",
      "src": "neighborhoods/auth_permission.svg",
      "width": 1330,
      "height": 720
    },
    "table:barcode_barcodesequence": {
      "title": "barcode_barcodesequence Neighborhood",
      "src": "neighborhoods/barcode_barcodesequence.svg",
      "width": 1070,
      "height": 720
    },
    "table:barcode_box": {
      "title": "barcode_box Neighborhood",
      "src": "neighborhoods/barcode_box.svg",
      "width": 1679,
      "height": 870
    },
    "table:barcode_boxmovement": {
      "title": "barcode_boxmovement Neighborhood",
      "src": "neighborhoods/barcode_boxmovement.svg",
      "width": 1070,
      "height": 870
    },
    "table:barcode_labelprintlog": {
      "title": "barcode_labelprintlog Neighborhood",
      "src": "neighborhoods/barcode_labelprintlog.svg",
      "width": 1070,
      "height": 720
    },
    "table:barcode_loosestock": {
      "title": "barcode_loosestock Neighborhood",
      "src": "neighborhoods/barcode_loosestock.svg",
      "width": 1100,
      "height": 870
    },
    "table:barcode_pallet": {
      "title": "barcode_pallet Neighborhood",
      "src": "neighborhoods/barcode_pallet.svg",
      "width": 1762,
      "height": 720
    },
    "table:barcode_palletmovement": {
      "title": "barcode_palletmovement Neighborhood",
      "src": "neighborhoods/barcode_palletmovement.svg",
      "width": 1093,
      "height": 720
    },
    "table:barcode_scanlog": {
      "title": "barcode_scanlog Neighborhood",
      "src": "neighborhoods/barcode_scanlog.svg",
      "width": 1070,
      "height": 720
    },
    "table:company_company": {
      "title": "company_company Neighborhood",
      "src": "neighborhoods/company_company.svg",
      "width": 6745,
      "height": 906
    },
    "table:company_usercompany": {
      "title": "company_usercompany Neighborhood",
      "src": "neighborhoods/company_usercompany.svg",
      "width": 1070,
      "height": 720
    },
    "table:company_userrole": {
      "title": "company_userrole Neighborhood",
      "src": "neighborhoods/company_userrole.svg",
      "width": 1330,
      "height": 720
    },
    "table:construction_gatein_constructiongateentry": {
      "title": "construction_gatein_constructiongateentry Neighborhood",
      "src": "neighborhoods/construction_gatein_constructiongateentry.svg",
      "width": 1197,
      "height": 744
    },
    "table:construction_gatein_constructionmaterialcategory": {
      "title": "construction_gatein_constructionmaterialcategory Neighborhood",
      "src": "neighborhoods/construction_gatein_constructionmaterialcategory.svg",
      "width": 1457,
      "height": 720
    },
    "table:daily_needs_gatein_categorylist": {
      "title": "daily_needs_gatein_categorylist Neighborhood",
      "src": "neighborhoods/daily_needs_gatein_categorylist.svg",
      "width": 1420,
      "height": 720
    },
    "table:daily_needs_gatein_dailyneedgateentry": {
      "title": "daily_needs_gatein_dailyneedgateentry Neighborhood",
      "src": "neighborhoods/daily_needs_gatein_dailyneedgateentry.svg",
      "width": 1443,
      "height": 720
    },
    "table:daily_needs_gatein_dailyneedgateentryitem": {
      "title": "daily_needs_gatein_dailyneedgateentryitem Neighborhood",
      "src": "neighborhoods/daily_needs_gatein_dailyneedgateentryitem.svg",
      "width": 1160,
      "height": 720
    },
    "table:database_connections_databaseconnection": {
      "title": "database_connections_databaseconnection Neighborhood",
      "src": "neighborhoods/database_connections_databaseconnection.svg",
      "width": 1079,
      "height": 720
    },
    "table:dispatch_plans_dispatchplan": {
      "title": "dispatch_plans_dispatchplan Neighborhood",
      "src": "neighborhoods/dispatch_plans_dispatchplan.svg",
      "width": 1810,
      "height": 1144
    },
    "table:dispatch_plans_transporterapinvoiceattachment": {
      "title": "dispatch_plans_transporterapinvoiceattachment Neighborhood",
      "src": "neighborhoods/dispatch_plans_transporterapinvoiceattachment.svg",
      "width": 1155,
      "height": 720
    },
    "table:dispatch_plans_transporterapinvoiceline": {
      "title": "dispatch_plans_transporterapinvoiceline Neighborhood",
      "src": "neighborhoods/dispatch_plans_transporterapinvoiceline.svg",
      "width": 1516,
      "height": 720
    },
    "table:dispatch_plans_transporterapinvoiceposting": {
      "title": "dispatch_plans_transporterapinvoiceposting Neighborhood",
      "src": "neighborhoods/dispatch_plans_transporterapinvoiceposting.svg",
      "width": 1477,
      "height": 720
    },
    "table:django_admin_log": {
      "title": "django_admin_log Neighborhood",
      "src": "neighborhoods/django_admin_log.svg",
      "width": 1070,
      "height": 720
    },
    "table:django_apscheduler_djangojob": {
      "title": "django_apscheduler_djangojob Neighborhood",
      "src": "neighborhoods/django_apscheduler_djangojob.svg",
      "width": 1357,
      "height": 720
    },
    "table:django_apscheduler_djangojobexecution": {
      "title": "django_apscheduler_djangojobexecution Neighborhood",
      "src": "neighborhoods/django_apscheduler_djangojobexecution.svg",
      "width": 1125,
      "height": 720
    },
    "table:django_content_type": {
      "title": "django_content_type Neighborhood",
      "src": "neighborhoods/django_content_type.svg",
      "width": 1364,
      "height": 720
    },
    "table:django_migrations": {
      "title": "django_migrations Neighborhood",
      "src": "neighborhoods/django_migrations.svg",
      "width": 1070,
      "height": 720
    },
    "table:django_session": {
      "title": "django_session Neighborhood",
      "src": "neighborhoods/django_session.svg",
      "width": 1070,
      "height": 720
    },
    "table:driver_management_driver": {
      "title": "driver_management_driver Neighborhood",
      "src": "neighborhoods/driver_management_driver.svg",
      "width": 2634,
      "height": 720
    },
    "table:driver_management_vehicleentry": {
      "title": "driver_management_vehicleentry Neighborhood",
      "src": "neighborhoods/driver_management_vehicleentry.svg",
      "width": 3231,
      "height": 960
    },
    "table:gate_core_bstgatein": {
      "title": "gate_core_bstgatein Neighborhood",
      "src": "neighborhoods/gate_core_bstgatein.svg",
      "width": 2033,
      "height": 870
    },
    "table:gate_core_bstgateinitem": {
      "title": "gate_core_bstgateinitem Neighborhood",
      "src": "neighborhoods/gate_core_bstgateinitem.svg",
      "width": 1410,
      "height": 720
    },
    "table:gate_core_bstgateout": {
      "title": "gate_core_bstgateout Neighborhood",
      "src": "neighborhoods/gate_core_bstgateout.svg",
      "width": 1711,
      "height": 960
    },
    "table:gate_core_bstgateoutitem": {
      "title": "gate_core_bstgateoutitem Neighborhood",
      "src": "neighborhoods/gate_core_bstgateoutitem.svg",
      "width": 1364,
      "height": 720
    },
    "table:gate_core_bstgatereturn": {
      "title": "gate_core_bstgatereturn Neighborhood",
      "src": "neighborhoods/gate_core_bstgatereturn.svg",
      "width": 1766,
      "height": 870
    },
    "table:gate_core_dispatchgatelock": {
      "title": "gate_core_dispatchgatelock Neighborhood",
      "src": "neighborhoods/gate_core_dispatchgatelock.svg",
      "width": 1104,
      "height": 720
    },
    "table:gate_core_dispatchgateout": {
      "title": "gate_core_dispatchgateout Neighborhood",
      "src": "neighborhoods/gate_core_dispatchgateout.svg",
      "width": 2088,
      "height": 1234
    },
    "table:gate_core_dispatchgateoutline": {
      "title": "gate_core_dispatchgateoutline Neighborhood",
      "src": "neighborhoods/gate_core_dispatchgateoutline.svg",
      "width": 1104,
      "height": 720
    },
    "table:gate_core_emptyvehiclegatein": {
      "title": "gate_core_emptyvehiclegatein Neighborhood",
      "src": "neighborhoods/gate_core_emptyvehiclegatein.svg",
      "width": 1731,
      "height": 870
    },
    "table:gate_core_emptyvehiclegateinitem": {
      "title": "gate_core_emptyvehiclegateinitem Neighborhood",
      "src": "neighborhoods/gate_core_emptyvehiclegateinitem.svg",
      "width": 1104,
      "height": 720
    },
    "table:gate_core_emptyvehiclegateout": {
      "title": "gate_core_emptyvehiclegateout Neighborhood",
      "src": "neighborhoods/gate_core_emptyvehiclegateout.svg",
      "width": 1451,
      "height": 870
    },
    "table:gate_core_gateattachment": {
      "title": "gate_core_gateattachment Neighborhood",
      "src": "neighborhoods/gate_core_gateattachment.svg",
      "width": 1070,
      "height": 720
    },
    "table:gate_core_jobworkgatein": {
      "title": "gate_core_jobworkgatein Neighborhood",
      "src": "neighborhoods/gate_core_jobworkgatein.svg",
      "width": 1776,
      "height": 964
    },
    "table:gate_core_jobworkgateinitem": {
      "title": "gate_core_jobworkgateinitem Neighborhood",
      "src": "neighborhoods/gate_core_jobworkgateinitem.svg",
      "width": 1104,
      "height": 720
    },
    "table:gate_core_rejectedqcreturnentry": {
      "title": "gate_core_rejectedqcreturnentry Neighborhood",
      "src": "neighborhoods/gate_core_rejectedqcreturnentry.svg",
      "width": 1728,
      "height": 870
    },
    "table:gate_core_rejectedqcreturnitem": {
      "title": "gate_core_rejectedqcreturnitem Neighborhood",
      "src": "neighborhoods/gate_core_rejectedqcreturnitem.svg",
      "width": 1437,
      "height": 720
    },
    "table:gate_core_unitchoice": {
      "title": "gate_core_unitchoice Neighborhood",
      "src": "neighborhoods/gate_core_unitchoice.svg",
      "width": 1802,
      "height": 720
    },
    "table:grpo_grpoattachment": {
      "title": "grpo_grpoattachment Neighborhood",
      "src": "neighborhoods/grpo_grpoattachment.svg",
      "width": 1118,
      "height": 720
    },
    "table:grpo_grpolineposting": {
      "title": "grpo_grpolineposting Neighborhood",
      "src": "neighborhoods/grpo_grpolineposting.svg",
      "width": 1118,
      "height": 720
    },
    "table:grpo_grpoposting": {
      "title": "grpo_grpoposting Neighborhood",
      "src": "neighborhoods/grpo_grpoposting.svg",
      "width": 1385,
      "height": 798
    },
    "table:grpo_grpoposting_po_receipts": {
      "title": "grpo_grpoposting_po_receipts Neighborhood",
      "src": "neighborhoods/grpo_grpoposting_po_receipts.svg",
      "width": 1118,
      "height": 720
    },
    "table:grpo_servicegrpoattachment": {
      "title": "grpo_servicegrpoattachment Neighborhood",
      "src": "neighborhoods/grpo_servicegrpoattachment.svg",
      "width": 1118,
      "height": 720
    },
    "table:grpo_servicegrpolineposting": {
      "title": "grpo_servicegrpolineposting Neighborhood",
      "src": "neighborhoods/grpo_servicegrpolineposting.svg",
      "width": 1419,
      "height": 720
    },
    "table:grpo_servicegrpoposting": {
      "title": "grpo_servicegrpoposting Neighborhood",
      "src": "neighborhoods/grpo_servicegrpoposting.svg",
      "width": 1759,
      "height": 720
    },
    "table:inventory_sapbatchstock": {
      "title": "inventory_sapbatchstock Neighborhood",
      "src": "neighborhoods/inventory_sapbatchstock.svg",
      "width": 1120,
      "height": 720
    },
    "table:inventory_sapcompany": {
      "title": "inventory_sapcompany Neighborhood",
      "src": "neighborhoods/inventory_sapcompany.svg",
      "width": 2398,
      "height": 906
    },
    "table:inventory_sapinventoryagingsnapshot": {
      "title": "inventory_sapinventoryagingsnapshot Neighborhood",
      "src": "neighborhoods/inventory_sapinventoryagingsnapshot.svg",
      "width": 1120,
      "height": 720
    },
    "table:inventory_sapinventorymovement": {
      "title": "inventory_sapinventorymovement Neighborhood",
      "src": "neighborhoods/inventory_sapinventorymovement.svg",
      "width": 1118,
      "height": 720
    },
    "table:inventory_sapinventoryvaluation": {
      "title": "inventory_sapinventoryvaluation Neighborhood",
      "src": "neighborhoods/inventory_sapinventoryvaluation.svg",
      "width": 1118,
      "height": 748
    },
    "table:inventory_sapitem": {
      "title": "inventory_sapitem Neighborhood",
      "src": "neighborhoods/inventory_sapitem.svg",
      "width": 1120,
      "height": 820
    },
    "table:inventory_sapitemgroup": {
      "title": "inventory_sapitemgroup Neighborhood",
      "src": "neighborhoods/inventory_sapitemgroup.svg",
      "width": 1118,
      "height": 720
    },
    "table:inventory_sapitemwarehousestock": {
      "title": "inventory_sapitemwarehousestock Neighborhood",
      "src": "neighborhoods/inventory_sapitemwarehousestock.svg",
      "width": 1118,
      "height": 720
    },
    "table:inventory_sapsyncrun": {
      "title": "inventory_sapsyncrun Neighborhood",
      "src": "neighborhoods/inventory_sapsyncrun.svg",
      "width": 1118,
      "height": 720
    },
    "table:inventory_sapwarehouse": {
      "title": "inventory_sapwarehouse Neighborhood",
      "src": "neighborhoods/inventory_sapwarehouse.svg",
      "width": 1118,
      "height": 720
    },
    "table:labour_verification_departmentlabourresponse": {
      "title": "labour_verification_departmentlabourresponse Neighborhood",
      "src": "neighborhoods/labour_verification_departmentlabourresponse.svg",
      "width": 1169,
      "height": 720
    },
    "table:labour_verification_labourverificationrequest": {
      "title": "labour_verification_labourverificationrequest Neighborhood",
      "src": "neighborhoods/labour_verification_labourverificationrequest.svg",
      "width": 1429,
      "height": 720
    },
    "table:mail_emaillog": {
      "title": "mail_emaillog Neighborhood",
      "src": "neighborhoods/mail_emaillog.svg",
      "width": 1070,
      "height": 720
    },
    "table:maintenance_gatein_maintenancegateentry": {
      "title": "maintenance_gatein_maintenancegateentry Neighborhood",
      "src": "neighborhoods/maintenance_gatein_maintenancegateentry.svg",
      "width": 1113,
      "height": 744
    },
    "table:maintenance_gatein_maintenancetype": {
      "title": "maintenance_gatein_maintenancetype Neighborhood",
      "src": "neighborhoods/maintenance_gatein_maintenancetype.svg",
      "width": 1406,
      "height": 720
    },
    "table:notifications_notification": {
      "title": "notifications_notification Neighborhood",
      "src": "neighborhoods/notifications_notification.svg",
      "width": 1070,
      "height": 720
    },
    "table:notifications_userdevice": {
      "title": "notifications_userdevice Neighborhood",
      "src": "neighborhoods/notifications_userdevice.svg",
      "width": 1070,
      "height": 720
    },
    "table:outbound_dispatch_goodsissueposting": {
      "title": "outbound_dispatch_goodsissueposting Neighborhood",
      "src": "neighborhoods/outbound_dispatch_goodsissueposting.svg",
      "width": 1070,
      "height": 720
    },
    "table:outbound_dispatch_outboundloadrecord": {
      "title": "outbound_dispatch_outboundloadrecord Neighborhood",
      "src": "neighborhoods/outbound_dispatch_outboundloadrecord.svg",
      "width": 1114,
      "height": 720
    },
    "table:outbound_dispatch_picktask": {
      "title": "outbound_dispatch_picktask Neighborhood",
      "src": "neighborhoods/outbound_dispatch_picktask.svg",
      "width": 1083,
      "height": 720
    },
    "table:outbound_dispatch_shipmentorder": {
      "title": "outbound_dispatch_shipmentorder Neighborhood",
      "src": "neighborhoods/outbound_dispatch_shipmentorder.svg",
      "width": 1769,
      "height": 730
    },
    "table:outbound_dispatch_shipmentorderitem": {
      "title": "outbound_dispatch_shipmentorderitem Neighborhood",
      "src": "neighborhoods/outbound_dispatch_shipmentorderitem.svg",
      "width": 1357,
      "height": 720
    },
    "table:outbound_gatein_outboundgateentry": {
      "title": "outbound_gatein_outboundgateentry Neighborhood",
      "src": "neighborhoods/outbound_gatein_outboundgateentry.svg",
      "width": 1135,
      "height": 720
    },
    "table:outbound_gatein_outboundpurpose": {
      "title": "outbound_gatein_outboundpurpose Neighborhood",
      "src": "neighborhoods/outbound_gatein_outboundpurpose.svg",
      "width": 1371,
      "height": 720
    },
    "table:person_gatein_contractor": {
      "title": "person_gatein_contractor Neighborhood",
      "src": "neighborhoods/person_gatein_contractor.svg",
      "width": 1394,
      "height": 720
    },
    "table:person_gatein_entrylog": {
      "title": "person_gatein_entrylog Neighborhood",
      "src": "neighborhoods/person_gatein_entrylog.svg",
      "width": 1502,
      "height": 762
    },
    "table:person_gatein_gate": {
      "title": "person_gatein_gate Neighborhood",
      "src": "neighborhoods/person_gatein_gate.svg",
      "width": 1385,
      "height": 720
    },
    "table:person_gatein_labour": {
      "title": "person_gatein_labour Neighborhood",
      "src": "neighborhoods/person_gatein_labour.svg",
      "width": 1454,
      "height": 720
    },
    "table:person_gatein_persontype": {
      "title": "person_gatein_persontype Neighborhood",
      "src": "neighborhoods/person_gatein_persontype.svg",
      "width": 1385,
      "height": 720
    },
    "table:person_gatein_visitor": {
      "title": "person_gatein_visitor Neighborhood",
      "src": "neighborhoods/person_gatein_visitor.svg",
      "width": 1385,
      "height": 720
    },
    "table:production_execution_breakdowncategory": {
      "title": "production_execution_breakdowncategory Neighborhood",
      "src": "neighborhoods/production_execution_breakdowncategory.svg",
      "width": 1357,
      "height": 720
    },
    "table:production_execution_finalqccheck": {
      "title": "production_execution_finalqccheck Neighborhood",
      "src": "neighborhoods/production_execution_finalqccheck.svg",
      "width": 1104,
      "height": 720
    },
    "table:production_execution_inprocessqccheck": {
      "title": "production_execution_inprocessqccheck Neighborhood",
      "src": "neighborhoods/production_execution_inprocessqccheck.svg",
      "width": 1104,
      "height": 720
    },
    "table:production_execution_lineclearance": {
      "title": "production_execution_lineclearance Neighborhood",
      "src": "neighborhoods/production_execution_lineclearance.svg",
      "width": 1407,
      "height": 834
    },
    "table:production_execution_lineclearanceitem": {
      "title": "production_execution_lineclearanceitem Neighborhood",
      "src": "neighborhoods/production_execution_lineclearanceitem.svg",
      "width": 1132,
      "height": 720
    },
    "table:production_execution_lineskuconfig": {
      "title": "production_execution_lineskuconfig Neighborhood",
      "src": "neighborhoods/production_execution_lineskuconfig.svg",
      "width": 1155,
      "height": 720
    },
    "table:production_execution_machine": {
      "title": "production_execution_machine Neighborhood",
      "src": "neighborhoods/production_execution_machine.svg",
      "width": 1780,
      "height": 720
    },
    "table:production_execution_machinebreakdown": {
      "title": "production_execution_machinebreakdown Neighborhood",
      "src": "neighborhoods/production_execution_machinebreakdown.svg",
      "width": 1141,
      "height": 888
    },
    "table:production_execution_machinechecklistentry": {
      "title": "production_execution_machinechecklistentry Neighborhood",
      "src": "neighborhoods/production_execution_machinechecklistentry.svg",
      "width": 1155,
      "height": 852
    },
    "table:production_execution_machinechecklisttemplate": {
      "title": "production_execution_machinechecklisttemplate Neighborhood",
      "src": "neighborhoods/production_execution_machinechecklisttemplate.svg",
      "width": 1415,
      "height": 720
    },
    "table:production_execution_machineruntime": {
      "title": "production_execution_machineruntime Neighborhood",
      "src": "neighborhoods/production_execution_machineruntime.svg",
      "width": 1104,
      "height": 720
    },
    "table:production_execution_productionline": {
      "title": "production_execution_productionline Neighborhood",
      "src": "neighborhoods/production_execution_productionline.svg",
      "width": 1732,
      "height": 720
    },
    "table:production_execution_productionmanpower": {
      "title": "production_execution_productionmanpower Neighborhood",
      "src": "neighborhoods/production_execution_productionmanpower.svg",
      "width": 1104,
      "height": 720
    },
    "table:production_execution_productionmaterialusage": {
      "title": "production_execution_productionmaterialusage Neighborhood",
      "src": "neighborhoods/production_execution_productionmaterialusage.svg",
      "width": 1120,
      "height": 720
    },
    "table:production_execution_productionrun": {
      "title": "production_execution_productionrun Neighborhood",
      "src": "neighborhoods/production_execution_productionrun.svg",
      "width": 5018,
      "height": 852
    },
    "table:production_execution_productionrun_machines": {
      "title": "production_execution_productionrun_machines Neighborhood",
      "src": "neighborhoods/production_execution_productionrun_machines.svg",
      "width": 1113,
      "height": 720
    },
    "table:production_execution_productionruncost": {
      "title": "production_execution_productionruncost Neighborhood",
      "src": "neighborhoods/production_execution_productionruncost.svg",
      "width": 1104,
      "height": 720
    },
    "table:production_execution_productionsegment": {
      "title": "production_execution_productionsegment Neighborhood",
      "src": "neighborhoods/production_execution_productionsegment.svg",
      "width": 1104,
      "height": 720
    },
    "table:production_execution_resourcecompressedair": {
      "title": "production_execution_resourcecompressedair Neighborhood",
      "src": "neighborhoods/production_execution_resourcecompressedair.svg",
      "width": 1106,
      "height": 720
    },
    "table:production_execution_resourceelectricity": {
      "title": "production_execution_resourceelectricity Neighborhood",
      "src": "neighborhoods/production_execution_resourceelectricity.svg",
      "width": 1104,
      "height": 720
    },
    "table:production_execution_resourcegas": {
      "title": "production_execution_resourcegas Neighborhood",
      "src": "neighborhoods/production_execution_resourcegas.svg",
      "width": 1104,
      "height": 720
    },
    "table:production_execution_resourcelabour": {
      "title": "production_execution_resourcelabour Neighborhood",
      "src": "neighborhoods/production_execution_resourcelabour.svg",
      "width": 1104,
      "height": 720
    },
    "table:production_execution_resourcemachinecost": {
      "title": "production_execution_resourcemachinecost Neighborhood",
      "src": "neighborhoods/production_execution_resourcemachinecost.svg",
      "width": 1104,
      "height": 720
    },
    "table:production_execution_resourceoverhead": {
      "title": "production_execution_resourceoverhead Neighborhood",
      "src": "neighborhoods/production_execution_resourceoverhead.svg",
      "width": 1104,
      "height": 720
    },
    "table:production_execution_resourcewater": {
      "title": "production_execution_resourcewater Neighborhood",
      "src": "neighborhoods/production_execution_resourcewater.svg",
      "width": 1104,
      "height": 720
    },
    "table:production_execution_wastelog": {
      "title": "production_execution_wastelog Neighborhood",
      "src": "neighborhoods/production_execution_wastelog.svg",
      "width": 1134,
      "height": 720
    },
    "table:production_planning_dailyproductionentry": {
      "title": "production_planning_dailyproductionentry Neighborhood",
      "src": "neighborhoods/production_planning_dailyproductionentry.svg",
      "width": 1070,
      "height": 720
    },
    "table:production_planning_planmaterialrequirement": {
      "title": "production_planning_planmaterialrequirement Neighborhood",
      "src": "neighborhoods/production_planning_planmaterialrequirement.svg",
      "width": 1099,
      "height": 720
    },
    "table:production_planning_productionplan": {
      "title": "production_planning_productionplan Neighborhood",
      "src": "neighborhoods/production_planning_productionplan.svg",
      "width": 1399,
      "height": 720
    },
    "table:production_planning_weeklyplan": {
      "title": "production_planning_weeklyplan Neighborhood",
      "src": "neighborhoods/production_planning_weeklyplan.svg",
      "width": 1398,
      "height": 720
    },
    "table:quality_control_arrivalslipattachment": {
      "title": "quality_control_arrivalslipattachment Neighborhood",
      "src": "neighborhoods/quality_control_arrivalslipattachment.svg",
      "width": 1083,
      "height": 720
    },
    "table:quality_control_inspectionparameterresult": {
      "title": "quality_control_inspectionparameterresult Neighborhood",
      "src": "neighborhoods/quality_control_inspectionparameterresult.svg",
      "width": 1097,
      "height": 720
    },
    "table:quality_control_materialarrivalslip": {
      "title": "quality_control_materialarrivalslip Neighborhood",
      "src": "neighborhoods/quality_control_materialarrivalslip.svg",
      "width": 1366,
      "height": 784
    },
    "table:quality_control_materialtype": {
      "title": "quality_control_materialtype Neighborhood",
      "src": "neighborhoods/quality_control_materialtype.svg",
      "width": 1663,
      "height": 720
    },
    "table:quality_control_productionqcresult": {
      "title": "quality_control_productionqcresult Neighborhood",
      "src": "neighborhoods/quality_control_productionqcresult.svg",
      "width": 1083,
      "height": 720
    },
    "table:quality_control_productionqcsession": {
      "title": "quality_control_productionqcsession Neighborhood",
      "src": "neighborhoods/quality_control_productionqcsession.svg",
      "width": 1725,
      "height": 720
    },
    "table:quality_control_qcparametermaster": {
      "title": "quality_control_qcparametermaster Neighborhood",
      "src": "neighborhoods/quality_control_qcparametermaster.svg",
      "width": 1385,
      "height": 720
    },
    "table:quality_control_rawmaterialinspection": {
      "title": "quality_control_rawmaterialinspection Neighborhood",
      "src": "neighborhoods/quality_control_rawmaterialinspection.svg",
      "width": 1803,
      "height": 964
    },
    "table:raw_material_gatein_poitemreceipt": {
      "title": "raw_material_gatein_poitemreceipt Neighborhood",
      "src": "neighborhoods/raw_material_gatein_poitemreceipt.svg",
      "width": 1343,
      "height": 720
    },
    "table:raw_material_gatein_poreceipt": {
      "title": "raw_material_gatein_poreceipt Neighborhood",
      "src": "neighborhoods/raw_material_gatein_poreceipt.svg",
      "width": 1378,
      "height": 852
    },
    "table:security_checks_securitycheck": {
      "title": "security_checks_securitycheck Neighborhood",
      "src": "neighborhoods/security_checks_securitycheck.svg",
      "width": 1079,
      "height": 720
    },
    "table:stock_dashboard_stockalertlog": {
      "title": "stock_dashboard_stockalertlog Neighborhood",
      "src": "neighborhoods/stock_dashboard_stockalertlog.svg",
      "width": 1070,
      "height": 720
    },
    "table:token_blacklist_blacklistedtoken": {
      "title": "token_blacklist_blacklistedtoken Neighborhood",
      "src": "neighborhoods/token_blacklist_blacklistedtoken.svg",
      "width": 1104,
      "height": 720
    },
    "table:token_blacklist_outstandingtoken": {
      "title": "token_blacklist_outstandingtoken Neighborhood",
      "src": "neighborhoods/token_blacklist_outstandingtoken.svg",
      "width": 1330,
      "height": 720
    },
    "table:vehicle_management_transporter": {
      "title": "vehicle_management_transporter Neighborhood",
      "src": "neighborhoods/vehicle_management_transporter.svg",
      "width": 1371,
      "height": 720
    },
    "table:vehicle_management_vehicle": {
      "title": "vehicle_management_vehicle Neighborhood",
      "src": "neighborhoods/vehicle_management_vehicle.svg",
      "width": 2654,
      "height": 720
    },
    "table:vehicle_management_vehicletype": {
      "title": "vehicle_management_vehicletype Neighborhood",
      "src": "neighborhoods/vehicle_management_vehicletype.svg",
      "width": 1371,
      "height": 720
    },
    "table:warehouse_bomrequest": {
      "title": "warehouse_bomrequest Neighborhood",
      "src": "neighborhoods/warehouse_bomrequest.svg",
      "width": 1364,
      "height": 720
    },
    "table:warehouse_bomrequestline": {
      "title": "warehouse_bomrequestline Neighborhood",
      "src": "neighborhoods/warehouse_bomrequestline.svg",
      "width": 1097,
      "height": 720
    },
    "table:warehouse_finishedgoodsreceipt": {
      "title": "warehouse_finishedgoodsreceipt Neighborhood",
      "src": "neighborhoods/warehouse_finishedgoodsreceipt.svg",
      "width": 1120,
      "height": 720
    },
    "table:weighment_weighment": {
      "title": "weighment_weighment Neighborhood",
      "src": "neighborhoods/weighment_weighment.svg",
      "width": 1121,
      "height": 720
    }
  }
};
