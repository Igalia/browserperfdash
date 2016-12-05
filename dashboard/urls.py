from django.conf.urls import include, url
from dashboard.views import *

urlpatterns = [
    url(r'^$', HomePageView.as_view(), name='home'),
]