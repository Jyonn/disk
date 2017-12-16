# from django.conf.urls import url
from django.urls import path

from User.router import rt_user, rt_user_token, rt_user_avatar
from User.views import avatar_callback

urlpatterns = [
    path('', rt_user),
    path('token', rt_user_token),
    path('avatar', rt_user_avatar),
    path('avatar/callback', avatar_callback)
]
