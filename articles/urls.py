from django.urls import path

from . import views

urlpatterns = (
    [
        path("config", views.configure, name="list_articles_config"),
        path("index", views.index, name="list_articles"),
    ]
)
