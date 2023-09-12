from django.urls import path, re_path

from . import views

urlpatterns = [
    path('ListBS/', views.listBS),
    path('ListFP/', views.listFP),
    path('ListFA/', views.listApproved),
    path('CreateBS/',views.CreateBS),
    re_path(r'CreateFP/(?P<ID>[\w-]+)/$',views.CreateFP),
    re_path(r'ListBS/(?P<ID>[\w-]+)/$', views.DetailBS),
    re_path(r'ListFP/(?P<ID>[\w-]+)/$', views.DetailFP),
    re_path(r'ListFA/BS/(?P<ID>[\w-]+)/$', views.DetailBS),
    re_path(r'ListFA/FP/(?P<ID>[\w-]+)/$', views.DetailFP),

    path('BSExport/', views.exportbon),
]