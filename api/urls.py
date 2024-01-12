from django.urls import path, include
from rest_framework import  routers

from api.views.articles import ArticlesWithWordsView, OpenSubtitlesWithWordsView, SongsWithWordsView
from api.views.words import UserWordsViewSet

router = routers.DefaultRouter()

urlpatterns = [
    path("", include(router.urls)),
    path('articles/', ArticlesWithWordsView.as_view()),
    path('subtitles/', OpenSubtitlesWithWordsView.as_view()),
    path('songs/', SongsWithWordsView.as_view()),
    path('words/', UserWordsViewSet.as_view()),
]
