""" Adel Liu 180111

资源API子路由
"""
from django.urls import path

from Resource.views import FolderView, LinkView, CoverView, TokenView, SelectView, BaseView, \
    BaseInfoView, PathView, DownloadView

urlpatterns = [
    path('<str:res_str_id>/folder', FolderView.as_view()),
    path('<str:res_str_id>/link', LinkView.as_view()),
    path('<str:res_str_id>/cover', CoverView.as_view()),
    path('<str:res_str_id>/token', TokenView.as_view()),
    path('<str:res_str_id>/selector', SelectView.as_view()),
    path('<str:res_str_id>/path', PathView.as_view()),
    path('<str:res_str_id>/base', BaseInfoView.as_view()),
    path('<str:res_str_id>/dl', DownloadView.as_view()),
    path('<str:res_str_id>', BaseView.as_view()),
]
