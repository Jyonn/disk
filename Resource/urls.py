# from django.conf.urls import url
from django.urls import path

from Resource.router import rt_res_token, rt_res

urlpatterns = [
    path('token', rt_res_token),
    path('<slug:slug>', rt_res),
]