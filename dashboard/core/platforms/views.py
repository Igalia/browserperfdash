from dashboard.core.platforms.models import Platform
from dashboard.core.bots.reports.models import BotReportData
from dashboard.core.platforms.serializers import PlatformListSerializer

from rest_framework.generics import ListAPIView


class PlatformForWhichResultsExistList(ListAPIView):
    """Fetch platforms for which results exist for home page"""
    model = Platform
    serializer_class = PlatformListSerializer

    def get_queryset(self):
        return Platform.objects.filter(
            id__in=BotReportData.objects.distinct(
                'bot__platform'
            ).values('bot__platform'),
            enabled=True
        )

