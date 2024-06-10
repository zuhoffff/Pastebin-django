from django import forms
from pastebin_main_app.models import Metadata
from django.utils import timezone

class PasteSubmissionForm(forms.ModelForm):
    # Field that not related to db:
    text = forms.CharField(max_length=10000, required=True)
    password = forms.CharField(max_length=150, required=True)

    paste_duration = forms.DurationField(
        initial=timezone.timedelta(days=2),
        widget=forms.TextInput(attrs={
            'placeholder':'2 days 0 hours 0 minutes',
            'class': 'flatpickr'

        })
    )
    
    def clean_paste_duration(self):
        expiry_time = self.cleaned_data['paste_duration']
        if expiry_time.total_seconds() <= 0:
            raise forms.ValidationError("Expiry time must be in the future.")
        return expiry_time

    class Meta:
        model = Metadata
        fields = ['author']
