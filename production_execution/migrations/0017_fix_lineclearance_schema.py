from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('production_execution', '0016_update_line_config_add_name_remove_unique'),
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
