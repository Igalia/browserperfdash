from rest_framework import serializers
from .models import BotReportData


# Serializers define the API representation.
class BotReportDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = BotReportData
        fields = ('bot', 'browser', 'browser_version', 'root_test', 'test_path', 'test_version',
                  'metric_tested', 'mean_value', 'stddev', 'timestamp')