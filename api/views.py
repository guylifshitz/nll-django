from words.models import Word, WordRating
from words.permissions import IsNotTestUser
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication 
from .serializers import WordsSerializer, WordsSerializer2, WordRatingsSerializer

# TODO handle arabic
class WordsViewSet(viewsets.ModelViewSet):
    lookup_field = "text"
    queryset = Word.objects.filter(language="hebrew").order_by("rank")[:100]
    authentication_classes = [TokenAuthentication]
    # why isn't the test user allowed here?
    permission_classes = [IsAuthenticated, IsNotTestUser]
    # authentication_classes = []
    # permission_classes = []
    serializer_class = WordsSerializer

# TODO handle arabic
class WordDetail(viewsets.ReadOnlyModelViewSet):
    lookup_field = "text"
    permission_classes = ()
    queryset = Word.objects.filter(language="hebrew").order_by("rank").all()
    serializer_class = WordsSerializer2


class WordRatingsViewSet(viewsets.ModelViewSet):
    queryset = WordRating.objects.filter().order_by("rating").all()
    serializer_class = WordRatingsSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

