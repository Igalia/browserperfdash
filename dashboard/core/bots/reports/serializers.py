from rest_framework import serializers

from dashboard.core.bots.reports.models import BotReportData
from dashboard.core.metric_units.serializers import MetricUnitSerializer
from dashboard.core.tests.serializers import TestListListSerializer


class TestPathListSerializer(serializers.Serializer):
    test_path = serializers.CharField()
    root_test = serializers.CharField()
    aggregation = serializers.CharField()


class TestsForBrowserBotListSerializer(serializers.Serializer):
    root_test = TestListListSerializer()


class ResultsForSubtestListSerializer(serializers.ModelSerializer):
    timestamp = serializers.SerializerMethodField()

    def get_timestamp(self,obj):
        return obj.timestamp.strftime('%s')

    class Meta:
        model = BotReportData
        fields = (
            'timestamp', 'browser', 'mean_value', 'stddev', 'browser_version',
            'delta', 'bot', 'test_version'
        )


class BotResultMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = BotReportData
        fields = ('id', 'test_version')


class BotReportDataSerializer(serializers.ModelSerializer):
    prev_results = serializers.SerializerMethodField()
    metric_unit = MetricUnitSerializer()

    def get_prev_results(self, obj):
        if not obj.prev_result:
            return None
        else:
            return {
                "id": obj.prev_result.id,
                "test_version": obj.prev_result.test_version,
                "mean_value": obj.prev_result.mean_value,
                "browser_version": obj.prev_result.browser_version,
                "stddev": obj.prev_result.stddev,
                "metric_unit_prefixed": obj.prev_result.metric_unit_prefixed
            }

    class Meta:
        model = BotReportData
        fields = (
            'id', 'bot', 'browser', 'browser_version', 'root_test',
            'test_path', 'test_version', 'metric_unit',
            'metric_unit_prefixed', 'mean_value', 'stddev', 'delta',
            'prev_results'
        )
