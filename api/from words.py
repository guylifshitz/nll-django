from words.models import Word, WordRating
from articles.models import Rss_feed
from django.db.models import Prefetch
from django.db import connection
import json
from rest_framework.response import Response
from rest_framework import views
from django.contrib.auth.models import User
import random

class ArticlesWithWordsView(views.APIView):
    def getArticlesWithWords(self, language, practice_words, known_words, start_date_cutoff, end_date_cutoff, article_display_count):
        with connection.cursor() as cursor:
            query = """(SELECT id, ratio, lemma_found_count, known_found_count FROM 
            (SELECT id, lemma_found_count, known_found_count, lemma_found_count::decimal / title_parsed_lemma_length::decimal AS ratio FROM
            (SELECT id, array_length("title_parsed_lemma", 1) AS title_parsed_lemma_length, 
            array_length(ARRAY( SELECT * FROM UNNEST( "title_parsed_lemma" ) WHERE UNNEST = ANY( array[%s])),1) AS lemma_found_count,
            array_length(ARRAY( SELECT * FROM UNNEST( "title_parsed_lemma" ) WHERE UNNEST = ANY( array[%s])),1) AS known_found_count
            FROM articles_rss_feed WHERE published_datetime >= %s AND published_datetime <= %s AND language = %s) t1 ) t2 WHERE ratio NOTNULL ORDER BY ratio desc, lemma_found_count desc, known_found_count desc NULLS LAST limit %s);"""
            cursor.execute(
                query, [practice_words, known_words, start_date_cutoff, end_date_cutoff, language, article_display_count]
            )
            rows = cursor.fetchall()

        article_ids = []
        for r in rows:
            print(r[0])
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

    def get(self, request):
        guy = User.objects.get(username="guy")
        language = request.GET.get('language', 'hebrew')

        lemmas_to_find = set()
        formatted_articles = []

        practice_words = Word.objects.filter(language=language, rank__gte=1, rank__lte=100).all()
        known_words = Word.objects.filter(language=language, rank__gte=1, rank__lte=500).all()
        practice_words = [w.text for w in practice_words]
        known_words = [w.text for w in known_words]

        articles = self.getArticlesWithWords(language, practice_words, known_words, "2020-01-01", "2023-01-01", 100)

        # articles = 
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
                break

            for index, word in enumerate(article.title_parsed_clean):
                lemmas_to_find.add(article.title_parsed_lemma[index])
                article_words.append({
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
                "published_datetime": article.published_datetime,
                "title": article.title,
                "link": article.link,
                "summary": article.summary,
                "translation": article.title_translation,
                "tag_level_1": article.source,
                "tag_level_2": str(article.feed_names),
                "article_words": article_words
            }
            )


        queryset = WordRating.objects.filter(user=guy)
        lemmas = Word.objects.prefetch_related(
        Prefetch("word_ratings", to_attr="word_ratings_list", queryset=queryset)
        ).filter(language=language, text__in=lemmas_to_find).order_by("rank").all()

        formatted_lemmas = []
        for lemma in lemmas:
            if lemma.word_ratings_list:
                familiarity_label = lemma.word_ratings_list[-1].rating
            else:
                familiarity_label = 0

            isKnown = familiarity_label > 0

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

        yourdata= {"articles": formatted_articles, "lemmas": formatted_lemmas}
        results = ArticleAndWordSerializer(yourdata, many=False).data
        return Response(results)



class UserWordsViewSet(views.APIView):

    # TODO correctly handle authentication
    # from rest_framework.authtoken.models import Token
    # Token.objects.all().delete()
    # guy = User.objects.get(username="guy")
    # token = Token.objects.create(user=guy)
    # print("TOKEN:", token.key)

    def get_words(self, language, lower_rank_cutoff, upper_rank_cutoff, lemmas_to_find):

        querys = Q(language=language)
        if lower_rank_cutoff:
            querys &= Q(rank__gte=lower_rank_cutoff)
        if upper_rank_cutoff:
            querys &= Q(rank__lte=upper_rank_cutoff)
        if lemmas_to_find:
            querys &= Q(text__in=lemmas_to_find)

        lemmas = Word.objects.prefetch_related(
        Prefetch("word_ratings", to_attr="word_ratings_list", queryset=queryset)
        ).filter(querys).order_by("rank").all()

        return lemmas

    def post(self, request):
        guy = User.objects.get(username="guy")

        body_data = json.loads(request.body)

        language  = body_data.get("language", None)
        lower_rank_cutoff = body_data.get("lower_rank_cutoff", None)
        upper_rank_cutoff = body_data.get("upper_rank_cutoff", None)
        words_list = body_data.get("words_list", None)
        lemmas = set()

        return Response({"success": True, "lemmas": lemmas}, status=200)

    def get(self, request):
        guy = User.objects.get(username="guy")

        queryset = WordRating.objects.filter(user=guy)
        lemmas = Word.objects.prefetch_related(
        Prefetch("word_ratings", to_attr="word_ratings_list", queryset=queryset)
        )
        lemmas = lemmas.filter(language="hebrew", rank__gte=1, rank__lte=100).order_by("rank").all()
        lemmas =
        output = UserWordSerializer(lemmas, many=True).data
        return Response(output)

        # yourdata= {"articles": articles, "words": words}
        # results = ArticleAndWordSerializer(yourdata, many=False).data
        # return Response(results)
