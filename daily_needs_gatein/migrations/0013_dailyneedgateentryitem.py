from decimal import Decimal

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


def copy_existing_daily_need_items(apps, schema_editor):
    DailyNeedGateEntry = apps.get_model("daily_needs_gatein", "DailyNeedGateEntry")
    DailyNeedGateEntryItem = apps.get_model("daily_needs_gatein", "DailyNeedGateEntryItem")

    items_to_create = []
    for entry in DailyNeedGateEntry.objects.all().iterator():
        if entry.material_name and entry.quantity and entry.unit_id:
            items_to_create.append(
                DailyNeedGateEntryItem(
                    daily_need_entry_id=entry.id,
                    line_no=1,
                    material_name=entry.material_name,
                    quantity=entry.quantity,
                    unit_id=entry.unit_id,
                )
            )

    DailyNeedGateEntryItem.objects.bulk_create(items_to_create, ignore_conflicts=True)


def remove_copied_daily_need_items(apps, schema_editor):
    DailyNeedGateEntryItem = apps.get_model("daily_needs_gatein", "DailyNeedGateEntryItem")
    DailyNeedGateEntryItem.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("daily_needs_gatein", "0012_dailyneedgateentry_updated_at"),
        ("gate_core", "0004_remove_unitchoice_created_at_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="DailyNeedGateEntryItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("line_no", models.PositiveIntegerField(default=1)),
                ("material_name", models.CharField(max_length=200)),
                (
                    "quantity",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=10,
                        validators=[
                            django.core.validators.MinValueValidator(
                                Decimal("0.01"),
                                message="Quantity must be positive",
                            )
                        ],
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "daily_need_entry",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="items",
                        to="daily_needs_gatein.dailyneedgateentry",
                    ),
                ),
                (
                    "unit",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="daily_need_entry_items",
                        to="gate_core.unitchoice",
                    ),
                ),
            ],
            options={
                "ordering": ["line_no", "id"],
            },
        ),
        migrations.AddIndex(
            model_name="dailyneedgateentryitem",
            index=models.Index(fields=["daily_need_entry", "line_no"], name="daily_needs_daily_n_c8dac6_idx"),
        ),
        migrations.AddConstraint(
            model_name="dailyneedgateentryitem",
            constraint=models.UniqueConstraint(
                fields=("daily_need_entry", "line_no"),
                name="unique_daily_need_entry_line",
            ),
        ),
        migrations.RunPython(copy_existing_daily_need_items, remove_copied_daily_need_items),
    ]
