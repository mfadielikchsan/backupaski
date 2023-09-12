from django.urls import path, re_path
from . import views

urlpatterns = [
    path('CreateBE/', views.createBE),
    path('ListBE/', views.listBE),
    path('ListCheck/', views.listCheck),


    re_path(r'ListBE/(?P<ID>[\w-]+)/$', views.view),
    re_path(r'Revise/(?P<ID>[\w-]+)/$', views.revise),
    re_path(r'ListCheck/(?P<ID>[\w-]+)/$', views.viewCheck),
    re_path(r'Generate/(?P<ID>[\w-]+)/$', views.pdf),
]