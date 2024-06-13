from django import forms
from pastebin_main_app.models import Metadata
from django.utils import timezone

# Design: 
# put both timestamp and time provided by the user in form of datetime object
# make sure timezone is handled (the time should be stored as utc and shown in user's local time)
# put expiry time to the expiry registry in unix utc int format for ease of operations on it
# when retrieving the expiry time to show a text paste to user make sure it coverted the right way


class PasteSubmissionForm(forms.ModelForm):
    # Field that not related to db:
    text = forms.CharField(max_length=10000, required=True)
    password = forms.CharField(max_length=150, required=False, widget=forms.PasswordInput())
    # Hidden timestamp field

    class Meta:
        model = Metadata
        fields = ['author','expiry_time']
        widgets = {
            'expiry_time': forms.DateTimeInput(attrs={'class': 'flatpickr'},
                                               format='%Y-%m-%dT%H:%M')
        }