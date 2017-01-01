from django.conf.urls import include, url
from dashboard.views import *
from . import views

urlpatterns = [
    url(r'^all/$', AllResultsView.as_view(), name='all_results'),
    url(r'^bot-report', BotReportView.as_view()),
    url(r'^result/$', BotDataReportList.as_view(), name='result-list'),
    url(r'^browser/$', BrowsersList.as_view(), name='browser-list'),
    url(r'^bot/$', BotsList.as_view(), name='bots-list'),
    url(r'^platform/$', PlatformList.as_view(), name='platforms-list'),
    url(r'^gpu/$', GPUTypeList.as_view(), name='bots-list'),
    url(r'^cpu/$', CPUArchitectureList.as_view(), name='bots-list'),
]