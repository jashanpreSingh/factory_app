from django.db import migrations


SALES_DISPATCH_OUT_PERMISSIONS = [
    ("can_view_sales_dispatch_out", "Can view sales dispatch out"),
    ("can_create_sales_dispatch_out", "Can create sales dispatch out"),
]


def add_sales_dispatch_out_permissions(apps, schema_editor):
    ContentType = apps.get_model("contenttypes", "ContentType")
    Permission = apps.get_model("auth", "Permission")
    Group = apps.get_model("auth", "Group")

    ct, _ = ContentType.objects.get_or_create(
        app_label="gate_core",
        model="gatecore",
    )

    permission_objects = []
    for codename, name in SALES_DISPATCH_OUT_PERMISSIONS:
        permission, created = Permission.objects.get_or_create(
            codename=codename,
            content_type=ct,
            defaults={"name": name},
        )
        if not created and permission.name != name:
            permission.name = name
            permission.save(update_fields=["name"])
        permission_objects.append(permission)

    try:
        group = Group.objects.get(name="gate_core")
    except Group.DoesNotExist:
        return

    group.permissions.add(*permission_objects)


def remove_sales_dispatch_out_permissions(apps, schema_editor):
    ContentType = apps.get_model("contenttypes", "ContentType")
    Permission = apps.get_model("auth", "Permission")

    try:
        ct = ContentType.objects.get(app_label="gate_core", model="gatecore")
    except ContentType.DoesNotExist:
        return

    Permission.objects.filter(
        codename__in=[codename for codename, _ in SALES_DISPATCH_OUT_PERMISSIONS],
        content_type=ct,
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("gate_core", "0021_bst_in_return_sap_reference"),
    ]

    operations = [
        migrations.RunPython(
            add_sales_dispatch_out_permissions,
            remove_sales_dispatch_out_permissions,
        ),
    ]
