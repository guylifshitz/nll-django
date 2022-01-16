from django.shortcuts import render
from articles.models import Rss_feeds
from words.models import Words
from mongoengine import Q


def word(request, word_id):
    word = Words.objects.filter(_id=word_id).first()
    word_to_show = {
        "word": word["_id"],
        "translation": word["translation"],
        "frequency": word["count"],
        "language": word["language"],
    }
    return render(request, "word.html", {"word": word_to_show})


def flashcards(request):
    lower_freq_cutoff = int(request.GET.get("lower_freq_cutoff", 10))
    upper_freq_cutoff = int(request.GET.get("upper_freq_cutoff", 20))

    # words = Words.objects(Q(count__gte=lower_freq_cutoff) & Q(count__lte=upper_freq_cutoff))
    words = Words.objects.all()

    # print(f"There are {len(words)} words in this set.")
    words_to_show = []
    for word in words:
        word_to_show = {
            "word": word["_id"],
            "translation": word["translation"],
            "frequency": word["count"],
            "language": word["language"],
        }
        words_to_show.append(word_to_show)

    words_to_show = sorted(words_to_show, key=lambda d: d["frequency"], reverse=True)

    import pandas as pd
    pd.DataFrame(words_to_show).to_csv("words.csv")

    words_to_show = words_to_show[lower_freq_cutoff:upper_freq_cutoff]
    print(f"Last word frequency: {words_to_show[-1]['frequency']}")
    return render(request, "flashcards.html", {"words": words_to_show})
