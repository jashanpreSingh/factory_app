from django.db import migrations, models


def enable_partial_dispatch(apps, schema_editor):
    DispatchSettings = apps.get_model('barcode', 'DispatchSettings')
    DispatchSettings.objects.update(allow_partial_dispatch=True)


def seed_scanned_unit_quantities(apps, schema_editor):
    DispatchScannedUnit = apps.get_model('barcode', 'DispatchScannedUnit')
    for unit in DispatchScannedUnit.objects.all().iterator():
        unit.total_box_qty = unit.qty
        unit.dispatch_qty = unit.qty
        unit.remaining_qty = 0
        unit.scan_status = 'DISPATCHED'
        unit.save(
            update_fields=[
                'total_box_qty',
                'dispatch_qty',
                'remaining_qty',
                'scan_status',
            ]
        )


class Migration(migrations.Migration):

    dependencies = [
        ('barcode', '0009_dispatchsessionline_bill_boxes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dispatchsettings',
            name='allow_partial_dispatch',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='dispatchscannedunit',
            name='dispatch_qty',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=18),
        ),
        migrations.AddField(
            model_name='dispatchscannedunit',
            name='remaining_qty',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=18),
        ),
        migrations.AddField(
            model_name='dispatchscannedunit',
            name='scan_status',
            field=models.CharField(
                choices=[
                    ('ACTIVE', 'Active'),
                    ('REMOVED', 'Removed'),
                    ('DISPATCHED', 'Dispatched'),
                ],
                default='ACTIVE',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='dispatchscannedunit',
            name='total_box_qty',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=18),
        ),
        migrations.AddIndex(
            model_name='dispatchscannedunit',
            index=models.Index(fields=['session', 'scan_status'], name='barcode_dis_session_5eec97_idx'),
        ),
        migrations.RunPython(enable_partial_dispatch, migrations.RunPython.noop),
        migrations.RunPython(seed_scanned_unit_quantities, migrations.RunPython.noop),
    ]
