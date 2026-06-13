from django.db import migrations


def create_audit_groups(apps, schema_editor):
    """
    Create two groups:
      - 'audit' : can submit and view their own invoice-tracker entries.
      - 'audit_auditor' : Delhi office auditor - can view all entries, advance
        status (received documents / pre-audited) and edit remarks.
    """
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')

    submit_codenames = ['add_auditinvoiceentry', 'view_auditinvoiceentry']
    auditor_codenames = [
        'view_auditinvoiceentry',
        'change_auditinvoiceentry',
        'can_audit_invoice_entries',
        'can_view_all_audit_entries',
    ]

    submit_group, _ = Group.objects.get_or_create(name='audit')
    submit_group.permissions.set(
        Permission.objects.filter(
            content_type__app_label='audit',
            codename__in=submit_codenames,
        )
    )

    auditor_group, _ = Group.objects.get_or_create(name='audit_auditor')
    auditor_group.permissions.set(
        Permission.objects.filter(
            content_type__app_label='audit',
            codename__in=auditor_codenames,
        )
    )


def remove_audit_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name__in=['audit', 'audit_auditor']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('audit', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_audit_groups, remove_audit_groups),
    ]
