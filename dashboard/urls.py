from django.conf.urls import include, url
from dashboard.views import *
from . import views

urlpatterns = [
    url(r'^$', HomePageView.as_view(), name='home'),
    url(r'^bot-report', BotReportView.as_view()),
]