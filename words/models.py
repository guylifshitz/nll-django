from django.db import models
from django.contrib.auth.models import User

# from djongo import models

# import djongo.models.indexes


def default_json_values():
    return []


class Word(models.Model):
    # objects = models.DjongoManager()

    class Meta:
        indexes = [
            models.Index(fields=["text"]),
            models.Index(fields=["language"]),
            models.Index(fields=["rank"]),
        ]

    # _id = models.CharField(primary_key=True, max_length=100)
    text = models.CharField(primary_key=True, max_length=100, null=False)
    word_diacritic = models.CharField(max_length=100, null=True)
    translation = models.CharField(max_length=300, null=True)
    root = models.CharField(max_length=100, null=True)
    flexion_counts = models.JSONField(null=True, blank=True, default=default_json_values)
    rank = models.IntegerField(null=True)
    count = models.IntegerField(null=True)
    rank_open_subtitles = models.IntegerField(null=True)
    count_open_subtitles = models.IntegerField(null=True)
    language = models.CharField(max_length=100)

    user_translations = models.JSONField(null=True, blank=True, default=default_json_values)
    user_roots = models.JSONField(null=True, blank=True, default=default_json_values)

    user_translations_with_user = models.JSONField(
        null=True, blank=True, default=default_json_values
    )
    user_roots_with_user = models.JSONField(null=True, blank=True, default=default_json_values)

    @property
    def best_root(self):
        root = self.root
        if self.user_roots:
            root = self.user_roots[-1]
        if not root:
            root = self.root
        return root

    @property
    def best_translation(self):
        translation = self.translation
        if self.user_translations:
            translation = self.user_translations[-1]
        if not translation:
            translation = self.translation
        return translation



    @property
    def normalized_flexion_counts(self):
        flexions = self.flexion_counts
        if not flexions:
            flexions = {}

        flexions_sum = sum(list(flexions.values()))
        flexions = {k: v for k, v in sorted(flexions.items(), key=lambda item: item[1], reverse=True)}
        flexions = {k: max(int(v / flexions_sum * 100), 1) for k, v in flexions.items()}
        flexions = {k: flexions[k] for k in list(flexions)[:10]}

        if not flexions:
            flexions = ""
        return flexions


class Flexion(models.Model):
    # objects = models.DjongoManager()

    # class Meta:
    #     db_table = "flexions"

    # text = models.CharField(primary_key=True, max_length=100)
    # _id = models.CharField(max_length=100)
    text = models.CharField(primary_key=True, max_length=100, null=False)
    language = models.CharField(max_length=100)
    translation_google = models.CharField(max_length=300, null=True)
    translation_azure = models.CharField(max_length=300, null=True)
    count = models.IntegerField(null=True)
    # lemma = models.CharField(max_length=1000)
    # user_suggested_translations = models.ArrayField()


class WordRating(models.Model):
    # objects = models.DjongoManager()

    class Meta:
        # db_table = "word_ratings"
        unique_together = (
            "word",
            "user",
        )
        indexes = [
            models.Index(fields=["word", "user"]),
            models.Index(fields=["word"]),
            models.Index(fields=["user"]),
        ]

        constraints = [
            models.UniqueConstraint(fields=["word", "user"], name="unique_word_user_combination")
        ]
        # indexes = [TextIndex(fields=["word", "user"])]

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    word = models.ForeignKey(Word, on_delete=models.CASCADE, related_name="word_ratings")
    rating = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.rating}"
        # return f"{self.user.username} - {self.word._id} - {self.rating}"
