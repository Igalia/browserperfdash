import urllib

from dashboard.core.metric_units.models import MetricUnit
from dashboard.core.metric_units.serializers import MetricUnitSerializer
from dashboard.core.bots.reports.models import BotReportData
from dashboard.core.tests.models import Test

from rest_framework.generics import ListAPIView


class MetricsForTestList(ListAPIView):
    """ Show up metrics for a given test and subtest"""
    model = MetricUnit
    serializer_class = MetricUnitSerializer

    def get_queryset(self):
        return MetricUnit.objects.filter(
            name__in=BotReportData.objects.filter(
                root_test=Test.objects.filter(pk=self.kwargs.get('test')),
                test_path=urllib.parse.unquote(self.kwargs.get('subtest'))
            )[:1].values('metric_unit')
        )
