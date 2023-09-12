from django.db.models import fields
from import_export import resources
from .models import SellingPrice,PriceItem

class SellingPrice(resources.ModelResource):
    class Meta:
        model = SellingPrice

class PriceItem(resources.ModelResource):
    class Meta:
        model = PriceItem