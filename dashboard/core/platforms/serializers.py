from dashboard.core.platforms.models import Platform
from rest_framework import serializers


class PlatformListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Platform
        fields = ('id', 'name')