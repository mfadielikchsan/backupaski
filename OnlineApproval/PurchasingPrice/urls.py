from django.urls import path,re_path

from . import views

urlpatterns = [
    path('Create/', views.create),
    path('ListPP/', views.listPP),
    path('ListCheck/', views.listcheck),

    re_path(r'Generate/(?P<PP_Number>[\w-]+)/$', views.pdf),
    re_path(r'ListPP/(?P<PP_Number>[\w-]+)/$', views.detail),
    re_path(r'Check/(?P<PP_Number>[\w-]+)/$', views.check),
    re_path(r'Revise/(?P<PP_Number>[\w-]+)/$', views.revise),
]