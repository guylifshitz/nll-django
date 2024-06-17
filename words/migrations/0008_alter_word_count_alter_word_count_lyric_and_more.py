# Generated by Django 5.0.1 on 2024-06-03 11:18

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('words', '0007_wordrating_created_at_wordrating_updated_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='word',
            name='count',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='word',
            name='count_lyric',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='word',
            name='count_rss',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='word',
            name='count_rss_feed',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='word',
            name='count_subtitle',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='word',
            name='count_wikipedia',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='word',
            name='parser_translations',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.TextField(), blank=True, null=True, size=None),
        ),
        migrations.AlterField(
            model_name='word',
            name='rank',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='word',
            name='rank_lyric',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='word',
            name='rank_rss',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='word',
            name='rank_rss_feed',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='word',
            name='rank_subtitle',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='word',
            name='rank_wikipedia',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='word',
            name='root',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='word',
            name='translation_azure',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='word',
            name='translation_google',
            field=models.TextField(blank=True, null=True),
        ),
    ]
