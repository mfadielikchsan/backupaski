from django.urls import path,re_path

from . import views

urlpatterns = [
   
    path('Create/', views.create),
    path('ListPO/', views.listPO),
    path('ListPO/<po_number>/<revision>/', views.detailPO),
    path('Revise/<po_number>/<revision>/', views.revisePO),
    re_path(r'Generate/(?P<ID>[\w-]+)/$', views.pdf),
    re_path(r'Send/(?P<ID>[\w-]+)/$', views.send),
    path('ListPOExport/', views.exportlistPO),
   
]