from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gate_core", "0015_emptyvehiclegateout_cancel_reason_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="emptyvehiclegatein",
            name="document_notes",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="emptyvehiclegatein",
            name="document_reference",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="emptyvehiclegatein",
            name="sap_comments",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="emptyvehiclegatein",
            name="sap_doc_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="emptyvehiclegatein",
            name="sap_doc_entry",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="emptyvehiclegatein",
            name="sap_doc_num",
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name="emptyvehiclegatein",
            name="sap_from_warehouse",
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name="emptyvehiclegatein",
            name="sap_line_count",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="emptyvehiclegatein",
            name="sap_reference",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name="emptyvehiclegatein",
            name="sap_to_warehouse",
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name="emptyvehiclegatein",
            name="sap_total_quantity",
            field=models.DecimalField(decimal_places=3, default=0, max_digits=18),
        ),
        migrations.AddIndex(
            model_name="emptyvehiclegatein",
            index=models.Index(fields=["sap_doc_entry"], name="gcevg_sapdoc_idx"),
        ),
    ]
