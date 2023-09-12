from django.urls import path, re_path

from . import views

urlpatterns = [
    path('', views.home),
    path('Create/', views.create),
    path('CreatePRMRP/', views.createPRMRP),
    path('ListPRMRP/', views.listPRMRP),
    path('ListPP/', views.listPP),
    path('ListBudget/', views.listbudget),
    path('Asset/', views.assetlist),
    path('SAPNumber/', views.addprnumber),
    path('NewCostCenter/', views.costcenter),
    path('NewPRItem/', views.newitem),
    path('BudgetExport/', views.exportbudget),
    path('CostCenterExport/', views.exportcostcenter),
    path('ItemListExport/', views.exportitem),
    path('BudgetUsageExport/', views.exportbudgetusage),
    path('ItemPRExport/', views.exportfinishedPR),
    path('ListPRExport/', views.exportlistfinishedPR),
    path('SendMail/',views.email),
    

    re_path(r'ListPP/(?P<ID>[\w-]+)/$', views.detail),
    re_path(r'ListPRMRP/(?P<ID>[\w-]+)/$', views.detailPRMRP),
    re_path(r'Asset/(?P<ID>[\w-]+)/$', views.detailasset),
    re_path(r'SAPNumber/(?P<ID>[\w-]+)/$', views.detailnumber),
    re_path(r'Revise/(?P<ID>[\w-]+)/$', views.revise),
    re_path(r'ReviseMRP/(?P<ID>[\w-]+)/$', views.reviseMRP),
    re_path(r'Generate/(?P<ID>[\w-]+)/$', views.pdf),
    re_path(r'GenerateMRP/(?P<ID>[\w-]+)/$', views.approvalMRP),

]
