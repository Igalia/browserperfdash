from django.views.generic import TemplateView
from django.http import HttpResponse, HttpResponseBadRequest
from rest_framework.views import APIView
from rest_framework import authentication, permissions, generics, exceptions
from dashboard.models import Bot, Browser, BotReportData, CPUArchitecture, GPUType, Platform, Test, MetricUnit
from dashboard.helpers.benchmark_results import BenchmarkResults
from dashboard.serializers import BotReportDataSerializer, BotsForResultsExistListSerializer, \
    BotsFullDetailsForResultsExistListSerializer, BrowsersForResultsExistListSerializer, PlatformListSerializer, \
    GPUTypeListSerializer, CPUArchitectureListSerializer, TestPathListSerializer, MetricUnitSerializer, \
    TestsForBrowserBotListSerializer, ResultsForSubtestListSerializer
from datetime import datetime, timedelta
import json, urllib.request, urllib.parse, urllib.error, logging, sys

log = logging.getLogger(__name__)

if len(sys.argv) > 1 and sys.argv[1] == 'test':
    log = logging.getLogger()
    log.disabled = True


db_character_separator = '\\'


class DefaultHomeView(TemplateView):
    """Home page view"""
    template_name="index.html"


class GraphPlotView(TemplateView):
    """Graph view"""
    template_name = "plot.html"


class BotAuthentication(authentication.BaseAuthentication):
    """Bot authentication view, used to authenticate data sending bots via API"""

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
        bot = bot_obj.filter(platform__in=platform_obj, cpuArchitecture__in=cpu_obj, gpuType__in=gpu_obj,
                             enabled=True)

        requested_time = datetime.utcnow() + timedelta(days=-days_since)
        queryset = super(BotDataReportImprovementListView, self).get_queryset()
        return queryset.filter(aggregation='None', timestamp__gt=requested_time, root_test__in=root_test,
                               bot__in=bot, browser__in=browser_obj, is_improvement=True).order_by('-delta')[:limit]


class BotDataReportRegressionListView(generics.ListAPIView):
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
        bot = bot_obj.filter(platform__in=platform_obj, cpuArchitecture__in=cpu_obj, gpuType__in=gpu_obj,
                                 enabled=True)
        requested_time = datetime.utcnow() + timedelta(days=-days_since)
        queryset = super(BotDataReportRegressionListView, self).get_queryset()
        return queryset.filter(aggregation='None', timestamp__gt=requested_time, root_test__in=root_test,
                               bot__in=bot, browser__in=browser_obj, is_improvement=False).order_by('-delta')[:limit]


class BotsForResultsExistList(generics.ListAPIView):
    """Fetch just the botname for the plot pages"""
    model = Bot
    serializer_class = BotsForResultsExistListSerializer

    def get_queryset(self):
        if self.kwargs.get('browser') == 'all':
            browser_obj = Browser.objects.all()
        else:
            browser_obj = Browser.objects.filter(pk=self.kwargs.get('browser'))
        return Bot.objects.filter(
            name__in=BotReportData.objects.filter(browser__in=browser_obj).distinct('bot').values('bot'),
            enabled=True
        )


class BotsFullDetailsForResultsExistList(generics.ListAPIView):
    """Fetch detailed bot fields for the home page"""
    model = Bot
    serializer_class = BotsFullDetailsForResultsExistListSerializer

    def get_queryset(self):
        if self.kwargs.get('browser') == 'all':
            browser_obj = Browser.objects.all()
        else:
            browser_obj = Browser.objects.filter(pk=self.kwargs.get('browser'))
        return Bot.objects.filter(
            name__in=BotReportData.objects.filter(browser__in=browser_obj).distinct('bot').values('bot'),
            enabled=True
        )


class BrowsersForResultsExistList(generics.ListAPIView):
    """List out browsers in home page and plot page"""
    model = Browser
    serializer_class = BrowsersForResultsExistListSerializer

    def get_queryset(self):
        return Browser.objects.filter(
            id__in=BotReportData.objects.distinct('browser').values('browser'),
            enabled=True
        )


class PlatformForWhichResultsExistList(generics.ListAPIView):
    """Fetch platforms for which results exist for home page"""
    model = Platform
    serializer_class = PlatformListSerializer

    def get_queryset(self):
        return Platform.objects.filter(
            id__in=BotReportData.objects.distinct('bot__platform').values('bot__platform'),
            enabled=True
        )


class GPUTypeForWhichResultsExistList(generics.ListAPIView):
    """Fetch GPU Types for which results exist for home page"""
    model = GPUType
    serializer_class = GPUTypeListSerializer

    def get_queryset(self):
        return GPUType.objects.filter(
            id__in=BotReportData.objects.distinct('bot__gpuType').values('bot__gpuType'),
            enabled=True
        )


class CPUArchitectureForWhichResultsExistList(generics.ListAPIView):
    """Fetch CPU Architectures for which results exist for home page"""
    model = CPUArchitecture
    serializer_class = CPUArchitectureListSerializer

    def get_queryset(self):
        return CPUArchitecture.objects.filter(
            id__in=BotReportData.objects.distinct('bot__cpuArchitecture').values('bot__cpuArchitecture'),
            enabled=True
        )


class TestPathList(generics.ListAPIView):
    serializer_class = TestPathListSerializer

    def get_queryset(self):
        if self.kwargs.get('browser') == 'all':
            browser_obj = Browser.objects.all()
        else:
            browser_obj = Browser.objects.filter(pk=self.kwargs.get('browser'))
        test = Test.objects.filter(pk=self.kwargs.get('test'))
        return BotReportData.objects.filter(browser__in=browser_obj, root_test=test).distinct('test_path')


class MetricsForTestList(generics.ListAPIView):
    """ Show up metrics for a given test and subtest"""
    model = MetricUnit
    serializer_class = MetricUnitSerializer

    def get_queryset(self):
        return MetricUnit.objects.filter(
            name__in=BotReportData.objects.filter(
                root_test=Test.objects.filter(pk=self.kwargs.get('test')),
                test_path=urllib.parse.unquote(self.kwargs.get('subtest'))
            )[:1].values('metric_unit')
        )


class TestsForBrowserBotList(generics.ListAPIView):
    serializer_class = TestsForBrowserBotListSerializer

    def get_queryset(self):
        if self.kwargs.get('browser') == 'all':
            browser_obj = Browser.objects.all()
        else:
            browser_obj = Browser.objects.filter(pk=self.kwargs.get('browser'))
        try:
            bot = Bot.objects.get(pk=self.kwargs.get('bot'))
            return BotReportData.objects.filter(browser__in=browser_obj, bot=bot).distinct('root_test')
        except Bot.DoesNotExist:
            return BotReportData.objects.filter(browser__in=browser_obj).distinct('root_test')


class ResultsForSubtestList(generics.ListAPIView):
    serializer_class = ResultsForSubtestListSerializer

    def get_queryset(self):
        if self.kwargs.get('browser') == 'all':
            browser_obj = Browser.objects.all()
        else:
            browser_obj = Browser.objects.filter(pk=self.kwargs.get('browser'))
        test = Test.objects.get(pk=self.kwargs.get('test'))
        test_path = urllib.parse.unquote(self.kwargs.get('subtest'))
        if self.kwargs.get('bot') == 'all':
            return BotReportData.objects.filter(browser__in=browser_obj, root_test=test, test_path=test_path).order_by(
                'timestamp')
        else:
            bot = Bot.objects.get(pk=self.kwargs.get('bot'))
            return BotReportData.objects.filter(browser__in=browser_obj, root_test=test, test_path=test_path, bot=bot) \
                .order_by('timestamp')


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

            return cls.calculate_prefix(munits, mean_value, curr_string, original_prefix)

    @classmethod
    def process_delta_and_improvement(cls, browser, root_test, test_path, mean_value, current_metric, aggregation):
        delta = 0.0
        # We take in the previous result (if exists)
        previous_result = BotReportData.objects.filter(
            browser=browser, root_test=root_test, test_path=test_path,metric_unit=current_metric, aggregation=aggregation
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
            ('bot_id', 'bot_name'),('bot_password', 'bot_password'), ('browser_id', 'test_browser'),
            ('browser_version', 'browser_version'), ('test_id', 'test_id'),
            ('test_version', 'test_veresion'),
            ('test_data', '{"RootTest": {"metrics": {"Time": {"current": [1, 2, 3]},
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
            log.error("Got invalid params from the bot: %s"% request.auth)
            return HttpResponseBadRequest("Some params are missing in the request")

        log.info("Started processing data from bot %s" % (bot_id))
        # The timestamp may/may not be there - hence not checking
        timestamp = datetime.fromtimestamp(float(self.request.POST.get('timestamp'))) \
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
            delta_and_prev_results = self.process_delta_and_improvement(browser, root_test, raw_path, mean_value,
                                                                        current_metric, aggregation)

            try:
                BotReportData.objects.create_report(
                    bot=bot, browser=browser, browser_version=browser_version, root_test=root_test, test_path=raw_path,
                    test_version=test_version, aggregation=aggregation, metric_unit=current_metric,
                    metric_unit_prefixed=modified_prefix, mean_value=mean_value, stddev=stddev,
                    delta=delta_and_prev_results[0], is_improvement=delta_and_prev_results[1],
                    prev_result=delta_and_prev_results[2], timestamp=timestamp
                )
            except Exception as e:
                log.error("Failed inserting data for bot: %s, browser: %s, browser_version: %s, root_test: %s, "
                          "test_description: %s and Exception %s" % (bot_id, browser_id, browser_version, test_id, raw_path,
                                                                     str(e))
                          )

        return HttpResponse("The POST went through")