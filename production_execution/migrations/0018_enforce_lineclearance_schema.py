from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('production_execution', '0017_fix_lineclearance_schema'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            ALTER TABLE production_execution_lineclearance
            ADD COLUMN IF NOT EXISTS production_incharge_sign varchar(200) NOT NULL DEFAULT '';

            ALTER TABLE production_execution_lineclearance
            DROP COLUMN IF EXISTS all_checks_passed;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
