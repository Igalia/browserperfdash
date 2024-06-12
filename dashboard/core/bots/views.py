from dashboard.core.bots.models import Bot
from dashboard.core.browsers.models import Browser
from dashboard.core.bots.reports.models import BotReportData

from dashboard.core.bots.serializers import \
    BotsForResultsExistListSerializer, \
    BotsFullDetailsForResultsExistListSerializer

from rest_framework.generics import ListAPIView


class BaseBotResultsView(ListAPIView):
    model = Bot

    def get_queryset(self):
        browser_filter = self.request.query_params.get('browser', None)
        browser_filter_by = {'pk': browser_filter} if browser_filter else {}
        browsers = Browser.objects.filter(**browser_filter_by)
        return Bot.objects.filter(
            name__in=BotReportData.objects.filter(
                browser__in=browsers
            ).distinct('bot').values('bot'),
            enabled=True
        )


class BotsForResultsExistList(BaseBotResultsView):
    serializer_class = BotsForResultsExistListSerializer


class BotsFullDetailsForResultsExistList(BaseBotResultsView):
    serializer_class = BotsFullDetailsForResultsExistListSerializer
