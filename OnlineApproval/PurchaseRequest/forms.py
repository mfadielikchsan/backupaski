from django import forms
from .models import PRitem, PRheader, Approval, CostCenter, Budget, ItemList, activity_log, MRPheader


class PRheader (forms.ModelForm):
    class Meta:
        model = PRheader
        fields = '__all__'


class PRitem (forms.ModelForm):
    class Meta:
        model = PRitem
        fields = '__all__'


class Approval (forms.ModelForm):
    class Meta:
        model = Approval
        fields = '__all__'


class CostCenter (forms.ModelForm):
    class Meta:
        model = CostCenter
        fields = '__all__'


class Budget (forms.ModelForm):
    class Meta:
        model = Budget
        fields = '__all__'


class ItemList (forms.ModelForm):
    class Meta:
        model = ItemList
        fields = '__all__'

class activity_log (forms.ModelForm):
    class Meta:
        model = activity_log
        fields = '__all__'

class MRPheader (forms.ModelForm):
    class Meta:
        model = MRPheader
        fields = '__all__'
