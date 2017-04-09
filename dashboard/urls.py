from django.conf.urls import include, url
from dashboard.views import *
from . import views

urlpatterns = [
    url(r'^report_list/$', BotDataReportList.as_view(), name='all_results'),
    url(r'^bot-report', BotReportView.as_view()),
    url(r'^browser/$', BrowsersList.as_view(), name='browser-list'),
    url(r'^browser_results_exist/$', BrowsersForResultsExistList.as_view()),
    url(r'^bot/$', BotsList.as_view(), name='bots-list'),
    url(r'^bot_results_exist/$', BotsForResultsExistList.as_view(), name='bots-list'),
    url(r'^platform/$', PlatformList.as_view(), name='platform-list'),
    url(r'^gpu/$', GPUTypeList.as_view(), name='gputype-list'),
    url(r'^cpu/$', CPUArchitectureList.as_view(), name='cpuarch-list'),
    url(r'^test/$', TestList.as_view(), name='test-list'),
    url(r'^test_results_exist/$', TestsForResultsExistList.as_view()),
    url(r'^testpath/(?P<browser>.+)/(?P<test>.+)$', TestPathList.as_view()),
    url(r'^test_version/(?P<browser>.+)/(?P<test>.+)/(?P<subtest>.+)$', TestVersionForTestPathList.as_view()),
    url(r'^results_for_version/(?P<browser>.+)/(?P<test>.+)/(?P<subtest>.+)/(?P<bot>.*)$', ResultsForVersionList.as_view()),
    url(r'^report/(?P<days_since>.*)$', BotDataReportListView.as_view()),
    url(r'^report_full/$', BotDataCompleteListView.as_view()),
    url(r'^report/(?P<pk>\d+)$', BotDataReportDetailView.as_view()),
    url(r'^report/test/(?P<pk>\d+)$', BotResultsForTestListView.as_view()),
    url(r'^graph/$', GraphPlotView.as_view(), name='graph_report')
]
