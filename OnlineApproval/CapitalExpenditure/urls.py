from django.urls import path, re_path
from . import views

urlpatterns = [
    path('Create/', views.createCP),
    path('ListDept/', views.listCP),
    path('Filter/', views.filter),
    path('ListAll/', views.listAll),
    path('Summary/', views.summary),
    
    re_path(r'Export/(?P<ID>[\w-]+)/$', views.ExcelDept),
    re_path(r'Revise/(?P<ID>[\w-]+)/$', views.revise),
    re_path(r'Generate/(?P<ID>[\w-]+)/$', views.excel),
    re_path(r'ListDept/(?P<ID>[\w-]+)/$', views.view),
    re_path(r'ListAll/(?P<ID>[\w-]+)/$', views.viewAll),
]