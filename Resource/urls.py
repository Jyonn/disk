""" Adel Liu 180111

资源API子路由
"""
from django.urls import path

from Resource.dev import set_unique_res_key
from Resource.router import rt_res_token, rt_dlpath_callback, rt_res_slug, \
    rt_res_slug_dl, rt_res, rt_res_folder, rt_res_link, rt_res_cover, rt_cover_callback, \
    rt_res_slug_base

urlpatterns = [
    path('', rt_res),
    path('<str:parent_str_id>/token', rt_res_token),
    path('<str:res_str_id>/cover', rt_res_cover),
    path('<str:res_str_id>/folder', rt_res_folder),
    path('<str:res_str_id>/link', rt_res_link),
    # path('<int:res_id>/vk', rt_res_vk),
    path('dlpath/callback', rt_dlpath_callback),
    path('cover/callback', rt_cover_callback),
    path('<slug:slug>', rt_res_slug),
    path('<slug:slug>/dl', rt_res_slug_dl),
    path('<slug:slug>/base', rt_res_slug_base),

    path('@set_unique_res_key', set_unique_res_key),
]
