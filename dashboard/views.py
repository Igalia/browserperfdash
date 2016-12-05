from django.shortcuts import render
from django.shortcuts import redirect
from django.views.generic import TemplateView


class HomePageView(TemplateView):
    template_name="index.html"