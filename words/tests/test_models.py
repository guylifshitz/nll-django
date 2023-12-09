from django.test import TestCase
from ..models import Word

class WordModelTest(TestCase):
    def setUp(self):
        self.word = Word.objects.create(
            text="example",
            word_diacritic="example_diacritic",
            translation="example_translation",
            root="example_root",
            flexion_counts={"example": 1},
            rank=1,
            count=1,
            rank_open_subtitles=1,
            count_open_subtitles=1,
            language="example_language",
            user_translations={"example_translation": "user"},
            user_roots={"example_root": "user"},
            user_translations_with_user={"example_translation": "user"},
            user_roots_with_user={"example_root": "user"},
        )

    def test_word_creation(self):
        self.assertEqual(self.word.text, "example")
        self.assertEqual(self.word.word_diacritic, "example_diacritic")
        self.assertEqual(self.word.translation, "example_translation")
        self.assertEqual(self.word.root, "example_root")
        self.assertEqual(self.word.flexion_counts, {"example": 1})
        self.assertEqual(self.word.rank, 1)
        self.assertEqual(self.word.count, 1)
        self.assertEqual(self.word.rank_open_subtitles, 1)
        self.assertEqual(self.word.count_open_subtitles, 1)
        self.assertEqual(self.word.language, "example_language")
        self.assertEqual(self.word.user_translations, {"example_translation": "user"})
        self.assertEqual(self.word.user_roots, {"example_root": "user"})
        self.assertEqual(self.word.user_translations_with_user, {"example_translation": "user"})
        self.assertEqual(self.word.user_roots_with_user, {"example_root": "user"})

    # def test_get_root(self):
    #     # Test when user_roots is not empty
    #     self.word.user_roots = ["root1", "root2", "root3"]
    #     expected_root = "root3"
    #     self.assertEqual(self.word.get_root(), expected_root)

    #     # Test when user_roots is empty
    #     self.word.user_roots = []
    #     expected_root = ""
    #     self.assertEqual(self.word.get_root(), expected_root)