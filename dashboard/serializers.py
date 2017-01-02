from rest_framework import serializers
from .models import BotReportData, Browser, Bot, Platform, GPUType, CPUArchitecture
import datetime
import pytz

# Serializers define the API representation.
class BrowserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Browser
        fields = ('id', 'name')


class BotListSerializer(serializers.ModelSerializer):
    gpuType = serializers.SerializerMethodField()
    cpuArchitecture = serializers.SerializerMethodField()
    platform = serializers.SerializerMethodField()

    def get_gpuType(self, obj):
        return obj.gpuType.name

    def get_cpuArchitecture(self, obj):
        return obj.cpuArchitecture.name

    def get_platform(self,obj):
        return obj.platform.name

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
    days_since = serializers.SerializerMethodField()

    def get_days_since(self,obj):
        current_time = pytz.utc.localize(datetime.datetime.utcnow())
        return (current_time - obj.timestamp).days

    class Meta:
        model = BotReportData
        fields = ( 'id', 'bot', 'gpu_type', 'cpu_arch', 'platform', 'browser', 'browser_version', 'root_test',
                  'test_path', 'test_version', 'metric_tested', 'mean_value', 'stddev', 'days_since' ,'delta')


