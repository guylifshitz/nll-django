import re
from articles.models import User_Document, User_Document_sentence
from pprint import pprint
from django.conf import settings
from .helpers import check_language_supported
import pandas as pd
import numpy as np
import nltk


def run(*args):
    doc_language = input("Document language:")
    doc_name = input("Document name:")
    user_id = input("User ID:")
    separate_by_period_or_newline = input("Separate by period(Y) or newline (N):")
    sepearate_by_period = False
    if separate_by_period_or_newline == "Y" or separate_by_period_or_newline == "y":
        sepearate_by_period = True
    doc_contents = open("scripts/user-input.txt", "r").read()
    parse_document(doc_language, doc_name, doc_contents, user_id, sepearate_by_period)


def parse_document(doc_language, doc_name, doc_contents, user_id, sepearate_by_period):

    doc_id = User_Document.objects.create(
        language=doc_language, document_name=doc_name, author_id=user_id
    )

    if sepearate_by_period:
        sentences = split_sentences(doc_contents)
    else:
        sentences = doc_contents.split("\n")

    for sentence_order, sentence in enumerate(sentences):
        print(sentence)
        User_Document_sentence.objects.create(
            source=doc_id,
            language=doc_language,
            sentence_order=sentence_order,
            text=sentence,
        )


def split_sentences(paragraph):
    text = re.sub("؟", "?", paragraph)
    sentences = []
    for sen in nltk.sent_tokenize(text):
        sentences.append(sen)
    return sentences
