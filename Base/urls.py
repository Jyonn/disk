""" Adel Liu 180226

base子路由
"""
from django.urls import path

from Base.views import get_error_dict

urlpatterns = [
    path('errors', get_error_dict),
]
