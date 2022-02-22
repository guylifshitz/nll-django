import pandas as pd
import matplotlib
matplotlib.use("agg")
import matplotlib.pyplot as plt

from pathlib import Path

def count_article_words(articles, cutoff):

    words = []
    for article in articles:
        for word in article["words"]:
            if word["lemma_foreign_index"] < cutoff:
                words.append(word["lemma_foreign"])
    from collections import Counter

    print(Counter(words))

    # get per day
    articles_word_holder = []
    for article in articles:
        article_word_holder = {}
        article_word_holder["published_datetime"] = article["published_datetime"]
        for word in article["words"]:
            if word["lemma_foreign_index"] < cutoff:
                article_word_holder[word["lemma_foreign"]] = 1
        articles_word_holder.append(article_word_holder)

    articles_words = pd.DataFrame(articles_word_holder)
    articles_words = articles_words.groupby("published_datetime").count()
    # articles_words.sort_values("published_datetime").to_csv("debug/per_date_word_counts.csv")

    for word in articles_words.columns:
        plt.clf()
        plot = articles_words[word].plot()
        fig = plot.get_figure()
        plt.title(word[::-1])

        image_path = Path(f"DEBUG/frequency_charts/{word}.png")
        image_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(image_path)
