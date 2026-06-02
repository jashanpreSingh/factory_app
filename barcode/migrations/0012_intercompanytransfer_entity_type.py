from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("barcode", "0011_intercompany_barcode_transfer"),
    ]

    operations = [
        migrations.AddField(
            model_name="intercompanytransfer",
            name="entity_type",
            field=models.CharField(
                choices=[("BOX", "Box"), ("PALLET", "Pallet")],
                default="BOX",
                max_length=20,
            ),
        ),
    ]
