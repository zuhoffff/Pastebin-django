from django import forms

class SlugForm(forms.Form):
    slug = forms.SlugField(label='Enter the identifier of a text-paste')