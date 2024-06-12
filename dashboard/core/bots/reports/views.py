import json
import urllib.request
import urllib.parse
import urllib.error
import logging
import sys
from datetime import datetime, timedelta

from django.http import HttpResponse, HttpResponseBadRequest

from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.generics import ListAPIView

from dashboard.core.bots.reports.models import BotReportData
from dashboard.core.bots.authentication_classes import BotAuthentication
from dashboard.core.bots.reports.utils.benchmark_results import \
    BenchmarkResults
from dashboard.core.browsers.models import Browser
from dashboard.core.bots.models import Bot
from dashboard.core.metric_units.models import MetricUnit
from dashboard.core.tests.models import Test
from dashboard.core.platforms.models import Platform
from dashboard.core.cpus.models import CPUArchitecture
from dashboard.core.gpus.models import GPUType

from dashboard.core.bots.reports.serializers import TestPathsListSerializer, \
    TestsForBrowserBotListSerializer, ResultsForSubtestListSerializer, \
    BotReportDataSerializer


log = logging.getLogger(__name__)

if len(sys.argv) > 1 and sys.argv[1] == 'test':
    log = logging.getLogger()
    log.disabled = True


db_character_separator = '\\'


class BaseReportDataListViewSerializer(ListAPIView):
    serializer_class = BotReportDataSerializer

    def build_filters(self, is_improvement=True) -> dict:
        days_since = int(self.request.query_params.get('days_since', 5))

        platform_filter = self.request.query_params.get('platform', None)
        platform_filter_by = {'pk': platform_filter} if platform_filter else {}
        platforms = Platform.objects.filter(**platform_filter_by)

        cpu_filter = self.request.query_params.get('cpu', None)
        cpu_filter_by = {'pk': cpu_filter} if cpu_filter else {}
        cpus = CPUArchitecture.objects.filter(**cpu_filter_by)

        gpu_filter = self.request.query_params.get('gpu', None)
        gpu_filter_by = {'pk': gpu_filter} if gpu_filter else {}
        gpus = GPUType.objects.filter(**gpu_filter_by)

        browser_filter = self.request.query_params.get('browser', None)
        browser_filter_by = {'pk': browser_filter} if browser_filter else {}
        browsers = Browser.objects.filter(**browser_filter_by)

        test_filter = self.request.query_params.get('test', None)
        test_filter_by = {'pk': test_filter} if test_filter else {}
        tests = Test.objects.filter(**test_filter_by)

        bot_filter = self.request.query_params.get('bot', None)
        bot_filter_by = {'pk': bot_filter} if bot_filter else {}
        bots = Bot.objects.filter(**bot_filter_by)

        bot = bots.filter(
            platform__in=platforms, cpuArchitecture__in=cpus,
            gpuType__in=gpus, enabled=True
        )
        requested_time = datetime.utcnow() + timedelta(days=-days_since)
        return {
            'timestamp__gt': requested_time,
            'root_test__in': tests,
            'bot__in': bot,
            'browser__in': browsers,
            'is_improvement': is_improvement,
        }


class BotDataReportImprovementListView(BaseReportDataListViewSerializer):
    model = BotReportData
    queryset = BotReportData.objects.filter(aggregation='None')

    def get_queryset(self):
        queryset = super(BotDataReportImprovementListView, self).get_queryset()
        filter_params = self.build_filters(is_improvement=True)
        limit = int(self.kwargs.get('limit', 10))
        return queryset.filter(**filter_params).exclude(
            prev_result__isnull=True).order_by('-delta')[:limit]


class BotDataReportRegressionListView(BaseReportDataListViewSerializer):
    model = BotReportData
    queryset = BotReportData.objects.filter(aggregation='None')

    def get_queryset(self):
        queryset = super(BotDataReportRegressionListView, self).get_queryset()
        filter_params = self.build_filters(is_improvement=False)
        limit = int(self.kwargs.get('limit', 10))
        return queryset.filter(**filter_params).exclude(
            prev_result__isnull=True).order_by('-delta')[:limit]


class TestPathsList(ListAPIView):
    serializer_class = TestPathsListSerializer

    def get_queryset(self):
        browser_filter = self.request.query_params.get('browser', None)
        browser_filter_by = {'pk': browser_filter} if browser_filter else {}
        browsers = Browser.objects.filter(**browser_filter_by)

        root_test_filter = self.request.query_params.get('root_test', None)
        root_test_filter_by = {'pk': root_test_filter} if root_test_filter \
            else {}
        root_test = Test.objects.filter(**root_test_filter_by)

        return BotReportData.objects.filter(
            browser__in=browsers, root_test__in=root_test
        ).distinct('test_path')


class TestsForBrowserBotList(ListAPIView):
    serializer_class = TestsForBrowserBotListSerializer

    def get_queryset(self):
        browser_filter = self.request.query_params.get('browser', None)
        browser_filter_by = {'pk': browser_filter} if browser_filter else {}
        browsers = Browser.objects.filter(**browser_filter_by)

        bot_filter = self.request.query_params.get('bot', None)
        bot_filter_by = {'pk': bot_filter} if bot_filter else {}
        bots = Bot.objects.filter(**bot_filter_by)

        return BotReportData.objects.filter(
            browser__in=browsers, bot__in=bots
        ).distinct('root_test')


class ResultsForSubTestList(ListAPIView):
    serializer_class = ResultsForSubtestListSerializer

    def get_queryset(self):
        browser_filter = self.request.query_params.get('browser', None)
        browser_filter_by = {'pk': browser_filter} if browser_filter else {}
        browsers = Browser.objects.filter(**browser_filter_by)

        test = Test.objects.get(pk=self.request.query_params.get('test'))
        test_path = urllib.parse.unquote(
            self.request.query_params.get('subtest')
        )

        bot_filter = self.request.query_params.get('bot', None)
        bot_filter_by = {'pk': bot_filter} if bot_filter else {}
        bots = Bot.objects.filter(**bot_filter_by)

        return BotReportData.objects.filter(
            browser__in=browsers, root_test=test, test_path=test_path,
            bot__in=bots
        ).order_by('timestamp')


class BotReportView(APIView):
    """View to accept in report data from evaluation bots"""
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
                curr_string += format(mean_value, '.2f') + \
                    " " + original_prefix
                return curr_string

            munits = munits[index + 1:]
            factor = mean_value / prefix['unit']

            if factor >= 1:
                # divisible, should add it to string
                mean_value = factor % 1 * prefix['unit']
                curr_string += str(int(factor)) + " " + prefix['symbol'] + " "

            return cls.calculate_prefix(
                munits, mean_value, curr_string, original_prefix
            )

    @classmethod
    def process_delta_and_improvement(cls, bot, browser, root_test, test_path,
                                      mean_value, current_metric, aggregation):
        delta = 0.0
        # We take in the previous result (if exists)
        previous_result = BotReportData.objects.filter(
            bot=bot, browser=browser, root_test=root_test, test_path=test_path,
            metric_unit=current_metric, aggregation=aggregation
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
        """
        The API expects POST data on /dash/bot-report/ in the following format:
            upload_data = OrderedDict([
            ('bot_id', 'bot_name'),('bot_password', 'bot_password'),
            ('browser_id', 'test_browser'),
            ('browser_version', 'browser_version'), ('test_id', 'test_id'),
            ('test_version', 'test_veresion'),
            ('test_data', '{"RootTest": {"metrics": {"Time": {"current":
            [1, 2, 3]},
                "Score": {"current": [2, 3, 4]}}}}')
            ])
        """
        try:
            browser_id = self.request.POST.get('browser_id')
            browser_version = self.request.POST.get('browser_version')
            test_id = self.request.POST.get('test_id')
            test_version = self.request.POST.get('test_version')
            bot_id = self.request.POST.get('bot_id')
            json_data = self.request.POST.get('test_data')
        except AttributeError:
            log.error(
                'Got invalid params from the bot: {0}'.format(request.auth))
            return HttpResponseBadRequest(
                'Some params are missing in the request'
            )

        log.info('Started processing data from bot {0}'.format(bot_id))
        # The timestamp may/may not be there - hence not checking
        timestamp = None
        if self.request.POST.get('timestamp'):
            timestamp = datetime.fromtimestamp(
                float(self.request.POST.get('timestamp'))
            )
        try:
            test_data = json.loads(json_data)
        except AttributeError:
            return HttpResponseBadRequest(
                'Error parsing JSON file from bot: {0}'.format(request.auth)
            )

        bot = Bot.objects.get(pk=bot_id)

        if not bot.enabled:
            log.error('Got data from disabled bot: {0}'.format(bot_id))
            return HttpResponseBadRequest(
                'The bot {0} is not enabled'.format(bot_id))

        try:
            browser = Browser.objects.get(pk=browser_id)
        except Browser.DoesNotExist:
            log.error(
                'Got invalid browser {0} from bot: {1}'.format(
                    browser_id, bot_id)
            )
            return HttpResponseBadRequest('The browser does not exist')

        try:
            root_test = Test.objects.get(pk=test_id)
        except Test.DoesNotExist:
            log.error(
                'Got invalid root test: {0} from bot: {1} for browser: {2}, '
                'browser_version: {3}'.format(
                    test_id, bot_id, browser_id, browser_version)
            )
            return HttpResponseBadRequest(
                'The test {0} does not exist'.format(test_id)
            )

        test_data_results = BenchmarkResults(test_data)
        results_table = test_data_results.fetch_db_entries(
            skip_aggregated=False
        )

        for result in results_table:
            raw_path = result['name']

            metric_name = self.extract_metric(result['metric'])
            stddev = float(result['stdev'])
            mean_value = float(result['value'])
            unit = result['unit']

            try:
                current_metric = MetricUnit.objects.get(pk=metric_name)
                if len(current_metric.prefix) > 0:
                    modified_prefix = self.calculate_prefix(
                        current_metric.prefix, mean_value, curr_string="",
                        original_prefix=current_metric.unit
                    )
                else:
                    modified_prefix = str(mean_value) + \
                        " " + current_metric.unit
            except MetricUnit.DoesNotExist:
                log.error(
                    'Got wrong Metric {0} for bot: {1}, browser: {2}, '
                    'browser_version: {3}, root_test: {4}, test_description: '
                    '{5}'.format(
                        metric_name, bot_id, browser_id, browser_version,
                        test_id, raw_path)
                )
                return HttpResponseBadRequest(
                    'The Metric Unit {0} does not exist'.format(metric_name)
                )

            if current_metric.unit != unit:
                log.error(
                    'Got wrong unit {0} for metric unit {1} data for bot: '
                    '{2}, browser: {3}, browser_version: {4}, root_test: {5}, '
                    'test_description: {6}'.format(
                        unit, metric_name, bot_id, browser_id,
                        browser_version, test_id, raw_path
                    )
                )
                return HttpResponseBadRequest(
                    'The received unit: {0} field of Metric Unit {1} does not '
                    'match'.format(unit, metric_name))

            if self.is_aggregated(metric=result['metric']):
                aggregation = self.extract_aggregation(metric=result['metric'])
            else:
                aggregation = 'None'

            # Calculate the change and store it during processing the POST
            delta_and_prev_results = self.process_delta_and_improvement(
                bot, browser, root_test, raw_path, mean_value,
                current_metric, aggregation
            )

            try:
                BotReportData.objects.create_report(
                    bot=bot, browser=browser, browser_version=browser_version,
                    root_test=root_test, test_path=raw_path,
                    test_version=test_version, aggregation=aggregation,
                    metric_unit=current_metric,
                    metric_unit_prefixed=modified_prefix,
                    mean_value=mean_value,
                    stddev=stddev, delta=delta_and_prev_results[0],
                    is_improvement=delta_and_prev_results[1],
                    prev_result=delta_and_prev_results[2], timestamp=timestamp
                )
            except Exception as e:
                log.error(
                    'Failed inserting data for bot: {0}, browser: {1}, '
                    'browser_version: {2}, root_test: {3}, test_description: '
                    '{4} and Exception {5}'.format(
                        bot_id, browser_id, browser_version, test_id,
                        raw_path, e)
                )
                return HttpResponseBadRequest(
                    'Exception while inserting the data: {0}'.format(e))

        return HttpResponse('The POST went through')
