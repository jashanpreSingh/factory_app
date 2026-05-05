from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('production_execution', '0018_rename_electricity_cost_per_unit'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            ALTER TABLE production_execution_lineclearance
            DROP COLUMN IF EXISTS all_checks_passed;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
