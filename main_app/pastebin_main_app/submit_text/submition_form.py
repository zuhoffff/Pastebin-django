from django import forms
from pastebin_main_app.models import Metadata
from django.utils import timezone

class PasteSubmissionForm(forms.ModelForm):
    # Field that not related to db:
    text = forms.CharField(max_length=10000, required=True)
    password = forms.CharField(max_length=150, required=False, widget=forms.PasswordInput())

    expiry_time = forms.DateTimeField(
        input_formats=['%Y-%m-%dT%H:%M:%SZ'],
        widget=forms.TextInput(attrs={
            'placeholder': '',
            'class': 'flatpickr'
        })
    )

    class Meta:
        model = Metadata
        fields = ['author']
