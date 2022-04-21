from django import forms


class WordsForm(forms.Form):
    # languages = (("arabic", "Arabic"), ("hebrew", "Hebrew"))
    # language = forms.ChoiceField(choices=languages)
    #  TODO add a dataset field, for when we can handle other sources, like subtitiles.

    lower_freq_cutoff = forms.IntegerField(label="From")
    upper_freq_cutoff = forms.IntegerField(label="To")
