import hashlib
import uuid
from words.models import Word, WordRating
from articles.models import Rss_feed, Song_lyrics, Open_subtitles
from django.db.models import Prefetch
from django.db import connection
from django.db.models import Q
import json
from rest_framework.response import Response
from rest_framework import views
from django.contrib.auth.models import User
import random
import datetime

class ThingWithWordsView(views.APIView):

    # TODO: this doesnt handle empty known_words on sql query
    def getEntries(self, language, practice_words, known_words, entry_display_count, start_date, end_date):
        with connection.cursor() as cursor:

            known_words = set(known_words) - set(practice_words)
            known_words = list(known_words)

            if self.table_name == "articles_song_lyrics":
                entry_display_count = min(entry_display_count, 30)

            print("known_words", known_words, "practice_words", practice_words)
            if len(practice_words) > 10:
                query = f"""(SELECT id, ratio, practice_found_count, known_found_count FROM 
                (SELECT id, practice_found_count, known_found_count, practice_found_count::decimal / title_parsed_lemma_length::decimal AS ratio FROM
                (SELECT id, array_length("title_parsed_lemma", 1) AS title_parsed_lemma_length, 
                array_length(ARRAY( SELECT * FROM UNNEST( "title_parsed_lemma" ) WHERE UNNEST = ANY( array[%s])),1) AS practice_found_count,
                array_length(ARRAY( SELECT * FROM UNNEST( "title_parsed_lemma" ) WHERE UNNEST = ANY( array[%s])),1) AS known_found_count
                FROM {self.table_name} WHERE language = %s) t1 ) t2 WHERE ratio NOTNULL ORDER BY ratio desc, practice_found_count desc, known_found_count desc NULLS LAST limit %s);"""
            else:
                query = f"""(SELECT id, ratio, practice_found_count, known_found_count FROM 
                (SELECT id, practice_found_count, known_found_count, (practice_found_count::decimal + known_found_count::decimal) / title_parsed_lemma_length::decimal AS ratio FROM
                (SELECT id, array_length("title_parsed_lemma", 1) AS title_parsed_lemma_length, 
                array_length(ARRAY( SELECT * FROM UNNEST( "title_parsed_lemma" ) WHERE UNNEST = ANY( array[%s])),1) AS practice_found_count,
                array_length(ARRAY( SELECT * FROM UNNEST( "title_parsed_lemma" ) WHERE UNNEST = ANY( array[%s])),1) AS known_found_count
                FROM {self.table_name} WHERE language = %s) t1 ) t2 WHERE ratio NOTNULL ORDER BY ratio desc limit %s);"""
            cursor.execute(
                query, [practice_words, known_words, language, entry_display_count]
            )
            rows = cursor.fetchall()

        entry_ids = []
        for r in rows:
            entry_ids.append(r[0])
        print("entry_ids", entry_ids)

        entry_ids = entry_ids[0:entry_display_count+1]

        if self.table_name == "articles_open_subtitle":
            entries = Open_subtitles.objects.filter(id__in=entry_ids).order_by("id").all()
        elif self.table_name == "articles_song_lyrics":
            entries = Song_lyrics.objects.filter(id__in=entry_ids).order_by("id").all()

        output_entries = []
        for entry_id in entry_ids:
            for entry in entries:
                if entry_id == entry.id:
                    output_entries.append(entry)
        return output_entries 

    def formatEntries(self, articles, language, practice_words,known_words, guy):
        formatted_articles =[]
        lemmas_to_find = set()
        for article in articles:
            article_lines = []
            article_line_words = []

            all_same_length = len(article.title_parsed_clean) == len(article.title_parsed_lemma) == len(article.title_parsed_segmented) == len(article.title_parsed_postag) == len(article.title_parsed_feats)
            if not all_same_length:
                print(article.title_parsed_clean, len(article.title_parsed_clean))
                print(article.title_parsed_lemma, len(article.title_parsed_lemma))
                print(article.title_parsed_segmented, len(article.title_parsed_segmented))
                print(article.title_parsed_postag, len(article.title_parsed_postag))
                print(article.title_parsed_feats, len(article.title_parsed_feats))

                print("---")
                continue

            for index, word in enumerate(article.title_parsed_clean):
                lemmas_to_find.add(article.title_parsed_lemma[index])
                flexion_translation = "NOT DONE YET"
                if language == 'arabic':
                    flexion_translation = ""
                    if article.title_parsed_roots and article.title_parsed_flexion_gloss and article.title_parsed_lemma_gloss:
                        flexion_translation = article.title_parsed_roots[index] + " // LEM:"+ article.title_parsed_flexion_gloss[index].replace("_", " ") + " // FLEX:"+ article.title_parsed_lemma_gloss[index].replace("_", " ")

                if article.title_parsed_lemma[index] == "###":
                    article_lines.append(article_line_words)
                    article_line_words = []
                else:
                    article_line_words.append({
                        "id": hashlib.md5(f"{article.id} - {index}".encode()).hexdigest(),
                        "text": article.title_parsed_clean[index],
                        "lemma": article.title_parsed_lemma[index],
                        "segmented": article.title_parsed_segmented[index],
                        "part_of_speech": article.title_parsed_postag[index],
                        "features": article.title_parsed_feats[index],
                        "flexion_translation": flexion_translation,
                        "is_name": article.title_parsed_postag[index] == 'noun_prop',
                    }
                )
                    
            article_lines.append(article_line_words)

            formatted_articles.append(
            {
                "id": hashlib.md5(f"{article.id}".encode()).hexdigest(),
                "published_datetime": article.published_datetime,
                "title": article.title,
                "link": article.link,
                "extra_text": article.summary,
                "translation": article.title_translation,
                "tag_level_1": article.source,
                "tag_level_2": str(article.feed_names),
                "article_lines": article_lines
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

        articles = self.getEntries(language, practice_words, known_words, 100, start_date, end_date)
        output = self.formatEntries(articles, language, practice_words, known_words, guy)

        # results = ArticleAndWordSerializer(output, many=False).data

        return Response(output, status=200)

class SongsWithWordsView(ThingWithWordsView):
    table_name = "articles_song_lyrics"

class OpenSubtitlesWithWordsView(ThingWithWordsView):
    table_name = "articles_open_subtitle"

class ArticlesWithWordsView(ThingWithWordsView):
    table_name = "articles_rss_feed"

    # TODO: this doesnt handle empty known_words on sql query
    def getEntries(self, language, practice_words, known_words, article_display_count, start_date, end_date,):
        with connection.cursor() as cursor:

            known_words = set(known_words) - set(practice_words)
            known_words = list(known_words)
            print(start_date, end_date, language, article_display_count)
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

