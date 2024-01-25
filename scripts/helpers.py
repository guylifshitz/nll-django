import six
import json
import uuid
from google.cloud import translate_v2 as translate
from google.oauth2 import service_account
import requests

from articles.models import (
    Wikipedia,
    Wikipedia_sentence,
    Subtitle,
    Subtitle_sentence,
    Lyric,
    Lyric_sentence,
    Rss,
    Rss_sentence,
)


supported_sources = ["rss", "lyric", "subtitle", "wikipedia"]
language_name_to_code = {"arabic": "ar", "hebrew": "he"}
supported_language_codes = language_name_to_code.values()
supported_languages = language_name_to_code.keys()


def check_language_supported(language: str):
    if language not in supported_language_codes:
        raise Exception(f"Language should be one of {supported_language_codes}")
    return True


def check_source_supported(source: str):
    if source not in supported_sources:
        raise Exception(f"Source should be one of {supported_sources}")
    return True


def chunks(list: list, size: int):
    size = max(1, size)
    return (list[i : i + size] for i in range(0, len(list), size))


def get_source_model(source_name: str):
    match source_name:
        case "rss":
            return Rss, Rss_sentence
        case "lyric":
            return Lyric, Lyric_sentence
        case "wikipedia":
            return Wikipedia, Wikipedia_sentence
        case "subtitle":
            return Subtitle, Subtitle_sentence


def translate_texts_google(
    texts: list[str], source_language: str, target_language="en"
):
    """Translates text into the target language.

    Target must be an ISO 639-1 language code.
    See https://g.co/cloud/translate/v2/translate-reference#supported_languages
    """

    assert type(texts) == list

    credentials = service_account.Credentials.from_service_account_file(
        "config/google_credentials.json"
    )

    translate_client = translate.Client(credentials=credentials)

    if isinstance(texts, six.binary_type):
        texts = texts.decode("utf-8")

    try:
        result = translate_client.translate(
            texts, source_language=source_language, target_language=target_language
        )
        translations = [r["translatedText"] for r in result]

        print(f"Translated (Google): {list(zip(texts, translations))}")

        return translations

    except Exception as e:
        print(e)
        pass


def translate_texts_azure(texts, source_language, target_language="en"):
    assert type(texts) == list

    with open("config/azure_credentials.json") as f:
        azurConfig = json.load(f)

    subscription_key = azurConfig["KEY"]
    endpoint = azurConfig["ENDPOINT"]
    location = azurConfig["LOCATION"]

    path = "/translate"
    constructed_url = endpoint + path

    params = {
        "api-version": "3.0",
        "from": source_language,
        "to": target_language,
    }
    constructed_url = endpoint + path

    headers = {
        "Ocp-Apim-Subscription-Key": subscription_key,
        "Ocp-Apim-Subscription-Region": location,
        "Content-type": "application/json",
        "X-ClientTraceId": str(uuid.uuid4()),
    }

    body = [{"text": text} for text in texts]

    request = requests.post(constructed_url, params=params, headers=headers, json=body)
    print(params)
    print(request)
    response = request.json()
    print(response)
    translations = [trans["translations"][0]["text"] for trans in response]

    print(f"Translated (Azure): {zip(texts, translations)}")

    return translations
