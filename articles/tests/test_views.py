from django.test import TestCase
from ..views import format_features

class FormatFeaturesTest(TestCase):
    def test_format_features_empty(self):
        postag = "NOUN"
        features = []
        expected_result = ""
        self.assertEqual(format_features(postag, features), expected_result)

    def test_format_features_singular_male(self):
        postag = "NOUN"
        features = ["num=S", "gen=M"]
        expected_result = "m"
        self.assertEqual(format_features(postag, features), expected_result)

    def test_format_features_plural_female(self):
        postag = "NOUN"
        features = ["num=P", "gen=F"]
        expected_result = "pf"
        self.assertEqual(format_features(postag, features), expected_result)

    def test_format_features_past_tense(self):
        postag = "VERB"
        features = ["tense=PAST"]
        expected_result = "past."
        self.assertEqual(format_features(postag, features), expected_result)

    def test_format_features_imperative_tense(self):
        postag = "VERB"
        features = ["tense=IMPERATIVE"]
        expected_result = "impe."
        self.assertEqual(format_features(postag, features), expected_result)

    def test_format_features_beinoni_tense(self):
        postag = "VERB"
        features = ["tense=BEINONI"]
        expected_result = "bein."
        self.assertEqual(format_features(postag, features), expected_result)