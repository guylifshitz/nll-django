import traceback
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField

# from djongo import models

# import djongo.models.indexes


def default_json_values():
    return []


class Word(models.Model):
    # objects = models.DjongoManager()

    class Meta:
        indexes = [
            models.Index(fields=["id"]),
            models.Index(fields=["text"]),
            models.Index(fields=["language"]),
            models.Index(fields=["rank"]),
            models.Index(fields=["rank_lyric"]),
            models.Index(fields=["rank_rss_feed"]),
            models.Index(fields=["rank_subtitle"]),
            models.Index(fields=["rank_wikipedia"]),
        ]
        constraints = [
            models.UniqueConstraint(fields=["text", "language"], name="unique_word")
        ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    language = models.CharField(max_length=2)
    created_at = models.DateTimeField(auto_now_add=True)

    text = models.TextField(null=False)

    translation = models.TextField(null=True)
    translation_google = models.TextField(null=True, blank=True)
    translation_azure = models.TextField(null=True, blank=True)
    user_translations = models.JSONField(null=True, blank=True, default={})
    root = models.CharField(max_length=100, null=True, blank=True)
    flexion_counts = models.JSONField(
        null=True, blank=True, default=default_json_values
    )
    count = models.IntegerField(null=True, blank=True)
    rank = models.IntegerField(null=True, blank=True)
    count_rss_feed = models.IntegerField(null=True, blank=True)
    rank_rss_feed = models.IntegerField(null=True, blank=True)
    count_subtitle = models.IntegerField(null=True, blank=True)
    rank_subtitle = models.IntegerField(null=True, blank=True)
    count_wikipedia = models.IntegerField(null=True, blank=True)
    rank_wikipedia = models.IntegerField(null=True, blank=True)
    count_lyric = models.IntegerField(null=True, blank=True)
    rank_lyric = models.IntegerField(null=True, blank=True)
    count_rss = models.IntegerField(null=True, blank=True)
    rank_rss = models.IntegerField(null=True, blank=True)

    user_translations = models.JSONField(
        null=True, blank=True, default=default_json_values
    )
    user_roots = models.JSONField(null=True, blank=True, default=default_json_values)

    parser_translations = ArrayField(
        models.TextField(),
        null=True,
        blank=True,
    )

    user_translations_with_user = models.JSONField(
        null=True, blank=True, default=default_json_values
    )
    user_roots_with_user = models.JSONField(
        null=True, blank=True, default=default_json_values
    )

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
        translation = ""
        if self.translation:
            translation += self.translation
        if self.user_translations:
            translation = ", ".join(
                [
                    translation["translation"] + self.get_pos_tag(translation)
                    for translation in self.user_translations[-1]
                ]
            )
        if self.parser_translations:
            translation += "(" + ", ".join(self.parser_translations) + ")"
        return translation

    def get_pos_tag(self, translation):
        pos_mapping = {
            "noun": "n.",
            "verb": "v.",
            "adjective": "adj.",
            "adverb": "adv.",
            "pronoun": "pron.",
            "preposition": "prep.",
            # "conjunction": "conj.",
            # "interjection": "interj.",
        }
        pos_tag = ""
        if translation.get("pos") and translation["pos"] != "general":
            pos_tag = f" ({pos_mapping[translation['pos']]})"
        return pos_tag

    def normalized_flexion_counts(self, count_column):
        try:
            flexions = self.word_flexions_list
            flexions = {flex.text: getattr(flex, count_column) for flex in flexions}
            flexions = dict(
                filter(lambda flexion: flexion[1] != None, flexions.items())
            )

            try:
                flexions_sum = sum(list(flexions.values()))
            except:
                flexions_sum = 1
            print("flexions_sum", flexions)
            flexions = {
                k: v
                for k, v in sorted(
                    flexions.items(), key=lambda item: item[1], reverse=True
                )
            }
            flexions = {
                k: max(int(v / flexions_sum * 100), 1) for k, v in flexions.items()
            }
            flexions = {k: flexions[k] for k in list(flexions)[:10]}

            if not flexions:
                flexions = ""
        except Exception as e:
            print("Error flexion:", e)
            traceback.print_exc()

            flexions = ""

        return flexions


class Flexion(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["text", "lemma", "language"], name="unique_flexion"
            )
        ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lemma = models.ForeignKey(Word, on_delete=models.CASCADE, related_name="flexions")

    language = models.CharField(max_length=2)
    created_at = models.DateTimeField(auto_now_add=True)

    text = models.TextField(null=False)
    # lemma = models.CharField(max_length=1000)
    translation_google = models.TextField(null=True)
    translation_azure = models.TextField(null=True)
    parser_translations = ArrayField(models.TextField(), null=True)

    # user_suggested_translations = models.ArrayField()
    count = models.IntegerField(null=True)
    count_rss = models.IntegerField(null=True)
    count_lyric = models.IntegerField(null=True)
    count_subtitle = models.IntegerField(null=True)
    count_wikipedia = models.IntegerField(null=True)


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
            models.UniqueConstraint(
                fields=["word", "user"], name="unique_word_user_combination"
            )
        ]
        # indexes = [TextIndex(fields=["word", "user"])]

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    word = models.ForeignKey(
        Word, on_delete=models.CASCADE, related_name="word_ratings"
    )
    rating = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.rating}"
        # return f"{self.user.username} - {self.word._id} - {self.rating}"
