from rest_framework import serializers
from .models import BotReportData, Browser, Bot, Platform, GPUType, CPUArchitecture


# Serializers define the API representation.
class BrowserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Browser
        fields = ('id', 'name')


class BotListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Bot
        fields = ('name', 'cpuArchitecture', 'gpuType', 'platform')


class PlatformListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Platform
        fields = ('id', 'name')


class GPUTypeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = GPUType
        fields = ('id', 'name')


class CPUArchitectureListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CPUArchitecture
        fields = ('id', 'name')


class BotReportDataSerializer(serializers.ModelSerializer):
    gpu_type = serializers.CharField(source='bot.gpuType', read_only=True)
    cpu_arch = serializers.CharField(source='bot.cpuArchitecture', read_only=True)
    platform = serializers.CharField(source='bot.platform', read_only=True)

    class Meta:
        model = BotReportData
        fields = ('bot', 'gpu_type', 'cpu_arch', 'platform', 'browser', 'browser_version', 'root_test',
                  'test_path', 'test_version', 'metric_tested', 'mean_value', 'stddev', 'timestamp')


