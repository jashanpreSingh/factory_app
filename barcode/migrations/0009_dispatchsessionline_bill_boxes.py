from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('barcode', '0008_barcodemaster_dispatchsettings_palletboxhistory_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='dispatchsessionline',
            name='bill_boxes',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=18),
        ),
    ]
