from django import forms
from .models import PriceChange,PC_Item,VendorSelection,VS_Item


class VendorSelection (forms.ModelForm):
    class Meta:
        model = VendorSelection
        fields = '__all__'

class VS_Item (forms.ModelForm):
    class Meta:
        model = VS_Item
        fields = '__all__'

class PriceChange (forms.ModelForm):
    class Meta:
        model = PriceChange
        fields = '__all__'

class PC_Item (forms.ModelForm):
    class Meta:
        model = PC_Item
        fields = '__all__'