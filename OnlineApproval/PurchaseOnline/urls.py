from django.urls import path, re_path

from . import views

urlpatterns = [
    path('VS/Create/', views.CreateVS),
    path('VS/List/', views.ListVS),
    re_path(r'VS/Detail/(?P<ID>[\w-]+)/$',views.DetailVS),

    path('PC/Create/', views.CreatePC),
    path('PC/List/', views.ListPC),
    re_path(r'PC/Detail/(?P<ID>[\w-]+)/$',views.DetailPC),
]