from django import forms


class ArticlesForm(forms.Form):

    languages = (("arabic", "Arabic"), ("hebrew", "Hebrew"))
    language = forms.ChoiceField(choices=languages)

    known_cutoff = forms.IntegerField()
    practice_cutoff = forms.IntegerField()
    start_date = forms.DateField()
    sort_by_word = forms.BooleanField()
    article_display_count = forms.IntegerField()
