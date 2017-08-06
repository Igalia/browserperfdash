from dashboard.core.bots.models import Bot
from rest_framework import serializers

from dashboard.core.platforms.serializers import PlatformListSerializer
from dashboard.core.gpus.serializers import GPUTypeListSerializer
from dashboard.core.cpus.serializers import CPUArchitectureListSerializer


class BotsForResultsExistListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bot
        fields = ('name', )


class BotsFullDetailsForResultsExistListSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    platform = PlatformListSerializer()
    cpuArchitecture = CPUArchitectureListSerializer()
    gpuType = GPUTypeListSerializer()

    class Meta:
        model = Bot
        fields = ('name', 'platform', 'cpuArchitecture', 'gpuType')