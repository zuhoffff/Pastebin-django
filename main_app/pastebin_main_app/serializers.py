from rest_framework import serializers
from pastebin_main_app.models import Metadata

class MetadataSerializer(serializers.ModelSerializer):
    is_protected = serializers.ReadOnlyField()

    class Meta:
        model = Metadata
        fields = ['name', 'slug', 'author', 'timestamp', 'expiry_time', 'is_protected']