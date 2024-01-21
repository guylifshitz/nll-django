from bs4 import BeautifulSoup
from articles.models import Wikipedia, Wikipedia_sentence
from pprint import pprint
from django.conf import settings
from .helpers import check_language_supported
import pandas as pd
import mwparserfromhell
import mwxml
import re
import nltk

data_folder = "/Users/guy/guy/project/nll/datasets/wikipedia"


def run(*args):
    print(args)
    if len(args) != 1:
        raise Exception("1 arguments expected")
    language = args[0]
    check_language_supported(language)

    # input(
    #     "[DELETE: Lyric] This script will DELETE all lyrics and lyric sentences in the database. [Press Enter to continue]"
    # )
    Wikipedia.objects.filter(language=language).delete()
    Wikipedia_sentence.objects.filter(language=language).delete()

    print("Loading Wikipedia data...")
    top_page_names = get_page_names_from_wikirank(language)
    wiki_pages = load_wikipedia(top_page_names, language)

    print("Formatting Wikipedia data...")
    wiki_pages = get_formated_articles(wiki_pages)

    print("Processing Wikipedia data...")
    process_article(wiki_pages, language)


# Contains 2000 articles from: https://www.wikirank.net/
def get_page_names_from_wikirank(language: str):
    ranking_data = {}
    for i in range(1, 20):
        with open(f"{data_folder}/rankings/{language}/{language}_{i}.html", "r") as f:
            contents = f.read()
            soup = BeautifulSoup(contents, "lxml")
            rankings = soup.find_all(class_="rnks")
            for ranking in rankings:
                columns = ranking.find_all("td")
                page_name = columns[1].text
                ranking = int(columns[0].text)
                ranking_data[page_name] = ranking
    return ranking_data.keys()


# Contains 500 articles from https://pageviews.wmcloud.org/topviews/
def get_page_names_from_topviews(language: str):
    top_views_df = pd.read_csv(f"{data_folder}/stats/topviews-2022-{language}.csv")
    return top_views_df["Page"].unique()


def load_wikipedia(top_page_names, language):
    mwxml_dump = mwxml.Dump.from_file(
        open(
            f"{data_folder}/{language}wiki-20240101-pages-articles-multistream.xml",
            "rb",
        )
    )
    top_pages = []
    for page in mwxml_dump:
        if page.title in top_page_names:
            revisions = []
            for rev in page:
                revisions.append(rev)

            top_pages.append({"page": page, "revisions": revisions})
    return top_pages


def get_formated_articles(wiki_pages):
    formated_pages = []
    for page in wiki_pages:
        paresed_wikicode = mwparserfromhell.parse(
            page["revisions"][0].text, skip_style_tags=True
        )
        clean_wikicode = remove_refs(paresed_wikicode)
        first_section_text = clean_wikicode.strip_code()
        first_section_paragraphs = list(
            filter(lambda x: x != "", first_section_text.split("\n"))
        )
        page_data = {
            "title": page["page"].title,
            "paragraphs": first_section_paragraphs,
        }
        formated_pages.append(page_data)

    return formated_pages


def remove_refs(parsed_wikicode):
    bad_nodes = []

    for node in parsed_wikicode.nodes:
        if type(node) == mwparserfromhell.nodes.tag.Tag:
            if node.tag.matches("ref"):
                bad_nodes.append(node)

    for bad_node in bad_nodes:
        parsed_wikicode.remove(bad_node)

    return parsed_wikicode


def process_article(wiki_pages, language):
    for page in wiki_pages:
        for paragraph_order, paragraph in enumerate(page["paragraphs"]):
            if len(paragraph) < 100:
                continue

            page_name = f"{page['title']} - {paragraph_order}"
            source_id = Wikipedia.objects.create(
                language=language,
                page_name=page_name,
            )

            sentences = split_sentences(paragraph)
            for sentence_order, sentence in enumerate(sentences):
                Wikipedia_sentence.objects.create(
                    source=source_id,
                    language=language,
                    sentence_order=sentence_order,
                    text=sentence,
                )


def split_sentences(paragraph):
    text = re.sub("؟", "?", paragraph)
    sentences = []
    for sen in nltk.sent_tokenize(text):
        sentences.append(sen)
    return sentences
