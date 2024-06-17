from django import forms
from .models import Metadata

class SlugForm(forms.Form):
    slug = forms.SlugField(label='Enter the identifier of a text-paste')

    # Check if obj exists
    def check_if_exists(self):
        if Metadata.objects.filter(slug = self.cleaned_data['slug']).exists():
            return True
        return False