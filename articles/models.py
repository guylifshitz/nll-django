from mongoengine import Document, fields

class Rss_feeds(Document):
    meta = {"strict": False}

    source = fields.StringField()
    feed_name = fields.StringField()

    language = fields.StringField()
    published_datetime = fields.DateField()
    link = fields.StringField()

    title = fields.StringField()
    title_translation = fields.StringField()
    title_parsed_clean = fields.ListField()
    title_parsed_lemma = fields.ListField()
    title_parsed_segmented = fields.ListField()
    title_parsed_prefixes = fields.ListField()
    title_parsed_POSTAG = fields.ListField()
    title_parsed_FEATS = fields.ListField()
    title_parsed_translation_override = fields.ListField()
    
