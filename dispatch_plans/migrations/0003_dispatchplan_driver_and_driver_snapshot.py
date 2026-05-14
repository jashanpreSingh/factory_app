import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dispatch_plans", "0002_dispatchplan_linked_vehicle_entry_and_more"),
        ("driver_management", "0006_alter_vehicleentry_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="dispatchplan",
            name="driver",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="dispatch_plans",
                to="driver_management.driver",
            ),
        ),
        migrations.AddField(
            model_name="dispatchplan",
            name="driver_id_proof_number",
            field=models.CharField(blank=True, default="", max_length=50),
        ),
        migrations.AddField(
            model_name="dispatchplan",
            name="driver_id_proof_type",
            field=models.CharField(blank=True, default="", max_length=50),
        ),
        migrations.AddField(
            model_name="dispatchplan",
            name="driver_license_no",
            field=models.CharField(blank=True, default="", max_length=50),
        ),
        migrations.AddField(
            model_name="dispatchplan",
            name="driver_mobile_no",
            field=models.CharField(blank=True, default="", max_length=50),
        ),
        migrations.AddField(
            model_name="dispatchplan",
            name="driver_name",
            field=models.CharField(blank=True, default="", max_length=100),
        ),
        migrations.AddIndex(
            model_name="dispatchplan",
            index=models.Index(fields=["company", "driver"], name="dispatch_pl_company_d4f18f_idx"),
        ),
    ]
