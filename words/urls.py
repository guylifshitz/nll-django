from django.urls import path

from . import views

urlpatterns = (
    [
        path("flashcards/", views.flashcards, name="flashcards"),
        path("index/", views.index, name="words_index"),
        path("config/", views.configure, name="words_config"),
    ]
)
