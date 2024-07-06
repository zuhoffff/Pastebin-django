from django import forms
from pastebin_main_app.models import Metadata
from django.utils import timezone
import pytz

# Design: 
# put expiry time provided by the user in form of datetime object
# make sure timezone is handled (the time should be stored as utc and shown in user's local time)
# put expiry time to the expiry registry in unix utc int format for ease of operations on it
# when retrieving the expiry time to show a text paste to user: make sure its align with his local time


class PasteSubmissionForm(forms.ModelForm):
    text = forms.CharField(max_length=10000, required=True)
    password = forms.CharField(max_length=150, required=False, widget=forms.PasswordInput())
    # timezone = forms.CharField(widget=forms.HiddenInput())

    class Meta:
        model = Metadata
        fields = ['author','expiry_time','name']
        widgets = {
            'expiry_time': forms.DateTimeInput(attrs={'class': 'flatpickr'},
                                               format='%Y-%m-%dT%H:%M')
        }
    
    # def clean_expiry_time(self):
    #     expiry_time = self.cleaned_data.get('expiry_time')
    #     timezone_str = self.cleaned_data.get('timezone')

    #     user_tz = pytz.timezone(timezone_str)
    #     # Localize the expiry_time to the user's timezone
    #     localized_expiry_time = user_tz.localize(expiry_time)
    #     # Convert the localized time to UTC
    #     utc_expiry_time = localized_expiry_time.astimezone(pytz.utc)
    #     return utc_expiry_time