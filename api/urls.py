from rest_framework import routers
from django.urls import path, include
from .views import WordsViewSet, WordDetail, WordRatingsViewSet

router = routers.DefaultRouter()
router.register(r"words", WordsViewSet, "words")
router.register(r"similar_words", WordDetail, "words2")
router.register(r"rating", WordRatingsViewSet, "rating")

urlpatterns = [
    path("", include(router.urls)),
]
