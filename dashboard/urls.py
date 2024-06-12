from django.conf.urls import url
from dashboard.core.bots.reports.views import BotReportView
from django.views.generic import TemplateView

from dashboard.core.gpus.views import GPUTypeForWhichResultsExistList
from dashboard.core.cpus.views import CPUArchitectureForWhichResultsExistList
from dashboard.core.platforms.views import PlatformForWhichResultsExistList
from dashboard.core.browsers.views import BrowsersForResultsExistList
from dashboard.core.metric_units.views import MetricsForTestList
from dashboard.core.bots.views import BotsForResultsExistList, \
    BotsFullDetailsForResultsExistList
from dashboard.core.bots.reports.views import TestsForBrowserBotList, \
    ResultsForSubTestList, BotDataReportImprovementListView, \
    BotDataReportRegressionListView, TestPathsList

urlpatterns = [
    url(
        r'^graph/$', TemplateView.as_view(template_name="plot.html"),
        name='graph_report'
    ),
    url(r'^bot-report', BotReportView.as_view()),
    url(r'^gpus$', GPUTypeForWhichResultsExistList.as_view()),
    url(r'^cpus$', CPUArchitectureForWhichResultsExistList.as_view()),
    url(r'^platforms$', PlatformForWhichResultsExistList.as_view()),
    url(r'^browsers$', BrowsersForResultsExistList.as_view()),
    url(r'^bots$', BotsForResultsExistList.as_view()),
    url(r'^bot-full-details$', BotsFullDetailsForResultsExistList.as_view()),
    url(r'^test-paths', TestPathsList.as_view()),
    url(r'^test-metrics/(?P<test>[-\w]+)/(?P<subtest>.+)$',
        MetricsForTestList.as_view()),
    url(r'^tests$', TestsForBrowserBotList.as_view()),
    url(r'^results$', ResultsForSubTestList.as_view()),
    url(r'^report/improvements', BotDataReportImprovementListView.as_view()),
    url(r'^report/regressions', BotDataReportRegressionListView.as_view())
]
