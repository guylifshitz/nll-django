from django.urls import path, include
from rest_framework import routers

from api.views.articles import (
    ArticlesWithWordsView,
    WikipediaWithWordsView,
    SubtitlesWithWordsView,
    LyricWithWordsView,
)
from api.views.words import UserWordsViewSet

router = routers.DefaultRouter()

urlpatterns = [
    path("", include(router.urls)),
    path("articles/", ArticlesWithWordsView.as_view()),
    path("wikipedia/", WikipediaWithWordsView.as_view()),
    path("subtitles/", SubtitlesWithWordsView.as_view()),
    path("songs/", LyricWithWordsView.as_view()),
    path("words/", UserWordsViewSet.as_view()),
]
