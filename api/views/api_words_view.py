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


class UserWordRatingsSet(views.APIView):
    def get_words(self, user, language):
        word_ratings = WordRating.objects.filter(user=user)
        return word_ratings

    def build_output(self, word_ratings):
        output = []
        for word_rating in word_ratings:
            output.append(
                {
                    "id": word_rating.word.id,
                    "text": word_rating.word.text,
                    "language": word_rating.word.language,
                    "familiarity_label": word_rating.rating,
                    "created_at": word_rating.created_at,
                    "updated_at": word_rating.updated_at,
                }
            )
        return output

    def get(self, request):
        guy = User.objects.get(username="guy")

        body_data = json.loads(request.body)

        language = body_data.get("language", None)
        if not language:
            return Response(
                {"success": False, "error": "language is required"}, status=400
            )

        word_ratings = self.get_words(user=guy, language=language)

        return Response(
            {"success": True, "word_ratings": self.build_output(word_ratings)},
            status=200,
        )
        pass

    def put(self, request):
        guy = User.objects.get(username="guy")

        body_data = json.loads(request.body)

        language = body_data.get("language", None)
        word_text = body_data.get("word_text", None)

        if not word_text or not language:
            return Response({"success": False}, status=400)

        rating = body_data.get("rating", None)

        word = Word.objects.get(text=word_text, language=language)

        try:
            WordRating.objects.create(user=guy, word=word, rating=rating)
        except:
            word_rating = WordRating.objects.filter(user=guy, word=word).first()
            word_rating.rating = rating
            word_rating.save()

        return Response({"success": True}, status=200)


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
            if language == "ar":
                search_words = [araby.strip_diacritics(w) for w in search_words]
            elif language == "he":
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
                ),
                Prefetch(
                    "flexions",
                    to_attr="word_flexions_list",
                ),
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
                    "id": lemma.id,
                    "text": lemma.text,
                    "translation": lemma.best_translation,
                    "root": lemma.best_root,
                    "language": lemma.language,
                    "count": lemma.count,
                    "rank": f"news: {lemma.rank_rss}   song:{lemma.rank_lyric}  wikipedia:{lemma.rank_wikipedia}  subtitles:{lemma.rank_subtitle}",
                    "flexion_counts": lemma.normalized_flexion_counts("count_lyric"),
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


class UserTranslation(views.APIView):

    def put(self, request):
        body_data = json.loads(request.body)

        print(body_data)
        word_id = body_data.get("id", None)
        new_translations = body_data.get("new_translations", None)

        print(word_id)
        word = Word.objects.get(id=word_id)
        print(word)
        word.user_translations.append(new_translations)
        word.save()

        return Response({"success": True}, status=200)

    def post(self, request):
        body_data = json.loads(request.body)
        print(body_data)
        word_id = body_data.get("id", None)
        word = Word.objects.get(id=word_id)

        return Response({"user_translations": word.user_translations}, status=200)
