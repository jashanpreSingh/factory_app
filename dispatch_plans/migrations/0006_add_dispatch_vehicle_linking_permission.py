from django.db import migrations


NEW_PERMISSION = ("can_link_dispatch_vehicle", "Can link dispatch vehicles")
LEGACY_PERMISSION_CODENAMES = (
    "can_view_dispatch_plans",
    "can_edit_dispatch_plans",
)


def create_dispatch_vehicle_linking_permission(apps, schema_editor):
    ContentType = apps.get_model("contenttypes", "ContentType")
    Permission = apps.get_model("auth", "Permission")
    Group = apps.get_model("auth", "Group")

    content_type = ContentType.objects.get(
        app_label="dispatch_plans",
        model="dispatchplan",
    )
    permission, _ = Permission.objects.get_or_create(
        content_type=content_type,
        codename=NEW_PERMISSION[0],
        defaults={"name": NEW_PERMISSION[1]},
    )

    legacy_permissions = Permission.objects.filter(
        content_type=content_type,
        codename__in=LEGACY_PERMISSION_CODENAMES,
    )
    groups = Group.objects.filter(permissions__in=legacy_permissions).distinct()
    for group in groups:
        group.permissions.add(permission)


def remove_dispatch_vehicle_linking_permission(apps, schema_editor):
    ContentType = apps.get_model("contenttypes", "ContentType")
    Permission = apps.get_model("auth", "Permission")
    Group = apps.get_model("auth", "Group")

    try:
        content_type = ContentType.objects.get(
            app_label="dispatch_plans",
            model="dispatchplan",
        )
        permission = Permission.objects.get(
            content_type=content_type,
            codename=NEW_PERMISSION[0],
        )
    except (ContentType.DoesNotExist, Permission.DoesNotExist):
        return

    for group in Group.objects.filter(permissions=permission):
        group.permissions.remove(permission)
    permission.delete()


class Migration(migrations.Migration):

    dependencies = [
        ("dispatch_plans", "0005_dispatchplan_bilty_attachment"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="dispatchplan",
            options={
                "ordering": ["-updated_at", "-created_at"],
                "permissions": [
                    ("can_view_dispatch_plans", "Can view Dispatch Plans dashboard"),
                    ("can_edit_dispatch_plans", "Can edit Dispatch Plans bookings"),
                    ("can_link_dispatch_vehicle", "Can link dispatch vehicles"),
                ],
            },
        ),
        migrations.RunPython(
            create_dispatch_vehicle_linking_permission,
            remove_dispatch_vehicle_linking_permission,
        ),
    ]
