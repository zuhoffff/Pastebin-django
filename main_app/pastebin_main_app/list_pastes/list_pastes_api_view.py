from django.views.generic import ListView
from pastebin_main_app.models import Metadata
from rest_framework import generics, filters
from django.shortcuts import render
import logging
from django_filters.rest_framework import DjangoFilterBackend
from pastebin_main_app.serializers import MetadataSerializer
from pastebin_main_app.list_pastes.custom_filters import MetadataFilter

logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
 
# TODO: make filtering visuals smoother
# TODO: integrate api with the front-end

class ListPastesApiView(generics.ListAPIView):
    queryset=Metadata.objects.all() # default queryset
    serializer_class = MetadataSerializer
    filter_backends=[DjangoFilterBackend,filters.OrderingFilter, filters.SearchFilter]
    filterset_class = MetadataFilter # custom filter for sorting by private/public
    ordering_fields = ['name', 'slug', 'timestamp', 'expiry_time', 'author']
    search_fields = ['name', 'slug', 'author',]

    def get_queryset(self):
        queryset = super().get_queryset()
        filter_param = self.request.query_params.get('filter', 'all')   
        
        if filter_param == 'public':
            queryset = queryset.filter(password__isnull=True)
        elif filter_param == 'private':
            queryset = queryset.exclude(password__isnull=True)
        
        return queryset
    
    # INTERFACE FOR INTERACTION WITH API
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
        
        # Render the template with the serialized data
        return render(request, 'list_pastes.html', {'metadata_list': serializer.data})