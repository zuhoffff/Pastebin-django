from django.views.generic import ListView
from pastebin_main_app.models import Metadata
from django.db.models import Case, Value, When, CharField
import logging
from django.http.response import HttpResponse, JsonResponse
from django.template.loader import render_to_string

logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
 
# TODO: add paging

# TODO: update list in realtime when some pastes expire
# TODO: alternate the names of the labels (use expiry time instead of hardcode expiry_time)
# TODO: make filtering visuals smoother

class ListPastes(ListView):
    model=Metadata
    template_name = 'list_pastes.html'
    context_object_name = 'metadatas'

    def get_queryset(self):
        self.fields = ['name', 'slug', 'author', 'timestamp', 'expiry_time']
        queryset = self.model.objects.values(*self.fields).annotate(
            is_protected=Case(
                When(password__isnull=True, then=Value('public')),
                default=Value('private'),
                output_field=CharField()
            )
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['fields'] = self.fields + ['is_protected']
        return context
    
    def get(self, request, *args, **kwargs):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            filter_param = request.GET.get('filter', 'all')
            sort_param = request.GET.get('sort', 'name')
            order_param = request.GET.get('order', 'asc')  # New parameter for sorting order

            queryset = self.get_queryset()

            if filter_param == 'public':
                queryset = queryset.filter(is_protected='public')

            valid_sort_fields = ['name', 'slug', 'timestamp', 'expiry_time']
            if sort_param in valid_sort_fields:
                if order_param == 'desc':
                    sort_param = f'-{sort_param}'
                queryset = queryset.order_by(sort_param)

            html = render_to_string('list_pastes_part.html', {'metadatas': queryset})
            return JsonResponse({'html': html})
        else:
            return super().get(request, *args, **kwargs)