from articles.models import Subtitle, Subtitle_sentence
from pprint import pprint
from django.conf import settings
from .helpers import check_language_supported
import pandas as pd
import numpy as np

data_folder = "/Users/guy/guy/project/nll/datasets/opensubtitles"
rows_to_keep = 1000000


def run(*args):
    if len(args) != 1:
        raise Exception("1 arguments expected")
    language = args[0]
    check_language_supported(language)

    input(
        f"[DELETE: Subtitle] This script will DELETE all Subtitles and Subtitle sentences in the database in language:{language}. [Press Enter to continue]"
    )
    Subtitle.objects.filter(language=language).delete()
    Subtitle_sentence.objects.filter(language=language).delete()

    print("Loading Subtitle data...")
    sentence_ids_df, imdb_titles = load_data(language)
    print("Parsing Subtitle data...")
    parse_subtitles(sentence_ids_df, imdb_titles, None, language)


def load_data(language):
    if language == "he":
        language_folder = "en-he"
    else:
        language_folder = "ar-en"

    print("loading english sentences")
    english_sentences = load_language_sentences(
        f"{data_folder}/{language_folder}/txt/OpenSubtitles.{language_folder}.en"
    ).add_suffix("_english")
    print("loading foreign sentences")
    foreign_sentences = load_language_sentences(
        f"{data_folder}/{language_folder}/txt/OpenSubtitles.{language_folder}.{language}"
    ).add_suffix("_foreign")
    print("loading ids")
    sentence_ids_df = load_sentence_ids(
        f"{data_folder}/{language_folder}/txt/OpenSubtitles.{language_folder}.ids"
    )
    print("merging sentence dataframes")
    sentence_ids_df = pd.merge(
        sentence_ids_df,
        english_sentences,
        left_index=True,
        right_index=True,
    )
    sentence_ids_df = pd.merge(
        sentence_ids_df,
        foreign_sentences,
        left_index=True,
        right_index=True,
    )

    print("loading imdb")
    imdb_titles, imdb_people = load_imdb(
        f"{data_folder}/imdb",
        sentence_ids_df["title_imdb_id_clean"].unique(),
    )

    return sentence_ids_df, imdb_titles


def load_language_sentences(file_path):
    with open(file_path) as sentences_file:
        contents = sentences_file.read()
    sentences = contents.split("\n")
    sentences = pd.DataFrame(sentences, columns=["sentence"]).tail(rows_to_keep)
    return sentences


def load_sentence_ids(file_path):
    sentence_ids_df = pd.read_csv(
        file_path,
        sep="\t",
        names=["id_lang1", "id_lang2", "text_lang1", "text_lang2"],
    ).tail(rows_to_keep)

    print("splitting sentence_id id columns")

    id_components = sentence_ids_df["id_lang1"].str.split("/")

    language_1 = id_components.iloc[0][0]
    language_2 = sentence_ids_df["id_lang2"].iloc[0].split("/")[0]

    if language_1 == "en":
        language_1 = "english"
        language_2 = "foreign"
    else:
        language_1 = "foreign"
        language_2 = "english"

    sentence_ids_df.rename(
        columns={
            "text_lang1": f"text_lang_{language_1}",
            "text_lang2": f"text_lang_{language_2}",
        }
    )

    sentence_ids_df["title_year"] = id_components.str[1]
    sentence_ids_df["title_imdb_id"] = id_components.str[2]
    sentence_ids_df["thing"] = id_components.str[3]
    sentence_ids_df["title_imdb_id_clean"] = "tt" + sentence_ids_df[
        "title_imdb_id"
    ].str.zfill(7)

    return sentence_ids_df


def load_imdb(imdb_path, imdb_ids):
    # LOAD DATA
    print("loading imdb data")
    imdb_title_basics = pd.read_csv(f"{imdb_path}/title.basics.tsv", sep="\t")
    imdb_title_basics_full = pd.read_csv(f"{imdb_path}/title.basics.tsv", sep="\t")
    imdb_title_ratings = pd.read_csv(f"{imdb_path}/title.ratings.tsv", sep="\t")
    # imdb_title_akas = pd.read_csv(f"{imdb_path}/title.akas.tsv", sep="\t")
    # imdb_title_crew = pd.read_csv(f"{imdb_path}/title.crew.tsv", sep="\t")
    imdb_title_episodes = pd.read_csv(f"{imdb_path}/title.episode.tsv", sep="\t")
    # imdb_title_principals = pd.read_csv(f"{imdb_path}/title.principals.tsv", sep="\t")
    # imdb_name_basics = pd.read_csv(f"{imdb_path}/name.basics.tsv", sep="\t")

    # FILTER DATA
    imdb_title_basics = imdb_title_basics[imdb_title_basics["tconst"].isin(imdb_ids)]
    imdb_title_episodes = imdb_title_episodes[
        (imdb_title_episodes["tconst"].isin(imdb_ids))
        | (imdb_title_episodes["parentTconst"].isin(imdb_ids))
    ]
    imdb_title_ratings = imdb_title_ratings[imdb_title_ratings["tconst"].isin(imdb_ids)]

    # MERGE DATA: people
    print("merging imdb people")
    # imdb_people = pd.merge(
    #     imdb_title_principals,
    #     imdb_name_basics,
    #     on="nconst",
    #     how="right",
    #     suffixes=("_principals", "_namebasics"),
    # )
    imdb_people = None

    print("merging imdb titles")
    imdb_titles = pd.merge(
        imdb_title_basics, imdb_title_ratings, on="tconst", how="left"
    )
    imdb_titles = pd.merge(imdb_titles, imdb_title_episodes, on="tconst", how="left")
    imdb_titles = pd.merge(
        imdb_titles,
        imdb_title_basics_full[
            ["tconst", "primaryTitle", "originalTitle", "startYear", "endYear"]
        ],
        left_on="parentTconst",
        right_on="tconst",
        suffixes=("", "_series"),
        how="left",
    )
    imdb_titles = imdb_titles.replace(np.nan, None).replace("\\N", None)
    return imdb_titles, imdb_people


def parse_subtitles(sentence_ids_df, imdb_titles, imdb_people, language):
    for imdb_group_id, group in sentence_ids_df.groupby("title_imdb_id_clean"):
        group_size = 20
        group_chunks = [
            group[i : i + group_size] for i in range(0, group.shape[0], group_size)
        ]

        imdb_row = imdb_titles[imdb_titles["tconst"] == imdb_group_id]
        if imdb_row.shape[0] == 0:
            continue

        for chunk_count, group_chunk in enumerate(group_chunks):
            imdb_row.loc[:, "newTitle"] = (
                imdb_row["originalTitle"].iloc[0] + f" [{chunk_count}]"
            )

            source_id = insert_subtitle(imdb_row)
            english_sentences = group_chunk["sentence_english"].tolist()
            foreign_sentences = group_chunk["sentence_foreign"].tolist()

            for sentence_order, (foreign_sentence, english_sentence) in enumerate(
                zip(foreign_sentences, english_sentences)
            ):
                Subtitle_sentence.objects.create(
                    source=source_id,
                    language=language,
                    sentence_order=sentence_order,
                    text=foreign_sentence,
                    translation=english_sentence,
                )


def insert_subtitle(title_row):
    source_id = Subtitle.objects.create(
        title_original=get_title(title_row),
        title_foreign=None,
        title_english=None,
        year=title_row["startYear"].iloc[0],
        series_year_start=title_row["startYear_series"].iloc[0],
        series_year_end=title_row["endYear_series"].iloc[0],
        season_number=title_row["seasonNumber"].iloc[0],
        episode_number=title_row["episodeNumber"].iloc[0],
        runtime_minutes=title_row["runtimeMinutes"].iloc[0],
        type=title_row["titleType"].iloc[0],
        genres=title_row["genres"].iloc[0].split(","),
        people=None,
        number_ratings=int(title_row["numVotes"].iloc[0]),
        imdb_id=title_row["tconst"].iloc[0],
    )
    return source_id


def get_title(title_row):
    title = title_row["newTitle"].iloc[0]
    series_title = title_row["originalTitle_series"].iloc[0]
    if series_title:
        title = f"{series_title}: {title}"
    return title
