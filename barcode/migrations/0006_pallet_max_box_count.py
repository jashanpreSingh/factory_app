from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('barcode', '0005_barcodesequence'),
    ]

    operations = [
        migrations.AddField(
            model_name='pallet',
            name='max_box_count',
            field=models.PositiveIntegerField(
                default=0,
                help_text='Editable pallet capacity fetched from SAP HANA when available',
            ),
        ),
    ]
