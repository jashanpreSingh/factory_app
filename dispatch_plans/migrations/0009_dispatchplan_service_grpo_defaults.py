from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dispatch_plans", "0008_add_dispatch_invoice_fields"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql="""
                        ALTER TABLE dispatch_plans_dispatchplan
                            ADD COLUMN IF NOT EXISTS budget_delivery_point varchar(100) NOT NULL DEFAULT '',
                            ADD COLUMN IF NOT EXISTS effective_month date NULL,
                            ADD COLUMN IF NOT EXISTS product_variety varchar(50) NOT NULL DEFAULT '',
                            ADD COLUMN IF NOT EXISTS sac_code varchar(30) NOT NULL DEFAULT '',
                            ADD COLUMN IF NOT EXISTS sac_entry integer NULL,
                            ADD COLUMN IF NOT EXISTS service_location_code integer NULL,
                            ADD COLUMN IF NOT EXISTS service_location_name varchar(100) NOT NULL DEFAULT '',
                            ADD COLUMN IF NOT EXISTS total_litres numeric(18, 3) NULL;
                    """,
                    reverse_sql="""
                        ALTER TABLE dispatch_plans_dispatchplan
                            DROP COLUMN IF EXISTS budget_delivery_point,
                            DROP COLUMN IF EXISTS effective_month,
                            DROP COLUMN IF EXISTS product_variety,
                            DROP COLUMN IF EXISTS sac_code,
                            DROP COLUMN IF EXISTS sac_entry,
                            DROP COLUMN IF EXISTS service_location_code,
                            DROP COLUMN IF EXISTS service_location_name,
                            DROP COLUMN IF EXISTS total_litres;
                    """,
                )
            ],
            state_operations=[
                migrations.AddField(
                    model_name="dispatchplan",
                    name="budget_delivery_point",
                    field=models.CharField(blank=True, default="", max_length=100),
                ),
                migrations.AddField(
                    model_name="dispatchplan",
                    name="effective_month",
                    field=models.DateField(blank=True, null=True),
                ),
                migrations.AddField(
                    model_name="dispatchplan",
                    name="product_variety",
                    field=models.CharField(blank=True, default="", max_length=50),
                ),
                migrations.AddField(
                    model_name="dispatchplan",
                    name="sac_code",
                    field=models.CharField(blank=True, default="", max_length=30),
                ),
                migrations.AddField(
                    model_name="dispatchplan",
                    name="sac_entry",
                    field=models.IntegerField(blank=True, null=True),
                ),
                migrations.AddField(
                    model_name="dispatchplan",
                    name="service_location_code",
                    field=models.IntegerField(blank=True, null=True),
                ),
                migrations.AddField(
                    model_name="dispatchplan",
                    name="service_location_name",
                    field=models.CharField(blank=True, default="", max_length=100),
                ),
                migrations.AddField(
                    model_name="dispatchplan",
                    name="total_litres",
                    field=models.DecimalField(
                        blank=True, decimal_places=3, max_digits=18, null=True
                    ),
                ),
            ],
        ),
    ]
