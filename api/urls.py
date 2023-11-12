from django.urls import path, include
from words.models import Word, WordRating
from words.permissions import IsNotTestUser
from rest_framework import serializers, viewsets, routers
import rest_framework
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

# TODO rename classes in this file, follow django form
class WordsSerializer(serializers.ModelSerializer):
    new_user_root = rest_framework.serializers.CharField(
        max_length=300, allow_blank=True, write_only=True
    )
    new_user_translation = rest_framework.serializers.CharField(
        max_length=300, allow_blank=True, write_only=True
    )
    username = rest_framework.serializers.CharField(
        max_length=100, allow_blank=True, write_only=True
    )

    class Meta:
        model = Word
        fields = ["text", "new_user_root", "new_user_translation", "username"]
        extra_kwargs = {
            "new_user_root": {"read_only": True},
            "new_user_translation": {"read_only": True},
            "username": {"read_only": True},
        }

    # def validate(self, attrs):
    #     # attrs.pop("new_user_root", None)
    #     print("attrs", attrs)
    #     return super().validate(attrs)

    def create(self, validated_data):
        raise NotImplemented

    def update(self, instance, validated_data):
        username = validated_data.get("username", None)

        new_user_root = validated_data.get("new_user_root", None)
        if not instance.user_roots:
            instance.user_roots = []
            instance.user_roots_with_user = []
        if new_user_root:
            instance.user_roots.append(new_user_root)
            instance.user_roots_with_user.append({"root": new_user_root, "username": username})

        new_user_translation = validated_data.get("new_user_translation", None)
        if not instance.user_translations:
            instance.user_translations = []
            instance.user_translations_with_user = []
        if new_user_translation:
            instance.user_translations.append(new_user_translation)
            instance.user_translations_with_user.append(
                {"translation": new_user_translation, "username": username}
            )

        instance.save()
        return instance

class WordsSerializer2(serializers.ModelSerializer):
    root = rest_framework.serializers.CharField(max_length=300, allow_blank=True, read_only=True)
    similar_words = rest_framework.serializers.CharField(
        max_length=300, allow_blank=True, read_only=True
    )
    similar_roots = rest_framework.serializers.CharField(
        max_length=300, allow_blank=True, read_only=True
    )

    class Meta:
        model = Word
        fields = ["text", "root", "similar_roots", "similar_words"]

        extra_kwargs = {
            "root": {"read_only": True},
            "similar_roots": {"read_only": True},
            "similar_words": {"read_only": True},
        }

    # TODO move comparison methods to a helper class
    # TODO handle arabic
    def comparable_word_maker(self, word):
        similar_look_matchings = [
            ["ח", "ה", "ת"],
            ["ו", "ז", "ן"],
            ["כ", "ב"],
            ["כּ", "בּ"],
            ["ם", "מ", "ט", "ס"],
            ["נ", "ג"],
            ["ע", "צ"],
            ["ו", "וֹ", "וֹ"],
            ["ד", "ר", "ך", "ךּ"],
            ["שׁ", "שׂ"],
        ]

        similar_sound = [
            ["ב", "ו"],
            ["ט", "ת"],
            ["ח", "כ"],
            ["א", "ע"],
            ["כּ", "ק"],
            ["שׂ", "ס"],
            [""],
            [""],
        ]

        word = word.replace(" ", "")
        word = word.replace("-", "")

        for idx, similar_look_letters in enumerate(similar_look_matchings):
            for letter in similar_look_letters:
                word = word.replace(letter, str(idx))
        return word

    # TODO handle arabic
    def find_similar_words(self, instance, field):
        from fuzzywuzzy import fuzz

        language = instance.language
        root = instance.serializable_value(field)

        if not root:
            return []

        comparable_word = self.comparable_word_maker(root)

        top_words = Word.objects.filter(language=language).order_by("rank").all()[0:1000]
        similar_roots = []
        for top_word in top_words:
            if not top_word.serializable_value(field):
                continue
            comparable_word_2 = self.comparable_word_maker(top_word.serializable_value(field))
            similar_score = fuzz.ratio(comparable_word, comparable_word_2)
            if similar_score >= 70:
                similar_roots.append(
                    {
                        "text": top_word.text,
                        "root": top_word.root,
                        "translation": top_word.translation,
                        # "comparable_word": comparable_word_2,
                        "similar_score": similar_score,
                    }
                )
        similar_roots = sorted(similar_roots, key=lambda d: d["similar_score"], reverse=True)
        return similar_roots

    def to_representation(self, instance):
        return {
            "root": instance.root,
            "similar_roots": self.find_similar_words(instance, "root"),
            "similar_words": self.find_similar_words(instance, "text"),
        }


# TODO handle arabic
class WordsViewSet(viewsets.ModelViewSet):
    lookup_field = "text"
    queryset = Word.objects.filter(language="hebrew").order_by("rank").all()

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsNotTestUser]
    serializer_class = WordsSerializer

# TODO handle arabic
class WordDetail(viewsets.ReadOnlyModelViewSet):
    lookup_field = "text"
    permission_classes = ()
    queryset = Word.objects.filter(language="hebrew").order_by("rank").all()
    serializer_class = WordsSerializer2


class WordRatingsSerializer(serializers.ModelSerializer):
    find_text = rest_framework.serializers.CharField(
        max_length=300, allow_blank=False, write_only=True
    )
    new_rating = rest_framework.serializers.IntegerField(write_only=True, min_value=1, max_value=5)

    class Meta:
        model = WordRating
        fields = ["find_text", "new_rating"]
        extra_kwargs = {
            "find_text": {"read_only": True},
            "new_rating": {"read_only": True},
        }

    def create(self, validated_data):
        user = self.context["request"].user
        word = Word.objects.get(text=validated_data["find_text"])
        validated_data = {
            "user": user,
            "word": word,
            "rating": validated_data["new_rating"],
        }
        print(word)
        obj, was_created = WordRating.objects.update_or_create(
            user=user, word=word, defaults=validated_data
        )

        return obj


class WordRatingsViewSet(viewsets.ModelViewSet):
    queryset = WordRating.objects.filter().order_by("rating").all()
    serializer_class = WordRatingsSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]


router = routers.DefaultRouter()
router.register(r"words", WordsViewSet, "words")
router.register(r"similar_words", WordDetail, "words2")
router.register(r"rating", WordRatingsViewSet, "rating")

urlpatterns = [
    path("", include(router.urls)),
]
