from articles.models import Wikipedia, Wikipedia_sentence
from pprint import pprint
from django.conf import settings
from .helpers import check_language_supported
import pandas as pd
import numpy as np


def run(*args):
    # input(
    #     "Make sure to run the import lyrics script first, since it deletes all the existing lyrics. Press enter to continue..."
    # )

    songs_df = read_song_lyrics()
    parse_songs(songs_df)


def read_song_lyrics():
    print("Load habibi dataset...")
    songs_df = pd.read_csv(
        "/Users/guy/guy/project/nll/datasets/habibi/arabicLyrics.csv"
    )
    songs_df = songs_df.replace(np.nan, None).replace("\\N", None)

    return songs_df


def parse_songs(songs_df):
    for song_id, songLines in songs_df.groupby("songID"):
        print(f"Insert song {song_id}")
        first_row = songLines.iloc[0]
        lyric_id = Wikipedia.objects.create(
            language="ar",
            song_title=first_row["SongTitle"],
            artist=first_row["Singer"],
            singer_nationality=first_row["SingerNationality"],
            dialect=first_row["SongDialect"],
            website_id=song_id,
            source_name="habibi",
        )

        sentences = songLines.sort_values("LyricsOrder")["Lyrics"].tolist()
        for sentence_order, sentence in enumerate(sentences):
            Wikipedia_sentence.objects.create(
                source=lyric_id,
                sentence_order=sentence_order,
                text=sentence,
            )
