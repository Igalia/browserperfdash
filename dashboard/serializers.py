from rest_framework import serializers
from .models import BotReportData, Platform, GPUType, CPUArchitecture, Test, MetricUnit


class BrowsersForResultsExistListSerializer(serializers.ModelSerializer):
    browser_id = serializers.CharField()
    browser = serializers.CharField()

    class Meta:
        model = BotReportData
        fields = ('browser_id', 'browser')


class GPUTypeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = GPUType
        fields = ('id', 'name')


class CPUArchitectureListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CPUArchitecture
        fields = ('id', 'name')


class PlatformListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Platform
        fields = ('id', 'name')


class BotsForResultsExistListSerializer(serializers.Serializer):
    bot = serializers.CharField(max_length=50)


class BotsFullDetailsForResultsExistListSerializer(serializers.Serializer):
    name = serializers.CharField()
    platform = PlatformListSerializer()
    cpuArchitecture = CPUArchitectureListSerializer()
    gpuType = GPUTypeListSerializer()

    class Meta:
        fields = '__all__'


class TestListListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = ('id',)


class TestPathListSerializer(serializers.Serializer):
    test_path = serializers.CharField()
    root_test = serializers.CharField()
    aggregation = serializers.CharField()


class MetricUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetricUnit
        fields = ('name', 'unit', 'is_better')


class MetricsForTestListSerializer(serializers.Serializer):
    metric_unit = MetricUnitSerializer()


class TestsForBrowserBotListSerializer(serializers.Serializer):
    root_test = TestListListSerializer()


class ResultsForSubtestListSerializer(serializers.ModelSerializer):
    timestamp = serializers.SerializerMethodField()

    def get_timestamp(self,obj):
        return obj.timestamp.strftime('%s')

    class Meta:
        model = BotReportData
        fields = ('timestamp', 'browser', 'mean_value', 'stddev', 'browser_version', 'delta', 'bot', 'test_version')


class BotResultMinimalSerializer(serializers.ModelSerializer):

    class Meta:
        model = BotReportData
        fields = ('id', 'test_version')


class BotReportDataSerializer(serializers.ModelSerializer):
    prev_results = serializers.SerializerMethodField()
    metric_unit = MetricUnitSerializer()

    def get_prev_results(self, obj):
        if obj.prev_result:
            return {"id": obj.prev_result.id,
                    "test_version": obj.prev_result.test_version,
                    "mean_value": obj.prev_result.mean_value,
                    "browser_version": obj.prev_result.browser_version,
                    "stddev": obj.prev_result.stddev,
                    "metric_unit_prefixed": obj.prev_result.metric_unit_prefixed
                    }
        else:
            return None

    class Meta:
        model = BotReportData
        fields = ('id', 'bot', 'browser', 'browser_version', 'root_test','test_path', 'test_version', 'metric_unit',
                  'metric_unit_prefixed', 'mean_value', 'stddev', 'delta', 'prev_results')
