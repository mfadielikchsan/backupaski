from django import forms
from . import models

class Capex(forms.ModelForm):
    class Meta:
        model = models.capex
        fields = '__all__'

class CapexItem(forms.ModelForm):
    class Meta:
        model = models.cpitem
        fields = '__all__'

class Approval(forms.ModelForm):
    class Meta:
        model = models.Approval
        fields = '__all__'

