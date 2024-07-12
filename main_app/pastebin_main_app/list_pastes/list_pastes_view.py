# views.py
from django.shortcuts import render
from django.views.generic import TemplateView
from django.urls import reverse
import requests

#ALTERNATIVE INTERFACE FOR INTERACTION WITH API
class ListPastesView(TemplateView):
    template_name = 'list_pastes.html'
    
    # make request to my api:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        api_url = self.request.build_absolute_uri(reverse('pastes_api'))
        context['pastes'] = requests.get(api_url)
        return context
