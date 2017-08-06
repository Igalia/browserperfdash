from dashboard.core.browsers.models import Browser
from dashboard.core.bots.reports.models import BotReportData
from dashboard.core.browsers.serializers import \
    BrowsersForResultsExistListSerializer

from rest_framework.generics import ListAPIView


class BrowsersForResultsExistList(ListAPIView):
    """List out browsers in home page and plot page"""
    model = Browser
    serializer_class = BrowsersForResultsExistListSerializer

    def get_queryset(self):
        return Browser.objects.filter(
            id__in=BotReportData.objects.distinct(
                'browser'
            ).values('browser'),
            enabled=True
        )