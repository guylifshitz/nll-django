import datetime
import requests
import pandas as pd
import json


local_url = "http://localhost:8001"
remote_url = "http://localhost:8002"


def run():
    df_local = download_words_from_api(local_url, "he")
    df_remote = download_words_from_api(remote_url, "he")

    df_local.to_csv(
        f"../BACKUP/word_ratings_local_{datetime.datetime.now().isoformat()}.csv"
    )
    df_remote.to_csv(
        f"../BACKUP/word_ratings_remote_{datetime.datetime.now().isoformat()}.csv"
    )
    df_merged = merge_word_ratings(df_local, df_remote)

    df_merged = df_merged[
        df_merged["familiarity_label_local"] != df_merged["familiarity_label_remote"]
    ]


def download_words_from_api(base_url, language_code):
    url = f"{base_url}/api/word_ratings/"
    response = requests.get(
        url,
        headers={"content-type": "application/json"},
        data=json.dumps({"language": language_code}),
    )
    data = response.json()["word_ratings"]
    df = pd.DataFrame(
        data,
    )  # [["id", "text", "language", "familiarity_label"]]
    df["updated_at"] = pd.to_datetime(df["updated_at"], infer_datetime_format=True)
    df["created_at"] = pd.to_datetime(df["created_at"], infer_datetime_format=True)
    df = df[df["familiarity_label"] != 0]
    return df


def merge_word_ratings(df_local, df_remote):
    df_local = df_local.set_index("text")
    df_remote = df_remote.set_index("text")
    df_merged = pd.merge(df_local, df_remote, on="text", suffixes=("_local", "_remote"))
    return df_merged


def update_word_ratings(df_merged, base_url, language_code):
    for index, row in df_merged.iterrows():
        print(index)
        text = index
        print(row)
        if row["updated_at_local"] > row["updated_at_remote"]:
            print(f"Update remote: {text} to {row['familiarity_label_local']}")
            update_word_rating(text, row["familiarity_label_local"], remote_url, "he")
        elif row["updated_at_local"] < row["updated_at_remote"]:
            print(f"Update local: {text} to {row['familiarity_label_local']}")
            update_word_rating(text, row["familiarity_label_local"], local_url, "he")


def update_word_rating(word_text, rating, base_url, language_code):
    url = f"{base_url}/api/word_ratings/"
    response = requests.put(
        url,
        headers={"content-type": "application/json"},
        data=json.dumps(
            {"word_text": word_text, "rating": rating, "language": language_code}
        ),
    )
    return response


run()
