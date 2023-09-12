from django.urls import path,re_path

from . import views

urlpatterns = [
    path('Create/Data/', views.datacreate.as_view()),
    path('Create/', views.create),
    path('CreateSP/', views.createSP),
    path('ListSP/', views.listSP),
    path('ListInput/', views.listinput),
    path('ListSPExport/', views.exportSPList),

    re_path(r'Generate/(?P<ID>[\w-]+)/$', views.pdf),
    re_path(r'ListSP/(?P<ID>[\w-]+)/$', views.detail),
    re_path(r'Revise/(?P<ID>[\w-]+)/$', views.revise),
    re_path(r'ListInput/(?P<ID>[\w-]+)/$', views.check),
    re_path(r'Export/(?P<ID>[\w-]+)/$', views.exportDetail),
]