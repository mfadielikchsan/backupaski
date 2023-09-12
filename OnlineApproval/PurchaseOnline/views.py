from django.shortcuts import render
from . import forms
from . import models
from PurchaseRequest import models as PRModels
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.core import serializers
from django.shortcuts import redirect
from django.core.mail import send_mail, EmailMessage
from django.conf import settings

import datetime
import pdfkit

def is_memberadditem(user):
    return user.groups.filter(name='Allow_Add_Item').exists()

@login_required
@user_passes_test(is_memberadditem)
def CreateVS (request):

    if request.method == "GET":
        VS = forms.VendorSelection()
        VS.fields['VS_Number'].initial = 'ASKIVS'+request.user.username + str(models.VendorSelection.objects.filter(
                VS_Number__contains=request.user.username, VS_Status__isnull=False).exclude(VS_Number__contains='rev').count()+1).zfill(5)
        VSItem = forms.VS_Item()

        approval = list(PRModels.Approval.objects.filter(
                User=request.user.username))
        data = serializers.serialize(
                "json", PRModels.Approval.objects.filter(User=request.user.username))
        mode = "create"
    elif "create" in request.POST:
        print("create")
        print(request.POST)
        
        if models.VendorSelection.objects.filter(VS_Number=request.POST['VS_Number']).exists():
            VS = forms.VendorSelection(request.POST, instance=models.VendorSelection.objects.get(
                VS_Number=request.POST['VS_Number']))
        else:
            VS = forms.VendorSelection(request.POST)
        if VS.is_valid():
            VS.save()
        else:
            print(VS.errors)
        VSItem = forms.VS_Item()
        approval = list(PRModels.Approval.objects.filter(
                User=request.user.username))
        data = serializers.serialize(
                "json", PRModels.Approval.objects.filter(User=request.user.username))
        mode = "item"
    context = {
        'Judul': 'Create Vendor Selection',
        'VS': VS,
        'VSItem': VSItem,   
        'Approval' : approval,
        'Data': data,
        'mode' : mode,
    }
    return render(request, 'purchaseonline/CreateVS.html', context)

@login_required
@user_passes_test(is_memberadditem)
def ListVS (request):
    context = {
        'Judul': 'List Vendor Selection',        
    }
    return render(request, 'purchaseonline/listAP.html', context)

@login_required
@user_passes_test(is_memberadditem)
def DetailVS (request):
    context = {
        'Judul': 'Detail Vendor Selection',        
    }
    return render(request, 'purchaseonline/listAP.html', context)


@login_required
@user_passes_test(is_memberadditem)
def CreatePC (request):
    context = {
        'Judul': 'Create Price Change',        
    }
    return render(request, 'purchaseonline/listAP.html', context)

@login_required
@user_passes_test(is_memberadditem)
def ListPC (request):
    context = {
        'Judul': 'List Price Change',        
    }
    return render(request, 'purchaseonline/listAP.html', context)

@login_required
@user_passes_test(is_memberadditem)
def DetailPC (request):
    context = {
        'Judul': 'Detail Price Change',        
    }
    return render(request, 'purchaseonline/listAP.html', context)
