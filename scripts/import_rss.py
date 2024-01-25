import datetime
from pathlib import Path
from time import mktime
import traceback

import dateutil
from articles.models import Rss, Rss_sentence
from pprint import pprint
from .helpers import check_language_supported, language_name_to_code
import pandas as pd
import feedparser
from django.utils import timezone
from django.db.models import Func, F, Count
import time

rss_data_path = "/Users/guy/guy/project/nll/git-django-parser/rss_feeds"


def run(*args):
    rss_files_already_parsed = get_rss_feed_files_already_parsed()
    print("rss_files_already_parsed", rss_files_already_parsed)

    # Rss.objects.all().delete()
    # Rss_sentence.objects.all().delete()

    rss_file_paths = get_all_new_feed_download_paths(rss_files_already_parsed)
    parse_feeds(rss_file_paths)


# TOOO
def get_rss_feed_files_already_parsed():
    return (
        Rss.objects.annotate(files=Func(F("rss_files"), function="unnest"))
        .values_list("files", flat=True)
        .distinct()
    )


def get_relateive_path(rss_file):
    return "/".join(rss_file.parts[-3:])


def get_all_new_feed_download_paths(rss_files_already_parsed):
    rss_file_paths = Path(rss_data_path).glob("**/**/*.xml")
    rss_file_paths = [path for path in rss_file_paths if path.is_file()]
    rss_file_paths = sorted(rss_file_paths)

    print("before filter", len(rss_file_paths))
    rss_file_paths = list(
        filter(
            lambda f: get_relateive_path(f) not in rss_files_already_parsed,
            rss_file_paths,
        )
    )
    print("after filter", len(rss_file_paths))
    return list(rss_file_paths)


def get_published_time(rss_entry):
    parsed_time = rss_entry.get(
        "published_parsed", rss_entry.get("updated_parsed", None)
    )
    string_time = rss_entry.get("published", rss_entry.get("updated", None))

    if parsed_time:
        published_datetime_sec = mktime(parsed_time)
        published_datetime = datetime.datetime.fromtimestamp(published_datetime_sec)
    elif string_time:
        published_datetime = string_time
        published_datetime = dateutil.parser.parse(published_datetime)
    else:
        return None

    published_datetime = timezone.make_aware(
        published_datetime, timezone=timezone.get_current_timezone()
    )
    return published_datetime


def parse_feeds(rss_file_paths: list[Path]):
    feed_config = pd.read_json(f"{rss_data_path}/rss_list.json")
    print(feed_config)
    for rss_file in rss_file_paths:
        try:
            entries = feedparser.parse(str(rss_file)).entries
            feed_provider = rss_file.parent.parent.name
            feed_name = rss_file.parent.name
            source_language = feed_config[feed_config["site"] == feed_provider].iloc[0][
                "language"
            ]

            source_language_code = language_name_to_code[source_language]
            for e in entries:
                # import ipdb

                # ipdb.set_trace()
                published_datetime = get_published_time(e)
                data = {
                    "article_link": e["link"],
                    "rss_files": [get_relateive_path(rss_file)],
                    "feed_provider": feed_provider,
                    "feed_names": [feed_name],
                    "language": source_language_code,
                    "published_datetime": published_datetime,
                    # "updated_datetime": datetime.datetime.fromtimestamp(
                    #     mktime(e["updated_parsed"])
                    # ),
                    "summary": e.get("summary", None),
                    "article_title": e["title"],
                    # "created_datetime": datetime.datetime.fromtimestamp(
                    #     mktime(e["created_parsed"])
                    # ),
                    # "expired_datetime": datetime.datetime.fromtimestamp(
                    #     mktime(e["expired_parsed"])
                    # ),
                }
                obj, created = Rss.objects.update_or_create(
                    article_link=e["link"],
                    defaults={},
                    create_defaults=data,
                )
                print(rss_file)
                print(e["link"])
                print("Created?:", created)
                print("-")

                if not created:
                    obj.rss_files.append(get_relateive_path(rss_file))
                    if feed_name not in obj.feed_names:
                        obj.feed_names.append(feed_name)
                    obj.save()
                else:
                    Rss_sentence.objects.create(
                        source=obj,
                        language=source_language_code,
                        text=e["title"],
                        sentence_order=1,
                    )

            # "other_fields": get_all_other_fields(data),

        except Exception:
            print("ERROR:", rss_file)
            print(traceback.format_exc())
            try:
                entries = feedparser.parse(str(rss_file)).entries
                print("entries", entries)
            except Exception:
                pass
