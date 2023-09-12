from django import forms
from .models import BonSementara,Penyelesaian


class BonSementara (forms.ModelForm):
    class Meta:
        model = BonSementara
        fields = '__all__'

class Penyelesaian (forms.ModelForm):
    class Meta:
        model = Penyelesaian
        fields = '__all__'