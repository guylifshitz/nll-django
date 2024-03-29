# Generated by Django 5.0.1 on 2024-01-24 21:59

import django.contrib.postgres.fields
import django.db.models.deletion
import uuid
import words.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Flexion',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('language', models.CharField(max_length=2)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('text', models.TextField()),
                ('translation_google', models.TextField(null=True)),
                ('translation_azure', models.TextField(null=True)),
                ('count', models.IntegerField(null=True)),
                ('count_rss', models.IntegerField(null=True)),
                ('count_lyric', models.IntegerField(null=True)),
                ('count_subtitle', models.IntegerField(null=True)),
                ('count_wikipedia', models.IntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='WordRating',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('rating', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Word',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('language', models.CharField(max_length=2)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('text', models.TextField()),
                ('translation', models.TextField(null=True)),
                ('translation_google', models.TextField(null=True)),
                ('translation_azure', models.TextField(null=True)),
                ('root', models.CharField(max_length=100, null=True)),
                ('flexion_counts', models.JSONField(blank=True, default=words.models.default_json_values, null=True)),
                ('count', models.IntegerField(null=True)),
                ('rank', models.IntegerField(null=True)),
                ('count_rss_feed', models.IntegerField(null=True)),
                ('rank_rss_feed', models.IntegerField(null=True)),
                ('count_subtitle', models.IntegerField(null=True)),
                ('rank_subtitle', models.IntegerField(null=True)),
                ('count_wikipedia', models.IntegerField(null=True)),
                ('rank_wikipedia', models.IntegerField(null=True)),
                ('count_lyric', models.IntegerField(null=True)),
                ('rank_lyric', models.IntegerField(null=True)),
                ('count_rss', models.IntegerField(null=True)),
                ('rank_rss', models.IntegerField(null=True)),
                ('user_translations', models.JSONField(blank=True, default=words.models.default_json_values, null=True)),
                ('user_roots', models.JSONField(blank=True, default=words.models.default_json_values, null=True)),
                ('parser_translations', django.contrib.postgres.fields.ArrayField(base_field=models.TextField(), null=True, size=None)),
                ('user_translations_with_user', models.JSONField(blank=True, default=words.models.default_json_values, null=True)),
                ('user_roots_with_user', models.JSONField(blank=True, default=words.models.default_json_values, null=True)),
            ],
            options={
                'indexes': [models.Index(fields=['id'], name='words_word_id_128a62_idx'), models.Index(fields=['text'], name='words_word_text_c757ab_idx'), models.Index(fields=['language'], name='words_word_languag_35ee86_idx'), models.Index(fields=['rank'], name='words_word_rank_955b91_idx'), models.Index(fields=['rank_lyric'], name='words_word_rank_ly_9ddeb3_idx'), models.Index(fields=['rank_rss_feed'], name='words_word_rank_rs_f578a5_idx'), models.Index(fields=['rank_subtitle'], name='words_word_rank_su_2c59ea_idx'), models.Index(fields=['rank_wikipedia'], name='words_word_rank_wi_026a5f_idx')],
            },
        ),
        migrations.AddConstraint(
            model_name='word',
            constraint=models.UniqueConstraint(fields=('text', 'language'), name='unique_word'),
        ),
        migrations.AddField(
            model_name='wordrating',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='wordrating',
            name='word',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='word_ratings', to='words.word'),
        ),
        migrations.AddIndex(
            model_name='wordrating',
            index=models.Index(fields=['word', 'user'], name='words_wordr_word_id_2bd799_idx'),
        ),
        migrations.AddIndex(
            model_name='wordrating',
            index=models.Index(fields=['word'], name='words_wordr_word_id_d7c995_idx'),
        ),
        migrations.AddIndex(
            model_name='wordrating',
            index=models.Index(fields=['user'], name='words_wordr_user_id_4b3348_idx'),
        ),
        migrations.AddConstraint(
            model_name='wordrating',
            constraint=models.UniqueConstraint(fields=('word', 'user'), name='unique_word_user_combination'),
        ),
        migrations.AlterUniqueTogether(
            name='wordrating',
            unique_together={('word', 'user')},
        ),
    ]
