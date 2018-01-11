""" Adel Liu 180111

用户APi子路由
"""
from django.urls import path

from User.router import rt_user, rt_user_token, rt_user_avatar, rt_username, rt_avatar_callback

urlpatterns = [
    path('', rt_user),
    path('@<str:username>', rt_username),
    path('token', rt_user_token),
    path('avatar', rt_user_avatar),
    path('avatar/callback', rt_avatar_callback),
]
