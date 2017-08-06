from dashboard.core.bots.models import Bot
from dashboard.core.browsers.models import Browser
from dashboard.core.bots.reports.models import BotReportData

from dashboard.core.bots.serializers import \
    BotsForResultsExistListSerializer, \
    BotsFullDetailsForResultsExistListSerializer

from rest_framework.generics import ListAPIView


class BotsForResultsExistList(ListAPIView):
    """Fetch just the botname for the plot pages"""
    model = Bot
    serializer_class = BotsForResultsExistListSerializer

    def get_queryset(self):
        if self.kwargs.get('browser') == 'all':
            browser_obj = Browser.objects.all()
        else:
            browser_obj = Browser.objects.filter(
                pk=self.kwargs.get('browser')
            )
        return Bot.objects.filter(
            name__in=BotReportData.objects.filter(
                browser__in=browser_obj
            ).distinct('bot').values('bot'),
            enabled=True
        )


class BotsFullDetailsForResultsExistList(ListAPIView):
    """Fetch detailed bot fields for the home page"""
    model = Bot
    serializer_class = BotsFullDetailsForResultsExistListSerializer

    def get_queryset(self):
        if self.kwargs.get('browser') == 'all':
            browser_obj = Browser.objects.all()
        else:
            browser_obj = Browser.objects.filter(
                pk=self.kwargs.get('browser')
            )
        return Bot.objects.filter(
            name__in=BotReportData.objects.filter(
                browser__in=browser_obj
            ).distinct('bot').values('bot'),
            enabled=True
        )


