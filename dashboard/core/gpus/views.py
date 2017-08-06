from dashboard.core.gpus.models import GPUType
from dashboard.core.bots.reports.models import BotReportData
from dashboard.core.gpus.serializers import GPUTypeListSerializer

from rest_framework.generics import ListAPIView


class GPUTypeForWhichResultsExistList(ListAPIView):
    """Fetch GPU Types for which results exist for home page"""
    model = GPUType
    serializer_class = GPUTypeListSerializer

    def get_queryset(self):
        return GPUType.objects.filter(
            id__in=BotReportData.objects.distinct(
                'bot__gpuType'
            ).values('bot__gpuType'),
            enabled=True
        )