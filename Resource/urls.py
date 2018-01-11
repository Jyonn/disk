# from django.conf.urls import url
from django.urls import path

from Resource.router import rt_res_token, rt_dlpath_callback, rt_res_slug, rt_res_visit_key, rt_res_dl, rt_res

urlpatterns = [
    path('', rt_res),
    path('token', rt_res_token),
    path('dlpath/callback', rt_dlpath_callback),
    path('<slug:slug>', rt_res_slug),
    path('<slug:slug>/vk', rt_res_visit_key),
    path('<slug:slug>/dl', rt_res_dl),
]
