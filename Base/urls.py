""" Adel Liu 190815

base子路由
"""
from django.urls import path

from Base.views import ErrorView, CleanerView

urlpatterns = [
    path('errors', ErrorView.as_view()),
    path('cleaner', CleanerView.as_view()),
]
