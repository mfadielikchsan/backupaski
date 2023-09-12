from django.db.models import fields
from import_export import resources
from .models import capex, cpitem

class Capex(resources.ModelResource):
    class Meta:
        model = capex

class CapexItem(resources.ModelResource):
    class Meta:
        model = cpitem