from django import forms
from pastebin_main_app.models import Metadata

class TextPasteData(forms.ModelForm):
    class Meta:
        model = Metadata
        fields = ['']