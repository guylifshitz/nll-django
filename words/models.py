from django.db import models
from django.contrib.auth.models import User

def default_json_values():
    return []

# TODO: change primary key to an "id" AutoField
class Word(models.Model):
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

    class Meta:
        indexes = [
            models.Index(fields=["text"]),
            models.Index(fields=["language"]),
            models.Index(fields=["rank"]),
        ]

class Flexion(models.Model):
    # _id = models.CharField(max_length=100)
    text = models.CharField(primary_key=True, max_length=100, null=False)
    language = models.CharField(max_length=100)
    translation_google = models.CharField(max_length=300, null=True)
    translation_azure = models.CharField(max_length=300, null=True)
    count = models.IntegerField(null=True)
    # lemma = models.CharField(max_length=1000)
    # user_suggested_translations = models.ArrayField()


class WordRating(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    word = models.ForeignKey(Word, on_delete=models.CASCADE, related_name="word_ratings")
    rating = models.IntegerField(default=0)

    class Meta:
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

    def __str__(self):
        return f"{self.rating}"
        # return f"{self.user.username} - {self.word._id} - {self.rating}"
