""" Adel Liu 180111

用户APi子路由
"""
from django.urls import path

from User.router import rt_user, rt_username

urlpatterns = [
    path('', rt_user),
    path('@<str:username>', rt_username),
]
