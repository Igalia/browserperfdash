from django.conf.urls import include, url
from dashboard.views import *
from . import views

urlpatterns = [
    url(r'^report_list/$', BotDataReportList.as_view(), name='all_results'),
    url(r'^report_detail_view/$', BotDataReportDetail.as_view()),
    url(r'^bot-report', BotReportView.as_view()),
    url(r'^browser/$', BrowsersList.as_view(), name='browser-list'),
    url(r'^bot/$', BotsList.as_view(), name='bots-list'),
    url(r'^platform/$', PlatformList.as_view(), name='platform-list'),
    url(r'^gpu/$', GPUTypeList.as_view(), name='gputype-list'),
    url(r'^cpu/$', CPUArchitectureList.as_view(), name='cpuarch-list'),
    url(r'^test/$', TestList.as_view(), name='test-list'),
    url(r'^report/$', BotDataReportListView.as_view()),
    url(r'^report/(?P<pk>\d+)$', BotDataReportDetailView.as_view()),
    url(r'^report/test/(?P<pk>\d+)$', BotResultsForTestListView.as_view()),
]