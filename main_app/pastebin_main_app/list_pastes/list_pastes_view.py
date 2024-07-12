from django.views.generic import ListView
from pastebin_main_app.models import Metadata
from django.db.models import Case, Value, When, CharField
import logging
from django.http.response import JsonResponse
from django.template.loader import render_to_string
from django.core.paginator import Paginator
from rest_framework import generics, filters
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from pastebin_main_app.serializers import MetadataSerializer
from pastebin_main_app.list_pastes.custom_filters import MetadataFilter

logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
 
# TODO: add paging to the api
# TODO: make filtering visuals smoother
# TODO: integrate api with the front-end

class ListPastesApiView(generics.ListAPIView):
    queryset=Metadata.objects.all() # default queryset
    serializer_class = MetadataSerializer
    filter_backends=[DjangoFilterBackend,filters.OrderingFilter, filters.SearchFilter]
    filterset_class = MetadataFilter # custom filter for sorting by private/public
    ordering_fields = ['name', 'slug', 'timestamp', 'expiry_time', 'author']
    search_fields = ['name', 'slug', 'author']

    def get_queryset(self):
        queryset = super().get_queryset()
        filter_param = self.request.query_params.get('filter', 'all')   
        
        if filter_param == 'public':
            queryset = queryset.filter(password__isnull=True)
        elif filter_param == 'private':
            queryset = queryset.exclude(password__isnull=True)
        
        return queryset