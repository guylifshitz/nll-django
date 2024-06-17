from django.conf import settings
from django.db import models
from django.contrib.postgres.fields import ArrayField
import uuid


class Article(models.Model):
    class Meta:
        abstract = True

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    language = models.CharField(max_length=2, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)


class Sentence(models.Model):
    class Meta:
        abstract = True

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    language = models.CharField(max_length=2)
    created_at = models.DateTimeField(auto_now_add=True)

    text = models.TextField()
    translation = models.TextField(null=True)

    translation_google = models.TextField(null=True)
    translation_azure = models.TextField(null=True)

    time_translated = models.DateTimeField(null=True)

    sentence_order = models.IntegerField()

    parsed_text = ArrayField(models.TextField(), null=True)
    parsed_clean = ArrayField(models.TextField(), null=True)
    parsed_segmented = ArrayField(models.TextField(), null=True)
    parsed_lemma = ArrayField(models.TextField(), null=True)
    parsed_pos = ArrayField(models.TextField(), null=True)
    parsed_features = ArrayField(models.TextField(), null=True)
    parsed_prefixes = ArrayField(models.TextField(), null=True)
    parsed_suffixes = ArrayField(models.TextField(), null=True)
    parsed_roots = ArrayField(models.TextField(), null=True)
    parsed_gloss_lemma = ArrayField(models.TextField(), null=True)
    parsed_gloss_flexion = ArrayField(models.TextField(), null=True)


class Rss(Article):
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["article_link"], name="unique_rss_article")
        ]

    feed_provider = models.TextField()
    rss_files = ArrayField(models.TextField())
    feed_names = ArrayField(models.TextField())
    summary = models.TextField(null=True)
    article_link = models.TextField()
    article_title = models.TextField()
    published_datetime = models.DateTimeField()
    updated_datetime = models.DateTimeField(null=True)

    @property
    def link(self):
        return self.article_link

    @property
    def title(self):
        return self.feed_provider

    @property
    def tag_level_1(self):
        return self.title + ": " + ", ".join(self.feed_names)

    @property
    def tag_level_2(self):
        return self.published_datetime.strftime("%d-%m-%Y")

    @property
    def extra_text(self):
        return self.summary


class Rss_sentence(Sentence):
    source = models.ForeignKey(Rss, on_delete=models.CASCADE, related_name="sentences")


class Lyric(Article):
    song_title = models.TextField()
    artist = models.TextField(null=True)
    genre = models.TextField(null=True)
    year = models.IntegerField(null=True)
    views = models.IntegerField(null=True)
    website_id = models.TextField(null=True)
    source_name = models.TextField(null=True)
    dialect = models.TextField(null=True)
    singer_nationality = models.TextField(null=True)

    @property
    def title(self):
        return f"{self.artist}: {self.song_title} ({self.year}) ({self.genre})"

    @property
    def extra_text(self):
        return f"{self.views} views"

    @property
    def link(self):
        return None

    @property
    def tag_level_2(self):
        return self.year


class Lyric_sentence(Sentence):
    source = models.ForeignKey(
        Lyric, on_delete=models.CASCADE, related_name="sentences"
    )


class Subtitle(Article):
    title_original = models.TextField()
    title_foreign = models.TextField(null=True)
    title_english = models.TextField(null=True)
    year = models.IntegerField(null=True)
    series_year_start = models.IntegerField(null=True)
    series_year_end = models.IntegerField(null=True)
    season_number = models.IntegerField(null=True)
    episode_number = models.IntegerField(null=True)
    runtime_minutes = models.IntegerField(null=True)
    type = models.TextField(null=True)
    genres = ArrayField(models.TextField(null=True))
    people = models.JSONField(null=True)
    number_ratings = models.IntegerField(null=True)
    imdb_id = models.TextField(null=True)

    @property
    def link(self):
        return f"https://www.imdb.com/title/{self.imdb_id}"

    @property
    def title(self):
        return self.title_original

    @property
    def extra_text(self):
        return str(self.number_ratings)

    @property
    def tag_level_2(self):
        return self.year


class Subtitle_sentence(Sentence):
    source = models.ForeignKey(
        Subtitle, on_delete=models.CASCADE, related_name="sentences"
    )


class Wikipedia(Article):
    page_name = models.TextField()

    @property
    def link(self):
        return "https://en.wikipedia.org/wiki/" + self.page_name

    @property
    def title(self):
        return self.page_name

    @property
    def tag_level_2(self):
        return self.page_name


class Wikipedia_sentence(Sentence):
    source = models.ForeignKey(
        Wikipedia, on_delete=models.CASCADE, related_name="sentences"
    )


class User_Document(Article):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    document_name = models.TextField()

    @property
    def title(self):
        return self.document_name

    @property
    def link(self):
        return self.document_name

    @property
    def extra_text(self):
        return self.document_name

    @property
    def tag_level_1(self):
        return self.document_name

    @property
    def tag_level_2(self):
        return self.document_name

    @property
    def tag_level_2(self):
        return self.document_name


class User_Document_sentence(Sentence):
    source = models.ForeignKey(
        User_Document, on_delete=models.CASCADE, related_name="sentences"
    )


#######
#####################
#######
#####################
#######
#####################
#######
#####################
#######
#####################
#######
#####################
#######
#####################
#######
#####################


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
