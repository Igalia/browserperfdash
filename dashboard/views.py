from django.shortcuts import render
from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.http import Http404
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotAllowed
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from rest_framework import generics
from dashboard.models import *
from rest_framework import exceptions
import json
from pprint import pprint
from helpers.benchmark_results import BenchmarkResults

import logging

log = logging.getLogger(__name__)


class BotAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        bot_name = request.POST.get('bot_id')
        bot_password = request.POST.get('bot_password')

        if not bot_name or not bot_password:
            return None

        try:
            bot = Bot.objects.get(name=bot_name)
            if bot.password != bot_password:
                return None
        except Bot.DoesNotExist:
            raise exceptions.AuthenticationFailed('This bot cannot be authenticated')

        return (bot, None)


class HomePageView(TemplateView):
    template_name="index.html"


class BotReportView(APIView):
    authentication_classes = (BotAuthentication,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def post(self, request, format=None):
        browser_id = self.request.POST.get('browser_id')
        browser_version = self.request.POST.get('browser_version')
        test_id = self.request.POST.get('test_id')
        test_data = json.load(self.request.FILES.get('test_data'))
        test_version = self.request.POST.get('test_version')
        bot = Bot.objects.get(pk=self.request.POST.get('bot_id'))
        try:
            browser = Browser.objects.get(pk=browser_id)
        except Browser.DoesNotExist:
            return HttpResponseBadRequest("The browser does not exist")
        try:
            test = Test.objects.get(pk=test_id)
        except Test.DoesNotExist:
            return HttpResponseBadRequest("The test does not exist")

        test_data_id = test_data.keys()[0]
        if test_data_id != test_id:
            return HttpResponseBadRequest("The data do not correspond to the test param")

        test_data_results = BenchmarkResults(test_data).format_dict()
        metrics_data = test_data_results[test_data_id]['metrics']
        metrics = []
        for metric in metrics_data:
            metrics.append(metric)

        for metric in metrics:
            aggregator = metrics_data[metric].keys()[0]
            try:
                current_metric = MetricUnit.objects.get(pk=metric)
            except MetricUnit.DoesNotExist:
                return HttpResponseBadRequest("The Metric Unit does not exist")
            if aggregator is None or aggregator in ['Total', 'Arithmetic', 'Geometric']:
                unit = metrics_data[metric].get(aggregator)['unit']
                if unit != current_metric.unit:
                    return HttpResponseBadRequest("The unit provided is inconsistent with the metric tested")

                raw_values = json.dumps(metrics_data[metric].get(aggregator)['raw_values'])
                stddev = float(metrics_data[metric].get(aggregator)['stdev'])
                mean_value = float(metrics_data[metric].get(aggregator)['mean_value'])

                BotReportData.objects.create_report(bot=bot, browser=browser, browser_version=browser_version,
                                                    test=test, test_version=test_version, aggregation='Total',
                                                    metric_tested=current_metric, mean_value=mean_value, stddev=stddev,
                                                    raw_values=raw_values)
                print("Data inserted for %s"% metric)

        return HttpResponse("<p> The POST went through, and inserted data correctly </p>")