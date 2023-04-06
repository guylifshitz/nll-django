from djongo import models


class Rss_feeds(models.Model):
    class Meta:
        db_table = "rss_feeds"

    source = models.CharField(max_length=100)
    feed_name = models.JSONField()

    language = models.CharField(max_length=100)
    published_datetime = models.DateField()
    link = models.CharField(max_length=100)

    title = models.CharField(max_length=100)
    title_translation = models.CharField(max_length=100)
    title_parsed_clean = models.JSONField()
    title_parsed_lemma = models.JSONField()
    title_parsed_segmented = models.JSONField()
    title_parsed_prefixes = models.JSONField()
    title_parsed_POSTAG = models.JSONField()
    title_parsed_FEATS = models.JSONField()
    title_parsed_translation_override = models.JSONField()

    summary = models.CharField(max_length=100)

    objects = models.DjongoManager()


class open_subtitles(models.Model):
    meta = {"strict": False}

    _id = models.CharField(max_length=100)

    source = models.CharField(max_length=100)

    language = models.CharField(max_length=100)

    hebrew = models.CharField(max_length=100)
    title_translation = models.CharField(max_length=100)
    title_parsed_clean = models.JSONField()
    title_parsed_lemma = models.JSONField()
    title_parsed_segmented = models.JSONField()
    title_parsed_prefixes = models.JSONField()
    title_parsed_POSTAG = models.JSONField()
    title_parsed_FEATS = models.JSONField()
    title_parsed_translation_override = models.JSONField()
