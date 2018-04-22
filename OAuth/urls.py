from django.urls import path

from OAuth.router import rt_qtb_callback

urlpatterns = [
    path('qtb/callback', rt_qtb_callback),
]