import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AuditInvoiceEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tracker_type', models.CharField(choices=[('FACTORY', 'Factory'), ('MAYAPURI', 'Mayapuri'), ('MART', 'Mart'), ('IMPORT_EXPORT', 'Import/Export')], max_length=20)),
                ('serial_no', models.PositiveIntegerField(help_text="Per-type running serial number (the Excel 'S. No.').")),
                ('invoice_date', models.DateField()),
                ('party_name', models.CharField(max_length=255)),
                ('invoice_no', models.CharField(max_length=120)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=18)),
                ('grpo_no', models.CharField(blank=True, default='', max_length=120)),
                ('dispatch_date', models.DateField(blank=True, null=True)),
                ('record_date', models.DateField(blank=True, null=True)),
                ('receiving_date', models.DateField(blank=True, null=True)),
                ('rec_from_imp_exp_date', models.DateField(blank=True, null=True)),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('DOCUMENTS_RECEIVED', 'Documents Received'), ('PRE_AUDITED', 'Pre-Audited')], default='PENDING', max_length=20)),
                ('auditor_remarks', models.TextField(blank=True, default='')),
                ('documents_received_at', models.DateTimeField(blank=True, null=True)),
                ('pre_audited_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('documents_received_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='audit_documents_received', to=settings.AUTH_USER_MODEL)),
                ('pre_audited_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='audit_pre_audited', to=settings.AUTH_USER_MODEL)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='audit_entries_created', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Audit Invoice Entry',
                'verbose_name_plural': 'Audit Invoice Entries',
                'ordering': ['-created_at'],
                'unique_together': {('tracker_type', 'serial_no')},
                'permissions': [('can_audit_invoice_entries', 'Can advance audit status and add remarks'), ('can_view_all_audit_entries', 'Can view all audit entries (auditor)')],
            },
        ),
    ]
