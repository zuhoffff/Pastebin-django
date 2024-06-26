# allows to view all created pastes
from typing import Any
from django.db.models.query import QuerySet
from django.http import HttpResponse, JsonResponse
from django.views.generic import ListView
from django.urls import reverse
from pastebin_main_app.models import Metadata
from django.shortcuts import render
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ListPastes(ListView):
    model=Metadata
    template_name = 'list_pastes.html'
    context_object_name = 'metadatas'

    def get_queryset(self):
        self.fields = ['name', 'slug', 'author', 'timestamp', 'expiry_time']
        queryset = self.model.objects.values(*self.fields)
        logger.info(list(queryset))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['fields'] = self.fields
        return context