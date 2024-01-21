import hashlib
import uuid
from words.models import Word, WordRating
from articles.models import (
    Rss_feed,
    Song,
    Open_subtitles,
    Song_habibi,
    Wikipedia,
    Wikipedia_sentence,
    Subtitle,
    Subtitle_sentence,
    Lyric,
    Lyric_sentence,
)
from django.db.models import Prefetch
from django.db import connection
from django.db.models import Q
import json
from rest_framework.response import Response
from rest_framework import views
from django.contrib.auth.models import User
import random
import datetime
from psycopg2.extensions import AsIs
from itertools import chain, groupby
from operator import itemgetter


class ThingWithWordsView(views.APIView):
    # TODO: this doesnt handle empty known_words on sql query
    def get_entries(
        self,
        language,
        practice_words,
        known_words,
        entry_display_count,
        start_date,
        end_date,
    ):
        with connection.cursor() as cursor:
            known_words = set(known_words) - set(practice_words)
            known_words = list(known_words)

            if (
                self.table_name == "articles_song_lyrics"
                or self.table_name == "articles_song_habibi"
            ):
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

        entry_ids = entry_ids[0 : entry_display_count + 1]

        if self.table_name == "articles_open_subtitle":
            entries = (
                Open_subtitles.objects.filter(id__in=entry_ids).order_by("id").all()
            )
        elif self.table_name == "articles_song_lyrics":
            entries = Song.objects.filter(id__in=entry_ids).order_by("id").all()
        elif self.table_name == "articles_song_habibi":
            entries = Song_habibi.objects.filter(id__in=entry_ids).order_by("id").all()
        elif self.table_name == "articles_wikipedia":
            entries = Wikipedia.objects.filter(id__in=entry_ids).order_by("id").all()

        output_entries = []
        for entry_id in entry_ids:
            for entry in entries:
                if entry_id == entry.id:
                    output_entries.append(entry)
        return output_entries

    def format_entries(self, articles, language, practice_words, known_words, guy):
        formatted_articles = []
        lemmas_to_find = set()
        for article in articles:
            article_lines = []
            article_line_words = []

            all_same_length = (
                len(article.title_parsed_clean)
                == len(article.title_parsed_lemma)
                == len(article.title_parsed_segmented)
                == len(article.title_parsed_postag)
                == len(article.title_parsed_feats)
            )
            if not all_same_length:
                print(article.title_parsed_clean, len(article.title_parsed_clean))
                print(article.title_parsed_lemma, len(article.title_parsed_lemma))
                print(
                    article.title_parsed_segmented, len(article.title_parsed_segmented)
                )
                print(article.title_parsed_postag, len(article.title_parsed_postag))
                print(article.title_parsed_feats, len(article.title_parsed_feats))

                print("---")
                continue

            for index, word in enumerate(article.title_parsed_clean):
                lemmas_to_find.add(article.title_parsed_lemma[index])
                flexion_translation = "NOT DONE YET"
                if language == "arabic":
                    flexion_translation = ""
                    if (
                        article.title_parsed_roots
                        and article.title_parsed_flexion_gloss
                        and article.title_parsed_lemma_gloss
                    ):
                        flexion_translation = (
                            article.title_parsed_roots[index]
                            + " // LEM:"
                            + article.title_parsed_flexion_gloss[index].replace(
                                "_", " "
                            )
                            + " // FLEX:"
                            + article.title_parsed_lemma_gloss[index].replace("_", " ")
                        )

                # if article.title_parsed_lemma[index] == "###":
                if article.title_parsed_lemma[index] == "@":
                    article_lines.append(article_line_words)
                    article_line_words = []
                else:
                    article_line_words.append(
                        {
                            "id": hashlib.md5(
                                f"{article.id} - {index}".encode()
                            ).hexdigest(),
                            "text": article.title_parsed_clean[index],
                            "lemma": article.title_parsed_lemma[index],
                            "segmented": article.title_parsed_segmented[index],
                            "part_of_speech": article.title_parsed_postag[index],
                            "features": article.title_parsed_feats[index],
                            "flexion_translation": flexion_translation,
                            "is_name": article.title_parsed_postag[index]
                            == "noun_prop",
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
                    "article_lines": article_lines,
                }
            )

        formatted_lemmas = self.get_lemmas(
            lemmas_to_find, language, practice_words, known_words, guy
        )

        yourdata = {"articles": formatted_articles, "lemmas": formatted_lemmas}

        return yourdata

    # TODO: consider commmon code with UserWordsViewSet
    def get_lemmas(
        self, all_article_lemmas, language, practice_words, known_words, guy
    ):
        wordrating_queryset = WordRating.objects.filter(user=guy)

        lemmas = (
            Word.objects.prefetch_related(
                Prefetch(
                    "word_ratings",
                    to_attr="word_ratings_list",
                    queryset=wordrating_queryset,
                )
            )
            .filter(language=language, text__in=all_article_lemmas)
            .order_by("rank")
            .all()
        )

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
                    "rank": f"{lemma.rank}",
                    "familiarity_label": familiarity_label,
                    "isKnown": isKnown,
                    "isPractice": isPractice,
                }
            )

        return formatted_lemmas

    def get_known_words(self, user, language):
        wordrating_queryset = WordRating.objects.filter(user=user)
        known_words = (
            Word.objects.prefetch_related(
                Prefetch(
                    "word_ratings",
                    to_attr="word_ratings_list",
                    queryset=wordrating_queryset,
                )
            )
            .filter(language=language, word_ratings__rating__gt=0)
            .order_by("rank")
            .all()
        )
        return known_words

    def post(self, request):
        guy = User.objects.get(username="guy")

        body_data = json.loads(request.body)

        language = body_data.get("language", None)
        start_date = body_data.get("start_date", None)
        end_date = body_data.get("end_date", None)
        if not start_date:
            start_date = "01/01/2020"
        if not end_date:
            end_date = "01/01/3000"

        if not language:
            return Response(
                {"success": False, "error": "language is required"}, status=400
            )

        practice_words = body_data.get("practice_words", None)
        # known_words.append("punc")
        known_words = self.get_known_words(guy, language)
        known_words = [w.text for w in known_words]

        articles = self.get_entries(
            language, practice_words, known_words, 30, start_date, end_date
        )
        output = self.format_entries(
            articles, language, practice_words, known_words, guy
        )

        # results = ArticleAndWordSerializer(output, many=False).data

        return Response(output, status=200)


class SongsWithWordsView(ThingWithWordsView):
    table_name = "articles_song_lyrics"
    # table_name = "articles_song_habibi"


class ArticlesWithWordsView(ThingWithWordsView):
    table_name = "articles_rss_feed"

    # TODO: this doesnt handle empty known_words on sql query
    def get_entries(
        self,
        language,
        practice_words,
        known_words,
        article_display_count,
        start_date,
        end_date,
    ):
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
                query,
                [
                    practice_words,
                    known_words,
                    start_date,
                    end_date,
                    language,
                    article_display_count,
                ],
            )
            rows = cursor.fetchall()

        article_ids = []
        for r in rows:
            article_ids.append(r[0])
        print("article_ids", article_ids)

        article_ids = article_ids[0 : article_display_count + 1]

        articles = Rss_feed.objects.filter(link__in=article_ids).order_by("id").all()
        output_articles = []
        for article_id in article_ids:
            for article in articles:
                if article_id == article.id:
                    output_articles.append(article)
        return output_articles


class SourceWithSentncesAndWordsView(ThingWithWordsView):
    sentence_ids = []
    sentence_ratios = {}

    def get_entries(
        self,
        language,
        practice_words,
        known_words,
        article_display_count,
        start_date,
        end_date,
    ):
        language = "ar" if language == "arabic" else "he"

        with connection.cursor() as cursor:
            known_words = set(known_words) - set(practice_words)
            known_words = list(known_words)

            print("Find sentences with: ")
            print("language:", language)
            print("table_name:", self.table_name)
            print("practice_words:", practice_words)
            print("known_words:", known_words)
            if len(practice_words) > 10:
                query = """(SELECT id, source_id, ratio, practice_found_count, known_found_count, parsed_lemma_length, punct_found_count FROM 
                (SELECT id, source_id, practice_found_count, known_found_count, parsed_lemma_length, punct_found_count, ROUND(practice_found_count::decimal / (parsed_lemma_length::decimal - punct_found_count::decimal ),1) AS ratio FROM
                (SELECT id, source_id, array_length("parsed_lemma", 1) AS parsed_lemma_length, 
                cardinality(ARRAY( SELECT * FROM UNNEST( "parsed_pos" ) WHERE UNNEST = 'punc')) AS punct_found_count,
                array_length(ARRAY( SELECT * FROM UNNEST( "parsed_lemma" ) WHERE UNNEST = ANY( array[%(practice_words)s])),1) AS practice_found_count,
                array_length(ARRAY( SELECT * FROM UNNEST( "parsed_lemma" ) WHERE UNNEST = ANY( array[%(known_words)s])),1) AS known_found_count
                FROM %(sentence_table)s WHERE language = %(language)s) t1 ) t2 WHERE ratio NOTNULL and (parsed_lemma_length - punct_found_count) > 1 ORDER BY ratio desc, practice_found_count desc, known_found_count desc NULLS LAST limit %(limit)s);"""
            else:
                query = """(SELECT id, source_id, ratio, practice_found_count, known_found_count, parsed_lemma_length FROM 
                (SELECT id, source_id, practice_found_count, known_found_count, parsed_lemma_length, (practice_found_count::decimal + known_found_count::decimal) / parsed_lemma_length::decimal AS ratio FROM
                (SELECT id, source_id, array_length("parsed_lemma", 1) AS parsed_lemma_length, 
                array_length(ARRAY( SELECT * FROM UNNEST( "parsed_lemma" ) WHERE UNNEST = ANY( array[%(practice_words)s])),1) AS practice_found_count,
                array_length(ARRAY( SELECT * FROM UNNEST( "parsed_lemma" ) WHERE UNNEST = ANY( array[%(known_words)s])),1) AS known_found_count
                FROM %(sentence_table)s WHERE language = %(language)s) t1 ) t2 WHERE ratio NOTNULL ORDER BY known_found_count desc limit %(limit)s);"""
            cursor.execute(
                query,
                {
                    "sentence_table": AsIs(f"{self.table_name}_sentence"),
                    "language": language,
                    "practice_words": practice_words,
                    "known_words": known_words,
                    "limit": article_display_count,
                },
            )
            print(query)
            print(
                {
                    "sentence_table": AsIs(f"{self.table_name}_sentence"),
                    "language": language,
                    "practice_words": practice_words,
                    "known_words": known_words,
                    "limit": article_display_count,
                },
            )
            rows = cursor.fetchall()
        source_ids = []
        ratios = []
        result_rows = []
        print("rows", rows)
        for r in rows:
            self.sentence_ids.append(r[0])
            self.sentence_ratios[str(r[0])] = r[2]
            source_ids.append(r[1])
            result_rows.append(r)
        # source_ids = self.custom_sort_order(result_rows)
        source_ids = source_ids[0 : article_display_count + 1]
        source_ids = list(dict.fromkeys(source_ids))

        print("source_ids", source_ids)
        print("Load articles...")

        sentence_set = self.sentence_model.objects.all()

        sources = (
            self.source_model.objects.prefetch_related(
                Prefetch(
                    "sentences",
                    to_attr="sentence_list",
                    queryset=sentence_set,
                )
            )
            .filter(id__in=source_ids)
            .all()
        )
        print("Done loading", len(sources), "articles")

        output_sources = []
        for source_id in source_ids:
            for source in sources:
                if source_id == source.id:
                    output_sources.append(source)
        return output_sources

    def generate_empty_line(self):
        return [
            {
                "id": hashlib.md5(f"{uuid.uuid4()}".encode()).hexdigest(),
                "text": "",
                "lemma": "",
                "segmented": "",
                "part_of_speech": "",
                "features": "",
                "flexion_translation": "",
                "is_name": False,
            }
        ]

    def generate_bad_line(self):
        return [
            {
                "id": hashlib.md5(f"{uuid.uuid4()}".encode()).hexdigest(),
                "text": "OUCH",
                "lemma": "OUCH",
                "segmented": "OUCH",
                "part_of_speech": "OUCH",
                "features": "OUCH",
                "flexion_translation": "OUCH",
                "is_name": False,
            }
        ]

    def format_entries(self, articles, language, practice_words, known_words, guy):
        formatted_articles = []
        lemmas_to_find = set()

        language_code = "ar" if language == "arabic" else "he"

        for article in articles:
            article_lines = []

            sentences = set(article.sentence_list)

            output_sentences = []
            for sentence in sentences:
                if not sentence.parsed_clean:
                    article_lines.append(self.generate_bad_line())
                    continue

                try:
                    article_line_words = []

                    for index, word in enumerate(sentence.parsed_clean):
                        lemmas_to_find.add(sentence.parsed_lemma[index])
                        flexion_translation = "NOT DONE YET"
                        if language_code == "ar":
                            flexion_translation = ""
                            if (
                                sentence.parsed_roots
                                and sentence.parsed_gloss_flexion
                                and sentence.parsed_gloss_lemma
                            ):
                                flexion_translation = (
                                    sentence.parsed_roots[index]
                                    + " // LEM:"
                                    + sentence.parsed_gloss_flexion[index].replace(
                                        "_", " "
                                    )
                                    + " // FLEX:"
                                    + sentence.parsed_gloss_lemma[index].replace(
                                        "_", " "
                                    )
                                )
                        else:
                            flexion_translation = "NOT DONE YET"

                        article_line_words.append(
                            {
                                "id": sentence.id,
                                "text": sentence.parsed_clean[index],
                                "lemma": sentence.parsed_lemma[index],
                                "segmented": sentence.parsed_segmented[index],
                                "part_of_speech": sentence.parsed_pos[index],
                                "features": sentence.parsed_features[index],
                                "flexion_translation": flexion_translation,
                                "is_name": sentence.parsed_pos[index] == "noun_prop",
                            }
                        )
                except:
                    article_lines.append(self.generate_bad_line())

                if sentence.id in self.sentence_ids:
                    translation = str(self.sentence_ratios[str(sentence.id)]) + str(
                        sentence.translation
                    )

                    article_lines.append(self.generate_empty_line())
                    article_lines.append(self.generate_empty_line())
                    article_lines.append(self.generate_empty_line())
                    article_lines.append(article_line_words)
                    article_lines.append(self.generate_empty_line())
                    article_lines.append(self.generate_empty_line())
                    article_lines.append(self.generate_empty_line())
                else:
                    article_lines.append(article_line_words)

            formatted_articles.append(
                {
                    "id": hashlib.md5(
                        f"{article.id}+{random.randint(0,100000)}".encode()
                    ).hexdigest(),
                    "published_datetime": None,
                    "title": article.title,
                    "link": article.link,
                    "extra_text": article.extra_text,
                    "translation": translation,
                    # + " // "
                    # + "\n".join([sentence.translation for sentence in sentences]),
                    "tag_level_1": article.title,
                    "tag_level_2": [None],
                    "article_lines": article_lines,
                }
            )

        formatted_lemmas = self.get_lemmas(
            lemmas_to_find, language, practice_words, known_words, guy
        )

        yourdata = {"articles": formatted_articles, "lemmas": formatted_lemmas}

        return yourdata

    def custom_sort_order(self, result_rows):
        return result_rows


class WikipediaWithWordsView(SourceWithSentncesAndWordsView):
    table_name = "articles_wikipedia"
    source_model = Wikipedia
    sentence_model = Wikipedia_sentence


class SubtitlesWithWordsView(SourceWithSentncesAndWordsView):
    table_name = "articles_subtitle"
    source_model = Subtitle
    sentence_model = Subtitle_sentence

    def custom_sort_order(self, result_rows):
        def get_sorted_ids(ratio_results):
            ratio_article_ids = [r[1] for r in ratio_results]
            return list(
                Subtitle.objects.filter(id__in=ratio_article_ids)
                .order_by("-number_ratings")
                .values_list("id", flat=True)
            )

        result_rows = [
            get_sorted_ids(group)
            for ratio, group in groupby(result_rows, key=itemgetter(2))
        ]
        return list(chain.from_iterable(result_rows))


class LyricWithWordsView(SourceWithSentncesAndWordsView):
    table_name = "articles_lyric"
    source_model = Lyric
    sentence_model = Lyric_sentence
