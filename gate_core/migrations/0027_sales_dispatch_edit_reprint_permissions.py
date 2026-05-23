from django.db import migrations


SALES_DISPATCH_PERMISSIONS = [
    ("can_view_sales_dispatch_out", "Can view sales dispatch out"),
    ("can_create_sales_dispatch_out", "Can create sales dispatch out"),
    ("can_edit_sales_dispatch_out", "Can edit sales dispatch out"),
    ("can_upload_sales_dispatch_photo", "Can upload sales dispatch truck photo"),
    ("can_print_sales_dispatch_gatepass", "Can print sales dispatch gatepass"),
    ("can_reprint_sales_dispatch_gatepass", "Can reprint sales dispatch gatepass"),
    ("can_commit_sales_dispatch_print", "Can commit sales dispatch print"),
    ("can_reject_sales_dispatch_out", "Can reject sales dispatch out"),
    ("can_cancel_sales_dispatch_out", "Can cancel sales dispatch out"),
    ("can_dispatch_sales_dispatch_out", "Can mark sales dispatch out as dispatched"),
    ("can_view_sales_dispatch_reports", "Can view sales dispatch reports"),
]

SALES_DISPATCH_LOCK_PERMISSIONS = [
    ("can_manage_sales_dispatch_lock", "Can manage sales dispatch lock"),
]


def add_missing_permissions_to_group(apps, schema_editor):
    ContentType = apps.get_model("contenttypes", "ContentType")
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    SalesDispatchGateOut = apps.get_model("gate_core", "SalesDispatchGateOut")
    SalesDispatchLock = apps.get_model("gate_core", "SalesDispatchLock")

    permissions = []
    content_type = ContentType.objects.get_for_model(SalesDispatchGateOut)
    for codename, name in SALES_DISPATCH_PERMISSIONS:
        permission, created = Permission.objects.get_or_create(
            codename=codename,
            content_type=content_type,
            defaults={"name": name},
        )
        if not created and permission.name != name:
            permission.name = name
            permission.save(update_fields=["name"])
        permissions.append(permission)

    lock_content_type = ContentType.objects.get_for_model(SalesDispatchLock)
    for codename, name in SALES_DISPATCH_LOCK_PERMISSIONS:
        permission, created = Permission.objects.get_or_create(
            codename=codename,
            content_type=lock_content_type,
            defaults={"name": name},
        )
        if not created and permission.name != name:
            permission.name = name
            permission.save(update_fields=["name"])
        permissions.append(permission)

    for group in Group.objects.filter(name__in=["Gate Core", "Gate"]):
        group.permissions.add(*permissions)


class Migration(migrations.Migration):

    dependencies = [
        ("gate_core", "0026_salesdispatchgatepassprintlog"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="salesdispatchgateout",
            options={
                "ordering": ["-created_at"],
                "permissions": SALES_DISPATCH_PERMISSIONS,
            },
        ),
        migrations.RunPython(add_missing_permissions_to_group, migrations.RunPython.noop),
    ]
