from dashboard.core.metric_units.models import MetricUnit
from rest_framework import serializers


class MetricUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetricUnit
        fields = ('name', 'unit', 'is_better')
