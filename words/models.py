from django.db import models
from mongoengine import Document, fields


class Words(Document):
    meta = {"strict": False}

    _id = fields.StringField()
    word_diacritic = fields.StringField()
    translation = fields.StringField()
    rank = fields.IntField()
    count = fields.IntField()
    language = fields.StringField()


class Flexions(Document):
    _id = fields.StringField()
    translation_google = fields.StringField()
    translation_azure = fields.StringField()
    count = fields.IntField()
    # lemma = fields.StringField()
    # user_suggested_translations = fields.ListField()
    language = fields.StringField()
