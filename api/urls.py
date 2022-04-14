from django.urls import path, include
from words.models import Words
from rest_framework_mongoengine import serializers, viewsets, routers
import rest_framework


class WordsSerializer(serializers.DocumentSerializer):
    new_user_root = rest_framework.serializers.CharField(
        max_length=300, allow_blank=True, write_only=True
    )

    class Meta:
        model = Words
        fields = ["_id", "new_user_root"]
        extra_kwargs = {"new_user_root": {"read_only": True}}

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
        instance.save()
        return instance


class WordsViewSet(viewsets.ModelViewSet):
    lookup_field = "_id"
    queryset = Words.objects.all().limit(10)
    serializer_class = WordsSerializer


router = routers.DefaultRouter()
router.register(r"words", WordsViewSet, "words")

urlpatterns = [
    path("", include(router.urls)),
]
