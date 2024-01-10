from words.models import Word, WordRating
from articles.models import Rss_feed
from rest_framework import serializers
import rest_framework

class ArticleWordSerializer(serializers.Serializer):
    id = serializers.CharField()
    text = serializers.CharField()
    lemma = serializers.CharField()
    segmented = serializers.CharField()
    part_of_speech = serializers.CharField()
    features = serializers.CharField()
    flexion_translation = serializers.CharField()
    
class ArticleSerializer(serializers.Serializer):
    id = serializers.CharField()
    published_datetime = serializers.DateField()
    title = serializers.CharField()
    translation = serializers.CharField()
    link = serializers.CharField()
    extra_text = serializers.CharField()
    tag_level_1 = serializers.CharField()
    tag_level_2 = serializers.CharField()
    article_words = ArticleWordSerializer(many=True)

class UserWordSerializer(serializers.Serializer):
    id = serializers.CharField()
    text = serializers.CharField()
    translation = serializers.CharField()
    root = serializers.CharField()
    language = serializers.CharField()
    count = serializers.IntegerField()
    rank = serializers.IntegerField()
    familiarity_label = serializers.IntegerField()
    isKnown = serializers.BooleanField()
    isPractice = serializers.BooleanField()

class ArticleAndWordSerializer(serializers.Serializer):
   lemmas = UserWordSerializer(many=True)
   articles = ArticleSerializer(many=True)
