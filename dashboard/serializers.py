from rest_framework import serializers
from .models import BotReportData, Browser, Bot, Platform, GPUType, CPUArchitecture, Test, MetricUnit

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


class BotDetailsListSerializer(serializers.ModelSerializer):
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
    aggregation = serializers.CharField()


class TestVersionForTestPathListSerializer(serializers.Serializer):
    test_version = serializers.CharField(max_length=500)
    metrics = serializers.SerializerMethodField()

    def get_metrics(self,obj):
        return { 'metric': obj.metric_unit.name, 'is_better': obj.metric_unit.is_better }


class ResultsForVersionListSerializer(serializers.Serializer):
    timestamp = serializers.SerializerMethodField()
    mean_value = serializers.FloatField()
    stddev = serializers.FloatField()
    browser_version = serializers.CharField(max_length=500)
    delta = serializers.FloatField()
    unit = serializers.SerializerMethodField()
    is_better = serializers.SerializerMethodField()
    bot = serializers.CharField()
    test_version = serializers.CharField()

    def get_unit(self,obj):
        return obj.metric_unit.unit

    def get_is_better(self,obj):
        return obj.metric_unit.is_better

    def get_timestamp(self,obj):
        return obj.timestamp.strftime('%s')


class BotResultMinimalSerializer(serializers.ModelSerializer):

    class Meta:
        model = BotReportData
        fields = ('id', 'test_version')


class MetricUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetricUnit
        fields = ('name', 'unit', 'is_better')


class BotReportDataSerializer(serializers.ModelSerializer):
    prev_results = serializers.SerializerMethodField()
    metric_unit = MetricUnitSerializer()

    def get_prev_results(self, obj):
        if obj.prev_result:
            return {"id": obj.prev_result.id,
                    "test_version": obj.prev_result.test_version,
                    "mean_value": obj.prev_result.mean_value,
                    "timestamp": obj.prev_result.timestamp,
                    "browser_version": obj.prev_result.browser_version,
                    "stddev": obj.prev_result.stddev,
                    "metric_unit_prefixed": obj.prev_result.metric_unit_prefixed
                    }
        else:
            return None

    class Meta:
        model = BotReportData
        fields = ('id', 'bot', 'browser', 'browser_version', 'root_test','test_path', 'test_version', 'metric_unit',
                  'metric_unit_prefixed', 'mean_value', 'stddev', 'timestamp', 'delta', 'is_improvement', 'prev_results')


class BotDataCompleteSerializer(serializers.ModelSerializer):
    metric_unit = serializers.SerializerMethodField()

    def get_metric_unit(self, obj):
        return { "name": obj.metric_unit.name, "unit": obj.metric_unit.unit, "is_better": obj.metric_unit.is_better }


    class Meta:
        model = BotReportData
        fields = ('id', 'bot', 'root_test', 'test_path', 'test_version', 'metric_unit', 'mean_value', 'stddev',
                  'aggregation', 'timestamp', 'is_improvement')

