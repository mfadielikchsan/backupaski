from django.db.models import fields
from import_export import resources
from .models import BonSementara, Penyelesaian

class BonSementara(resources.ModelResource):
    class Meta:
        model = BonSementara

class Penyelesaian(resources.ModelResource):
    class Meta:
        model = Penyelesaian



