""" Adel Liu 180111

用户APi子路由
"""
from django.urls import path

from User.views import BaseView, QitianView

urlpatterns = [
    path('', BaseView.as_view()),
    path('@<str:qt_user_app_id>', QitianView.as_view()),
]
