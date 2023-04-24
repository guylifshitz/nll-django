from django.urls import path, include
from words.models import Words, WordRatings
from rest_framework import serializers, viewsets, routers
import rest_framework
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication


class WordsSerializer(serializers.ModelSerializer):
    new_user_root = rest_framework.serializers.CharField(
        max_length=300, allow_blank=True, write_only=True
    )
    new_user_translation = rest_framework.serializers.CharField(
        max_length=300, allow_blank=True, write_only=True
    )

    class Meta:
        model = Words
        fields = ["_id", "new_user_root", "new_user_translation"]
        # fields = ["_id", "new_user_translation"]
        extra_kwargs = {
            "new_user_root": {"read_only": True},
            "new_user_translation": {"read_only": True},
        }

    # def validate(self, attrs):
    #     # attrs.pop("new_user_root", None)
    #     print("attrs", attrs)
    #     return super().validate(attrs)

    def create(self, validated_data):
        raise NotImplemented

    def update(self, instance, validated_data):
        new_user_root = validated_data.get("new_user_root", None)
        if not instance.user_roots:
            instance.user_roots = []
        if new_user_root:
            instance.user_roots.append(new_user_root)

        new_user_translation = validated_data.get("new_user_translation", None)
        if not instance.user_translations:
            instance.user_translations = []
        if new_user_translation:
            instance.user_translations.append(new_user_translation)

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
        model = Words
        fields = ["_id", "root", "similar_roots", "similar_words"]

        extra_kwargs = {
            "root": {"read_only": True},
            "similar_roots": {"read_only": True},
            "similar_words": {"read_only": True},
        }

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

    def find_similar_words(self, instance, field):
        from fuzzywuzzy import fuzz

        root = instance.serializable_value(field)

        if not root:
            return []

        comparable_word = self.comparable_word_maker(root)

        top_words = Words.objects.filter(language="hebrew").order_by("rank").all()[0:1000]
        similar_roots = []
        for top_word in top_words:
            if not top_word.serializable_value(field):
                continue
            comparable_word_2 = self.comparable_word_maker(top_word.serializable_value(field))
            similar_score = fuzz.ratio(comparable_word, comparable_word_2)
            if similar_score >= 50:
                similar_roots.append(
                    {
                        "_id": top_word._id,
                        "root": top_word.root,
                        "comparable_word": comparable_word_2,
                        "translation": top_word.translation,
                        "similar_score": similar_score,
                    }
                )
        similar_roots = sorted(similar_roots, key=lambda d: d["similar_score"], reverse=True)
        return similar_roots

    def to_representation(self, instance):
        return {
            "root": instance.root,
            "similar_roots": self.find_similar_words(instance, "root"),
            "similar_words": self.find_similar_words(instance, "_id"),
        }


class WordsViewSet(viewsets.ModelViewSet):
    lookup_field = "_id"
    queryset = Words.objects.filter(language="hebrew").order_by("rank").all()
    serializer_class = WordsSerializer


class WordDetail(viewsets.ReadOnlyModelViewSet):
    lookup_field = "_id"
    permission_classes = ()
    queryset = Words.objects.filter(language="hebrew").order_by("rank").all()
    serializer_class = WordsSerializer2


class WordRatingsSerializer(serializers.ModelSerializer):
    word_text = rest_framework.serializers.CharField(
        max_length=300, allow_blank=True, write_only=True
    )

    class Meta:
        model = WordRatings
        fields = ["_id", "word_text", "rating"]
        extra_kwargs = {
            "word_text": {"read_only": True},
        }

    def create(self, validated_data):
        user = self.context["request"].user
        word = Words.objects.get(_id=validated_data["word_text"])
        validated_data = {
            "user": user,
            "word": word,
            "rating": validated_data["rating"],
        }
        obj, was_created = WordRatings.objects.update_or_create(
            user=user, word=word, defaults=validated_data
        )

        return obj


class WordRatingsViewSet(viewsets.ModelViewSet):
    queryset = WordRatings.objects.filter().order_by("rating").all()
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
