from rest_framework import serializers
from pastebin_main_app.models import Metadata

class MetadataSerializer(serializers.ModelSerializer):
    is_protected = serializers.SerializerMethodField()

    class Meta:
        model = Metadata
        fields = ['name', 'slug', 'author', 'timestamp', 'expiry_time', 'is_protected']

    def get_is_protected(self, obj):
        return 'private' if obj.get_is_protected() else 'public'