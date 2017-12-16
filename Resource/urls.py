# from django.conf.urls import url
from django.urls import path

from Resource.router import rt_res_token, rt_res, rt_res_visit_key, rt_res_dl

urlpatterns = [
    path('token', rt_res_token),
    path('<slug:slug>', rt_res),
    path('<slug:slug>/vk', rt_res_visit_key),
    path('<slug:slug>/dl', rt_res_dl),
]
