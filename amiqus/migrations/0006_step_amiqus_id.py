# Generated by Django 5.1.7 on 2025-04-29 14:21

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("amiqus", "0005_form_step_review"),
    ]

    operations = [
        migrations.AddField(
            model_name="step",
            name="amiqus_id",
            field=models.CharField(
                help_text="The id returned from the Amiqus API. These should be unique on the record.",
                max_length=40,
                null=True,
                verbose_name="Amiqus ID",
            ),
        ),
    ]
