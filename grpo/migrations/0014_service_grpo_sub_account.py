from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("grpo", "0013_servicegrpolineposting_location_code_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="servicegrpoposting",
            name="sub_account",
            field=models.CharField(blank=True, default="", max_length=100),
        ),
        migrations.AddField(
            model_name="servicegrpolineposting",
            name="sub_account",
            field=models.CharField(blank=True, default="", max_length=100),
        ),
    ]
