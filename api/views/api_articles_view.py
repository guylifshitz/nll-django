import hashlib
import uuid
from words.models import Word, WordRating
from articles.models import (
    Rss,
    Rss_sentence,
    Lyric,
    Lyric_sentence,
    Subtitle,
    Subtitle_sentence,
    Wikipedia,
    Wikipedia_sentence,
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
from scripts.helpers import supported_language_codes


class SourceWithSentncesAndWordsView(views.APIView):
    sentence_ids = []
    sentence_ratios = {}
    datetime_filter = None
    table_query = "%(sentence_table)s"

    def get_source_entries(
        self,
        language_code,
        practice_words,
        known_words,
        article_display_count,
        start_date=None,
        end_date=None,
    ):
        with connection.cursor() as cursor:
            known_words = set(known_words) - set(practice_words)
            known_words = list(known_words)

            print("Find sentences with: ")
            print("language:", language_code)
            print("table_name:", self.table_name)
            print("practice_words:", practice_words)
            print("known_words:", known_words)

            if len(practice_words) > 10:
                ratio_equation = "(practice_found_count::decimal / (parsed_lemma_length::decimal - punct_found_count::decimal ))"
                parsed_lemma_length_equation = 'array_length("parsed_lemma", 1)'
                punct_found_count_equation = "cardinality(ARRAY( SELECT * FROM UNNEST( \"parsed_pos\" ) WHERE UNNEST = 'punc'))"
                practice_found_count_equation = 'array_length(ARRAY( SELECT * FROM UNNEST( "parsed_lemma" ) WHERE UNNEST = ANY( array[%(practice_words)s])),1) AS practice_found_count'
                known_found_count_equation = 'array_length(ARRAY( SELECT * FROM UNNEST( "parsed_lemma" ) WHERE UNNEST = ANY( array[%(known_words)s])),1) AS known_found_count'
            else:
                ratio_equation = "ROUND((practice_found_count::decimal + known_found_count::decimal) / (parsed_lemma_length::decimal - punct_found_count::decimal ),1)"
                parsed_lemma_length_equation = 'array_length("parsed_lemma", 1)'
                punct_found_count_equation = "cardinality(ARRAY( SELECT * FROM UNNEST( \"parsed_pos\" ) WHERE UNNEST = 'punc'))"
                practice_found_count_equation = 'cardinality(ARRAY( SELECT * FROM UNNEST( "parsed_lemma" ) WHERE UNNEST = ANY( array[%(practice_words)s])))'
                known_found_count_equation = 'cardinality(ARRAY( SELECT * FROM UNNEST( "parsed_lemma" ) WHERE UNNEST = ANY( array[%(known_words)s])))'

            query = f"""(
                SELECT
                    *
                FROM 
                    (SELECT
                        *, 
                        {ratio_equation} AS ratio
                    FROM
                    (SELECT 
                        id,
                        source_id, 
                        {parsed_lemma_length_equation} AS parsed_lemma_length, 
                        {punct_found_count_equation} AS punct_found_count,
                        {practice_found_count_equation} AS practice_found_count,
                        {known_found_count_equation} AS known_found_count
                    FROM 
                        {self.table_query} WHERE language = %(language)s) t1 ) t2
                    WHERE
                        ratio NOTNULL 
                        AND (parsed_lemma_length - punct_found_count) > 4 
                        AND practice_found_count > 0 
                    ORDER BY
                        ratio desc,
                        practice_found_count desc,
                        known_found_count desc NULLS LAST
                    LIMIT
                        %(limit)s);"""

            cursor.execute(
                query,
                {
                    "sentence_table": AsIs(f"{self.table_name}_sentence"),
                    "language": language_code,
                    "practice_words": practice_words,
                    "known_words": known_words,
                    "limit": article_display_count,
                    "start_date": start_date,
                    "end_date": end_date,
                },
            )
            print(query, f"{self.table_name}_sentence")
            print(
                {
                    "sentence_table": AsIs(f"{self.table_name}_sentence"),
                    "language": language_code,
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
            print("r", r[1], r[2])
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

    def format_source_entries(
        self, articles, language_code, practice_words, known_words, guy
    ):
        formatted_articles = []
        lemmas_to_find = set()

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
                                "is_name": sentence.parsed_pos[index] == "noun_prop"
                                or sentence.parsed_lemma[index] == "punc",
                            }
                        )
                except:
                    article_lines.append(self.generate_bad_line())

                if sentence.id in self.sentence_ids:
                    translation = str(self.sentence_ratios[str(sentence.id)]) + str(
                        sentence.translation
                    )
                    if len(sentences) > 1:
                        article_lines.append(self.generate_empty_line())
                        article_lines.append(self.generate_empty_line())
                        article_lines.append(self.generate_empty_line())
                        article_lines.append(article_line_words)
                        article_lines.append(self.generate_empty_line())
                        article_lines.append(self.generate_empty_line())
                        article_lines.append(self.generate_empty_line())
                    else:
                        article_lines.append(article_line_words)
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
                    "extra_text": None,
                    "translation": translation,
                    # + " // "
                    # + "\n".join([sentence.translation for sentence in sentences]),
                    "tag_level_1": article.title,
                    "tag_level_2": [None],
                    "article_lines": article_lines,
                }
            )

        formatted_lemmas = self.get_lemmas(
            lemmas_to_find, language_code, practice_words, known_words, guy
        )

        yourdata = {"articles": formatted_articles, "lemmas": formatted_lemmas}

        return yourdata

    def custom_sort_order(self, result_rows):
        return result_rows

    # TODO: consider commmon code with UserWordsViewSet
    def get_lemmas(
        self, all_article_lemmas, language_code, practice_words, known_words, guy
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
            .filter(language=language_code, text__in=all_article_lemmas)
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

            rank_column = f"rank_{self.source_name}"
            formatted_lemmas.append(
                {
                    "id": lemma.text,
                    "text": lemma.text,
                    "translation": lemma.translation,
                    "root": lemma.root,
                    "language": lemma.language,
                    "count": lemma.count,
                    "rank": getattr(lemma, rank_column),
                    "familiarity_label": familiarity_label,
                    "isKnown": isKnown,
                    "isPractice": isPractice,
                }
            )

        return formatted_lemmas

    def get_known_words(self, user, language_code):
        wordrating_queryset = WordRating.objects.filter(user=user)
        known_words = (
            Word.objects.prefetch_related(
                Prefetch(
                    "word_ratings",
                    to_attr="word_ratings_list",
                    queryset=wordrating_queryset,
                )
            )
            .filter(language=language_code, word_ratings__rating__gt=0)
            .order_by("rank")
            .all()
        )
        return known_words

    def post(self, request):
        guy = User.objects.get(username="guy")

        body_data = json.loads(request.body)

        language_code = body_data.get("language", None)

        start_date = body_data.get("start_date", None)
        end_date = body_data.get("end_date", None)
        if not start_date:
            start_date = "01/01/2020"
        if not end_date:
            end_date = "01/01/3000"

        if not language_code:
            return Response(
                {"success": False, "error": "language is required"}, status=400
            )
        if language_code not in supported_language_codes:
            return Response(
                {
                    "success": False,
                    "error": f"language {language_code} is not supported",
                },
                status=400,
            )

        practice_words = body_data.get("practice_words", None)
        known_words = self.get_known_words(guy, language_code)
        known_words = [w.text for w in known_words]

        articles = self.get_source_entries(
            language_code, practice_words, known_words, 100, start_date, end_date
        )
        output = self.format_source_entries(
            articles, language_code, practice_words, known_words, guy
        )

        # results = ArticleAndWordSerializer(output, many=False).data

        return Response(output, status=200)


class WikipediaWithWordsView(SourceWithSentncesAndWordsView):
    source_name = "wikipedia"
    table_name = "articles_wikipedia"
    source_model = Wikipedia
    sentence_model = Wikipedia_sentence


class SubtitlesWithWordsView(SourceWithSentncesAndWordsView):
    source_name = "subtitle"
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
    source_name = "lyric"
    table_name = "articles_lyric"
    source_model = Lyric
    sentence_model = Lyric_sentence


class RssWithWordsView(SourceWithSentncesAndWordsView):
    table_name = "articles_rss"
    source_name = "rss"
    source_model = Rss
    sentence_model = Rss_sentence
    table_query = "(select articles_rss_sentence.*, articles_rss.published_datetime from articles_rss_sentence left join articles_rss  on articles_rss_sentence.source_id = articles_rss.id where published_datetime >= %(start_date)s and published_datetime <= %(end_date)s) joined_tables"
