from django import forms
from . import models

class PurchasingPrice (forms.ModelForm):
    class Meta:
        model = models.PurchasingPrice
        fields = '__all__'

class PP_Item (forms.ModelForm):
    class Meta:
        model = models.PP_Item
        fields = '__all__'

class Approval (forms.ModelForm):
    class Meta:
        model = models.Approval
        fields = '__all__'