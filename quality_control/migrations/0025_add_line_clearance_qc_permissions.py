from django.db import migrations


LINE_CLEARANCE_QC_PERMISSIONS = [
    ("can_view_line_clearance_qc", "Can view line clearance QC"),
    ("can_approve_line_clearance_qc", "Can approve line clearance QC"),
]


def create_line_clearance_qc_permissions(apps, schema_editor):
    ContentType = apps.get_model("contenttypes", "ContentType")
    Permission = apps.get_model("auth", "Permission")

    content_type, _ = ContentType.objects.get_or_create(
        app_label="quality_control",
        model="productionqcsession",
    )

    for codename, name in LINE_CLEARANCE_QC_PERMISSIONS:
        Permission.objects.get_or_create(
            content_type=content_type,
            codename=codename,
            defaults={"name": name},
        )


def remove_line_clearance_qc_permissions(apps, schema_editor):
    ContentType = apps.get_model("contenttypes", "ContentType")
    Permission = apps.get_model("auth", "Permission")

    try:
        content_type = ContentType.objects.get(
            app_label="quality_control",
            model="productionqcsession",
        )
    except ContentType.DoesNotExist:
        return

    Permission.objects.filter(
        content_type=content_type,
        codename__in=[codename for codename, _ in LINE_CLEARANCE_QC_PERMISSIONS],
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("contenttypes", "0002_remove_content_type_name"),
        ("quality_control", "0024_merge_factory_head_and_production_qc"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="productionqcsession",
            options={
                "ordering": ["session_number"],
                "permissions": [
                    ("can_view_production_qc", "Can view production QC"),
                    ("can_create_production_qc", "Can create production QC session"),
                    ("can_submit_production_qc", "Can submit production QC session"),
                    ("can_approve_production_qc", "Can approve production QC session"),
                    *LINE_CLEARANCE_QC_PERMISSIONS,
                ],
            },
        ),
        migrations.RunPython(
            create_line_clearance_qc_permissions,
            remove_line_clearance_qc_permissions,
        ),
    ]
