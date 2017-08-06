from dashboard.core.cpus.models import CPUArchitecture
from rest_framework import serializers


class CPUArchitectureListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CPUArchitecture
        fields = ('id', 'name')