from django import forms
from django.conf import settings


class ArticlesFormFromFile(forms.Form):

    languages = (("arabic", "Arabic"), ("hebrew", "Hebrew"))
    language = forms.ChoiceField(choices=languages)

    start_date = forms.DateField(input_formats=settings.DATE_INPUT_FORMATS)
    end_date = forms.DateField(input_formats=settings.DATE_INPUT_FORMATS)
    sort_by_word = forms.BooleanField(required=False)
    article_display_count = forms.IntegerField()

    file = forms.FileField()


class ArticlesForm(forms.Form):

    languages = (("arabic", "Arabic"), ("hebrew", "Hebrew"))
    language = forms.ChoiceField(choices=languages)

    known_cutoff = forms.IntegerField()
    practice_cutoff = forms.IntegerField()
    seen_cutoff = forms.IntegerField()
    start_date = forms.DateField(input_formats=settings.DATE_INPUT_FORMATS)
    end_date = forms.DateField(input_formats=settings.DATE_INPUT_FORMATS)
    sort_by_word = forms.BooleanField(required=False)
    article_display_count = forms.IntegerField()
