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
import datetime

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

    @classmethod
    def is_aggregated(cls, metric):
        return not metric.endswith(":None")

    @classmethod
    def extract_metric(cls, metric):
        return metric.split(':')[0]

    @classmethod
    def extract_aggregation(cls, metric):
        return metric.split(':')[1]

    def post(self, request, format=None):
        browser_id = self.request.POST.get('browser_id')
        browser_version = self.request.POST.get('browser_version')
        test_id = self.request.POST.get('test_id')
        test_data = json.load(self.request.FILES.get('test_data'))
        test_version = self.request.POST.get('test_version')
        bot_id = self.request.POST.get('bot_id')
        bot = Bot.objects.get(pk=bot_id)

        if not bot.enabled:
            log.error("Got data from disabled bot: %s" % (bot_id))
            return HttpResponseBadRequest("The bot %s is not enabled"% bot_id)

        try:
            browser = Browser.objects.get(pk=browser_id)
        except Browser.DoesNotExist:
            log.error("Got invalid browser %s from bot: %s" % (browser_id, bot_id))
            return HttpResponseBadRequest("The browser does not exist")
        try:
            root_test = Test.objects.get(pk=test_id)
        except Test.DoesNotExist:
            log.error("Got invalid root test: %s from bot: %s for browser: %s, browser_version: %s" %
                      (test_id, bot_id, browser_id, browser_version))
            return HttpResponseBadRequest("The test %s does not exist"% test_id )

        test_data_id = test_data.keys()[0]
        if test_data_id != test_id:
            return HttpResponseBadRequest("The data do not correspond to the test param")

        test_data_results = BenchmarkResults(test_data)
        results_table = BenchmarkResults._generate_db_entries(test_data_results._results)

        for result in results_table:
            raw_path = result['name']

            metric_name = self.extract_metric(result['metric'])
            stddev = float(result['stdev'])
            mean_value = float(result['value'])
            unit = result['unit']

            try:
                current_metric = MetricUnit.objects.get(pk=metric_name)
            except MetricUnit.DoesNotExist:
                log.error("Got wrong Metric %s for bot: %s, browser: %s, browser_version: %s, root_test: %s,"
                          " test_description: %s" % (metric_name, bot_id, browser_id, browser_version, test_id, raw_path)
                          )
                return HttpResponseBadRequest("The Metric Unit %s does not exist"% metric_name)

            if current_metric.unit != unit:
                log.error("Got wrong unit %s for metric unit %s data for bot: %s, browser: %s, browser_version: %s, "
                          "root_test: %s, test_description: %s" % (unit, metric_name, bot_id, browser_id, browser_version,
                                                                   test_id, raw_path)
                          )
                return HttpResponseBadRequest("The received unit: %s field of Metric Unit %s does not match" % (unit,metric_name))

            if self.is_aggregated(metric=result['metric']):
                aggregation = self.extract_aggregation(metric=result['metric'])
            else:
                aggregation = 'None'

            report = BotReportData.objects.create_report(bot=bot, browser=browser, browser_version=browser_version,
                                                         root_test=root_test, test_path=raw_path,
                                                         test_version=test_version, aggregation=aggregation,
                                                         metric_tested= current_metric, mean_value=mean_value,
                                                         stddev=stddev
                                                         )
            if report:
                log.info("Correctly received data for bot: %s, browser: %s, browser_version: %s, root_test: %s,"
                         " test_description: %s" % (bot_id, browser_id, browser_version, test_id,raw_path)
                         )
            else:
                log.error("Failed inserting data for bot: %s, browser: %s, browser_version: %s, root_test: %s, "
                          "test_description: %s" % (bot_id, browser_id, browser_version, test_id,raw_path)
                          )

        return HttpResponse("<p> The POST went through \n %s</p>")