from django.urls import path, include
from rest_framework import routers

from api.views.api_articles_view import (
    CreateUserArticleView,
    RssWithWordsView,
    WikipediaWithWordsView,
    SubtitlesWithWordsView,
    LyricWithWordsView,
    SentenceTranslationView,
    UserDocumentWithWordsView,
)
from api.views.api_words_view import (
    UserWordsViewSet,
    UserWordRatingsSet,
    UserTranslation,
)

router = routers.DefaultRouter()

urlpatterns = [
    path("", include(router.urls)),
    path("rss/", RssWithWordsView.as_view()),
    path("user-document/", UserDocumentWithWordsView.as_view()),
    path("wikipedia/", WikipediaWithWordsView.as_view()),
    path("subtitles/", SubtitlesWithWordsView.as_view()),
    path("songs/", LyricWithWordsView.as_view()),
    path("words/", UserWordsViewSet.as_view()),
    path("word_ratings/", UserWordRatingsSet.as_view()),
    path("user_translations/", UserTranslation.as_view()),
    path("sentence_translation/", SentenceTranslationView.as_view()),
    path("user_article/create/", CreateUserArticleView.as_view()),
]
