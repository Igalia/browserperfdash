from django.conf.urls import include, url
from dashboard.views import *
from . import views

urlpatterns = [
    url(r'^bot-report', BotReportView.as_view()),
    url(r'^results/$', BotDataReportList.as_view(), name='result-list')
]