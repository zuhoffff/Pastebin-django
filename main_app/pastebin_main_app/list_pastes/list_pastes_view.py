from django.views.generic import ListView
from pastebin_main_app.models import Metadata
from django.db.models import Case, Value, When, CharField
import logging

logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# TODO: add filters; use server-side filtering because of difference of datetime formats.
# if method is common get: render html : if method is ajax return just queryset 
# TODO: add revert sorting option
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

        logger.debug(queryset)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['fields'] = self.fields + ['is_protected']
        return context