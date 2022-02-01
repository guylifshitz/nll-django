from django import forms


class WordsForm(forms.Form):
    languages = (("arabic", "Arabic"), ("hebrew", "Hebrew"))
    language = forms.ChoiceField(choices=languages)

    lower_freq_cutoff = forms.IntegerField()
    upper_freq_cutoff = forms.IntegerField()
