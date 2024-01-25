import pandas as pd
import json
import requests
from pathlib import Path
from datetime import datetime


def run(*args):
    print("Load rss feeds list")
    feeds = get_feed_links()

    print("Download feeds")
    download_feeds(feeds, "rss_feeds")


def get_feed_links() -> pd.DataFrame:
    rss_list = pd.read_json("config/rss_feeds.json")

    merged = []
    for _, source in rss_list.iterrows():
        feeds = pd.DataFrame(source["feeds"])
        feeds = feeds.rename({"name": "feed_name", "url": "feed_url"}, axis=1)
        feeds["language"] = source["language"]
        feeds["source_site"] = source["site"]
        merged.append(feeds)
    return pd.concat(merged)


def download_feeds(feeds: pd.DataFrame, data_folder: str):
    download_time = datetime.utcnow().strftime("%Y-%m-%d--%H:%M:%S")

    failed_downloads = []

    for source_site, site_group in feeds.groupby("source_site"):
        for _, feed in site_group.iterrows():
            feed_url = feed["feed_url"]
            source_site = feed["source_site"]
            feed_name = feed["feed_name"]

            response = requests.get(feed_url)

            print(f"{response.status_code} : {source_site} : {feed_name}")

            if response.status_code != 200:
                # TODO log errors here
                failed_downloads.append(
                    {
                        "source_site": source_site,
                        "feed_name": feed_name,
                        "feed_url": feed_url,
                        "status_code": response.status_code,
                    }
                )
                continue

            dl_path = Path(
                f"{data_folder}/{source_site}/{feed_name}/{download_time}.xml"
            )
            dl_path.parent.mkdir(parents=True, exist_ok=True)

            with open(dl_path, "wb") as f:
                f.write(response.content)

    output_failed_downloads(failed_downloads, data_folder, download_time)


def output_failed_downloads(
    failed_downloads: list[dict], download_folder: str, download_time: str
):
    if len(failed_downloads) == 0:
        return

    Path(f"{download_folder}/logs").mkdir(parents=True, exist_ok=True)
    with open(
        f"{download_folder}/logs/rss_download_errors_{download_time}.json", "w"
    ) as f:
        print(f"Failed downloads: {failed_downloads}")
        json.dump(failed_downloads, f, indent=2)
