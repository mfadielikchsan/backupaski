from django import forms
from . import models

class Entertainment(forms.ModelForm):
    class Meta:
        model = models.Entertainment
        fields = "__all__"
        
class Approval(forms.ModelForm):
    class Meta:
        model = models.Approval
        fields = "__all__"
