import unicodedata
from words.models import Word, WordRating
from django.db.models import Prefetch
from django.db import connection
from django.db.models import Q
import json
from rest_framework.response import Response
from rest_framework import views
from django.contrib.auth.models import User
import pyarabic.araby as araby


class UserWordsViewSet(views.APIView):
    # TODO correctly handle authentication
    # from rest_framework.authtoken.models import Token
    # Token.objects.all().delete()
    # guy = User.objects.get(username="guy")
    # token = Token.objects.create(user=guy)
    # print("TOKEN:", token.key)
    def get_words(
        self,
        user,
        language,
        lower_rank_cutoff,
        upper_rank_cutoff,
        search_words,
        search_translation_words,
        order_by_column,
        search_exact=True,
    ):
        querys = Q(language=language)
        if lower_rank_cutoff:
            querys &= Q(rank__gte=lower_rank_cutoff)
        if upper_rank_cutoff:
            querys &= Q(rank__lte=upper_rank_cutoff)
        search_query = Q()
        if search_words:
            if language == "arabic":
                search_words = [araby.strip_diacritics(w) for w in search_words]
            elif language == "hebrew":
                search_words = [self.remove_niqqud(word) for word in search_words]

            for search_word in search_words:
                if search_exact:
                    search_query |= Q(text__iexact=search_word)
                else:
                    search_query |= Q(text__icontains=search_word)
        if search_translation_words:
            for search_translation_word in search_translation_words:
                if search_exact:
                    search_query |= Q(translation__iexact=search_translation_word)
                else:
                    search_query |= Q(translation__icontains=search_translation_word)

        querys &= search_query

        wordratings_query_set = WordRating.objects.filter(user=user)

        lemmas = (
            Word.objects.prefetch_related(
                Prefetch(
                    "word_ratings",
                    to_attr="word_ratings_list",
                    queryset=wordratings_query_set,
                )
            )
            .filter(querys)
            .order_by(order_by_column)
            # .order_by("rank_song_habibi")
            .all()[0:10000]
        )

        print("lemmas", lemmas.count())
        return lemmas

    def remove_niqqud(self, word):
        normalized = unicodedata.normalize("NFKD", word)
        no_diacritics = "".join([c for c in normalized if not unicodedata.combining(c)])
        return no_diacritics

    def build_output_from_lemmas(self, lemmas):
        output = []
        for lemma in lemmas:
            print("lemma.text", lemma)

            if lemma.word_ratings_list:
                familiarity_label = lemma.word_ratings_list[-1].rating
            else:
                familiarity_label = 0

            output.append(
                {
                    "id": lemma.text,
                    "text": lemma.text,
                    "translation": lemma.best_translation,
                    "root": lemma.best_root,
                    "language": lemma.language,
                    "count": lemma.count,
                    "rank": f"news: {lemma.rank_rss}   song:{lemma.rank_lyric}  wikipedia:{lemma.rank_wikipedia}  subtitles:{lemma.rank_subtitle}",
                    "flexion_counts": lemma.normalized_flexion_counts,
                    "familiarity_label": familiarity_label,
                }
            )
        return output

    def post(self, request):
        guy = User.objects.get(username="guy")

        body_data = json.loads(request.body)

        language = body_data.get("language", None)
        if not language:
            return Response(
                {"success": False, "error": "language is required"}, status=400
            )

        lower_rank_cutoff = body_data.get("lower_rank_cutoff", None)
        upper_rank_cutoff = body_data.get("upper_rank_cutoff", None)
        search_words = body_data.get("search_words", None)
        search_translation_words = body_data.get("search_translation_words", None)
        search_exact = body_data.get("search_exact", False)
        order_by = body_data.get("order_by", "")
        order_by_column = f"rank_{order_by}" if order_by else "rank"
        # order_by_column = "rank_lyric"
        language = "ar"
        print("search_exact", search_exact)
        print("search_words", search_words)

        lemmas_to_find = self.get_words(
            guy,
            language,
            lower_rank_cutoff,
            upper_rank_cutoff,
            search_words,
            search_translation_words,
            order_by_column,
            search_exact,
        )
        output = self.build_output_from_lemmas(lemmas_to_find)

        return Response({"success": True, "lemmas": output}, status=200)

    def put(self, request):
        guy = User.objects.get(username="guy")

        body_data = json.loads(request.body)

        language = body_data.get("language", None)
        language = "ar"
        word_text = body_data.get("word_text", None)

        if not word_text or not language:
            return Response({"success": False}, status=400)

        rating = body_data.get("rating", None)

        word = Word.objects.get(text=word_text, language=language)

        try:
            WordRating.objects.create(user=guy, word=word, rating=rating)
        except:
            WordRating.objects.filter(user=guy, word=word).update(rating=rating)

        return Response({"success": True}, status=200)
