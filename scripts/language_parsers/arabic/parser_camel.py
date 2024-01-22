import json
from camel_tools.tokenizers.word import simple_word_tokenize
from camel_tools.disambig.mle import MLEDisambiguator
from camel_tools.ner import NERecognizer

import pyarabic.araby as araby

from articles.models import Sentence

use_NER = False


def parse_sentences(sentences: list[Sentence]):
    print("Load models...")
    mle = MLEDisambiguator.pretrained()
    if use_NER:
        ner = NERecognizer.pretrained()

    for idx, sentence in enumerate(sentences):
        try:
            print("-------")
            print(f"Sentence#{idx}: {sentence.text} - {sentence.id}")

            parsed_title = simple_word_tokenize(sentence.text)
            if use_NER:
                ner_labels = ner.predict_sentence(parsed_title)
            else:
                ner_labels = ["O" for _ in range(len(parsed_title))]

            disambig = mle.disambiguate(parsed_title)

            # print(json.dumps(disambig, indent=2, ensure_ascii=False))
            print(disambig)

            if use_NER:
                print(ner_labels)
            missing_analysis = any(True for d in disambig if not d.analyses)

            if missing_analysis:
                pos_tags = [None for _ in range(len(parsed_title))]
                lemmas = [None for _ in range(len(parsed_title))]
                segemented = [None for _ in range(len(parsed_title))]
            else:
                # pos_tags = [handle_disambig(d, 'pos') for d in disambig]
                pos_tags = [handle_disambig(d, "pos") for d in disambig]
                lemmas = [handle_disambig(d, "lex") for d in disambig]
                roots = [handle_disambig(d, "root") for d in disambig]
                lemma_gloss = [handle_disambig(d, "stemgloss") for d in disambig]
                flexion_gloss = [handle_disambig(d, "gloss") for d in disambig]
                segemented = [handle_disambig(d, "d3seg") for d in disambig]
                form_gen = [handle_disambig(d, "form_gen") for d in disambig]
                form_num = [handle_disambig(d, "form_num") for d in disambig]

            lemmas = replace_punctuation(lemmas, pos_tags)

            feats = handle_feats(form_gen, form_num, ner_labels)
            prefixes = [None for _ in range(len(parsed_title))]

            if (
                len(parsed_title) != len(pos_tags)
                or len(parsed_title) != len(lemmas)
                or len(parsed_title) != len(prefixes)
                or len(parsed_title) != len(segemented)
                or len(parsed_title) != len(feats)
                or len(parsed_title) != len(roots)
                or len(parsed_title) != len(lemma_gloss)
                or len(parsed_title) != len(flexion_gloss)
            ):
                print("Problem with parsing title. Skipping...")
                continue

            assert len(parsed_title) == len(pos_tags)
            assert len(parsed_title) == len(lemmas)
            assert len(parsed_title) == len(prefixes)
            assert len(parsed_title) == len(segemented)
            assert len(parsed_title) == len(feats)
            assert len(parsed_title) == len(roots)
            assert len(parsed_title) == len(lemma_gloss)
            assert len(parsed_title) == len(flexion_gloss)

            sentence.parsed_clean = parsed_title
            sentence.parsed_lemma = lemmas
            sentence.parsed_segmented = segemented
            sentence.parsed_prefixes = prefixes
            sentence.parsed_pos = pos_tags
            sentence.parsed_features = feats
            sentence.parsed_roots = roots
            sentence.parsed_gloss_lemma = lemma_gloss
            sentence.parsed_gloss_flexion = flexion_gloss
        except:
            print("Skipping, bad data")


def replace_punctuation(lemmas, pos_tags):
    for i, (lemma, pos) in enumerate(zip(lemmas, pos_tags)):
        if pos == "punc":
            lemmas[i] = pos
    return lemmas


def get_all_keyvalues(word_disambig, key):
    analyses = word_disambig.analyses

    if len(analyses) != 1:
        import ipdb

        ipdb.set_trace()

    if len(analyses) == 0:
        return None
    values = [a.analysis[key] for a in analyses]
    return values


def handle_disambig(word_disambig, seg):
    analyses = word_disambig.analyses
    if len(analyses) == 0:
        return None
    value = analyses[0].analysis[seg]
    if value == "NOAN":
        return word_disambig.word
    return araby.strip_diacritics(value)


def handle_feats(form_gen, form_num, ner_labels):
    feats = []
    for fg, fn, ner in zip(form_gen, form_num, ner_labels):
        if ner != "O":
            if ner == "B-PER" or ner == "I-PER":
                feats.append("NAME: Person")
            elif ner == "B-LOC" or ner == "I-LOC":
                feats.append("NAME: Location")
            elif ner == "B-ORG" or ner == "I-ORG":
                feats.append("NAME: Organization")
            else:
                feats.append(ner)
        else:
            if fg == "na" or fg == "na":
                feats.append("")
            else:
                feats.append(fg + fn)

    return feats
