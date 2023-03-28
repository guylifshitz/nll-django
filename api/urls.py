from django.urls import path, include
from words.models import Words
from rest_framework_mongoengine import serializers, viewsets, routers
import rest_framework


class WordsSerializer(serializers.DocumentSerializer):
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
        if new_user_root:
            instance.user_roots.append(new_user_root)

        new_user_translation = validated_data.get("new_user_translation", None)
        if new_user_translation:
            instance.user_translations.append(new_user_translation)

        instance.save()
        return instance


class WordsSerializer2(serializers.DocumentSerializer):
    root = rest_framework.serializers.CharField(max_length=300, allow_blank=True, read_only=True)
    similar_roots = rest_framework.serializers.CharField(
        max_length=300, allow_blank=True, read_only=True
    )

    class Meta:
        model = Words
        fields = ["_id", "root", "similar_roots"]

        extra_kwargs = {
            "root": {"read_only": True},
            "similar_roots": {"read_only": True},
        }

    def comparable_root_maker(self, word):
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

    def find_similar_roots(self, instance):
        from fuzzywuzzy import fuzz

        root = instance["root"]

        if not root:
            return []

        comparable_root = self.comparable_root_maker(root)

        top_words = Words.objects.filter(language="hebrew").order_by("rank").all().limit(500)
        similar_roots = []
        for top_word in top_words:
            print(top_word["_id"], top_word["root"])
            if not top_word["root"]:
                continue
            comparable_root_2 = self.comparable_root_maker(top_word["root"])
            similar_score = fuzz.ratio(comparable_root, comparable_root_2)
            if similar_score >= 50:
                similar_roots.append(
                    {
                        "_id": top_word["_id"],
                        "root": top_word["root"],
                        "comparable_root": comparable_root_2,
                        "translation": top_word["translation"],
                        "similar_score": similar_score,
                    }
                )
        similar_roots = sorted(similar_roots, key=lambda d: d["similar_score"], reverse=True)
        return similar_roots

    def to_representation(self, instance):
        return {"root": instance.root, "similar_roots": self.find_similar_roots(instance)}


class WordsViewSet(viewsets.ModelViewSet):
    lookup_field = "_id"
    queryset = Words.objects.filter(language="hebrew").order_by("rank").all().limit(100)
    serializer_class = WordsSerializer


class WordDetail(viewsets.ReadOnlyModelViewSet):
    lookup_field = "_id"
    permission_classes = ()
    queryset = Words.objects.filter(language="hebrew").order_by("rank").all().limit(100)
    serializer_class = WordsSerializer2


router = routers.DefaultRouter()
router.register(r"words", WordsViewSet, "words")
router.register(r"similar_roots", WordDetail, "words2")

urlpatterns = [
    path("", include(router.urls)),
]
