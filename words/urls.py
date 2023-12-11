from django.urls import path

from . import views

urlpatterns = (
    [
        path("word/", views.word, name="word"),
        path("flashcards/", views.flashcards, name="flashcards"),
        path("index/", views.index, name="words_index"),
    ]
)
