from dashboard.core.cpus.models import CPUArchitecture
from dashboard.core.bots.reports.models import BotReportData
from dashboard.core.cpus.serializers import CPUArchitectureListSerializer

from rest_framework.generics import ListAPIView


class CPUArchitectureForWhichResultsExistList(ListAPIView):
    """Fetch CPU Architectures for which results exist for home page"""
    model = CPUArchitecture
    serializer_class = CPUArchitectureListSerializer

    def get_queryset(self):
        return CPUArchitecture.objects.filter(
            id__in=BotReportData.objects.distinct(
                'bot__cpuArchitecture'
            ).values('bot__cpuArchitecture'),
            enabled=True
        )
