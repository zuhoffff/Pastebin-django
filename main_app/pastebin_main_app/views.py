from django.http import HttpResponse
from django.views.generic import TemplateView, FormView
from .slugForm import SlugForm
from django.shortcuts import redirect

class HomePage(FormView):
    template_name = 'home.html'
    form_class = SlugForm

    def form_valid(self, form) -> HttpResponse:
        return redirect('check_protection', form.cleaned_data['slug'])