from django import forms
from pastebin_main_app.models import Metadata
from django.utils import timezone

# Design: 
# put expiry time provided by the user in form of datetime object
# make sure timezone is handled (the time should be stored as utc and shown in user's local time)
# put expiry time to the expiry registry in unix utc int format for ease of operations on it
# when retrieving the expiry time to show a text paste to user: make sure its align with his local time


class PasteSubmissionForm(forms.ModelForm):
    text = forms.CharField(max_length=10000, required=True)
    password = forms.CharField(max_length=150, required=False, widget=forms.PasswordInput())

    class Meta:
        model = Metadata
        fields = ['author','expiry_time','name']
        widgets = {
            'expiry_time': forms.DateTimeInput(attrs={'class': 'flatpickr'},
                                               format='%Y-%m-%dT%H:%M')
        }