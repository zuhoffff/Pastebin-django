from django.views.generic import ListView
from pastebin_main_app.models import Metadata
from django.db.models import Case, Value, When, CharField
import logging
from django.http.response import JsonResponse
from django.template.loader import render_to_string
from django.core.paginator import Paginator

logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
 
# TODO: optimize pagination; use listview pagination tools (instead of sending attributes explicitly)
# TODO: add paging buttons to the top of the page

# TODO: update list in realtime when some pastes expire
# TODO: alternate the names of the labels (use expiry time instead of hardcode expiry_time)
# TODO: make filtering visuals smoother

class ListPastes(ListView):
    paginate_by = 18 # default
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
    
    def get(self, request, *args, **kwargs):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            filter_param = request.GET.get('filter', 'all')
            sort_param = request.GET.get('sort', 'name')
            order_param = request.GET.get('order', 'asc')
            page = request.GET.get('page', 1)
            self.paginate_by = request.GET.get('paginate_by')

            queryset = self.get_queryset()

            if filter_param == 'public':
                queryset = queryset.filter(is_protected='public')

            valid_sort_fields = ['name', 'slug', 'timestamp', 'expiry_time']
            if sort_param in valid_sort_fields:
                if order_param == 'desc':
                    sort_param = f'-{sort_param}'
                queryset = queryset.order_by(sort_param)

            paginator = Paginator(queryset, self.paginate_by)
            paginated_queryset = paginator.page(page)

            html = render_to_string('list_pastes_part.html', {'metadatas': paginated_queryset})
            return JsonResponse({
                'html': html,
                'has_next': paginated_queryset.has_next(),
                'has_previous': paginated_queryset.has_previous(),
                'current_page': paginated_queryset.number,
                'num_pages': paginator.num_pages
            })
        else:
            return super().get(request, *args, **kwargs)