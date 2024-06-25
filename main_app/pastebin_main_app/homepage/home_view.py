from django.http import HttpResponse, JsonResponse
from django.views.generic import TemplateView, FormView
from .slug_form import SlugForm
from django.shortcuts import redirect

class HomePage(FormView):
    template_name = 'home.html'
    form_class = SlugForm

    def form_valid(self, form) -> HttpResponse:
        if form.check_if_exists():
            return redirect('check_protection', form.cleaned_data['slug'])
        else:
            return JsonResponse({'prompt_again': True})