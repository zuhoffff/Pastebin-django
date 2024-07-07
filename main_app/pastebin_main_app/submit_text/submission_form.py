from django import forms
from pastebin_main_app.models import Metadata
from django.utils import timezone

class PasteSubmissionForm(forms.ModelForm):
    text = forms.CharField(max_length=10000, required=True)
    password = forms.CharField(max_length=150, required=False, widget=forms.PasswordInput())
    # timezone = forms.CharField(widget=forms.HiddenInput())
    expiry_time = forms.DateTimeField(
        required=True,
        widget=forms.DateTimeInput(attrs={'class': 'flatpickr', 'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M']
    )

    class Meta:
        model = Metadata
        fields = ['author','name']