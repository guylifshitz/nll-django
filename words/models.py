from django.db import models
from mongoengine import Document, fields

class Words(Document):
    meta = {"strict": False}

    _id = fields.StringField()
    word_diacritic = fields.StringField()
    translation = fields.StringField()
    count = fields.IntField()
    language = fields.StringField()    
    word_diacritic =  fields.StringField()