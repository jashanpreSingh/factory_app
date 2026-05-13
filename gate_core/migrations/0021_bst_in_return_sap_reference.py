from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gate_core", "0020_rejectedqcreturnentry_gatepass_documents"),
    ]

    operations = [
        migrations.AddField(
            model_name="bstgatein",
            name="sap_receipt_doc_num",
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name="bstgatein",
            name="sap_receipt_doc_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="bstgatein",
            name="sap_receipt_reference",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name="bstgatereturn",
            name="sap_return_doc_num",
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name="bstgatereturn",
            name="sap_return_doc_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="bstgatereturn",
            name="sap_return_reference",
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
