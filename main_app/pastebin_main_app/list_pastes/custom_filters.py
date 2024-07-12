import django_filters
from pastebin_main_app.models import Metadata
import logging
logger = logging.getLogger()

class MetadataFilter(django_filters.FilterSet):
    is_protected = django_filters.BooleanFilter(field_name='password',method='filter_is_protected',label='Is protected')

    class Meta:
        model = Metadata
        fields = ['name', 'slug', 'author', 'timestamp', 'expiry_time', 'is_protected']

    def filter_is_protected(self, queryset, name, value):
        logger.info(value)
        if value:
        # PROTECTED
            return queryset.exclude(password__isnull=True)
        else:
        # PUBLIC
            return queryset.filter(password__isnull=True)