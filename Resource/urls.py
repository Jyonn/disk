# from django.conf.urls import url
from django.urls import path

from Resource.router import rt_res_token, rt_dlpath_callback, rt_res_slug, rt_res_slug_vk, rt_res_slug_dl, rt_res, \
    rt_res_slug_folder, rt_res_slug_link, rt_res_slug_cover, rt_cover_callback

urlpatterns = [
    path('', rt_res),
    path('token', rt_res_token),
    path('dlpath/callback', rt_dlpath_callback),
    path('cover/callback', rt_cover_callback),
    path('<slug:slug>', rt_res_slug),
    path('<slug:slug>/folder', rt_res_slug_folder),
    path('<slug:slug>/link', rt_res_slug_link),
    path('<slug:slug>/vk', rt_res_slug_vk),
    path('<slug:slug>/dl', rt_res_slug_dl),
    path('<slug:slug>/cover', rt_res_slug_cover),
]
