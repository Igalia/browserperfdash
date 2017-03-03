from rest_framework import serializers
from .models import BotReportData, Browser, Bot, Platform, GPUType, CPUArchitecture, Test
import datetime


class BrowserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Browser
        fields = ('id', 'name')


class BrowsersForResultsExistListSerializer(serializers.Serializer):
    browser_id = serializers.CharField(max_length=50)
    browser = serializers.CharField(max_length=50)


class TestsForResultsExistListSerializer(serializers.Serializer):
    root_test_id = serializers.CharField(max_length=50)


class BotsForResultsExistListSerializer(serializers.Serializer):
    bot = serializers.CharField(max_length=50)

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


class TestListListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = ('id', 'description')


class TestPathListSerializer(serializers.Serializer):
    test_path = serializers.CharField(max_length=500)
    root_test = serializers.CharField(max_length=200)


class TestVersionForTestPathListSerializer(serializers.Serializer):
    test_version = serializers.CharField(max_length=500)


class ResultsForVersionListSerializer(serializers.Serializer):
    timestamp = serializers.DateTimeField()
    mean_value = serializers.FloatField()
    stddev = serializers.FloatField()
    browser_version = serializers.CharField(max_length=500)
    delta = serializers.FloatField()
    unit = serializers.SerializerMethodField()

    def get_unit(self,obj):
        return obj.metric_tested.unit

class BotResultMinimalSerializer(serializers.ModelSerializer):

    class Meta:
        model = BotReportData
        fields = ('id', 'test_version')


class BotReportDataSerializer(serializers.ModelSerializer):
    gpu_type = serializers.CharField(source='bot.gpuType', read_only=True)
    cpu_arch = serializers.CharField(source='bot.cpuArchitecture', read_only=True)
    platform = serializers.CharField(source='bot.platform', read_only=True)
    bot_enabled = serializers.BooleanField(source='bot.enabled', read_only=True)
    days_since = serializers.SerializerMethodField()
    prev_results = serializers.SerializerMethodField()
    metric_unit = serializers.SerializerMethodField()

    def get_days_since(self,obj):
        current_time = datetime.datetime.utcnow()
        return (current_time - obj.timestamp).days

    def get_prev_results(self, obj):
        if obj.prev_result:
            return {"id": obj.prev_result.id,
                    "test_version": obj.prev_result.test_version,
                    "mean_value": obj.prev_result.mean_value,
                    "timestamp": obj.prev_result.timestamp,
                    "browser_version": obj.prev_result.browser_version,
                    "stddev": obj.prev_result.stddev,
                    }
        else:
            return None

    def get_metric_unit(self, obj):
        return { "name": obj.metric_tested.name, "unit": obj.metric_tested.unit, "is_better": obj.metric_tested.is_better }

    class Meta:
        model = BotReportData
        fields = ('id', 'bot', 'gpu_type', 'cpu_arch', 'platform', 'browser', 'browser_version',
                  'root_test','test_path', 'test_version', 'metric_unit', 'mean_value', 'stddev',
                  'days_since' ,'timestamp','delta', 'bot_enabled', 'is_improvement', 'prev_results')


class BotDataCompleteSerializer(serializers.ModelSerializer):
    metric_unit = serializers.SerializerMethodField()

    def get_metric_unit(self, obj):
        return { "name": obj.metric_tested.name, "unit": obj.metric_tested.unit, "is_better": obj.metric_tested.is_better }


    class Meta:
        model = BotReportData
        fields = ('id', 'bot', 'root_test', 'test_path', 'test_version', 'metric_unit', 'mean_value', 'stddev',
                  'aggregation', 'timestamp', 'is_improvement')

