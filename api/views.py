import uuid
from words.models import Word, WordRating
from articles.models import Rss_feed
from django.db.models import Prefetch
from django.db import connection
from django.db.models import Q
import json
from rest_framework.response import Response
from rest_framework import views
from .serializers import ArticleAndWordSerializer
from django.contrib.auth.models import User
import random
import datetime

class ArticlesWithWordsView(views.APIView):

    # TODO: this doesnt handle empty known_words on sql query
    def getArticlesWithWords(self, language, practice_words, known_words, start_date, end_date, article_display_count):
        with connection.cursor() as cursor:

            known_words = set(known_words) - set(practice_words)
            known_words = list(known_words)
        
            print("known_words", known_words, "practice_words", practice_words)
            if len(practice_words) > 10:
                query = """(SELECT id, ratio, practice_found_count, known_found_count FROM 
                (SELECT id, practice_found_count, known_found_count, practice_found_count::decimal / title_parsed_lemma_length::decimal AS ratio FROM
                (SELECT id, array_length("title_parsed_lemma", 1) AS title_parsed_lemma_length, 
                array_length(ARRAY( SELECT * FROM UNNEST( "title_parsed_lemma" ) WHERE UNNEST = ANY( array[%s])),1) AS practice_found_count,
                array_length(ARRAY( SELECT * FROM UNNEST( "title_parsed_lemma" ) WHERE UNNEST = ANY( array[%s])),1) AS known_found_count
                FROM articles_rss_feed WHERE published_datetime >= %s AND published_datetime <= %s AND language = %s) t1 ) t2 WHERE ratio NOTNULL ORDER BY ratio desc, practice_found_count desc, known_found_count desc NULLS LAST limit %s);"""
            else:
                query = """(SELECT id, ratio, practice_found_count, known_found_count FROM 
                (SELECT id, practice_found_count, known_found_count, (practice_found_count::decimal + known_found_count::decimal) / title_parsed_lemma_length::decimal AS ratio FROM
                (SELECT id, array_length("title_parsed_lemma", 1) AS title_parsed_lemma_length, 
                array_length(ARRAY( SELECT * FROM UNNEST( "title_parsed_lemma" ) WHERE UNNEST = ANY( array[%s])),1) AS practice_found_count,
                array_length(ARRAY( SELECT * FROM UNNEST( "title_parsed_lemma" ) WHERE UNNEST = ANY( array[%s])),1) AS known_found_count
                FROM articles_rss_feed WHERE published_datetime >= %s AND published_datetime <= %s AND language = %s) t1 ) t2 WHERE ratio NOTNULL ORDER BY ratio desc limit %s);"""
            cursor.execute(
                query, [practice_words, known_words, start_date, end_date, language, article_display_count]
            )
            rows = cursor.fetchall()

        article_ids = []
        for r in rows:
            article_ids.append(r[0])
        print("article_ids", article_ids)

        article_ids = article_ids[0:article_display_count+1]

        articles = Rss_feed.objects.filter(link__in=article_ids).order_by("id").all()
        output_articles = []
        for article_id in article_ids:
            for article in articles:
                if article_id == article.id:
                    output_articles.append(article)
        return output_articles 

    def formatArticles(self, articles, language, practice_words,known_words, guy):
        formatted_articles =[]
        lemmas_to_find = set()
        for article in articles:
            article_words = []

            all_same_length = len(article.title_parsed_clean) == len(article.title_parsed_lemma) == len(article.title_parsed_segmented) == len(article.title_parsed_postag) == len(article.title_parsed_feats)
            if not all_same_length:
                print("BAD LINE")
                print(article.title_parsed_clean, len(article.title_parsed_clean))
                print(article.title_parsed_lemma, len(article.title_parsed_lemma))
                print(article.title_parsed_segmented, len(article.title_parsed_segmented))
                print(article.title_parsed_postag, len(article.title_parsed_postag))
                print(article.title_parsed_feats, len(article.title_parsed_feats))

                print("---")
                continue

            for index, word in enumerate(article.title_parsed_clean):
                lemmas_to_find.add(article.title_parsed_lemma[index])
                article_words.append({
                    "id": uuid.uuid4().hex,
                    "text": article.title_parsed_clean[index],
                    "lemma": article.title_parsed_lemma[index],
                    "segmented": article.title_parsed_segmented[index],
                    "part_of_speech": article.title_parsed_postag[index],
                    "features": article.title_parsed_feats[index],
                    "flexion_translation": "NOT DONE YET",
                }
                )

            formatted_articles.append(
            {
                "id": uuid.uuid4().hex,
                "published_datetime": article.published_datetime,
                "title": article.title,
                "link": article.link,
                "extra_text": article.summary,
                "translation": article.title_translation,
                "tag_level_1": article.source,
                "tag_level_2": str(article.feed_names),
                "article_words": article_words
            }
        )
            
        formatted_lemmas = self.getLemmas(lemmas_to_find, language, practice_words, known_words, guy)

        yourdata= {"articles": formatted_articles, "lemmas": formatted_lemmas}

        return yourdata

    # TODO: consider commmon code with UserWordsViewSet
    def getLemmas(self, all_article_lemmas, language, practice_words, known_words, guy):
        wordrating_queryset = WordRating.objects.filter(user=guy)

        lemmas = Word.objects.prefetch_related(
        Prefetch("word_ratings", to_attr="word_ratings_list", queryset=wordrating_queryset)
        ).filter(language=language, text__in=all_article_lemmas).order_by("rank").all()

        formatted_lemmas = []
        for lemma in lemmas:
            if lemma.word_ratings_list:
                familiarity_label = lemma.word_ratings_list[-1].rating
            else:
                familiarity_label = 0

            # isKnown = familiarity_label > 0
            isKnown = lemma.text in known_words

            if lemma.text in practice_words:
                isPractice = True
            else:
                isPractice = False

            formatted_lemmas.append(
                {
                    "id": lemma.text,
                    "text": lemma.text,
                    "translation": lemma.translation,
                    "root": lemma.root,
                    "language": lemma.language,
                    "count": lemma.count,
                    "rank": lemma.rank,
                    "familiarity_label": familiarity_label,
                    'isKnown': isKnown,
                    'isPractice': isPractice,
                })

        return formatted_lemmas


    def get_known_words(self, user, language):
        wordrating_queryset = WordRating.objects.filter(user=user)
        known_words = Word.objects.prefetch_related(
        Prefetch("word_ratings", to_attr="word_ratings_list", queryset=wordrating_queryset)
        ).filter(language=language, word_ratings__rating__gt=0).order_by("rank").all()
        return known_words
    

    def post(self, request):
        guy = User.objects.get(username="guy")

        body_data = json.loads(request.body)

        language  = body_data.get("language", None)
        start_date = body_data.get("start_date", None)
        end_date = body_data.get("end_date", None)
        if not start_date:
            start_date = '01/01/2020'
        if not end_date:
            end_date = '01/01/3000'
            
        if not language:
            return Response({"success": False, "error": "language is required"}, status=400)
        
        practice_words = body_data.get("practice_words", None)
        known_words = self.get_known_words(guy, language)
        known_words = [w.text for w in known_words]

        articles = self.getArticlesWithWords(language, practice_words, known_words, start_date, end_date, 100)
        output = self.formatArticles(articles, language, practice_words, known_words, guy)

        results = ArticleAndWordSerializer(output, many=False).data
        return Response(results)


class UserWordsViewSet(views.APIView):

    # TODO correctly handle authentication
    # from rest_framework.authtoken.models import Token
    # Token.objects.all().delete()
    # guy = User.objects.get(username="guy")
    # token = Token.objects.create(user=guy)
    # print("TOKEN:", token.key)

    def get_words(self, 
                  user,
                  language, 
                  lower_rank_cutoff, 
                  upper_rank_cutoff, 
                  search_words, 
                  search_translation_words, 
                  search_exact = True, 
                  ):
        
        querys = Q(language=language)
        if lower_rank_cutoff:
            querys &= Q(rank__gte=lower_rank_cutoff)
        if upper_rank_cutoff:
            querys &= Q(rank__lte=upper_rank_cutoff)
        search_query = Q()
        if search_words:
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
        lemmas = Word.objects.prefetch_related(
        Prefetch("word_ratings", to_attr="word_ratings_list", queryset=wordratings_query_set)
        ).filter(querys).order_by("rank").all()[0:10000]

        return lemmas


    def build_output_from_lemmas(self, lemmas):
        output = []
        for lemma in lemmas:
            if lemma.word_ratings_list:
                familiarity_label = lemma.word_ratings_list[-1].rating
            else:
                familiarity_label = 0

            output.append(
                {
                    "id": lemma.text,
                    "text": lemma.text,
                    "translation": lemma.translation,
                    "root": lemma.root,
                    "language": lemma.language,
                    "count": lemma.count,
                    "rank": lemma.rank,
                    'flexion_counts': lemma.normalized_flexion_counts,
                    "familiarity_label": familiarity_label
                }
            )
        return output

    def post(self, request):
        guy = User.objects.get(username="guy")

        body_data = json.loads(request.body)

        language  = body_data.get("language", None)
        if not language:
            return Response({"success": False, "error": "language is required"}, status=400)

        lower_rank_cutoff = body_data.get("lower_rank_cutoff", None)
        upper_rank_cutoff = body_data.get("upper_rank_cutoff", None)
        search_words = body_data.get("search_words", None)
        search_translation_words = body_data.get("search_translation_words", None)
        search_exact = body_data.get("search_exact", False)

        print("search_exact", search_exact)
        print("search_words", search_words)
        
        lemmas_to_find = self.get_words(guy,
                                        language, 
                                        lower_rank_cutoff,
                                        upper_rank_cutoff,
                                        search_words,
                                        search_translation_words,
                                        search_exact)
        output = self.build_output_from_lemmas(lemmas_to_find)
        return Response({"success": True, "lemmas": output}, status=200)


    def put(self, request):
        guy = User.objects.get(username="guy")

        body_data = json.loads(request.body)

        language  = body_data.get("language", None)
        word_text = body_data.get("word_text", None)

        if not word_text or not language:
            return Response({"success": False}, status=400)

        
        rating = body_data.get("rating", None)

        word = Word.objects.get(text=word_text, language=language)

        # new_word_rating = WordRating.objects.create(user=guy, word=word, rating=rating)
        WordRating.objects.filter(user=guy, word=word).update(rating=rating)

        return Response({"success": True}, status=200)
    