from django.urls import path, include
from rest_framework import routers

from api.views.api_articles_view import (
    RssWithWordsView,
    WikipediaWithWordsView,
    SubtitlesWithWordsView,
    LyricWithWordsView,
)
from api.views.api_words_view import UserWordsViewSet

router = routers.DefaultRouter()

urlpatterns = [
    path("", include(router.urls)),
    path("rss/", RssWithWordsView.as_view()),
    path("wikipedia/", WikipediaWithWordsView.as_view()),
    path("subtitles/", SubtitlesWithWordsView.as_view()),
    path("songs/", LyricWithWordsView.as_view()),
    path("words/", UserWordsViewSet.as_view()),
]
