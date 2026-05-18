from django.db import migrations, models
import django.db.models.deletion


def backfill_line_dispatch_plan(apps, schema_editor):
    ServiceGRPOLinePosting = apps.get_model("grpo", "ServiceGRPOLinePosting")
    for line in ServiceGRPOLinePosting.objects.select_related("service_grpo_posting"):
        if line.dispatch_plan_id:
            continue
        line.dispatch_plan_id = line.service_grpo_posting.dispatch_plan_id
        line.save(update_fields=["dispatch_plan"])


class Migration(migrations.Migration):

    dependencies = [
        ("dispatch_plans", "0009_dispatchplan_service_grpo_defaults"),
        ("grpo", "0014_service_grpo_sub_account"),
    ]

    operations = [
        migrations.AddField(
            model_name="servicegrpolineposting",
            name="dispatch_plan",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="service_grpo_lines",
                to="dispatch_plans.dispatchplan",
            ),
        ),
        migrations.RunPython(backfill_line_dispatch_plan, migrations.RunPython.noop),
        migrations.AddIndex(
            model_name="servicegrpolineposting",
            index=models.Index(
                fields=["dispatch_plan"],
                name="grpo_servic_dispatc_line_idx",
            ),
        ),
    ]
