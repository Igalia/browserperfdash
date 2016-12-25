from rest_framework import serializers
from .models import BotReportData, Browser, Bot, Platform, GPUType, CPUArchitecture


# Serializers define the API representation.
class BotReportDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = BotReportData
        fields = ('bot', 'browser', 'browser_version', 'root_test', 'test_path', 'test_version',
                  'metric_tested', 'mean_value', 'stddev', 'timestamp')


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