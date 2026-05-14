from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "dispatch_plans",
            "0004_rename_dispatch_pl_company_d4f18f_idx_dispatch_pl_company_4e52c8_idx",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="dispatchplan",
            name="bilty_attachment",
            field=models.FileField(
                blank=True,
                null=True,
                upload_to="dispatch_plan_bilty/",
            ),
        ),
        migrations.AddField(
            model_name="dispatchplan",
            name="bilty_attachment_name",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
    ]
