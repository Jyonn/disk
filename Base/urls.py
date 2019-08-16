""" Adel Liu 190815

base子路由
"""
from django.urls import path

from Base.views import ErrorView

urlpatterns = [
    path('errors', ErrorView.as_view()),
]
