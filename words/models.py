from djongo import models
from django.contrib.auth.models import User

class Words(models.Model):
    objects = models.DjongoManager()

    class Meta:
        db_table = "words"

    _id = models.CharField(primary_key=True, max_length=100)
    word_diacritic = models.CharField(max_length=100)
    translation = models.CharField(max_length=300)
    root = models.CharField(max_length=100)
    flexion_counts = models.JSONField(null=True, blank=True, default=[])
    rank = models.IntegerField()
    count = models.IntegerField()
    rank_open_subtitles = models.IntegerField()
    count_open_subtitles = models.IntegerField()
    language = models.CharField(max_length=100)

    user_translations = models.JSONField(null=True, blank=True, default=[])
    user_roots = models.JSONField(null=True, blank=True, default=[])

class Flexions(models.Model):
    objects = models.DjongoManager()

    class Meta:
        db_table = "flexions"

    _id = models.CharField(primary_key=True, max_length=100)
    # _id = models.CharField(max_length=100)
    text = models.CharField(max_length=100)
    translation_google = models.CharField(max_length=300)
    translation_azure = models.CharField(max_length=300)
    count = models.IntegerField()
    # lemma = models.CharField(max_length=1000)
    # user_suggested_translations = models.ArrayField()
    language = models.CharField(max_length=100)


class WordRatings(models.Model):
    objects = models.DjongoManager()

    class Meta:
        db_table = "word_ratings"
        unique_together = ('word', 'user',)

        constraints = [
            models.UniqueConstraint(fields=["word", "user"], name="unique_word_user_combination")
        ]

    _id = models.ObjectIdField(primary_key=True, null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    word = models.ForeignKey(Words, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.rating}"
        # return f"{self.user.username} - {self.word._id} - {self.rating}"
    