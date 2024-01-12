from django.db import models
from django.contrib.postgres.fields import ArrayField


class Rss_feed(models.Model):
    id = models.CharField(max_length=1000, primary_key=True)
    source = models.CharField(max_length=300)
    feed_names = ArrayField(models.TextField())
    rss_files = ArrayField(models.TextField())

    language = models.CharField(max_length=100)
    published_datetime = models.DateField()
    link = models.CharField(max_length=1000)

    title = models.TextField()
    title_translation = models.TextField(null=True)
    title_parsed_clean = ArrayField(models.TextField(), null=True)
    title_parsed_lemma = ArrayField(models.TextField(), null=True)
    title_parsed_segmented = ArrayField(models.TextField(), null=True)
    # title_parsed_prefixes = ArrayField(ArrayField(models.TextField()), null=True)
    title_parsed_prefixes = models.JSONField(null=True)
    title_parsed_postag = ArrayField(models.TextField(), null=True)
    title_parsed_feats = ArrayField(models.TextField(), null=True)
    title_parsed_translation_override = ArrayField(models.TextField(), null=True)
    title_parsed_roots = ArrayField(models.TextField(), null=True)
    title_parsed_lemma_gloss = ArrayField(models.TextField(), null=True)
    title_parsed_flexion_gloss = ArrayField(models.TextField(), null=True)

    other_fields = models.JSONField(null=True)

    summary = models.TextField(null=True)



class Open_subtitles(models.Model):
    
    class Meta:
        db_table = "articles_open_subtitle"


    id = models.CharField(max_length=1000, primary_key=True)
    source = models.CharField(max_length=300)
    feed_names = ArrayField(models.TextField())
    rss_files = ArrayField(models.TextField())

    language = models.CharField(max_length=100)
    published_datetime = models.DateField()
    link = models.CharField(max_length=1000)

    title = models.TextField()
    title_translation = models.TextField(null=True)
    title_parsed_clean = ArrayField(models.TextField(), null=True)
    title_parsed_lemma = ArrayField(models.TextField(), null=True)
    title_parsed_segmented = ArrayField(models.TextField(), null=True)
    # title_parsed_prefixes = ArrayField(ArrayField(models.TextField()), null=True)
    title_parsed_prefixes = models.JSONField(null=True)
    title_parsed_postag = ArrayField(models.TextField(), null=True)
    title_parsed_feats = ArrayField(models.TextField(), null=True)
    title_parsed_translation_override = ArrayField(models.TextField(), null=True)
    title_parsed_roots = ArrayField(models.TextField(), null=True)
    title_parsed_lemma_gloss = ArrayField(models.TextField(), null=True)
    title_parsed_flexion_gloss = ArrayField(models.TextField(), null=True)

    other_fields = models.JSONField(null=True)

    summary = models.TextField(null=True)


class Song_lyrics(models.Model):
    id = models.CharField(max_length=1000, primary_key=True)
    source = models.CharField(max_length=300)
    feed_names = ArrayField(models.TextField())
    rss_files = ArrayField(models.TextField())

    language = models.CharField(max_length=100)
    published_datetime = models.DateField()
    link = models.CharField(max_length=1000)

    title = models.TextField()
    title_translation = models.TextField(null=True)
    title_parsed_clean = ArrayField(models.TextField(), null=True)
    title_parsed_lemma = ArrayField(models.TextField(), null=True)
    title_parsed_segmented = ArrayField(models.TextField(), null=True)
    # title_parsed_prefixes = ArrayField(ArrayField(models.TextField()), null=True)
    title_parsed_prefixes = models.JSONField(null=True)
    title_parsed_postag = ArrayField(models.TextField(), null=True)
    title_parsed_feats = ArrayField(models.TextField(), null=True)
    title_parsed_translation_override = ArrayField(models.TextField(), null=True)
    title_parsed_roots = ArrayField(models.TextField(), null=True)
    title_parsed_lemma_gloss = ArrayField(models.TextField(), null=True)
    title_parsed_flexion_gloss = ArrayField(models.TextField(), null=True)

    other_fields = models.JSONField(null=True)

    summary = models.TextField(null=True)

