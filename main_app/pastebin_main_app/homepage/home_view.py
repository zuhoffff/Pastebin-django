from django.http import HttpResponse, JsonResponse
from django.views.generic import TemplateView, FormView
from .slug_form import SlugForm
from django.shortcuts import redirect
from django.urls import reverse

class HomePage(FormView):
    template_name = 'home.html'
    form_class = SlugForm

    def form_valid(self, form) -> HttpResponse:
        if form.check_if_exists():
            return JsonResponse({'redirect_url': reverse('check_protection', kwargs={'slug': form.cleaned_data['slug']})})
            return redirect('check_protection', )
        else:
            return JsonResponse({'prompt_again': True})