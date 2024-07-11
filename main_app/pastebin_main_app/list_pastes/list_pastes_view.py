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

logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
 
# TODO: optimize pagination; use listview pagination tools (instead of sending attributes explicitly)
# TODO: repair the paging buttons

# TODO: make filtering visuals smoother

class ListPastesApiView(generics.ListAPIView):
    queryset=Metadata.objects.all() # default queryset
    serializer_class = MetadataSerializer
    filter_backends=[DjangoFilterBackend,filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['name', 'slug', 'author', 'timestamp', 'expiry_time']
    ordering_fields = ['name', 'slug', 'timestamp', 'expiry_time', 'author']
    search_fields = ['name', 'slug', 'author']