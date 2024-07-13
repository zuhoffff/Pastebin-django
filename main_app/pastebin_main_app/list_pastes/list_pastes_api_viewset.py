from django.views.generic import ListView
from pastebin_main_app.models import Metadata
from rest_framework import generics, filters, viewsets, renderers
from rest_framework.response import Response
import logging
from django_filters.rest_framework import DjangoFilterBackend
from pastebin_main_app.serializers import MetadataSerializer
from pastebin_main_app.list_pastes.custom_filters import MetadataFilter

logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
 
# TODO: make filtering visuals smoother
# TODO: integrate api with the front-end

class ListPastesApiSet(viewsets.ReadOnlyModelViewSet):
    template_name = 'list_pastes.html'
    queryset=Metadata.objects.all().order_by('slug') # default queryset
    serializer_class = MetadataSerializer
    filter_backends=[DjangoFilterBackend,filters.OrderingFilter, filters.SearchFilter]
    filterset_class = MetadataFilter # custom filter for sorting by private/public
    ordering_fields = ['name', 'slug', 'timestamp', 'expiry_time', 'author']
    search_fields = ['name', 'slug', 'author',]
    renderer_classes = [renderers.TemplateHTMLRenderer]   
    
    def list(self, request, *args, **kwargs):
        # response = super(ListPastesApiSet, self).list(request, *args, **kwargs)
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)

        return Response({'metadata_list': serializer.data,'page_obj': self.paginator.page}, template_name='list_pastes.html')

# The request.query_params attribute (an instance of QueryDict) holds all the query parameters. !

# Other solution would be to just create dedicated view for list action and only use HTML renderer. But then you would have a small code duplication.