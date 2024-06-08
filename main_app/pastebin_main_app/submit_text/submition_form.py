from django import forms
from pastebin_main_app.models import Metadata

class PasteSubmissionForm(forms.ModelForm):
    # Field that not related to db:
    text = forms.CharField(max_length=10000, required=True)

    class Meta:
        model = Metadata
        fields = ['author',  'password']
        