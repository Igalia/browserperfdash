from dashboard.core.gpus.models import GPUType
from rest_framework import serializers


class GPUTypeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = GPUType
        fields = ('id', 'name')
