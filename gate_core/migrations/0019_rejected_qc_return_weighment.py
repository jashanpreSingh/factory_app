from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gate_core", "0018_jobwork_production_order_link"),
    ]

    operations = [
        migrations.AddField(
            model_name="rejectedqcreturnentry",
            name="gross_weight",
            field=models.DecimalField(blank=True, decimal_places=3, max_digits=12, null=True),
        ),
        migrations.AddField(
            model_name="rejectedqcreturnentry",
            name="tare_weight",
            field=models.DecimalField(blank=True, decimal_places=3, max_digits=12, null=True),
        ),
        migrations.AddField(
            model_name="rejectedqcreturnentry",
            name="net_weight",
            field=models.DecimalField(
                blank=True,
                decimal_places=3,
                editable=False,
                max_digits=12,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="rejectedqcreturnentry",
            name="weighbridge_slip_no",
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name="rejectedqcreturnentry",
            name="first_weighment_time",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="rejectedqcreturnentry",
            name="second_weighment_time",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
