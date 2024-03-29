from django.db.models import Func, F, Count
from articles.models import Sentence
from scripts.helpers import (
    check_language_supported,
    check_source_supported,
    get_source_model,
)
from words.models import Word, Flexion
import pandas as pd


def run(*args):
    if len(args) != 2:
        raise Exception("2 arguments expected")
    language = args[0]
    source_name = args[1]
    print("language", language)
    check_language_supported(language)
    check_source_supported(source_name)

    source_model, sentence_model = get_source_model(source_name)
    print("source_model", source_model)
    print("Get roots per lemma...")
    roots = get_roots_per_lemma(sentence_model, language)
    print("Get lemma_gloss per lemma...")
    lemma_glosses = get_lemma_gloss_per_lemma(sentence_model, language)
    print("Get flexion_gloss per lemma...")
    flexion_glosses = get_flexion_gloss_per_lemma(sentence_model, language)
    print("Save roots...")
    save_roots(roots, language)
    print("Save lemma glosses...")
    save_lemma_glosses(lemma_glosses, language)
    print("Save flexion glosses...")
    save_flexion_glosses(lemma_glosses, language)


def get_roots_per_lemma(sentence_model: Sentence, language: str):
    lemma_roots = (
        sentence_model.objects.filter(language=language)
        .annotate(
            parsed_lemma2=Func(F("parsed_lemma"), function="unnest"),
            parsed_roots2=Func(F("parsed_roots"), function="unnest"),
        )
        .values("parsed_lemma2", "parsed_roots2")
        .annotate(count=Count("parsed_lemma2"))
        .values_list("parsed_lemma2", "parsed_roots2")
    )
    return lemma_roots


def get_lemma_gloss_per_lemma(sentence_model: Sentence, language: str):
    lemma_glosses = (
        sentence_model.objects.filter(language=language)
        .annotate(
            parsed_lemma2=Func(F("parsed_lemma"), function="unnest"),
            parsed_gloss_lemma2=Func(F("parsed_gloss_lemma"), function="unnest"),
        )
        .values("parsed_lemma2", "parsed_gloss_lemma2")
        .annotate(count=Count("parsed_lemma2"))
        .values_list("parsed_lemma2", "parsed_gloss_lemma2")
    )
    return lemma_glosses


def get_flexion_gloss_per_lemma(sentence_model: Sentence, language: str):
    flexion_glosses = (
        sentence_model.objects.filter(language=language)
        .annotate(
            parsed_lemma2=Func(F("parsed_lemma"), function="unnest"),
            parsed_gloss_flexion2=Func(F("parsed_gloss_flexion"), function="unnest"),
        )
        .values("parsed_lemma2", "parsed_gloss_flexion2")
        .annotate(count=Count("parsed_lemma2"))
        .values_list("parsed_lemma2", "parsed_gloss_flexion2")
    )
    return flexion_glosses


def save_roots(lemma_roots, language):
    for lemma, root in lemma_roots:
        Word.objects.filter(language=language, text=lemma).update(root=root)


def save_lemma_glosses(lemma_glosses, language):
    lemma_gloss_df = pd.DataFrame(lemma_glosses, columns=["lemma", "gloss"])
    for lemma, gloss in lemma_gloss_df.groupby("lemma"):
        glosses = gloss["gloss"].tolist()
        glosses = [gloss.split(";") for gloss in glosses]
        glosses = [item for sublist in glosses for item in sublist]
        glosses = list(set(glosses))
        Word.objects.filter(language=language, text=lemma).update(
            parser_translations=glosses
        )


def save_flexion_glosses(flexion_glosses, language):
    flexion_gloss_df = pd.DataFrame(flexion_glosses, columns=["lemma", "gloss"])
    for lemma, gloss in flexion_gloss_df.groupby("lemma"):
        glosses = gloss["gloss"].tolist()
        glosses = [gloss.split(";") for gloss in glosses]
        glosses = [item for sublist in glosses for item in sublist]
        glosses = list(set(glosses))
        Flexion.objects.filter(language=language, text=lemma).update(
            parser_translations=glosses
        )
