import json, urllib.request, urllib.parse, urllib.error, logging, sys
from datetime import datetime, timedelta
from threading import Thread
import time

from django.http import HttpResponse, HttpResponseBadRequest, StreamingHttpResponse

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

from dashboard.core.bots.reports.serializers import TestPathListSerializer, \
    TestsForBrowserBotListSerializer, ResultsForSubtestListSerializer, \
    BotReportDataSerializer


log = logging.getLogger(__name__)

if len(sys.argv) > 1 and sys.argv[1] == 'test':
    log = logging.getLogger()
    log.disabled = True


db_character_separator = '\\'

# https://stackoverflow.com/a/6894023
# https://alexandra-zaharia.github.io/posts/how-to-return-a-result-from-a-python-thread/
class ThreadWithReturnValue(Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._return_value = None

    def run(self):
        if self._target is not None:
            self._return_value = self._target(*self._args, **self._kwargs)

    def join(self, *args, **kwargs):
        super().join(*args, **kwargs)
        return self._return_value


class BotDataReportImprovementListView(ListAPIView):
    """Fetch improvements for main page tables"""

    model = BotReportData
    serializer_class = BotReportDataSerializer
    queryset = BotReportData.objects.filter(aggregation='None')

    def get_queryset(self):
        try:
            days_since = int(self.kwargs.get('days_since'))
        except ValueError:
            days_since = int(5)

        if self.kwargs.get('platform') == 'all':
            platform_obj = Platform.objects.all()
        else:
            platform_obj = Platform.objects.filter(pk=self.kwargs.get('platform'))

        if self.kwargs.get('cpu') == 'all':
            cpu_obj = CPUArchitecture.objects.all()
        else:
            cpu_obj = CPUArchitecture.objects.filter(pk=self.kwargs.get('cpu'))

        if self.kwargs.get('gpu') == 'all':
            gpu_obj = GPUType.objects.all()
        else:
            gpu_obj = GPUType.objects.filter(pk=self.kwargs.get('gpu'))

        if self.kwargs.get('browser') == 'all':
            browser_obj = Browser.objects.all()
        else:
            browser_obj = Browser.objects.filter(pk=self.kwargs.get('browser'))

        if self.kwargs.get('test') == 'all':
            root_test = Test.objects.all()
        else:
            root_test = Test.objects.filter(pk=self.kwargs.get('test'))

        if self.kwargs.get('bot') == 'all':
            bot_obj = Bot.objects.all()
        else:
            bot_obj = Bot.objects.filter(pk=self.kwargs.get('bot'))

        limit = int(self.kwargs.get('limit'))
        bot = bot_obj.filter(
            platform__in=platform_obj, cpuArchitecture__in=cpu_obj,
            gpuType__in=gpu_obj, enabled=True
        )

        requested_time = datetime.utcnow() + timedelta(days=-days_since)
        queryset = super(BotDataReportImprovementListView, self).get_queryset()
        return queryset.filter(
            aggregation='None', timestamp__gt=requested_time,
            root_test__in=root_test, bot__in=bot, browser__in=browser_obj,
            is_improvement=True
        ).order_by('-delta')[:limit]


class BotDataReportRegressionListView(ListAPIView):
    """Fetch regressions for main page tables"""

    model = BotReportData
    serializer_class = BotReportDataSerializer
    queryset = BotReportData.objects.filter(aggregation='None')

    def get_queryset(self):
        try:
            days_since = int(self.kwargs.get('days_since'))
        except ValueError:
            days_since = int(5)

        if self.kwargs.get('platform') == 'all':
            platform_obj = Platform.objects.all()
        else:
            platform_obj = Platform.objects.filter(pk=self.kwargs.get('platform'))

        if self.kwargs.get('cpu') == 'all':
            cpu_obj = CPUArchitecture.objects.all()
        else:
            cpu_obj = CPUArchitecture.objects.filter(pk=self.kwargs.get('cpu'))

        if self.kwargs.get('gpu') == 'all':
            gpu_obj = GPUType.objects.all()
        else:
            gpu_obj = GPUType.objects.filter(pk=self.kwargs.get('gpu'))

        if self.kwargs.get('browser') == 'all':
            browser_obj = Browser.objects.all()
        else:
            browser_obj = Browser.objects.filter(pk=self.kwargs.get('browser'))

        if self.kwargs.get('test') == 'all':
            root_test = Test.objects.all()
        else:
            root_test = Test.objects.filter(pk=self.kwargs.get('test'))

        if self.kwargs.get('bot') == 'all':
            bot_obj = Bot.objects.all()
        else:
            bot_obj = Bot.objects.filter(pk=self.kwargs.get('bot'))

        limit = int(self.kwargs.get('limit'))
        bot = bot_obj.filter(
            platform__in=platform_obj, cpuArchitecture__in=cpu_obj,
            gpuType__in=gpu_obj, enabled=True
        )
        requested_time = datetime.utcnow() + timedelta(days=-days_since)
        queryset = super(BotDataReportRegressionListView, self).get_queryset()
        return queryset.filter(
            aggregation='None', timestamp__gt=requested_time,
            root_test__in=root_test, bot__in=bot, browser__in=browser_obj,
            is_improvement=False
        ).order_by('-delta')[:limit]


class TestPathList(ListAPIView):
    serializer_class = TestPathListSerializer

    def get_queryset(self):
        if self.kwargs.get('browser') == 'all':
            browser_obj = Browser.objects.all()
        else:
            browser_obj = Browser.objects.filter(pk=self.kwargs.get('browser'))

        return BotReportData.objects.filter(
            browser__in=browser_obj,
            root_test=Test.objects.filter(pk=self.kwargs.get('test'))
        ).distinct('test_path')


class TestsForBrowserBotList(ListAPIView):
    serializer_class = TestsForBrowserBotListSerializer

    def get_queryset(self):
        if self.kwargs.get('browser') == 'all':
            browser_obj = Browser.objects.all()
        else:
            browser_obj = Browser.objects.filter(pk=self.kwargs.get('browser'))
        try:
            bot = Bot.objects.get(pk=self.kwargs.get('bot'))
            return BotReportData.objects.filter(
                browser__in=browser_obj, bot=bot
            ).distinct('root_test')
        except Bot.DoesNotExist:
            return BotReportData.objects.filter(
                browser__in=browser_obj
            ).distinct('root_test')


class ResultsForSubtestList(ListAPIView):
    serializer_class = ResultsForSubtestListSerializer

    def get_queryset(self):
        if self.kwargs.get('browser') == 'all':
            browser_obj = Browser.objects.all()
        else:
            browser_obj = Browser.objects.filter(pk=self.kwargs.get('browser'))
        test = Test.objects.get(pk=self.kwargs.get('test'))
        test_path = urllib.parse.unquote(self.kwargs.get('subtest'))
        if self.kwargs.get('bot') == 'all':
            return BotReportData.objects.filter(
                browser__in=browser_obj, root_test=test, test_path=test_path
            ).order_by('timestamp')
        else:
            bot = Bot.objects.get(pk=self.kwargs.get('bot'))
            return BotReportData.objects.filter(
                browser__in=browser_obj, root_test=test, test_path=test_path,
                bot=bot
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
                curr_string += format(mean_value, '.2f') + " " + original_prefix
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

        # Check that the key is there and it contains a value other than None
        def get_value_and_check_defined(data, key):
            value = data.get(key)
            if value == None:
                raise KeyError("variable %s is not defined" % key)
            if str(value) == "None":
                raise KeyError("variable %s can not be equal to str(None)" % key)
            return value

        try:
            response_for_worker = None
            browser_id = None
            browser_version = None
            test_id = None
            test_version = None
            bot_id = None
            json_data = None
            timestamp = None
            try:
                browser_id = get_value_and_check_defined(request.POST, 'browser_id')
                browser_version = get_value_and_check_defined(request.POST, 'browser_version')
                test_id = get_value_and_check_defined(request.POST, 'test_id')
                test_version = get_value_and_check_defined(request.POST, 'test_version')
                bot_id = get_value_and_check_defined(request.POST, 'bot_id')
                json_data = get_value_and_check_defined(request.POST, 'test_data')
            except Exception as e:
                log.error("Got invalid params from the bot: %s. Exception: %s" % (request.auth, str(e)))
                return HttpResponseBadRequest("Some params are missing in the request. Error: %s" % str(e))
            try:
                # The timestamp is optional
                bot_timestamp = self.request.POST.get('timestamp')
                if bot_timestamp:
                    timestamp = datetime.fromtimestamp(float(bot_timestamp))
            except Exception as e:
                return HttpResponseBadRequest("Error parsing the timestamp %s from bot: %s. Exception: %s"% (bot_timestamp, request.auth, str(e)))
            # We may take several seconds to process the data (600 or more sometimes), so if we wait until the processing is done before replying
            # then we risk that the connection is dropped due to timeout on the gateway or endpoint (NAT). To avoid that use a streaming_response
            # that each seconds outputs a "." indicating that processing is still ongoing
            streaming_response = StreamingHttpResponse(self.stream_process_benchmark_data(bot_id, browser_id, browser_version, test_id, test_version, json_data, timestamp))
            streaming_response.status_code = 202  # 202 Accepted, the worker knows how to handle it.
            return streaming_response
        except Exception as e:
                log.error("Exception at BotReportView.post() for bot: %s, browser: %s, browser_version: %s, test: %s, test_version %s, run_stamp: %s, and Exception %s"
                          % (bot_id, browser_id, browser_version, test_id, test_version, timestamp, str(e)))
                return HttpResponseBadRequest("Exception processing the data: %s" % str(e))


    def stream_process_benchmark_data(self, bot_id, browser_id, browser_version, test_id, test_version, json_data, timestamp):
        try:
            start_stamp = datetime.now()
            work_thread = ThreadWithReturnValue(target=self.process_benchmark_data, args=(bot_id, browser_id, browser_version, test_id, test_version, json_data, timestamp))
            work_thread.start()
            yield ("Processing data ")
            while work_thread.is_alive():
                yield (".")
                time.sleep(1)
            response_for_worker = work_thread.join()
            seconds_took = (datetime.now() - start_stamp).total_seconds()
            if isinstance(response_for_worker, HttpResponseBadRequest):
                log.error("Failed processing data in %f seconds for bot: %s, browser: %s, browser_version: %s, test: %s, test_version %s, run_stamp: %s, with error: %s"
                          % (seconds_took, bot_id, browser_id, browser_version, test_id, test_version, timestamp, str(response_for_worker.content.decode())))
            elif isinstance(response_for_worker, HttpResponse):
                log.info("Processed data in %f seconds for bot: %s, browser: %s, browser_version: %s, test: %s, test_version: %s, run_stamp: %s"
                          % (seconds_took, bot_id, browser_id, browser_version, test_id, test_version, timestamp))
            else:
                raise ValueError("Unexpected return value at stream_process_benchmark_data() from the worker thread with type %s" % type(response_for_worker))
            yield ("\nHTTP_202_FINAL_STATUS_CODE = %s\nHTTP_202_FINAL_MSG_NEXT_LINES\n%s" % (response_for_worker.status_code, response_for_worker.content.decode()))
        except Exception as e:
            log.error("Exception at BotReportView.stream_process_benchmark_data() for bot: %s, browser: %s, browser_version: %s, test: %s, test_version: %s, run_stamp: %s. Exception: %s"
                       % (bot_id, browser_id, browser_version, test_id, test_version, timestamp, str(e)))
            yield ("\nException: %s\n" % (str(e)))


    def process_benchmark_data(self, bot_id, browser_id, browser_version, test_id, test_version, json_data, timestamp):
        try:
            try:
                test_data = json.loads(json_data)
            except Exception as e:
                return HttpResponseBadRequest("Error parsing JSON file from bot: %s. Exception: %s"% (bot_id, str(e)))

            bot = Bot.objects.get(pk=bot_id)

            if not bot.enabled:
                log.error("Got data from disabled bot: %s" % bot_id)
                return HttpResponseBadRequest("The bot %s is not enabled"% bot_id)

            try:
                browser = Browser.objects.get(pk=browser_id)
            except Browser.DoesNotExist:
                log.error("Got invalid browser %s from bot: %s" % (browser_id, bot_id))
                return HttpResponseBadRequest("The browser does not exist")

            try:
                root_test = Test.objects.get(pk=test_id)
            except Test.DoesNotExist:
                log.error("Got invalid root test: %s from bot: %s for browser: %s, browser_version: %s"
                          %(test_id, bot_id, browser_id, browser_version))
                return HttpResponseBadRequest("The test %s does not exist"% test_id)

            try:
                test_data_results = BenchmarkResults(test_data)
                results_table = test_data_results.fetch_db_entries(skip_aggregated=False)
            except Exception as e:
                log.error("Exception processing the json test data from bot %s,browser: %s, browser_version: %s, test %s. %s"
                          % (bot_id, browser_id, browser_version, test_id, str(e)))
                return HttpResponseBadRequest("Exception processing the json data: %s" % str(e))

            for result in results_table:
                raw_path = result['name']

                metric_name = self.extract_metric(result['metric'])
                stddev = float(result['stdev'])
                mean_value = float(result['value'])
                unit = result['unit']

                try:
                    current_metric = MetricUnit.objects.get(pk=metric_name)
                    if len(current_metric.prefix) > 0:
                        modified_prefix = self.calculate_prefix(current_metric.prefix, mean_value, curr_string="", original_prefix=current_metric.unit)
                    else:
                        modified_prefix = str(mean_value) + " " + current_metric.unit
                except MetricUnit.DoesNotExist:
                    log.error("Got wrong Metric %s for bot: %s, browser: %s, browser_version: %s, root_test: %s, test_description: %s"
                              % (metric_name, bot_id, browser_id, browser_version,test_id, raw_path))
                    return HttpResponseBadRequest("The Metric Unit %s does not exist"% metric_name)

                if current_metric.unit != unit:
                    log.error("Got wrong unit %s for metric unit %s data for bot: %s, browser: %s, browser_version: %s, root_test: %s, test_description: %s"
                              % (unit, metric_name, bot_id, browser_id, browser_version,test_id, raw_path))
                    return HttpResponseBadRequest("The received unit: %s field of Metric Unit %s does not match" % (unit,metric_name))

                if self.is_aggregated(metric=result['metric']):
                    aggregation = self.extract_aggregation(metric=result['metric'])
                else:
                    aggregation = 'None'

                # It seems some subtest results can have 0 as value for mean_value.
                # It happens sometimes with the stylebench benchmark where it gives
                # a mean_value of 0 ms (Time) for the run.
                # Funny, isn't it? How can it take 0ms to run? Is it even possible to
                # calculate a delta of improvement/regression with 0 ms of time?
                # I think something is wrong with that benchmark, maybe some
                # rounding error or some wrong type cast from float to integer.
                # Anyway, we have to deal with that corner case here somehow, so
                # for now just workaround this issue by simply avoiding to process
                # the result of the subtest when the value is 0, and also log
                # a warning in the admin dashboard with the details.
                if not mean_value:
                    log.warning("Ignoring result with value==%f and stddev=%f for data with metric unit \"%s\" at test: %s [%s] "
                                "from bot: %s running browser %s version %s" %
                                (mean_value, stddev, metric_name, test_id, raw_path, bot_id, browser_id, browser_version))
                    continue

                # Calculate the change and store it during processing the POST
                delta_and_prev_results = self.process_delta_and_improvement(bot, browser, root_test, raw_path, mean_value, current_metric, aggregation)

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
                        prev_result=delta_and_prev_results[2], timestamp=timestamp)
                except Exception as e:
                    log.error("Failed inserting data for bot: %s, browser: %s, browser_version: %s, root_test: %s, test_description: %s and Exception %s"
                              % (bot_id, browser_id, browser_version, test_id, raw_path, str(e)))
                    return HttpResponseBadRequest("Exception inserting the data "
                                                  "into the DB: %s" % str(e))

            return HttpResponse("The POST went through")
        except Exception as e:
            log.error("Unexpected exception at BotReportView.process_benchmark_data() for bot: %s, browser: %s, browser_version: %s, test: %s, test_version %s, run_stamp: %s, and Exception %s"
                  % (bot_id, browser_id, browser_version, test_id, test_version, timestamp, str(e)))
            return HttpResponseBadRequest("Exception processing the data: %s" % str(e))
