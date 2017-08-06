from dashboard.core.tests.models import Test
from rest_framework import serializers


class TestListListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = ('id',)