from django.db.models import fields
from import_export import resources
from .models import Budget,CostCenter,ItemList,PRheader,PRitem

class Budget(resources.ModelResource):
    class Meta:
        model = Budget

class CostCenter(resources.ModelResource):
    class Meta:
        model = CostCenter

class ItemList(resources.ModelResource):
    class Meta:
        model = ItemList

class PRheader(resources.ModelResource):
    class Meta:
        model = PRheader
        #fields = ('id','PP_Number','User_Name','PR_Number','PR_Date',)  

class PRitem(resources.ModelResource):
    class Meta:
        model = PRitem

