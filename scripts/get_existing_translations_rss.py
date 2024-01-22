from django.db.models import Func, F, Count
import psycopg2
from articles.models import Rss, Rss_sentence, Wikipedia, Wikipedia_sentence, Sentence
from words.models import Word

from pprint import pprint
from django.conf import settings
from .helpers import (
    language_name_to_code,
)
import pandas as pd
import scripts.language_parsers.arabic.parser_camel as arabic_parser
import scripts.language_parsers.hebrew.parser2 as hebrew_parser


def run(*args):
    print("Loading old articles sql.")
    existing_articles_df = load_existing_articles()
    print(existing_articles_df)
    print("Update new articles")
    parse_articles(existing_articles_df)


def load_existing_articles():
    connection = psycopg2.connect(
        "dbname='nll_production_copy_2024_01_22' user='guy' host='localhost'"
    )

    articles_df = pd.read_sql(
        "SELECT title, link, title_translation, language FROM articles_rss_feed",
        connection,
    )
    return articles_df


def parse_articles(existing_articles_df):
    for index, article_row in existing_articles_df.iterrows():
        link = article_row["link"]
        title_text = article_row["title"]
        title_translation = article_row["title_translation"]

        language = article_row["language"]
        if language not in language_name_to_code:
            print(f"Language not found: {language}")
            continue

        language_code = language_name_to_code[language]

        articles = Rss.objects.filter(article_link=link, language=language_code)
        if len(articles) == 0:
            print(f"Article not found: {link} ({language})")
            continue
        if len(articles) > 1:
            raise f"More than one article found: {link} ({language}), found {len(articles)} matches"
        print(f"Update {title_text}:{title_translation} ({language}) ")
        article_sentence = Rss_sentence.objects.filter(source=articles.first()).first()
        article_sentence.translation = title_translation
        article_sentence.save()
