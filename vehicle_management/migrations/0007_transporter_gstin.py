from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("vehicle_management", "0006_alter_vehicle_vehicle_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="transporter",
            name="gstin",
            field=models.CharField(blank=True, default="", max_length=20),
        ),
    ]
