from django.conf.urls import url
from dashboard.views import *

urlpatterns = [
    url(r'^graph/$', GraphPlotView.as_view(), name='graph_report'),
    url(r'^bot-report', BotReportView.as_view()),
    url(r'^gpu_results_exist/$', GPUTypeForWhichResultsExistList.as_view()),
    url(r'^cpu_results_exist/$', CPUArchitectureForWhichResultsExistList.as_view()),
    url(r'^platform_results_exist/$', PlatformForWhichResultsExistList.as_view()),
    url(r'^browser_results_exist/$', BrowsersForResultsExistList.as_view()),
    url(r'^bot_results_exist/(?P<browser>.+)$', BotsForResultsExistList.as_view()),
    url(r'^bot_full_details_for_exist/(?P<browser>.+)$', BotsFullDetailsForResultsExistList.as_view()),
    url(r'^testpath/(?P<browser>.+)/(?P<test>.+)$', TestPathList.as_view()),
    url(r'^test_metrics/(?P<test>[-\w]+)/(?P<subtest>.+)$', MetricsForTestList.as_view()),
    url(r'^tests_for_browser_bot/(?P<browser>.+)/(?P<bot>.*)$', TestsForBrowserBotList.as_view()),
    url(r'^results_for_subtest/(?P<browser>[-\w]+)/(?P<test>[-\w]+)/(?P<bot>[-\w]+)/(?P<subtest>.+)/$',
        ResultsForSubtestList.as_view()),
    url(r'^report/improvement/(?P<days_since>\d+)/(?P<platform>[-\w]+)/(?P<gpu>[-\w]+)/'
        r'(?P<cpu>[-\w]+)/(?P<browser>[-\w]+)/(?P<test>[-\w]+)/(?P<bot>[-\w]+)/(?P<limit>\d+)/$',
        BotDataReportImprovementListView.as_view()),
    url(r'^report/regression/(?P<days_since>\d+)/(?P<platform>[-\w]+)/(?P<gpu>[-\w]+)/'
        r'(?P<cpu>[-\w]+)/(?P<browser>[-\w]+)/(?P<test>[-\w]+)/(?P<bot>[-\w]+)/(?P<limit>\d+)/$',
        BotDataReportRegressionListView.as_view())
]
