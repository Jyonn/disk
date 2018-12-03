""" Adel Liu 180111

资源API子路由
"""
from django.urls import path

from Resource.dev import set_unique_res_key, set_default_cover_type
from Resource.router import rt_dlpath_callback, rt_cover_callback, rt_res

urlpatterns = [
    path('@set_unique_res_key', set_unique_res_key),
    path('@set_cover_type', set_default_cover_type),

    path('dlpath/callback', rt_dlpath_callback),
    path('cover/callback', rt_cover_callback),
    path('<str:res_str_id>/<str:suffix>', rt_res),
    path('<str:res_str_id>', rt_res),
]
