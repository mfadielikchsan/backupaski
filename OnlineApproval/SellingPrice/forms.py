from django import forms
from . import models

class SellingPrice (forms.ModelForm):
    class Meta:
        model = models.SellingPrice
        fields = '__all__'

class PriceItem (forms.ModelForm):
    class Meta:
        model = models.PriceItem
        fields = '__all__'

class Approval (forms.ModelForm):
    class Meta:
        model = models.Approval
        fields = '__all__'

# class activity_log(format.ModelForm):
#     class Meta:
#         model = models.activity_log
#         fields = '__all__'

