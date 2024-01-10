from django.urls import path, include
from rest_framework import  routers
from .views import ArticlesWithWordsView, UserWordsViewSet

# router = routers.DefaultRouter()
# router.register(r"rating", WordRatingsViewSet, "rating")
# router.register(r"articles", ArticlesWithWordsView.as_view(), "articles")

# urlpatterns = [
#     path("words/", UserWordsViewSet.as_view()),
# ]




# # urlpatterns = [
# #     path('words/', UserWordsViewSet.as_view()),
# #     path('articles/', ArticlesWithWordsView.as_view()),
# # ]


router = routers.DefaultRouter()
# router.register(r"words", UserWordsViewSet, "words")


urlpatterns = [
    path("", include(router.urls)),
    path('articles/', ArticlesWithWordsView.as_view()),
    path('words/', UserWordsViewSet.as_view()),
]
