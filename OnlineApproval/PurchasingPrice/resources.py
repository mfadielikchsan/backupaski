from django.db.models import fields
from import_export import resources
from .models import PurchasingPrice,PP_Item

class PurchasingPrice(resources.ModelResource):
    class Meta:
        model = PurchasingPrice

class PP_Item(resources.ModelResource):
    class Meta:
        model = PP_Item