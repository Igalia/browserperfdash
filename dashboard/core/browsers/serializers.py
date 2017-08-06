from dashboard.core.browsers.models import Browser
from rest_framework import serializers


class BrowsersForResultsExistListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Browser
        fields = ('id', 'name')