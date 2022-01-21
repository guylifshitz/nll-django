from django.urls import path

from . import views

urlpatterns = (
    [
        path("<word_id>", views.word, name="word"),
        path("flashcards/", views.flashcards, name="flashcards"),
        path("index/", views.index, name="index"),
    ]
)
