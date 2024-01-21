supported_languages = ["ar", "he"]


def check_language_supported(language):
    if language not in supported_languages:
        raise Exception("language should be either 'en' or 'ar'")
    return True
