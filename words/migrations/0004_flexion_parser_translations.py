# Generated by Django 5.0.1 on 2024-01-24 23:07

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('words', '0003_remove_flexion_translation'),
    ]

    operations = [
        migrations.AddField(
            model_name='flexion',
            name='parser_translations',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.TextField(), null=True, size=None),
        ),
    ]
