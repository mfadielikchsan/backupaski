from django import forms
from . import models


class POData (forms.ModelForm):
    class Meta:
        model = models.POData
        fields = '__all__'

class VendorData (forms.ModelForm):
    class Meta:
        model = models.VendorData
        fields = '__all__'

class POApproval (forms.ModelForm):
    class Meta:
        model = models.POApproval
        fields = '__all__'
        