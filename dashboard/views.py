from django.views.generic import TemplateView
from django.http import HttpResponse, HttpResponseBadRequest
from rest_framework.views import APIView
from rest_framework import authentication, permissions
from rest_framework import generics
from dashboard.models import *
from rest_framework import exceptions
import json
from helpers.benchmark_results import BenchmarkResults
from django.views.generic import ListView
from .serializers import *
from datetime import datetime, timedelta

import logging

log = logging.getLogger(__name__)
db_character_separator = '\\'

class BotAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        bot_name = request.POST.get('bot_id')
        bot_password = request.POST.get('bot_password')

        if not bot_name or not bot_password:
            return None

        try:
            bot = Bot.objects.get(name=bot_name)
            if bot.password != bot_password:
                raise exceptions.AuthenticationFailed('Bad authentication details')
        except Bot.DoesNotExist:
            raise exceptions.AuthenticationFailed('This bot cannot be authenticated')

        return (bot, bot_name)


class BotDataReportImprovementListView(generics.ListAPIView):
    model = BotReportData
    serializer_class = BotReportDataSerializer
    queryset = BotReportData.objects.filter(aggregation='None')

    def get_queryset(self):
        try:
            days_since = int(self.kwargs.get('days_since'))
        except ValueError:
            days_since = int(5)

        if not self.kwargs.get('platform') or self.kwargs.get('platform') == 'all':
            platform_obj = Platform.objects.all()
        elif self.kwargs.get('platform') != 'all':
            platform_obj = Platform.objects.filter(pk=self.kwargs.get('platform'))

        if not self.kwargs.get('cpu') or self.kwargs.get('cpu') == 'all':
            cpu_obj = CPUArchitecture.objects.all()
        elif self.kwargs.get('cpu') != 'all':
            cpu_obj = CPUArchitecture.objects.filter(pk=self.kwargs.get('cpu'))

        if not self.kwargs.get('gpu') or self.kwargs.get('gpu') == 'all':
            gpu_obj = GPUType.objects.all()
        elif self.kwargs.get('gpu') != 'all':
            gpu_obj = GPUType.objects.filter(pk=self.kwargs.get('gpu'))

        if not self.kwargs.get('browser') or self.kwargs.get('browser') == 'all':
            browser_obj = Browser.objects.all()
        elif self.kwargs.get('browser') != 'all':
            browser_obj = Browser.objects.filter(pk=self.kwargs.get('browser'))

        bot = Bot.objects.filter(platform__in=platform_obj, cpuArchitecture__in=cpu_obj, gpuType__in=gpu_obj,
                                 enabled=True)
        requested_time = datetime.utcnow() + timedelta(days=-days_since)
        queryset = super(BotDataReportImprovementListView, self).get_queryset()
        return queryset.filter(aggregation='None', timestamp__gt=requested_time,
                               bot__in=bot, browser__in=browser_obj, is_improvement=True).order_by('-delta')[:30]


class BotDataReportRegressionListView(generics.ListAPIView):
    model = BotReportData
    serializer_class = BotReportDataSerializer
    queryset = BotReportData.objects.filter(aggregation='None')

    def get_queryset(self):
        try:
            days_since = int(self.kwargs.get('days_since'))
        except ValueError:
            days_since = int(5)

        if not self.kwargs.get('platform') or self.kwargs.get('platform') == 'all':
            platform_obj = Platform.objects.all()
        elif self.kwargs.get('platform') != 'all':
            platform_obj = Platform.objects.filter(pk=self.kwargs.get('platform'))

        if not self.kwargs.get('cpu') or self.kwargs.get('cpu') == 'all':
            cpu_obj = CPUArchitecture.objects.all()
        elif self.kwargs.get('cpu') != 'all':
            cpu_obj = CPUArchitecture.objects.filter(pk=self.kwargs.get('cpu'))

        if not self.kwargs.get('gpu') or self.kwargs.get('gpu') == 'all':
            gpu_obj = GPUType.objects.all()
        elif self.kwargs.get('gpu') != 'all':
            gpu_obj = GPUType.objects.filter(pk=self.kwargs.get('gpu'))

        if not self.kwargs.get('browser') or self.kwargs.get('browser') == 'all':
            browser_obj = Browser.objects.all()
        elif self.kwargs.get('browser') != 'all':
            browser_obj = Browser.objects.filter(pk=self.kwargs.get('browser'))

        bot = Bot.objects.filter(platform__in=platform_obj, cpuArchitecture__in=cpu_obj, gpuType__in=gpu_obj,
                                 enabled=True)
        requested_time = datetime.utcnow() + timedelta(days=-days_since)
        queryset = super(BotDataReportRegressionListView, self).get_queryset()
        return queryset.filter(aggregation='None', timestamp__gt=requested_time,
                               bot__in=bot, browser__in=browser_obj, is_improvement=False).order_by('-delta')[:30]

class BotDataCompleteListView(generics.ListCreateAPIView):
    model = BotReportData
    queryset = BotReportData.objects.all()
    serializer_class = BotDataCompleteSerializer


class BotDataReportDetailView(generics.RetrieveAPIView):
    model = BotReportData
    queryset = BotReportData.objects.all()
    serializer_class = BotReportDataSerializer


class BotResultsForTestListView(generics.ListAPIView):
    model = BotReportData
    queryset = BotReportData.objects.filter(aggregation='None')
    serializer_class = BotReportDataSerializer

    def get_queryset(self):
        obj = BotReportData.objects.get(pk=self.kwargs.get('pk'))
        queryset = super(BotResultsForTestListView, self).get_queryset()
        return queryset.filter(browser=obj.browser, root_test=obj.root_test, test_path=obj.test_path,
                               aggregation=obj.aggregation, bot=obj.bot)


class BrowsersList(generics.ListAPIView):
    model = Browser
    queryset = Browser.objects.filter(enabled=True)
    serializer_class = BrowserListSerializer


class BrowsersForResultsExistList(generics.ListAPIView):
    model = BotReportData
    queryset = BotReportData.objects.distinct('browser')
    serializer_class = BrowsersForResultsExistListSerializer


class BotsList(generics.ListAPIView):
    model = Bot
    queryset = Bot.objects.filter(enabled=True)
    serializer_class = BotListSerializer


class BotDetailView(generics.RetrieveAPIView):
    model = Bot
    queryset = Bot.objects.all()
    serializer_class = BotDetailsListSerializer


class BotsForResultsExistList(generics.ListAPIView):
    serializer_class = BotsForResultsExistListSerializer

    def get_queryset(self):
        browser = Browser.objects.filter(pk=self.kwargs.get('browser'))
        return BotReportData.objects.filter(browser=browser).distinct('bot')


class PlatformList(generics.ListAPIView):
    model = Platform
    queryset = Platform.objects.filter(enabled=True)
    serializer_class = PlatformListSerializer


class GPUTypeList(generics.ListAPIView):
    model = GPUType
    queryset = GPUType.objects.filter(enabled=True)
    serializer_class = GPUTypeListSerializer


class CPUArchitectureList(generics.ListAPIView):
    model = CPUArchitecture
    queryset = CPUArchitecture.objects.filter(enabled=True)
    serializer_class = CPUArchitectureListSerializer


class TestList(generics.ListAPIView):
    model = Test
    queryset = Test.objects.filter(enabled=True)
    serializer_class = TestListListSerializer


class TestPathList(generics.ListAPIView):
    serializer_class = TestPathListSerializer

    def get_queryset(self):
        browser = Browser.objects.filter(pk=self.kwargs.get('browser'))
        test = Test.objects.filter(pk=self.kwargs.get('test'))
        return BotReportData.objects.filter(browser=browser, root_test=test).distinct('test_path')


class MetricsForTestList(generics.ListAPIView):
    serializer_class = MetricsForTestListSerializer

    def get_queryset(self):
        test = Test.objects.filter(pk=self.kwargs.get('test'))
        test_path = self.kwargs.get('subtest')
        return BotReportData.objects.filter(root_test=test, test_path=test_path)[:1]


class TestsForBrowserBottList(generics.ListAPIView):
    serializer_class = TestsForBrowserBottListSerializer

    def get_queryset(self):
        browser = Browser.objects.get(pk=self.kwargs.get('browser'))
        try:
            bot = Bot.objects.get(pk=self.kwargs.get('bot'))
            return BotReportData.objects.filter(browser=browser, bot=bot).distinct('root_test')
        except Bot.DoesNotExist:
            return BotReportData.objects.filter(browser=browser).distinct('root_test')




class ResultsForSubtestList(generics.ListAPIView):
    serializer_class = ResultsForSubtestListSerializer

    def get_queryset(self):
        browser = Browser.objects.get(pk=self.kwargs.get('browser'))
        test = Test.objects.get(pk=self.kwargs.get('test'))
        test_path = self.kwargs.get('subtest')
        try:
            bot = Bot.objects.get(pk=self.kwargs.get('bot'))
            return BotReportData.objects.filter(browser=browser, root_test=test, test_path=test_path, bot=bot) \
                .order_by('timestamp')
        except Bot.DoesNotExist:
            return BotReportData.objects.filter(browser=browser, root_test=test, test_path=test_path).order_by('timestamp')



class DefaultHomeView(ListView):
    template_name="index.html"

    def get_queryset(self):
        return BotReportData.objects.all()


class GraphPlotView(TemplateView):
    template_name = "plot.html"


class BotReportView(APIView):
    authentication_classes = (BotAuthentication,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    @classmethod
    def is_aggregated(cls, metric):
        return not metric.endswith(":None")

    @classmethod
    def extract_metric(cls, metric):
        return metric.split(db_character_separator)[0]

    @classmethod
    def extract_aggregation(cls, metric):
        return metric.split(db_character_separator)[1]

    @classmethod
    def calculate_prefix(cls, munits, mean_value, curr_string, original_prefix):
        for index, prefix in enumerate(munits):
            if len(munits) == 1:
                if mean_value > prefix['unit']:
                    mean_value = mean_value / prefix['unit']
                curr_string += format(mean_value, '.2f') + " " + original_prefix
                return curr_string

            munits = munits[index + 1:]
            factor = mean_value / prefix['unit']

            if factor >= 1:
                # divisible, should add it to string
                mean_value = factor % 1 * prefix['unit']
                curr_string += str(int(factor)) + " " + prefix['symbol'] + " "

            return cls.calculate_prefix(munits, mean_value, curr_string, original_prefix)


    @classmethod
    def process_delta_and_improvement(cls, browser, root_test, test_path, mean_value, current_metric):
        delta = 0.0
        # We take in the previous result (if exists)
        previous_result = BotReportData.objects.filter(browser=browser, root_test=root_test, test_path=test_path
                                                       ).order_by('-timestamp')[:1]

        is_improvement = False
        prev_result = None
        if previous_result:
            for res in previous_result:
                prev_result = res
                delta = abs(1-float(res.mean_value)/float(mean_value))*100.00
                if current_metric.is_better == 'up':
                    if float(res.mean_value) < float(mean_value):
                        is_improvement = True
                elif current_metric.is_better == 'dw':
                    if float(res.mean_value) > float(mean_value):
                        is_improvement = True

        return [delta, is_improvement, prev_result]

    def post(self, request, format=None):
        try:
            browser_id = self.request.POST.get('browser_id')
            browser_version = self.request.POST.get('browser_version')
            test_id = self.request.POST.get('test_id')
            test_version = self.request.POST.get('test_version')
            bot_id = self.request.POST.get('bot_id')
            json_data = self.request.POST.get('test_data')
        except AttributeError:
            log.error("Got invalid params from the bot: %s"% request.auth)
            return HttpResponseBadRequest("Some params are missing in the request")

        log.info("Started processing data from bot %s" % (bot_id))
        # The timestamp may/may not be there - hence not checking
        timestamp = datetime.datetime.fromtimestamp(float(self.request.POST.get('timestamp'))) \
            if self.request.POST.get('timestamp') else None
        try:
            test_data = json.loads(json_data)
        except AttributeError:
            return HttpResponseBadRequest("Error parsing JSON file from bot: %s "% request.auth)

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

        test_data_results = BenchmarkResults(test_data)
        results_table = test_data_results.fetch_db_entries(skip_aggregated=False)

        for result in results_table:
            raw_path = result['name']

            metric_name = self.extract_metric(result['metric'])
            stddev = float(result['stdev'])
            mean_value = float(result['value'])
            unit = result['unit']

            try:
                current_metric = MetricUnit.objects.get(pk=metric_name)
                if len(current_metric.prefix) > 0:
                    modified_prefix = self.calculate_prefix(current_metric.prefix, mean_value, curr_string="",
                                                            original_prefix=current_metric.unit)
                else:
                    modified_prefix = str(mean_value) + " " + current_metric.unit
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

            # Calculate the change and store it during processing the POST
            delta_improvements = self.process_delta_and_improvement(browser, root_test, raw_path, mean_value, current_metric)
            delta = delta_improvements[0]
            is_improvement = delta_improvements[1]
            prev_result = delta_improvements[2]

            report = BotReportData.objects.create_report(bot=bot, browser=browser, browser_version=browser_version,
                                                         root_test=root_test, test_path=raw_path,
                                                         test_version=test_version, aggregation=aggregation,
                                                         metric_unit=current_metric, metric_unit_prefixed=modified_prefix,
                                                         mean_value=mean_value, stddev=stddev,delta=delta,
                                                         is_improvement=is_improvement, prev_result=prev_result,
                                                         timestamp=timestamp)
            if not report:
                log.error("Failed inserting data for bot: %s, browser: %s, browser_version: %s, root_test: %s, "
                          "test_description: %s" % (bot_id, browser_id, browser_version, test_id,raw_path)
                          )

        return HttpResponse("The POST went through")