# allows to view all created pastes
from typing import Any
from django.db.models.query import QuerySet
from django.http import HttpResponse, JsonResponse
from django.views.generic import ListView
from django.urls import reverse
from pastebin_main_app.models import Metadata

class ListPastes(ListView):
    model=Metadata
    template_name = 'list_pastes.html'
    context_object_name = 'metadatas'

    def get_queryset(self):
        return self.model.objects.all()