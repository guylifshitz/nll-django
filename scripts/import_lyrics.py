from articles.models import Lyric, Lyric_sentence
from pprint import pprint
from django.conf import settings
from .helpers import check_language_supported
import pandas as pd


def run(*args):
    if len(args) != 1:
        raise Exception("1 arguments expected")
    language = args[0]
    check_language_supported(language)

    input(
        "[DELETE: Lyric] This script will DELETE all lyrics and lyric sentences in the database. [Press Enter to continue]"
    )
    Lyric.objects.filter(language=language).delete()
    Lyric_sentence.objects.filter(language=language).delete()

    songs_df = read_song_lyrics(language)
    parse_songs(songs_df, language)


def read_song_lyrics(language):
    print("Load dataset...")
    songs_df = pd.read_csv(
        f"/Users/guy/guy/project/nll/datasets/songs/song_lyrics_{language}.csv"
    )
    songs_df = songs_df[songs_df["language"] == language]
    songs_df.to_csv(
        f"/Users/guy/guy/project/nll/datasets/songs/song_lyrics_{language}.csv"
    )

    return songs_df


def parse_songs(songs_df, language):
    for idx, song_row in songs_df.iterrows():
        print(f"Insert song {idx}-{song_row['title']}...")
        lyric_id = Lyric.objects.create(
            language=language,
            song_title=song_row["title"],
            artist=song_row["artist"],
            year=song_row["year"],
            genre=song_row["tag"],
            views=song_row["views"],
            website_id=song_row["id"],
            source_name="song_lyrics",
        )

        sentences = song_row["lyrics"].split("\n")
        for sentence_order, sentence in enumerate(sentences):
            Lyric_sentence.objects.create(
                source=lyric_id,
                sentence_order=sentence_order,
                text=sentence,
            )
