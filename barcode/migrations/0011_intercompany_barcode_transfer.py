from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('barcode', '0010_dispatch_partial_box_scans'),
        ('company', '0003_alter_usercompany_role'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='IntercompanyTransfer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transfer_number', models.CharField(max_length=60, unique=True)),
                ('status', models.CharField(choices=[('DRAFT', 'Draft'), ('COMPLETED', 'Completed'), ('REVERSED', 'Reversed'), ('SAP_SYNC_FAILED', 'SAP Sync Failed')], default='COMPLETED', max_length=20)),
                ('total_barcodes', models.PositiveIntegerField(default=0)),
                ('total_qty', models.DecimalField(decimal_places=3, default=0, max_digits=18)),
                ('uom', models.CharField(blank=True, default='', max_length=30)),
                ('sap_enabled', models.BooleanField(default=False)),
                ('sap_doc_entry', models.IntegerField(blank=True, null=True)),
                ('sap_doc_num', models.CharField(blank=True, default='', max_length=80)),
                ('sap_status', models.CharField(blank=True, default='', max_length=40)),
                ('sap_error', models.TextField(blank=True, default='')),
                ('notes', models.TextField(blank=True, default='')),
                ('device_id', models.CharField(blank=True, default='', max_length=120)),
                ('reversed_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='intercompany_transfers_created', to=settings.AUTH_USER_MODEL)),
                ('destination_company', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='intercompany_transfers_in', to='company.company')),
                ('reversed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='intercompany_transfers_reversed', to=settings.AUTH_USER_MODEL)),
                ('reversed_of', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reverse_transfers', to='barcode.intercompanytransfer')),
                ('source_company', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='intercompany_transfers_out', to='company.company')),
            ],
            options={
                'ordering': ['-created_at'],
                'permissions': [('can_view_intercompany_transfer', 'Can view intercompany barcode transfers'), ('can_create_intercompany_transfer', 'Can create intercompany barcode transfers'), ('can_scan_intercompany_transfer', 'Can scan intercompany transfer barcodes'), ('can_reverse_intercompany_transfer', 'Can reverse intercompany barcode transfers'), ('can_manage_intercompany_transfer_settings', 'Can manage intercompany transfer settings')],
            },
        ),
        migrations.CreateModel(
            name='IntercompanyTransferLine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('barcode', models.CharField(max_length=200)),
                ('item_code', models.CharField(max_length=80)),
                ('item_name', models.CharField(blank=True, default='', max_length=255)),
                ('batch_number', models.CharField(blank=True, default='', max_length=120)),
                ('qty', models.DecimalField(decimal_places=3, max_digits=18)),
                ('uom', models.CharField(blank=True, default='', max_length=30)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('box', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='intercompany_transfer_lines', to='barcode.box')),
                ('from_company', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='intercompany_transfer_lines_out', to='company.company')),
                ('to_company', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='intercompany_transfer_lines_in', to='company.company')),
                ('transfer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lines', to='barcode.intercompanytransfer')),
            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='BarcodeAuditLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('barcode', models.CharField(max_length=200)),
                ('transaction_type', models.CharField(choices=[('MANUFACTURED', 'Manufactured'), ('SCANNED', 'Scanned'), ('TRANSFER_CREATED', 'Transfer Created'), ('TRANSFER_COMPLETED', 'Transfer Completed'), ('TRANSFER_REVERSED', 'Transfer Reversed'), ('DISPATCH_COMPLETED', 'Dispatch Completed')], max_length=40)),
                ('device_id', models.CharField(blank=True, default='', max_length=120)),
                ('notes', models.TextField(blank=True, default='')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('box', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='audit_logs', to='barcode.box')),
                ('from_company', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='barcode_audit_from', to='company.company')),
                ('to_company', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='barcode_audit_to', to='company.company')),
                ('transfer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='audit_logs', to='barcode.intercompanytransfer')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='barcode_audit_logs', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='intercompanytransfer',
            index=models.Index(fields=['source_company', 'destination_company', 'created_at'], name='barcode_int_source__c83d63_idx'),
        ),
        migrations.AddIndex(
            model_name='intercompanytransfer',
            index=models.Index(fields=['status', 'created_at'], name='barcode_int_status_95145c_idx'),
        ),
        migrations.AddIndex(
            model_name='intercompanytransfer',
            index=models.Index(fields=['transfer_number'], name='barcode_int_transfe_c200c6_idx'),
        ),
        migrations.AddIndex(
            model_name='intercompanytransfer',
            index=models.Index(fields=['sap_doc_entry'], name='barcode_int_sap_doc_8ac8fb_idx'),
        ),
        migrations.AddIndex(
            model_name='intercompanytransferline',
            index=models.Index(fields=['barcode'], name='barcode_int_barcode_05c51c_idx'),
        ),
        migrations.AddIndex(
            model_name='intercompanytransferline',
            index=models.Index(fields=['item_code', 'batch_number'], name='barcode_int_item_co_c9b951_idx'),
        ),
        migrations.AddIndex(
            model_name='intercompanytransferline',
            index=models.Index(fields=['from_company', 'to_company'], name='barcode_int_from_co_1ce729_idx'),
        ),
        migrations.AddConstraint(
            model_name='intercompanytransferline',
            constraint=models.UniqueConstraint(fields=('transfer', 'box'), name='unique_box_per_intercompany_transfer'),
        ),
        migrations.AddIndex(
            model_name='barcodeauditlog',
            index=models.Index(fields=['barcode', 'created_at'], name='barcode_bar_barcode_0aa102_idx'),
        ),
        migrations.AddIndex(
            model_name='barcodeauditlog',
            index=models.Index(fields=['transaction_type', 'created_at'], name='barcode_bar_transac_5bbf29_idx'),
        ),
        migrations.AddIndex(
            model_name='barcodeauditlog',
            index=models.Index(fields=['from_company', 'to_company'], name='barcode_bar_from_co_349986_idx'),
        ),
    ]
