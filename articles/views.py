from django.http import HttpResponse
from django.shortcuts import render
from articles.models import Rss_feeds
from words.models import Words
import datetime
import traceback
import mlconjug3

language_speech_mapping = {"arabic": "ar-SA", "hebrew": "he"}

def conjugate_verbs():
    if article["title_parsed_POSTAG"][index] == "VB":
        verb = lemma["translation"]
        if verb.startswith("to "):
            verb = verb.replace("to ", "")
        feats = article["title_parsed_FEATS"][index]

        number = "s"
        if "num=S" in feats:
            number = "s"
        elif "num=P" in feats:
            number = "p"

        person = "3"
        if "per=1" in feats:
            person = "1"     
        elif "per=2" in feats:
            person = "2"     
        elif "per=3" in feats:
            person = "3"

        tense = "past"
        if "tense=FUTURE" in feats:
            tense = "future"
        elif "tense=PAST" in feats:
            tense = "past"
        elif "tense=IMPERATIVE" in feats:
            tense = "imperative"
        elif "tense=BEINONI" in feats:
            tense = "imperative"
        else:
            tense = "imperative"

        cong = conjugator.conjugate(verb)
        if not cong.predicted:
            
            if tense == "future":
                conjugated = "will " + verb
            if tense == "past":
                conjugated = cong.conjug_info["indicative"]["indicative past tense"][f"{person}{number}"]
            else:
                conjugated = verb
            print()
            print()
            print(lemma["translation"])
            print(feats)
            print(conjugated)


def index(request):
    conjugator = mlconjug3.Conjugator(language='en')

    language = request.GET.get("language", "arabic")
    word_count_cutoff = int(request.GET.get("word_count_cutoff", 10))
    start_date_cutoff = request.GET.get("start_date", "01-01-1900")
    start_date_cutoff = datetime.datetime.strptime(start_date_cutoff, "%d-%m-%Y")
    article_display_count = int(request.GET.get("count", 100))

    articles = Rss_feeds.objects.filter(
        language=language, published_datetime__gte=start_date_cutoff, title_translation__ne=None
    )
    print(f"Got {len(articles)} articles")

    words = Words.objects.filter(language=language).order_by("-count")
    words_dict = {}
    for word in words:
        words_dict[word["_id"]] = word
    print(f"Got {len(words)} words")

    articles_to_render = []
    for article in articles:
        try:
            article_to_render = {}
            article_to_render["title"] = article["title"]
            article_to_render["title_parsed_clean"] = article["title_parsed_clean"]
            article_to_render["source"] = article["source"]
            article_to_render["feed_name"] = article["feed_name"]
            article_to_render["published_datetime"] = article["published_datetime"]
            article_to_render["title_translation"] = article["title_translation"]
            article_to_render["link"] = article["link"]

            words = []
            known_words_count = 0
            for index, lemma in enumerate(article["title_parsed_lemma"]):
                word_index = list(words_dict.keys()).index(lemma)
                lemma = words_dict[lemma]

                conjugate_verbs()

                word_translation = lemma["translation"].lower()

                word_foreign = "foreign"
                mix_word = article["title_parsed_clean"][index]
                mix_word_translation = lemma["translation"].lower()
                mix_word_lemma = lemma["_id"]
                mix_word_segmented = article["title_parsed_segmented"][index]
                word_prefixes = article["title_parsed_prefixes"][index]

                if word_prefixes:
                    word_prefixes = "".join(word_prefixes) + "+"
                else:
                    word_prefixes = ""

                if lemma["_id"] != mix_word_segmented:
                    mix_word_segmented = mix_word_segmented + f" ({lemma['_id']})"

                if word_index >= word_count_cutoff:
                    word_foreign = "native"
                    mix_word = word_prefixes + "" + lemma["translation"].lower()
                    mix_word_translation = article["title_parsed_clean"][index]

                    mix_word_tooltip_1 = mix_word_translation
                    mix_word_tooltip_2 = mix_word_segmented

                else:
                    mix_word_tooltip_1 = mix_word_segmented
                    mix_word_tooltip_2 = mix_word_translation
                    known_words_count = known_words_count + 1

                # DEBUG
                mix_word_tooltip_1 = mix_word_tooltip_1 + f" ({word_index})"

                word_components = {
                    "word": article["title_parsed_clean"][index],
                    "lemma": lemma["_id"],
                    "mix_word": mix_word,
                    "mix_word_translation": mix_word_translation,
                    "mix_word_lemma": mix_word_lemma,
                    "mix_word_tooltip_1": mix_word_tooltip_1,
                    "mix_word_tooltip_2": mix_word_tooltip_2,
                    "mix_segmented": mix_word_segmented,
                    "translation": word_translation,
                    "word_foreign": word_foreign,
                }
                words.append(word_components)

            article_to_render["words"] = words
            article_to_render["known_words_count"] = known_words_count
            article_to_render["known_words_ratio"] = known_words_count / max(len(words), 1)

            articles_to_render.append(article_to_render)
        except Exception as e:
            traceback.print_exc()

    articles_to_render = sorted(
        articles_to_render, key=lambda d: d["published_datetime"], reverse=True
    )
    articles_to_render = sorted(
        articles_to_render, key=lambda d: d["known_words_ratio"], reverse=True
    )
    articles_to_render = articles_to_render[0:article_display_count]
    speech_voice = language_speech_mapping[language]
    return render(
        request, "articles.html", {"articles": articles_to_render, "speech_voice": speech_voice}
    )
