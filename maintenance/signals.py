MAINTENANCE_ROLE_PERMISSIONS = {
    "maintenance": "__all__",
    "maintenance_admin": "__all__",
    "maintenance_head": [
        "can_view_maintenance_module",
        "can_view_maintenance_dashboard",
        "can_manage_maintenance_settings",
        "add_asset",
        "view_asset",
        "change_asset",
        "can_deactivate_asset",
        "add_assetcategory",
        "view_assetcategory",
        "change_assetcategory",
        "add_assetlocation",
        "view_assetlocation",
        "change_assetlocation",
        "add_assetdepartment",
        "view_assetdepartment",
        "change_assetdepartment",
        "add_assetphoto",
        "view_assetphoto",
        "change_assetphoto",
        "add_assetdocument",
        "view_assetdocument",
        "change_assetdocument",
        "can_view_work_order",
        "can_manage_work_order",
        "can_create_work_order",
        "can_assign_work_order",
        "can_start_work_order",
        "can_complete_work_order",
        "can_approve_work_order",
        "can_close_work_order",
        "add_maintenanceworkorder",
        "view_maintenanceworkorder",
        "change_maintenanceworkorder",
        "add_maintenanceworkorderphoto",
        "view_maintenanceworkorderphoto",
        "change_maintenanceworkorderphoto",
        "can_view_pm",
        "can_manage_pm",
        "can_view_spare",
        "can_manage_spare",
        "add_maintenancegatelink",
        "view_maintenancegatelink",
        "change_maintenancegatelink",
        "view_maintenancesparereceipt",
        "add_maintenancesparereceipt",
        "can_view_vendor",
        "can_manage_vendor",
        "add_maintenancevendorvisit",
        "view_maintenancevendorvisit",
        "change_maintenancevendorvisit",
        "can_view_maintenance_reports",
    ],
    "maintenance_technician": [
        "can_view_maintenance_module",
        "can_view_maintenance_dashboard",
        "view_asset",
        "add_assetphoto",
        "view_assetphoto",
        "change_assetphoto",
        "add_assetdocument",
        "view_assetdocument",
        "can_view_work_order",
        "can_create_work_order",
        "can_start_work_order",
        "can_complete_work_order",
        "add_maintenanceworkorder",
        "view_maintenanceworkorder",
        "change_maintenanceworkorder",
        "add_maintenanceworkorderphoto",
        "view_maintenanceworkorderphoto",
        "change_maintenanceworkorderphoto",
        "can_view_pm",
        "can_view_vendor",
        "view_maintenancevendorvisit",
    ],
    "maintenance_viewer": [
        "can_view_maintenance_module",
        "can_view_maintenance_dashboard",
        "view_asset",
        "view_assetcategory",
        "view_assetlocation",
        "view_assetdepartment",
        "view_assetphoto",
        "view_assetdocument",
        "can_view_work_order",
        "view_maintenanceworkorder",
        "view_maintenanceworkorderphoto",
        "can_view_pm",
        "can_view_spare",
        "view_maintenancegatelink",
        "view_maintenancesparereceipt",
        "can_view_vendor",
        "view_maintenancevendorvisit",
        "can_view_maintenance_reports",
    ],
}


def ensure_maintenance_groups(sender, app_config, **kwargs):
    if app_config.label != "maintenance":
        return

    from django.contrib.auth.models import Group, Permission

    permissions = Permission.objects.filter(content_type__app_label="maintenance")
    permissions_by_code = {permission.codename: permission for permission in permissions}

    for group_name, codenames in MAINTENANCE_ROLE_PERMISSIONS.items():
        group, _created = Group.objects.get_or_create(name=group_name)
        if codenames == "__all__":
            group.permissions.set(permissions)
            continue

        group.permissions.set(
            [
                permissions_by_code[codename]
                for codename in codenames
                if codename in permissions_by_code
            ]
        )
