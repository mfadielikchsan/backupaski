from PurchaseRequest.models import Approval, Budget, PRheader
from django.shortcuts import render
from django.shortcuts import redirect
from . import forms
from . import models
from . import resources
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.core import serializers
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse
from django.core.files.storage import default_storage
from tablib import Dataset
import django_excel as excel
import os
from pyexcel_xlsx import get_data
from django.db.models import Q

import json


import datetime
import pdfkit


# Create your views here.
def is_memberaddasset(user):
    return user.groups.filter(name='Allow_Add_Asset').exists()


def is_memberaddprno(user):
    return user.groups.filter(name='Allow_Add_PR_No').exists()

def is_memberadditem(user):
    return user.groups.filter(name='Allow_Add_Item').exists()

def is_memberPRMRP(user):
    return user.groups.filter(Q(name='Allow_Add_Item')|Q(name='Allow_Add_PR_No')).exists()

def is_admin(user):
    return user.groups.filter(name='Admin').exists()


def home(request):
    context = {
        'Judul': 'Online Approval System',
    }
    return render(request, 'CreatePR copy.html', context)


@login_required
def create(request):
    context = {
        'Judul': 'Create Purchase Request',
    }
    if request.method == "GET":
        prheader = forms.PRheader()
        pritem = forms.PRitem()
        prheader.fields['PP_Number'].initial = 'ASKIPP'+request.user.username + str(models.PRheader.objects.filter(
            PP_Number__contains=request.user.username, PR_Status__isnull=False).exclude(PP_Number__contains='rev').count()+1).zfill(5)
        approval = list(models.Approval.objects.filter(
            User=request.user.username))
        budget = list(models.Budget.objects.filter(
            Budget_User__contains=request.user.username).exclude(Current_Budget_Value__contains='-'))
        data = serializers.serialize(
            "json", models.Approval.objects.filter(User=request.user.username))
        context.update({'PRheader': prheader, 'Budget': budget,
                        'Data': data, 'Approval': approval, 'mode': "create"})
    else:
        models.activity_log(user = request.user.username,PP_Number=request.POST["PP_Number"],activity=request.POST).save()
    if 'create' in request.POST:
        if models.PRheader.objects.filter(PP_Number=request.POST['PP_Number']).exists():
            prheaderpost = forms.PRheader(request.POST, instance=models.PRheader.objects.get(
                PP_Number=request.POST['PP_Number']))
        else:
            prheaderpost = forms.PRheader(request.POST)
        pritem = forms.PRitem()
        pritem.fields['PP_Number'].initial = request.POST['PP_Number']
        print("CREATE")
        print(request.POST)
        if prheaderpost.is_valid():
            # if not models.PRheader.objects.filter(PP_Number = request.POST['PP_Number']).exists():
            prheaderpost.save()
        else:
            print(prheaderpost.errors)
        prheader = list(models.PRheader.objects.filter(
            PP_Number=request.POST['PP_Number']))
        itemlist = list(models.PRitem.objects.filter(
            PP_Number=request.POST['PP_Number']))
        if request.POST["Jenis_PP"] == "ZRAT-PR Asset":
            itemselect = serializers.serialize(
            "json", list(models.ItemList.objects.all()))
        else :
            itemselect = serializers.serialize(
            "json", list(models.ItemList.objects.all().exclude(Expense ='A')))
        costcenter = list(models.CostCenter.objects.all())
        context.update({'PRheader': prheader, 'PRitem': pritem, 'mode': "additem",
                        'itemlist': itemlist, 'ItemSelect': itemselect, 'CostCenter': costcenter})
    if 'additem' in request.POST:
        pritem = forms.PRitem(request.POST)
        print("ADD ITEM")
        print(request.POST)
        #print(models.PRitem.objects.filter(PP_Number = request.POST['PP_Number'], Nama_Barang = request.POST['Nama_Barang'], Note = request.POST['Note']).count())
        if pritem.is_valid() and models.PRitem.objects.filter(PP_Number=request.POST['PP_Number'], Nama_Barang=request.POST['Nama_Barang'], Note=request.POST['Note']).count() == 0:
            pritem.save()
            status = [request.POST['Nama_Barang'],
                      request.POST['PP_Number'], 'Add']
        else:
            print(pritem.errors)
            status = [request.POST['Nama_Barang'],
                      request.POST['PP_Number'], 'Fail']
        pritem = forms.PRitem()
        prheader = list(models.PRheader.objects.filter(
            PP_Number=request.POST['PP_Number']))
        itemlist = list(models.PRitem.objects.filter(
            PP_Number=request.POST['PP_Number']))

        if models.PRheader.objects.get(PP_Number=request.POST['PP_Number']).Jenis_PP == "ZRAT-PR Asset":
            itemselect = serializers.serialize(
            "json", list(models.ItemList.objects.all()))
        else :
            itemselect = serializers.serialize(
            "json", list(models.ItemList.objects.all().exclude(Expense ='A')))
        costcenter = list(models.CostCenter.objects.all())
        context.update({'PRheader': prheader, 'PRitem': pritem, 'mode': "additem", 'itemlist': itemlist,
                        'CostCenter': costcenter, 'status': status, 'ItemSelect': itemselect})
        print("header", prheader)
        print("item", itemlist)
    if 'deleteitem' in request.POST:
        print("DELETE ITEM")
        print(request.POST)
        models.PRitem.objects.filter(
            PP_Number=request.POST['PP_Number'], Nama_Barang=request.POST['deleteitem']).delete()
        prheader = list(models.PRheader.objects.filter(
            PP_Number=request.POST['PP_Number']))
        itemlist = list(models.PRitem.objects.filter(
            PP_Number=request.POST['PP_Number']))
        pritem = forms.PRitem()
        pritem.fields['PP_Number'].initial = request.POST['PP_Number']
        status = [request.POST['deleteitem'],
                  request.POST['PP_Number'], 'Delete']
        if models.PRheader.objects.get(PP_Number=request.POST['PP_Number']).Jenis_PP == "ZRAT-PR Asset":
            itemselect = serializers.serialize(
            "json", list(models.ItemList.objects.all()))
        else :
            itemselect = serializers.serialize(
            "json", list(models.ItemList.objects.all().exclude(Expense ='A')))
        costcenter = list(models.CostCenter.objects.all())
        context.update({'PRheader': prheader, 'PRitem': pritem, 'mode': "additem", 'itemlist': itemlist,
                        'CostCenter': costcenter, 'status': status, 'ItemSelect': itemselect})
    if 'finishitem' in request.POST:
        print('FINISH ADD ITEM')
        print(request.POST)
        prheader = models.PRheader.objects.get(
            PP_Number=request.POST['PP_Number'])
        prheaderform = forms.PRheader(instance=prheader)
        itemlist = list(models.PRitem.objects.filter(
            PP_Number=request.POST['PP_Number']))
        approval = models.Approval.objects.get(
            User=request.user.username, Supervisor=prheader.User_Name)
        if prheader.Budget_No is not None :
            budget = models.Budget.objects.get(Budget_No = prheader.Budget_No)
            if approval.DivHead is None and 'PROJECT' in budget.Budget_User:
                approval.DivHead = 'HENDRO WITJAKSONO'
                approval.DivHead_email = 'hendro.witjaksono@aski.co.id'
        # for app in approval:
        #    applist = list(app)
        #data =serializers.serialize("json",models.Approval.objects.filter(User = request.user.username))
        context.update({'PRheader': prheader, 'PRheaderform': prheaderform,
                        'Approval': approval, 'mode': "approval", 'itemlist': itemlist})
    if 'finish' in request.POST:
        print('FINISH ALL PROSES')
        prheader = models.PRheader.objects.get(
            PP_Number=request.POST['PP_Number'])
        prheaderform = forms.PRheader(
            request.POST, request.FILES, instance=prheader)
        approval = models.Approval.objects.get(
            Supervisor_email=request.POST['SPV_Email'],User=request.user.username)
        if prheader.Budget_No is not None :
            budget = models.Budget.objects.get(Budget_No = prheader.Budget_No)
            if approval.DivHead is None and 'PROJECT' in budget.Budget_User:
                approval.DivHead = 'HENDRO WITJAKSONO'
                approval.DivHead_email = 'hendro.witjaksono@aski.co.id'
        if prheaderform.is_valid():
            prheaderform.save()
        else:
            print(prheaderform.errors)

        print(request.POST)
        itemlist = list(models.PRitem.objects.filter(
            PP_Number=request.POST['PP_Number']))
        pritem = forms.PRitem()
        counter = 0
        contain = ''
        for item in itemlist:
            counter += 1
            contain += '''<tr style="height: 30px; font-size:12px;">
                    <td style="border: 1px solid black;">'''+str(counter)+'''</td>
                    <td style="border: 1px solid black;">'''+xstr(item.Expense)+'''</td>
                    <td style="border: 1px solid black;">'''+xstr(item.Jenis_Barang)+'''</td>
                    <td style="border: 1px solid black;">'''+xstr(item.Kode_Barang)+'''</td>
                    <td style="border: 1px solid black; text-align: left;padding-left: 5px;width:15%;">'''+item.Nama_Barang+" "+xstr(item.Detail_Spec)+'''</td>
                    <td style="border: 1px solid black;">'''+str(item.Jumlah_Order)+'''</td>
                    <td style="border: 1px solid black;">'''+str(item.Unit_Order)+'''</td>
                    <td style="border: 1px solid black;">'''+xstr(item.Harga_Satuan)+" "+xstr(item.Currency)+'''</td>
                    <td style="border: 1px solid black;">'''+xstr(item.Harga_Total)+" "+xstr(item.Currency)+'''</td>
                    <td style="border: 1px solid black;">'''+xstr(item.Tgl_Kedatangan)+'''</td>
                    <td style="border: 1px solid black;">'''+xstr(item.Cost_Center)+'''</td>
                    <td style="border: 1px solid black;">'''+xstr(item.Asset_No_GL_Account)+'''</td>
                    <td style="border: 1px solid black;">'''+xstr(item.Minimal_Stock)+'''</td>
                    <td style="border: 1px solid black;">'''+xstr(item.Actual_Stock)+'''</td>
                    <td style="border: 1px solid black;">'''+xstr(item.Average_Usage)+'''</td>
                    <td style="border: 1px solid black;"></td>
                    <td style="border: 1px solid black;"></td>
                    <td style="border: 1px solid black;">'''+xstr(item.Note)+'''</td>
                </tr>'''

        if approval.DivHead is None:
            apptable = """
                        <table style="border: 1px solid black; font-size: 12px;text-align: center;border-collapse: collapse;" >
                            <tbody >
                                <tr style="height:20px;">
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: center;">Pemesan</td>
                                    <td colspan="3" style="border: 1px solid black;width: 230px;text-align: center;vertical-align: center;">Disetujui/Mengetahui</td>
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: center;">Purchasing</td>
                                </tr>
                                <tr style="height:65px;">
                                    <td style="padding:10px;border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: center;font-style: italic;color: green;">Created """+str(prheader.Submit.strftime("%d/%m/%Y %H:%M:%S"))+"""</td>
                                    <td style="padding:10px;text-align: center;vertical-align: center;font-style: italic;color: green;" id="DEPH"></td>
                                    <td style="padding:10px;text-align: center;vertical-align: center;font-style: italic;color: green;" id="FIN"></td>
                                    <td style="padding:10px;text-align: center;vertical-align: center;font-style: italic;color: green;" id="DIR"></td>
                                    <td style="padding:10px;border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: center;font-style: italic;color: green;"></td>
                                </tr>
                                <tr style="height:15px;">
                                    <td style="border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">"""+prheader.User_Name.title()+"""</td>
                                    <td style="text-align: center;vertical-align: bottom;">"""+approval.DeptHead.title()+"""</td>
                                    <td style="text-align: center;vertical-align: bottom;">"""+approval.Finance.title()+"""</td>
                                    <td style="text-align: center;vertical-align: bottom;">"""+approval.Direktur.title()+"""</td>
                                    <td style="border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">"""+approval.Purchase.title()+"""</td>
                                </tr>
                                <tr style="height:20px;">
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: center;">User</td>
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: center;">Dept Head</td>
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: center;">Fin&Acc</td>
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: center;">Pres Dir</td>
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: center;">Purchasing</td>
                                </tr>
                            </tbody>
                        </table>
                        """
        elif approval.DeptHead is None:
            apptable = """
                        <table style="border: 1px solid black; font-size: 12px;text-align: center;border-collapse: collapse;" >
                            <tbody >
                                <tr style="height:20px;">
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: center;">Pemesan</td>
                                    <td colspan="3" style="border: 1px solid black;width: 230px;text-align: center;vertical-align: center;">Disetujui/Mengetahui</td>
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: center;">Purchasing</td>
                                </tr>
                                <tr style="height:65px;">
                                    <td style="padding:10px;border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: center;font-style: italic;color: green;">Created """+str(prheader.Submit.strftime("%d/%m/%Y %H:%M:%S"))+"""</td>
                                    <td style="padding:10px;text-align: center;vertical-align: center;font-style: italic;color: green;" id="DIVH"></td>
                                    <td style="padding:10px;text-align: center;vertical-align: center;font-style: italic;color: green;" id="FIN"></td>
                                    <td style="padding:10px;text-align: center;vertical-align: center;font-style: italic;color: green;" id="DIR"></td>
                                    <td style="padding:10px;border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: center;font-style: italic;color: green;"></td>
                                </tr>
                                <tr style="height:15px;">
                                    <td style="border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">"""+prheader.User_Name.title()+"""</td>
                                    <td style="text-align: center;vertical-align: bottom;">"""+approval.DivHead.title()+"""</td>
                                    <td style="text-align: center;vertical-align: bottom;">"""+approval.Finance.title()+"""</td>
                                    <td style="text-align: center;vertical-align: bottom;">"""+approval.Direktur.title()+"""</td>
                                    <td style="border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">"""+approval.Purchase.title()+"""</td>
                                </tr>
                                <tr style="height:20px;">
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: center;">User</td>
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: center;">Div Head</td>
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: center;">Fin&Acc</td>
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: center;">Pres Dir</td>
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: center;">Purchasing</td>
                                </tr>
                            </tbody>
                        </table>
                        """

        else:
            apptable = """
                        <table style="border: 1px solid black; font-size: 12px;text-align: center;border-collapse: collapse;" >
                            <tbody >
                                <tr style="height:20px;">
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: center;">Pemesan</td>
                                    <td colspan="4" style="border: 1px solid black;width: 230px;text-align: center;vertical-align: center;">Disetujui/Mengetahui</td>
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: center;">Purchasing</td>
                                </tr>
                                <tr style="height:65px;">
                                    <td style="padding:10px;border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: center;font-style: italic;color: green;">Created """+str(prheader.Submit.strftime("%d/%m/%Y %H:%M:%S"))+"""</td>
                                    <td style="padding:10px;text-align: center;vertical-align: center;font-style: italic;color: green;" id="DEPH"></td>
                                    <td style="padding:10px;text-align: center;vertical-align: center;font-style: italic;color: green;" id="DIVH"></td>
                                    <td style="padding:10px;text-align: center;vertical-align: center;font-style: italic;color: green;" id="FIN"></td>
                                    <td style="padding:10px;text-align: center;vertical-align: center;font-style: italic;color: green;" id="DIR"></td>
                                    <td style="padding:10px;border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: center;font-style: italic;color: green;"></td>
                                </tr>
                                <tr style="height:15px;">
                                    <td style="border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">"""+prheader.User_Name.title()+"""</td>
                                    <td style="text-align: center;vertical-align: bottom;">"""+approval.DeptHead.title()+"""</td>
                                    <td style="text-align: center;vertical-align: bottom;">"""+approval.DivHead.title()+"""</td>
                                    <td style="text-align: center;vertical-align: bottom;">"""+approval.Finance.title()+"""</td>
                                    <td style="text-align: center;vertical-align: bottom;">"""+approval.Direktur.title()+"""</td>
                                    <td style="border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">"""+approval.Purchase.title()+"""</td>
                                </tr>
                                <tr style="height:20px;">
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: center;">User</td>
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: center;">Dept Head</td>
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: center;">Div Head</td>
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: center;">Fin&Acc</td>
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: center;">Pres Dir</td>
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: center;">Purchasing</td>
                                </tr>
                            </tbody>
                        </table>
                        """
        #SPV = models.EmailList.objects.get(Email = request.POST['SPV_Email'])
       # Superior = ""
        if approval.DeptHead is None:
            Superior = approval.DivHead.title()
        else :
            Superior = approval.DeptHead.title()

        email_body = """\
            <html>
            <head style="margin-bottom: 0px;">Dear Mr/Ms """ + Superior  + """,</head>
            <body>
            <p style="margin-bottom: 0px;margin-top: 0px;">This purchase request needs your approval </>
            
            <center><h3 style="margin: 0px;padding: 0px;">Purchase Request</h3></center>
            <hr >
             <table style= "font-size: x-small;">
                <tr>
                    <td style ="width: 140px;">Company</td>
                    <td>: """+prheader.Company+"""</td>
                </tr>
                <tr>
                    <td>Bussiness Area</td>
                    <td>: """+prheader.Bussiness_Area+"""</td>
                </tr>
                <tr>
                    <td>Date Created</td>
                    <td>: """+str(prheader.Date_Created)+"""</td>
                </tr>
                <tr>
                    <td>Jenis PP </td>
                    <td>: """+prheader.Jenis_PP+"""</td>
                </tr>
                <tr>
                    <td>PP Number</td>
                    <td>: """+prheader.PP_Number+"""</td>
                </tr>
                <tr>
                    <td>User</td>
                    <td>: """+prheader.User_Name+"""</td>
                </tr>
            </table>
       
            <table  style="border: 1px solid black; font-size: 14px;text-align: center;border-collapse: collapse;font-weight: normal;">
                    <thead style="border: 1px solid black;">
                        <tr style="border: 1px solid black; height: 50px; word-break: normal;">
                            <th rowspan="2" style="padding: 5px; border: 1px solid black;font-weight: normal;">No</th>
                            <th rowspan="2" style="padding: 5px;border: 1px solid black;font-weight: normal;">A* (Exp)</th>
                            <th rowspan="2" style="padding: 5px;border: 1px solid black;font-weight: normal;">I* (Jenis)</th>
                            <th rowspan="2" style="padding: 5px;border: 1px solid black;font-weight: normal;">Kode Barang</th>
                            <th rowspan="2" style="padding: 5px;border: 1px solid black;font-weight: normal;">Nama Barang / Deskripsi Service</th>
                            <th colspan="2" style="padding: 5px;border: 1px solid black;font-weight: normal;">Dipesan</th>
                            <th colspan="2" style="padding: 5px;border: 1px solid black;font-weight: normal;">Perkiraan Harga</th>
                            <th rowspan="2" style="padding: 5px;border: 1px solid black;font-weight: normal;">Tanggal Kedatangan</th>
                            <th colspan="2" style="padding: 5px;border: 1px solid black; word-break: keep-all;font-weight: normal;">Account Assignment</th>
                            <th rowspan="2" style="padding: 5px;border: 1px solid black;font-weight: normal; transform: rotate(-90deg); width: 1%; vertical-align: middle; ">Min Stock</th>
                            <th rowspan="2" style="padding: 5px;border: 1px solid black; font-weight: normal;transform: rotate(-90deg); width: 1%; vertical-align: middle; ">Act Stock</th>
                            <th rowspan="2" style="padding: 5px;border: 1px solid black; font-weight: normal;transform: rotate(-90deg); width: 1%; vertical-align: middle; ">Avg Usage</th>
                            <th rowspan="2" style="padding: 5px;border: 1px solid black; font-weight: normal;transform: rotate(-90deg); width: 1%; vertical-align: middle; ">Budget</th>
                            <th rowspan="2" style="padding: 5px;border: 1px solid black; font-weight: normal;transform: rotate(-90deg); width: 1%; vertical-align: middle; ">Un-Budget</th>
                            <th rowspan="2" style="padding: 5px;border: 1px solid black; width: 100px;font-weight: normal;">Catatan</th>
                        </tr>
                        <tr style="height:50px">
                            <th style="padding: 5px;border: 1px solid black;font-weight: normal;">Jumlah</th>
                            <th style="padding: 5px;border: 1px solid black;font-weight: normal;">UoM</th>
                            <th style="padding: 5px;border: 1px solid black;font-weight: normal;">Satuan</th>
                            <th style="padding: 5px;border: 1px solid black;font-weight: normal;">Total</th>
                            <th style="padding: 5px;border: 1px solid black;font-weight: normal;">Cost Center</th>
                            <th style="padding: 5px;border: 1px solid black;font-weight: normal;">Asset No./GL Account</th>
                        </tr>
                    </thead>
                    <tbody>
                    """+contain+"""
                    </tbody>
            </table>
            <br>
            <table>
            <tr>
            <td style="width:75%;">
            """+apptable+"""
            
            </td>
            
            <td style="vertical-align: top;border: 1px solid black;">
                <table style="font-size: 12px;width:100%;">
                <tr>
                <td style ="width:40%;"></td>
                <td colspan="3" style="text-align: right;"> Khusus PP Asset(ZRAT)</td>
                </tr>
                <tr>
                <td>Budget No</td>
                <td>:</td>
                <td>"""+xdotstr(prheader.Budget_No)+"""<td>
                <td style ="width:10%;"></td>
                </tr>
                <tr>
                <td>Budget</td>
                <td>:</td>
                <td style="text-align: right;">"""+xdotstr(prheader.Budget_Rp)+"""<td>
                <td style ="width:10%;"></td>
                </tr>
                <tr>
                <td>PP diproses</td>
                <td>:</td>
                <td style="text-align: right;border-bottom: 1px solid black;">"""+xdotstr(prheader.PP_diProses)+"""<td>
                <td style ="width:10%;"></td>
                </tr>
                <tr>
                <td>Sisa</td>
                <td>:</td>
                <td style="text-align: right;">"""+xdotstr(prheader.Sisa_Budget)+"""<td>
                <td style ="width:10%;"></td>
                </tr>
                <tr>
                <td>PP diajukan</td>
                <td>:</td>
                <td style="text-align: right;border-bottom: 1px solid black;">"""+xdotstr(prheader.PP_diAjukan)+"""<td>
                <td style ="width:10%;"></td>
                </tr>
                <tr>
                <td>Sisa</td>
                <td>:</td>
                <td style="text-align: right;">"""+xdotstr(prheader.Sisa_Final)+"""<td>
                <td style ="width:10%;"></td>
                </tr>
                </table>
            </td>
            </tr>
            </table>
            <h6 style="margin:0px;font-size:12px;font-weight:normal;">(*) Kolom 'A' (Expense) ditandai 'F' untuk internal order, 'K' untuk cost center, 'P' untuk Project, dan 'A' untuk asset.</h6>
	        <h6 style="margin:0px;font-size:12px;font-weight:normal;">(*) Kolom 'I' (Jenis Barang) : K = Konsinyasi, L = Subcontracting, D = Service.</h6>																				
	        <h6 style="margin:0px;font-size:12px;font-weight:normal;">(*) "Catatan" dapat menunjukkan keterangan forecasting, tempat pengiriman spesifik, lokasi asset, dan lainnya.</h6>
            <br>
            <hr>
            <p> Please give your response by click approval button bellow and then click send button. A response at your earliest convenience would be much appreciated. </p>
            <table width="100%" cellspacing="0" cellpadding="0">
                <tr>
                    <td>
                        <table cellspacing="0" cellpadding="0">
                            <tr>
                                <td style="border-radius: 2px;width : 150px;text-align: center;" bgcolor="#4bf542">
                                    <a href="mailto:online.approval@aski.component.astra.co.id?subject=Approve:"""+prheader.PP_Number+"""&body=Approve Purchase Request with ID """+prheader.PP_Number+""" %0DApproval Message:" target="_blank" style="padding: 8px 12px; border: 1px solid #4bf542;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #ffffff;text-decoration: none;font-weight:bold;display: inline-block;">
                                        APPROVE             
                                    </a>
                                </td>
                                <td>&nbsp;&nbsp;</td>
                                <td style="border-radius: 2px;width: 150px;text-align: center;" bgcolor="#ED2939">
                                    <a href="mailto:online.approval@aski.component.astra.co.id?subject=Reject:"""+prheader.PP_Number+"""&body=Reject  Purchase Request with ID """+prheader.PP_Number+""" %0DReject Message:" target="_blank" style="padding: 8px 12px; border: 1px solid #ED2939;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #ffffff;text-decoration: none;font-weight:bold;display: inline-block;">
                                        REJECT             
                                    </a>
                                </td>
                                <td>&nbsp;&nbsp;</td>
                                <td style="border-radius: 2px;width: 150px;text-align: center;" bgcolor="#ebde34">
                                    <a href="mailto:online.approval@aski.component.astra.co.id?subject=Revise:"""+prheader.PP_Number+"""&body=Need Revise Purchase Request with ID """+prheader.PP_Number+""" %0DRevision Message:" target="_blank" style="padding: 8px 12px; border: 1px solid #ebde34;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #000000;text-decoration: none;font-weight:bold;display: inline-block;">
                                        REVISE             
                                    </a>
                                </td>
                                <td>&nbsp;&nbsp;</td>
                                <td style="border-radius: 2px;width: 150px;text-align: center;" bgcolor="#cccccc">
                                    <a href="mailto:"""+prheader.User_Email+"""?subject=Ask User:"""+prheader.PP_Number+"""&body=Ask User about Purchase Request with ID """+prheader.PP_Number+""" %0DAsk User Message: " target="_blank" style="padding: 8px 12px; border: 1px solid #cccccc;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #000000;text-decoration: none;font-weight:bold;display: inline-block;">
                                        ASK USER             
                                    </a>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
            
            <br>
            <i>This email is automatically generated by Online Approval System PT Astra Komponen Indonesia<i>


            </body>
            </html>
            """
        if approval.DeptHead is None:
            mailattach = EmailMessage(
                'Purchase Request Online Approval: ' + request.POST['PP_Number'],
                body=email_body,
                from_email=settings.EMAIL_HOST_USER,
                to=[request.POST['Div_Head_Email']],
            )
            mailattach.content_subtype = "html"

        else :
            mailattach = EmailMessage(
                'Purchase Request Online Approval: ' + request.POST['PP_Number'],
                body=email_body,
                from_email=settings.EMAIL_HOST_USER,
                to=[request.POST['Dept_Head_Email']],
            )
            mailattach.content_subtype = "html"

        

        if 'Attachment1' in request.FILES:
            mailattach.attach_file(
                'Media/Uploads/'+str(request.FILES['Attachment1']).replace(' ', '_'))
        if 'Attachment2' in request.FILES:
            mailattach.attach_file(
                'Media/Uploads/'+str(request.FILES['Attachment2']).replace(' ', '_'))
        if 'Attachment3' in request.FILES:
            mailattach.attach_file(
                'Media/Uploads/'+str(request.FILES['Attachment3']).replace(' ', '_'))

        mailattach.send()
        if approval.DeptHead is None:
            email = models.Send(htmlmessage=email_body,
                            mailfrom='online.approval@aski.component.astra.co.id',
                            mailto=request.POST['Div_Head_Email'],
                            PP_Number=request.POST['PP_Number'],
                            mailheader='Purchase Request Online Approval: ' + request.POST['PP_Number'])
        else :
            email = models.Send(htmlmessage=email_body,
                            mailfrom='online.approval@aski.component.astra.co.id',
                            mailto=request.POST['Dept_Head_Email'],
                            PP_Number=request.POST['PP_Number'],
                            mailheader='Purchase Request Online Approval: ' + request.POST['PP_Number'])
        email.save()
        if prheader.Budget_No is not None:
            models.Budget.objects.filter(Budget_No = prheader.Budget_No).update(Current_Budget_Value =prheader.Sisa_Final.replace(" IDR", ""))

        models.PRheader.objects.filter(
            PP_Number=request.POST['PP_Number']).update(PR_Status="Created")

        context.update(
            {'PRitem': pritem, 'mode': "finish", 'PRheader': prheader})

    return render(request, 'purchaserequest/CreatePR.html', context)


@login_required
def listPP(request):
    #print(request.user.username)
    if (request.user.username == "admin"):
        prheader = models.PRheader.objects.all().exclude(PR_Status = None).order_by('-PP_Number')


    elif (request.user.username == "FINANCE"):
        prheader = models.PRheader.objects.all().exclude(PR_Status = None).order_by('-PP_Number')
    elif (request.user.username == "ADMINFINANCE"):
        prheader = models.PRheader.objects.all().exclude(PR_Status = None).order_by('-PP_Number')
    elif (request.user.username == "PROCUREMENT"):
        prheader = models.PRheader.objects.filter(
            PR_Status="Finished").order_by('-PP_Number') | models.PRheader.objects.filter(
            PP_Number__contains=request.user.username).exclude(PR_Status = None).order_by('-PP_Number')
    else:
        prheader = models.PRheader.objects.filter(
            PP_Number__contains=request.user.username).exclude(PR_Status = None).order_by('-PP_Number')
    
    pritem = models.PRitem.objects.filter(PP_Number__in=list(prheader.exclude(PR_Status = "Revised").only("PP_Number")))

    if 'save' in request.POST:
        data = dict(request.POST)
        data.pop('csrfmiddlewaretoken')
        data.pop('table_length')
        for key in data.keys():
            var = key.split(" ", 2)
            value = str(data[key])[2:][:-2]
            if (len(value) > 0 and var[0] == "PS"):
                models.PRheader.objects.filter(PP_Number=var[1]).update(
                    Purchasing_Status=value)


    context = {
        'Judul': 'List Purchase Request',
        'PRheader': prheader,
        'PRitem' : pritem,
    }
    return render(request, 'purchaserequest/ListPP.html', context)


@login_required
def detail(request, ID):
    PP_Number = ID

    prheader = models.PRheader.objects.get(PP_Number=ID)
    itemlist = list(models.PRitem.objects.filter(PP_Number=ID))
    approval = models.Approval.objects.get(Supervisor_email=prheader.SPV_Email, User = PP_Number.replace("ASKIPP","").split("rev", 1)[0][:-5])
    budget = list(models.Budget.objects.all())

    if request.method == "POST":
        models.activity_log(user = request.user.username,PP_Number=PP_Number,activity=request.POST).save()
        prheaderform = forms.PRheader(
            request.POST, request.FILES, instance=prheader)

        if prheaderform.is_valid():
            prheaderform.save()
        else:
            print(prheaderform.errors)
    else:
        prheaderform = forms.PRheader(instance=prheader)

    context = {
        'Judul': 'Detail Purchase Request',
        'PP_Number': PP_Number,
        'PRheader': prheader,
        'PRheaderform': prheaderform,
        'itemlist': itemlist,
        'Approval': approval,
        'Budget': budget,
    }
    return render(request, 'purchaserequest/Detail.html', context)


@login_required
@user_passes_test(is_memberaddasset)
def assetlist(request):

    prheader = models.PRheader.objects.filter(
        PR_Status="AddAsset").order_by('-PP_Number')

    context = {
        'Judul': 'List Purchase Request',
        'PRheader': prheader,
    }
    return render(request, 'purchaserequest/ListAsset.html', context)


@login_required
@user_passes_test(is_memberaddasset)
def detailasset(request, ID):
    PP_Number = ID
    prheader = models.PRheader.objects.get(PP_Number=ID)
    itemlist = list(models.PRitem.objects.filter(PP_Number=ID).order_by('id'))
    approval = models.Approval.objects.get(Supervisor_email=prheader.SPV_Email, User = PP_Number.replace("ASKIPP","").split("rev", 1)[0][:-5])
    costcenter = list(models.CostCenter.objects.all())
    budget = list(models.Budget.objects.all())
    
    if 'revision' in request.POST:
        print(request.POST)
        models.HistoryApproval(PP_Number = PP_Number, Approval_By = 'Finance',Email_By = 'online.approval@aski.component.astra.co.id', Approval_Status = 'Need Revise', Comment = request.POST['revisemessage']).save()
        models.PRheader.objects.filter(PP_Number=PP_Number).update(PR_Status = 'NeedRevise')
        return assetlist(request)
    elif 'save' in request.POST:
        models.activity_log(user = request.user.username,PP_Number=PP_Number,activity=request.POST).save()
        data = dict(request.POST)
        data.pop('csrfmiddlewaretoken')
        print(data.keys())
        print(request.POST)
        for key in data.keys():
            var = key.split(" ", 2)
            value = str(data[key])[2:][:-2]
            if (len(value) > 0 and var[0] == "Asset"):
                models.PRitem.objects.filter(PP_Number=var[1], Nama_Barang=var[2]).update(
                    Asset_No_GL_Account=value)
            if (len(value) > 0 and var[0] == "Cost"):
                models.PRitem.objects.filter(
                    PP_Number=var[1], Nama_Barang=var[2]).update(Cost_Center=value)
            if (len(value) > 0 and var[0] == "Expense"):
                models.PRitem.objects.filter(
                    PP_Number=var[1], Nama_Barang=var[2]).update(Expense=value)
            if (len(value) > 0 and var[0] == "Jenis"):
                models.PRitem.objects.filter(
                    PP_Number=var[1], Nama_Barang=var[2]).update(Jenis_Barang=value)
            if (len(value) > 0 and var[0] == "BudgetNo"):
                if value =="delete":
                    print("delete")
                    models.PRheader.objects.filter(
                        PP_Number=var[1]).update(Budget_No=None,Budget_Rp=None,PP_diProses=None,Sisa_Budget=None,PP_diAjukan=None,Sisa_Final=None)
                else :
                    models.PRheader.objects.filter(
                        PP_Number=var[1]).update(Budget_No=value)
            if (len(value) > 0 and var[0] == "BudgetRp"):
                models.PRheader.objects.filter(
                    PP_Number=var[1]).update(Budget_Rp=value)
            if (len(value) > 0 and var[0] == "PPproses"):
                models.PRheader.objects.filter(
                    PP_Number=var[1]).update(PP_diProses=value)
            if (len(value) > 0 and var[0] == "SisaBudget"):
                models.PRheader.objects.filter(
                    PP_Number=var[1]).update(Sisa_Budget=value)
            if (len(value) > 0 and var[0] == "PPdiajukan"):
                models.PRheader.objects.filter(
                    PP_Number=var[1]).update(PP_diAjukan=value)
            if (len(value) > 0 and var[0] == "SisaFinal"):
                models.PRheader.objects.filter(
                    PP_Number=var[1]).update(Sisa_Final=value)
            if (len(value) > 0 and var[0] == "JenisPP"):
                models.PRheader.objects.filter(
                    PP_Number=var[1]).update(Jenis_PP=value)
        itemlist = list(models.PRitem.objects.filter(
            PP_Number=ID).order_by('id'))
        prheader = models.PRheader.objects.get(PP_Number=ID)
    elif 'finish' in request.POST:
        models.activity_log(user = request.user.username,PP_Number=PP_Number,activity=request.POST).save()
        if prheader.Budget_No is not None :
            bud = models.Budget.objects.get(Budget_No = prheader.Budget_No)
            if approval.DivHead is None and 'PROJECT' in bud.Budget_User:
                approval.DivHead = 'HENDRO WITJAKSONO'
                approval.DivHead_email = 'hendro.witjaksono@aski.co.id'
   
        counter = 0
        contain = ''
        for item in itemlist:
            counter += 1
            contain += '''<tr style="height: 30px; font-size:12px;">
                    <td style="border: 1px solid black;">'''+str(counter)+'''</td>
                    <td style="border: 1px solid black;">'''+xstr(item.Expense)+'''</td>
                    <td style="border: 1px solid black;">'''+xstr(item.Jenis_Barang)+'''</td>
                    <td style="border: 1px solid black;">'''+xstr(item.Kode_Barang)+'''</td>
                    <td style="border: 1px solid black; text-align: left;padding-left: 5px;width:15%;">'''+item.Nama_Barang+" "+xstr(item.Detail_Spec)+'''</td>
                    <td style="border: 1px solid black;">'''+str(item.Jumlah_Order)+'''</td>
                    <td style="border: 1px solid black;">'''+str(item.Unit_Order)+'''</td>
                    <td style="border: 1px solid black;">'''+xstr(item.Harga_Satuan)+" "+xstr(item.Currency)+'''</td>
                    <td style="border: 1px solid black;">'''+xstr(item.Harga_Total)+" "+xstr(item.Currency)+'''</td>
                    <td style="border: 1px solid black;">'''+xstr(item.Tgl_Kedatangan)+'''</td>
                    <td style="border: 1px solid black;">'''+xstr(item.Cost_Center)+'''</td>
                    <td style="border: 1px solid black;">'''+xstr(item.Asset_No_GL_Account)+'''</td>
                    <td style="border: 1px solid black;">'''+xstr(item.Minimal_Stock)+'''</td>
                    <td style="border: 1px solid black;">'''+xstr(item.Actual_Stock)+'''</td>
                    <td style="border: 1px solid black;">'''+xstr(item.Average_Usage)+'''</td>
                    <td style="border: 1px solid black;"></td>
                    <td style="border: 1px solid black;"></td>
                    <td style="border: 1px solid black;">'''+xstr(item.Note)+'''</td>
                </tr>'''

        if approval.DivHead is None:
            apptable = """
                        <table style="border: 1px solid black; font-size: 12px;text-align: center;border-collapse: collapse;" >
                            <tbody >
                                <tr style="height:15px;">
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Pemesan</td>
                                    <td colspan="3" style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Disetujui/Mengetahui</td>
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Purchasing</td>
                                </tr>
                                <tr style="height:50px;">
                                    <td style="border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;">Created """+str(prheader.Submit.strftime("%d/%m/%Y %H:%M:%S"))+"""</td>
                                    <td style="text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="DEPH"> Approved """ + str(prheader.Dept_Head_Approval_Date.strftime("%d/%m/%Y %H:%M:%S")) + """</td>
                                    <td style="text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="FIN"></td>
                                    <td style="text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="DIR"></td>
                                    <td style="border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;"></td>
                                </tr>
                                <tr style="height:20px;">
                                    <td style="border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">"""+prheader.User_Name.title()+"""</td>
                                    <td style="text-align: center;vertical-align: bottom;">"""+approval.DeptHead.title()+"""</td>
                                    <td style="text-align: center;vertical-align: bottom;">"""+approval.Finance.title()+"""</td>
                                    <td style="text-align: center;vertical-align: bottom;">"""+approval.Direktur.title()+"""</td>
                                    <td style="border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">"""+approval.Purchase.title()+"""</td>
                                </tr>
                                <tr style="height:15px;">
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Supervisor</td>
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Dept Head</td>
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Fin&Acc</td>
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Pres Dir</td>
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Purchasing</td>
                                </tr>
                            </tbody>
                        </table>
                        """
        elif approval.DeptHead is None:
            apptable = """
                        <table style="border: 1px solid black; font-size: 12px;text-align: center;border-collapse: collapse;" >
                            <tbody >
                                <tr style="height:15px;">
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Pemesan</td>
                                    <td colspan="3" style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Disetujui/Mengetahui</td>
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Purchasing</td>
                                </tr>
                                <tr style="height:50px;">
                                    <td style="border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;">Created """+str(prheader.Submit.strftime("%d/%m/%Y %H:%M:%S"))+"""</td>
                                    <td style="text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="DIVH"> Approved """ + str(prheader.Div_Head_Approval_Date.strftime("%d/%m/%Y %H:%M:%S")) + """</td>
                                    <td style="text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="FIN"></td>
                                    <td style="text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="DIR"></td>
                                    <td style="border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;"></td>
                                </tr>
                                <tr style="height:20px;">
                                    <td style="border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">"""+prheader.User_Name.title()+"""</td>
                                    <td style="text-align: center;vertical-align: bottom;">"""+approval.DivHead.title()+"""</td>
                                    <td style="text-align: center;vertical-align: bottom;">"""+approval.Finance.title()+"""</td>
                                    <td style="text-align: center;vertical-align: bottom;">"""+approval.Direktur.title()+"""</td>
                                    <td style="border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">"""+approval.Purchase.title()+"""</td>
                                </tr>
                                <tr style="height:15px;">
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Supervisor</td>
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Div Head</td>
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Fin&Acc</td>
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Pres Dir</td>
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Purchasing</td>
                                </tr>
                            </tbody>
                        </table>
                        """

        else:
            apptable = """
                        <table style="border: 1px solid black; font-size: 12px;text-align: center;border-collapse: collapse;" >
                            <tbody >
                                <tr style="height:15px;">
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Pemesan</td>
                                    <td colspan="4" style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Disetujui/Mengetahui</td>
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Purchasing</td>
                                </tr>
                                <tr style="height:50px;">
                                    <td style="border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;">Created """+str(prheader.Submit.strftime("%d/%m/%Y %H:%M:%S"))+"""</td>
                                    <td style="text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="DEPH">Approved """ + str(prheader.Dept_Head_Approval_Date.strftime("%d/%m/%Y %H:%M:%S")) + """</td>
                                    <td style="text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="DIVH">Approved """ + str(prheader.Div_Head_Approval_Date.strftime("%d/%m/%Y %H:%M:%S")) + """</td>
                                    <td style="text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="FIN"></td>
                                    <td style="text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="DIR"></td>
                                    <td style="border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;"></td>
                                </tr>
                                <tr style="height:20px;">
                                    <td style="border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">"""+prheader.User_Name.title()+"""</td>
                                    <td style="text-align: center;vertical-align: bottom;">"""+approval.DeptHead.title()+"""</td>
                                    <td style="text-align: center;vertical-align: bottom;">"""+approval.DivHead.title()+"""</td>
                                    <td style="text-align: center;vertical-align: bottom;">"""+approval.Finance.title()+"""</td>
                                    <td style="text-align: center;vertical-align: bottom;">"""+approval.Direktur.title()+"""</td>
                                    <td style="border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">"""+approval.Purchase.title()+"""</td>
                                </tr>
                                <tr style="height:15px;">
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">User</td>
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Dept Head</td>
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Div Head</td>
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Fin&Acc</td>
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Pres Dir</td>
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Purchasing</td>
                                </tr>
                            </tbody>
                        </table>
                        """
        #SPV = models.EmailList.objects.get(Email = request.POST['SPV_Email'])
        email_body = """\
            <html>
            <head style="margin-bottom: 0px;">Dear Mr/Ms """ + approval.Finance.title() + """,</head>
            <body>
            <p style="margin-bottom: 0px;margin-top: 0px;">This purchase request needs your approval </>
            
            <center><h3 style="margin: 0px;padding: 0px;">Purchase Request</h3></center>
            <hr >
             <table style= "font-size: x-small;">
                <tr>
                    <td style ="width: 140px;">Company</td>
                    <td>: """+prheader.Company+"""</td>
                </tr>
                <tr>
                    <td>Bussiness Area</td>
                    <td>: """+prheader.Bussiness_Area+"""</td>
                </tr>
                <tr>
                    <td>Date Created</td>
                    <td>: """+str(prheader.Date_Created)+"""</td>
                </tr>
                <tr>
                    <td>Jenis PP </td>
                    <td>: """+prheader.Jenis_PP+"""</td>
                </tr>
                <tr>
                    <td>PP Number</td>
                    <td>: """+prheader.PP_Number+"""</td>
                </tr>
                <tr>
                    <td>User</td>
                    <td>: """+prheader.User_Name+"""</td>
                </tr>
            </table>
       
            <table  style="border: 1px solid black; font-size: x-small;text-align: center;border-collapse: collapse;font-weight: normal;">
                    <thead style="border: 1px solid black;">
                        <tr style="border: 1px solid black; height: 50px; word-break: normal;">
                            <th rowspan="2" style="padding: 5px; border: 1px solid black;font-weight: normal;">No</th>
                            <th rowspan="2" style="padding: 5px;border: 1px solid black;font-weight: normal;">A* (Exp)</th>
                            <th rowspan="2" style="padding: 5px;border: 1px solid black;font-weight: normal;">I* (Jenis)</th>
                            <th rowspan="2" style="padding: 5px;border: 1px solid black;font-weight: normal;">Kode Barang</th>
                            <th rowspan="2" style="padding: 5px;border: 1px solid black;font-weight: normal;">Nama Barang / Deskripsi Service</th>
                            <th colspan="2" style="padding: 5px;border: 1px solid black;font-weight: normal;">Dipesan</th>
                            <th colspan="2" style="padding: 5px;border: 1px solid black;font-weight: normal;">Perkiraan Harga</th>
                            <th rowspan="2" style="padding: 5px;border: 1px solid black;font-weight: normal;">Tanggal Kedatangan</th>
                            <th colspan="2" style="padding: 5px;border: 1px solid black; word-break: keep-all;font-weight: normal;">Account Assignment</th>
                            <th rowspan="2" style="padding: 5px;border: 1px solid black;font-weight: normal; transform: rotate(-90deg); width: 1%; vertical-align: middle; ">Min Stock</th>
                            <th rowspan="2" style="padding: 5px;border: 1px solid black; font-weight: normal;transform: rotate(-90deg); width: 1%; vertical-align: middle; ">Act Stock</th>
                            <th rowspan="2" style="padding: 5px;border: 1px solid black; font-weight: normal;transform: rotate(-90deg); width: 1%; vertical-align: middle; ">Avg Usage</th>
                            <th rowspan="2" style="padding: 5px;border: 1px solid black; font-weight: normal;transform: rotate(-90deg); width: 1%; vertical-align: middle; ">Budget</th>
                            <th rowspan="2" style="padding: 5px;border: 1px solid black; font-weight: normal;transform: rotate(-90deg); width: 1%; vertical-align: middle; ">Un-Budget</th>
                            <th rowspan="2" style="padding: 5px;border: 1px solid black; width: 100px;font-weight: normal;">Catatan</th>
                        </tr>
                        <tr style="height:50px">
                            <th style="padding: 5px;border: 1px solid black;font-weight: normal;">Jumlah</th>
                            <th style="padding: 5px;border: 1px solid black;font-weight: normal;">UoM</th>
                            <th style="padding: 5px;border: 1px solid black;font-weight: normal;">Satuan</th>
                            <th style="padding: 5px;border: 1px solid black;font-weight: normal;">Total</th>
                            <th style="padding: 5px;border: 1px solid black;font-weight: normal;">Cost Center</th>
                            <th style="padding: 5px;border: 1px solid black;font-weight: normal;">Asset No./GL Account</th>
                        </tr>
                    </thead>
                    <tbody>
                    """+contain+"""
                    </tbody>
            </table>
            <br>

            <table>
            <tr>
            <td style="width:75%;">
            """+apptable+"""
            
            </td>
            
            <td style="vertical-align: top;border: 1px solid black;">
                               <table style="font-size: 12px;width:100%;">
                <tr>
                <td style ="width:40%;"></td>
                <td colspan="3" style="text-align: right;"> Khusus PP Asset(ZRAT)</td>
                </tr>
                <tr>
                <td>Budget No</td>
                <td>:</td>
                <td>"""+xdotstr(prheader.Budget_No)+"""<td>
                <td style ="width:10%;"></td>
                </tr>
                <tr>
                <td>Budget</td>
                <td>:</td>
                <td style="text-align: right;">"""+xdotstr(prheader.Budget_Rp)+"""<td>
                <td style ="width:10%;"></td>
                </tr>
                <tr>
                <td>PP diproses</td>
                <td>:</td>
                <td style="text-align: right;border-bottom: 1px solid black;">"""+xdotstr(prheader.PP_diProses)+"""<td>
                <td style ="width:10%;"></td>
                </tr>
                <tr>
                <td>Sisa</td>
                <td>:</td>
                <td style="text-align: right;">"""+xdotstr(prheader.Sisa_Budget)+"""<td>
                <td style ="width:10%;"></td>
                </tr>
                <tr>
                <td>PP diajukan</td>
                <td>:</td>
                <td style="text-align: right;border-bottom: 1px solid black;">"""+xdotstr(prheader.PP_diAjukan)+"""<td>
                <td style ="width:10%;"></td>
                </tr>
                <tr>
                <td>Sisa</td>
                <td>:</td>
                <td style="text-align: right;">"""+xdotstr(prheader.Sisa_Final)+"""<td>
                <td style ="width:10%;"></td>
                </tr>
                </table>
            </td>
            </tr>
            </table>
            <h6 style="margin:0px;font-size:12px;font-weight:normal;">(*) Kolom 'A' (Expense) ditandai 'F' untuk internal order, 'K' untuk cost center, 'P' untuk Project, dan 'A' untuk asset.</h6>
	        <h6 style="margin:0px;font-size:12px;font-weight:normal;">(*) Kolom 'I' (Jenis Barang) : K = Konsinyasi, L = Subcontracting, D = Service.</h6>																				
	        <h6 style="margin:0px;font-size:12px;font-weight:normal;">(*) "Catatan" dapat menunjukkan keterangan forecasting, tempat pengiriman spesifik, lokasi asset, dan lainnya.</h6>
            <br>
            <hr>
            <p> Please give your response by click approval button bellow and then click send button. A response at your earliest convenience would be much appreciated. </p>
            <table width="100%" cellspacing="0" cellpadding="0">
                <tr>
                    <td>
                        <table cellspacing="0" cellpadding="0">
                            <tr>
                                <td style="border-radius: 2px;width : 150px;text-align: center;" bgcolor="#4bf542">
                                    <a href="mailto:online.approval@aski.component.astra.co.id?subject=Approve:"""+prheader.PP_Number+"""&body=Approve Purchase Request with ID """+prheader.PP_Number+""" %0DApproval Message:" target="_blank" style="padding: 8px 12px; border: 1px solid #4bf542;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #ffffff;text-decoration: none;font-weight:bold;display: inline-block;">
                                        APPROVE             
                                    </a>
                                </td>
                                <td>&nbsp;&nbsp;</td>
                                <td style="border-radius: 2px;width: 150px;text-align: center;" bgcolor="#ED2939">
                                    <a href="mailto:online.approval@aski.component.astra.co.id?subject=Reject:"""+prheader.PP_Number+"""&body=Reject  Purchase Request with ID """+prheader.PP_Number+""" %0DReject Message:" target="_blank" style="padding: 8px 12px; border: 1px solid #ED2939;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #ffffff;text-decoration: none;font-weight:bold;display: inline-block;">
                                        REJECT             
                                    </a>
                                </td>
                                <td>&nbsp;&nbsp;</td>
                                <td style="border-radius: 2px;width: 150px;text-align: center;" bgcolor="#ebde34">
                                    <a href="mailto:online.approval@aski.component.astra.co.id?subject=Revise:"""+prheader.PP_Number+"""&body=Need Revise Purchase Request with ID """+prheader.PP_Number+""" %0DRevision Message:" target="_blank" style="padding: 8px 12px; border: 1px solid #ebde34;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #000000;text-decoration: none;font-weight:bold;display: inline-block;">
                                        REVISE             
                                    </a>
                                </td>
                                <td>&nbsp;&nbsp;</td>
                                <td style="border-radius: 2px;width: 150px;text-align: center;" bgcolor="#cccccc">
                                    <a href="mailto:"""+prheader.User_Email+"""?subject=Ask User:"""+prheader.PP_Number+"""&body=Ask User about Purchase Request with ID """+prheader.PP_Number+""" %0DAsk User Message: " target="_blank" style="padding: 8px 12px; border: 1px solid #cccccc;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #000000;text-decoration: none;font-weight:bold;display: inline-block;">
                                        ASK USER             
                                    </a>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
            
            <br>
            <i>This email is automatically generated by Online Approval System PT Astra Komponen Indonesia<i>


            </body>
            </html>
            """

        models.Send.objects.filter(PP_Number=PP_Number).update(
            htmlmessagefin=email_body)

        mailattach = EmailMessage(
            'Purchase Request Online Approval: ' + PP_Number,
            body=email_body,
            from_email=settings.EMAIL_HOST_USER,
            to=[prheader.Finance_Email],

        )
        mailattach.content_subtype = "html"
  
        if len(str(prheader.Attachment1))>1:
            mailattach.attach_file(
                'Media/'+str(prheader.Attachment1))
        if len(str(prheader.Attachment2))>1:
            mailattach.attach_file(
                'Media/'+str(prheader.Attachment2))
        if len(str(prheader.Attachment3))>1:
            mailattach.attach_file(
                'Media/'+str(prheader.Attachment3))

        mailattach.send()
        models.PRheader.objects.filter(
            PP_Number=ID).update(PR_Status='Added Asset No')
        
        return assetlist(request)
    context = {
        'Judul': 'Detail Purchase Request',
        'PP_Number': PP_Number,
        'PRheader': models.PRheader.objects.get(PP_Number=ID),
        'Budget' : budget,
        'itemlist': itemlist,
        'Approval': approval,
        'CostCenter': costcenter,
    }
    return render(request, 'purchaserequest/DetailAsset.html', context)


@login_required
@user_passes_test(is_memberaddprno)
def addprnumber(request):
    # print(request.user.username)
    prheader = models.PRheader.objects.filter(
        PR_Status="AddPRNumber").order_by('-PP_Number')

    context = {
        'Judul': 'List Purchase Request',
        'PRheader': prheader,
    }
    return render(request, 'purchaserequest/ListNumber.html', context)


@login_required
@user_passes_test(is_memberaddprno)
def detailnumber(request, ID):
    PP_Number = ID



    if 'save' in request.POST:
        models.activity_log(user = request.user.username,PP_Number=PP_Number,activity=request.POST).save()
        data = dict(request.POST)
        value = str(data['PR_Number'])[2:][:-2]
        if (len(value) > 0):
            models.PRheader.objects.filter(PP_Number=PP_Number).update(
                PR_Number=value, PR_Date=datetime.datetime.now(), PR_Status="Added PR Number")
        print(request.POST)

    prheader = models.PRheader.objects.get(PP_Number=ID)
    itemlist = list(models.PRitem.objects.filter(PP_Number=ID).order_by('id'))
    approval = models.Approval.objects.get(Supervisor_email=prheader.SPV_Email, User = PP_Number.replace("ASKIPP","").split("rev", 1)[0][:-5])
    if prheader.Budget_No is not None :
        bud = models.Budget.objects.get(Budget_No = prheader.Budget_No)
        if approval.DivHead is None and 'PROJECT' in bud.Budget_User:
                approval.DivHead = 'HENDRO WITJAKSONO'
                approval.DivHead_email = 'hendro.witjaksono@aski.co.id'

    if 'finish' in request.POST:
        models.activity_log(user = request.user.username,PP_Number=PP_Number,activity=request.POST).save()
        counter = 0
        contain = ''
        for item in itemlist:
            counter += 1
            contain += '''<tr style="height: 30px; font-size:12px;">
                    <td style="border: 1px solid black;">'''+str(counter)+'''</td>
                    <td style="border: 1px solid black;">'''+xstr(item.Expense)+'''</td>
                    <td style="border: 1px solid black;">'''+xstr(item.Jenis_Barang)+'''</td>
                    <td style="border: 1px solid black;">'''+xstr(item.Kode_Barang)+'''</td>
                    <td style="border: 1px solid black; text-align: left;padding-left: 5px;width:15%;">'''+item.Nama_Barang+" "+xstr(item.Detail_Spec)+'''</td>
                    <td style="border: 1px solid black;">'''+str(item.Jumlah_Order)+'''</td>
                    <td style="border: 1px solid black;">'''+str(item.Unit_Order)+'''</td>
                    <td style="border: 1px solid black;">'''+xstr(item.Harga_Satuan)+" "+xstr(item.Currency)+'''</td>
                    <td style="border: 1px solid black;">'''+xstr(item.Harga_Total)+" "+xstr(item.Currency)+'''</td>
                    <td style="border: 1px solid black;">'''+xstr(item.Tgl_Kedatangan)+'''</td>
                    <td style="border: 1px solid black;">'''+xstr(item.Cost_Center)+'''</td>
                    <td style="border: 1px solid black;">'''+xstr(item.Asset_No_GL_Account)+'''</td>
                    <td style="border: 1px solid black;">'''+xstr(item.Minimal_Stock)+'''</td>
                    <td style="border: 1px solid black;">'''+xstr(item.Actual_Stock)+'''</td>
                    <td style="border: 1px solid black;">'''+xstr(item.Average_Usage)+'''</td>
                    <td style="border: 1px solid black;"></td>
                    <td style="border: 1px solid black;"></td>
                    <td style="border: 1px solid black;">'''+xstr(item.Note)+'''</td>
                </tr>'''

        if approval.DivHead is None:
            apptable = """
                        <table style="border: 1px solid black; font-size: 12px;text-align: center;border-collapse: collapse;" >
                            <tbody >
                                <tr style="height:15px;">
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Pemesan</td>
                                    <td colspan="3" style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Disetujui/Mengetahui</td>
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Purchasing</td>
                                </tr>
                                <tr style="height:50px;">
                                    <td style="border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;">Created """+str(prheader.Submit.strftime("%d/%m/%Y %H:%M:%S"))+"""</td>
                                    <td style="text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="DEPH"> Approved """ + str(prheader.Dept_Head_Approval_Date.strftime("%d/%m/%Y %H:%M:%S")) + """</td>
                                    <td style="text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="FIN"> Approved """ + str(prheader.Finance_Approval_Date.strftime("%d/%m/%Y %H:%M:%S")) + """</td>
                                    <td style="text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="DIR"> Approved """ + str(prheader.Direktur_Approval_Date.strftime("%d/%m/%Y %H:%M:%S")) + """</td>
                                    <td style="border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;"></td>
                                </tr>
                                <tr style="height:20px;">
                                    <td style="border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">"""+prheader.User_Name.title()+"""</td>
                                    <td style="text-align: center;vertical-align: bottom;">"""+approval.DeptHead.title()+"""</td>
                                    <td style="text-align: center;vertical-align: bottom;">"""+approval.Finance.title()+"""</td>
                                    <td style="text-align: center;vertical-align: bottom;">"""+approval.Direktur.title()+"""</td>
                                    <td style="border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">"""+approval.Purchase.title()+"""</td>
                                </tr>
                                <tr style="height:15px;">
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Supervisor</td>
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Dept Head</td>
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Fin&Acc</td>
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Pres Dir</td>
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Purchasing</td>
                                </tr>
                            </tbody>
                        </table>
                        """
        elif approval.DeptHead is None:
            apptable = """
                        <table style="border: 1px solid black; font-size: 12px;text-align: center;border-collapse: collapse;" >
                            <tbody >
                                <tr style="height:15px;">
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Pemesan</td>
                                    <td colspan="3" style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Disetujui/Mengetahui</td>
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Purchasing</td>
                                </tr>
                                <tr style="height:50px;">
                                    <td style="border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;">Created """+str(prheader.Submit.strftime("%d/%m/%Y %H:%M:%S"))+"""</td>
                                    <td style="text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="DIVH"> Approved """ + str(prheader.Div_Head_Approval_Date.strftime("%d/%m/%Y %H:%M:%S")) + """</td>
                                    <td style="text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="FIN"> Approved """ + str(prheader.Finance_Approval_Date.strftime("%d/%m/%Y %H:%M:%S")) + """</td>
                                    <td style="text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="DIR"> Approved """ + str(prheader.Direktur_Approval_Date.strftime("%d/%m/%Y %H:%M:%S")) + """</td>
                                    <td style="border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;"></td>
                                </tr>
                                <tr style="height:20px;">
                                    <td style="border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">"""+prheader.User_Name.title()+"""</td>
                                    <td style="text-align: center;vertical-align: bottom;">"""+approval.DivHead.title()+"""</td>
                                    <td style="text-align: center;vertical-align: bottom;">"""+approval.Finance.title()+"""</td>
                                    <td style="text-align: center;vertical-align: bottom;">"""+approval.Direktur.title()+"""</td>
                                    <td style="border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">"""+approval.Purchase.title()+"""</td>
                                </tr>
                                <tr style="height:15px;">
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Supervisor</td>
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Div Head</td>
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Fin&Acc</td>
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Pres Dir</td>
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Purchasing</td>
                                </tr>
                            </tbody>
                        </table>
                        """

        else:
            apptable = """
                        <table style="border: 1px solid black; font-size: 12px;text-align: center;border-collapse: collapse;" >
                            <tbody >
                                <tr style="height:15px;">
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Pemesan</td>
                                    <td colspan="4" style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Disetujui/Mengetahui</td>
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Purchasing</td>
                                </tr>
                                <tr style="height:50px;">
                                    <td style="border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;">Created """+str(prheader.Submit.strftime("%d/%m/%Y %H:%M:%S"))+"""</td>
                                    <td style="text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="DEPH"> Approved """ + str(prheader.Dept_Head_Approval_Date.strftime("%d/%m/%Y %H:%M:%S")) + """</td>
                                    <td style="text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="DIVH"> Approved """ + str(prheader.Div_Head_Approval_Date.strftime("%d/%m/%Y %H:%M:%S")) + """</td>
                                    <td style="text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="FIN"> Approved """ + str(prheader.Finance_Approval_Date.strftime("%d/%m/%Y %H:%M:%S")) + """</td>
                                    <td style="text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="DIR"> Approved """ + str(prheader.Direktur_Approval_Date.strftime("%d/%m/%Y %H:%M:%S")) + """</td>
                                    <td style="border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;"></td>
                                </tr>
                                <tr style="height:20px;">
                                    <td style="border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">"""+prheader.User_Name.title()+"""</td>
                                    <td style="text-align: center;vertical-align: bottom;">"""+approval.DeptHead.title()+"""</td>
                                    <td style="text-align: center;vertical-align: bottom;">"""+approval.DivHead.title()+"""</td>
                                    <td style="text-align: center;vertical-align: bottom;">"""+approval.Finance.title()+"""</td>
                                    <td style="text-align: center;vertical-align: bottom;">"""+approval.Direktur.title()+"""</td>
                                    <td style="border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">"""+approval.Purchase.title()+"""</td>
                                </tr>
                                <tr style="height:15px;">
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">User</td>
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Dept Head</td>
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Div Head</td>
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Fin&Acc</td>
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Pres Dir</td>
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Purchasing</td>
                                </tr>
                            </tbody>
                        </table>
                        """
        #SPV = models.EmailList.objects.get(Email = request.POST['SPV_Email'])
        email_body = """\
            <html>
            <head style="margin-bottom: 0px;">Dear Mr/Ms """ + approval.Purchase.title() + """,</head>
            <body>
            <p style="margin-bottom: 0px;margin-top: 0px;">This purchase request needs your approval </>
            
            <center><h3 style="margin: 0px;padding: 0px;">Purchase Request</h3></center>
            <hr >
             <table style= "font-size: x-small;">
                <tr>
                    <td style ="width: 140px;">Company</td>
                    <td>: """+prheader.Company+"""</td>
                </tr>
                <tr>
                    <td>Bussiness Area</td>
                    <td>: """+prheader.Bussiness_Area+"""</td>
                </tr>
                <tr>
                    <td>Date Created</td>
                    <td>: """+str(prheader.Date_Created)+"""</td>
                </tr>
                <tr>
                    <td>Jenis PP </td>
                    <td>: """+prheader.Jenis_PP+"""</td>
                </tr>
                <tr>
                    <td>PP Number</td>
                    <td>: """+prheader.PP_Number+"""</td>
                </tr>
                <tr>
                    <td>User</td>
                    <td>: """+prheader.User_Name+"""</td>
                </tr>
            </table>
       
            <table  style="border: 1px solid black; font-size: x-small;text-align: center;border-collapse: collapse;font-weight: normal;">
                    <thead style="border: 1px solid black;">
                        <tr style="border: 1px solid black; height: 50px; word-break: normal;">
                            <th rowspan="2" style="padding: 5px; border: 1px solid black;font-weight: normal;">No</th>
                            <th rowspan="2" style="padding: 5px;border: 1px solid black;font-weight: normal;">A* (Exp)</th>
                            <th rowspan="2" style="padding: 5px;border: 1px solid black;font-weight: normal;">I* (Jenis)</th>
                            <th rowspan="2" style="padding: 5px;border: 1px solid black;font-weight: normal;">Kode Barang</th>
                            <th rowspan="2" style="padding: 5px;border: 1px solid black;font-weight: normal;">Nama Barang / Deskripsi Service</th>
                            <th colspan="2" style="padding: 5px;border: 1px solid black;font-weight: normal;">Dipesan</th>
                            <th colspan="2" style="padding: 5px;border: 1px solid black;font-weight: normal;">Perkiraan Harga</th>
                            <th rowspan="2" style="padding: 5px;border: 1px solid black;font-weight: normal;">Tanggal Kedatangan</th>
                            <th colspan="2" style="padding: 5px;border: 1px solid black; word-break: keep-all;font-weight: normal;">Account Assignment</th>
                            <th rowspan="2" style="padding: 5px;border: 1px solid black;font-weight: normal; transform: rotate(-90deg); width: 1%; vertical-align: middle; ">Min Stock</th>
                            <th rowspan="2" style="padding: 5px;border: 1px solid black; font-weight: normal;transform: rotate(-90deg); width: 1%; vertical-align: middle; ">Act Stock</th>
                            <th rowspan="2" style="padding: 5px;border: 1px solid black; font-weight: normal;transform: rotate(-90deg); width: 1%; vertical-align: middle; ">Avg Usage</th>
                            <th rowspan="2" style="padding: 5px;border: 1px solid black; font-weight: normal;transform: rotate(-90deg); width: 1%; vertical-align: middle; ">Budget</th>
                            <th rowspan="2" style="padding: 5px;border: 1px solid black; font-weight: normal;transform: rotate(-90deg); width: 1%; vertical-align: middle; ">Un-Budget</th>
                            <th rowspan="2" style="padding: 5px;border: 1px solid black; width: 100px;font-weight: normal;">Catatan</th>
                        </tr>
                        <tr style="height:50px">
                            <th style="padding: 5px;border: 1px solid black;font-weight: normal;">Jumlah</th>
                            <th style="padding: 5px;border: 1px solid black;font-weight: normal;">UoM</th>
                            <th style="padding: 5px;border: 1px solid black;font-weight: normal;">Satuan</th>
                            <th style="padding: 5px;border: 1px solid black;font-weight: normal;">Total</th>
                            <th style="padding: 5px;border: 1px solid black;font-weight: normal;">Cost Center</th>
                            <th style="padding: 5px;border: 1px solid black;font-weight: normal;">Asset No./GL Account</th>
                        </tr>
                    </thead>
                    <tbody>
                    """+contain+"""
                    </tbody>
            </table>
            <br>

            <table>
            <tr>
            <td style="width:75%;">
            """+apptable+"""
            
            </td>
            
            <td style="vertical-align: top;border: 1px solid black;">
                               <table style="font-size: 12px;width:100%;">
                <tr>
                <td style ="width:40%;"></td>
                <td colspan="3" style="text-align: right;"> Khusus PP Asset(ZRAT)</td>
                </tr>
                <tr>
                <td>Budget No</td>
                <td>:</td>
                <td>"""+xdotstr(prheader.Budget_No)+"""<td>
                <td style ="width:10%;"></td>
                </tr>
                <tr>
                <td>Budget</td>
                <td>:</td>
                <td style="text-align: right;">"""+xdotstr(prheader.Budget_Rp)+"""<td>
                <td style ="width:10%;"></td>
                </tr>
                <tr>
                <td>PP diproses</td>
                <td>:</td>
                <td style="text-align: right;border-bottom: 1px solid black;">"""+xdotstr(prheader.PP_diProses)+"""<td>
                <td style ="width:10%;"></td>
                </tr>
                <tr>
                <td>Sisa</td>
                <td>:</td>
                <td style="text-align: right;">"""+xdotstr(prheader.Sisa_Budget)+"""<td>
                <td style ="width:10%;"></td>
                </tr>
                <tr>
                <td>PP diajukan</td>
                <td>:</td>
                <td style="text-align: right;border-bottom: 1px solid black;">"""+xdotstr(prheader.PP_diAjukan)+"""<td>
                <td style ="width:10%;"></td>
                </tr>
                <tr>
                <td>Sisa</td>
                <td>:</td>
                <td style="text-align: right;">"""+xdotstr(prheader.Sisa_Final)+"""<td>
                <td style ="width:10%;"></td>
                </tr>
                </table>
            </td>
            </tr>
            </table>
            <h6 style="margin:0px;font-size:12px;font-weight:normal;">(*) Kolom 'A' (Expense) ditandai 'F' untuk internal order, 'K' untuk cost center, 'P' untuk Project, dan 'A' untuk asset.</h6>
	        <h6 style="margin:0px;font-size:12px;font-weight:normal;">(*) Kolom 'I' (Jenis Barang) : K = Konsinyasi, L = Subcontracting, D = Service.</h6>																				
	        <h6 style="margin:0px;font-size:12px;font-weight:normal;">(*) "Catatan" dapat menunjukkan keterangan forecasting, tempat pengiriman spesifik, lokasi asset, dan lainnya.</h6>
            <br>
            <hr>
            <p> Please give your response by click approval button bellow and then click send button. A response at your earliest convenience would be much appreciated. </p>
            <table width="100%" cellspacing="0" cellpadding="0">
                <tr>
                    <td>
                        <table cellspacing="0" cellpadding="0">
                            <tr>
                                <td style="border-radius: 2px;width : 150px;text-align: center;" bgcolor="#4bf542">
                                    <a href="mailto:online.approval@aski.component.astra.co.id?subject=Approve:"""+prheader.PP_Number+"""&body=Approve Purchase Request with ID """+prheader.PP_Number+""" %0DApproval Message:" target="_blank" style="padding: 8px 12px; border: 1px solid #4bf542;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #ffffff;text-decoration: none;font-weight:bold;display: inline-block;">
                                        ACCEPT             
                                    </a>
                                </td>
                                <td>&nbsp;&nbsp;</td>
                                <td style="border-radius: 2px;width: 150px;text-align: center;" bgcolor="#cccccc">
                                    <a href="mailto:"""+prheader.User_Email+"""?subject=Ask User:"""+prheader.PP_Number+"""&body=Ask User about Purchase Request with ID """+prheader.PP_Number+""" %0DAsk User Message: " target="_blank" style="padding: 8px 12px; border: 1px solid #cccccc;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #000000;text-decoration: none;font-weight:bold;display: inline-block;">
                                        ASK USER             
                                    </a>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
            
            <br>
            <i>This email is automatically generated by Online Approval System PT Astra Komponen Indonesia<i>


            </body>
            </html>
            """

        models.Send.objects.filter(PP_Number=PP_Number).update(
            htmlmessagefin=email_body)

        mailattach = EmailMessage(
            'Purchase Request Online Approval: ' + PP_Number,
            body=email_body,
            from_email=settings.EMAIL_HOST_USER,
            to=[prheader.Purchase_Email],

        )
        mailattach.content_subtype = "html"
  
        if len(str(prheader.Attachment1))>1:
            mailattach.attach_file(
                'Media/'+str(prheader.Attachment1))
        if len(str(prheader.Attachment2))>1:
            mailattach.attach_file(
                'Media/'+str(prheader.Attachment2))
        if len(str(prheader.Attachment3))>1:
            mailattach.attach_file(
                'Media/'+str(prheader.Attachment3))

        mailattach.send()
       
        return addprnumber(request)

    context = {
        'Judul': 'Detail Purchase Request',
        'PP_Number': PP_Number,
        'PRheader': prheader,
        'itemlist': itemlist,
        'Approval': approval,
    }
    return render(request, 'purchaserequest/DetailNumber.html', context)


def xstr(s):
    if s is None:
        return ''
    return str(s)


def xdotstr(s):
    if s is None:
        return '................................'
    return str(s)


@login_required
@user_passes_test(is_memberaddasset)
def listbudget(request):
    print(request.POST)
    models.activity_log(user = request.user.username,PP_Number="",activity=request.POST).save()
    if 'add' in request.POST:
        form = forms.Budget(request.POST)
        if models.Budget.objects.filter(Budget_No=request.POST["Budget_No"]).exists():
            print("Duplicate")
        else:
            if form.is_valid():
                #form.pop('csrfmiddlewaretoken')
                form.save()
            else:
                print(form.errors)
    if 'edit' in request.POST:
        models.Budget.objects.filter(Budget_No=request.POST["Budget No Edit"]).update(
                Plant = request.POST['Plant Edit'],
                Description = request.POST['Description Edit'],
                Project = request.POST['Project Edit'],
                Year = request.POST['Year Edit'],
                Budget_Value = request.POST['Budget Value Edit'],
                Budget_Unit = request.POST['Budget Unit Edit'],
                Budget_User = request.POST['Budget User Edit'],
                Modified_At = str(datetime.datetime.now()),
                Current_Budget_Value = request.POST['Current Budget Value Edit'],
                Budget_Note = request.POST['Budget Note Edit'])

    if 'delete' in request.POST:
        models.Budget.objects.filter(
            Budget_No=request.POST["DeleteBudget"]).delete()
    budget = list(models.Budget.objects.all().order_by("Budget_No"))
    context = {
        'Judul': 'List Budget',
        'ListBudget': budget,
        'listJSON' : serializers.serialize("json", budget),
        'BudgetForm': forms.Budget(),
        'ListUser' : list(models.Approval.objects.distinct('User'))
    }
    return render(request, 'purchaserequest/ListBudget.html', context)


@login_required
@user_passes_test(is_memberaddasset)
def costcenter(request):
    print(request.POST)
    models.activity_log(user = request.user.username,PP_Number="",activity=request.POST).save()
    if 'add' in request.POST:
        form = forms.CostCenter(request.POST)

        if form.is_valid():
            form.save()
        else:
            print(form.errors)

    if 'delete' in request.POST:
        models.CostCenter.objects.filter(
            Cost_Center=request.POST["DeleteCostCenter"]).delete()
    context = {
        'Judul': 'Add New Cost Center',
        'ListCostCenter': list(models.CostCenter.objects.all()),
        'CostCenterForm': forms.CostCenter(),
    }
    return render(request, 'purchaserequest/CostCenter.html', context)



@login_required
def revise(request,ID):
    PP_Number = ID
    prheader = models.PRheader.objects.get(PP_Number=ID)
    itemselect = serializers.serialize("json", list(models.ItemList.objects.all()))
    if 'rev' not in PP_Number:
        New_PP_Number = PP_Number + "rev1"
    else :
        New_PP_Number = PP_Number.split('rev', 1)[0] + "rev" + str(int(PP_Number.split('rev', 1)[1])+1)


    if request.method == "GET":
        if not models.PRheader.objects.filter(PP_Number = New_PP_Number).exists():
            newheader = models.PRheader.objects.get(PP_Number=PP_Number)
            newheader.PP_Number = New_PP_Number
            newheader.pk = None
            newheader.Dept_Head_Approval_Date = None
            newheader.Dept_Head_Approval_Status = None
            newheader.Div_Head_Approval_Date = None
            newheader.Div_Head_Approval_Status = None
            newheader.Finance_Approval_Date = None
            newheader.Finance_Approval_Status = None
            newheader.Direktur_Approval_Date = None
            newheader.Direktur_Approval_Status = None
            newheader.PR_Status = None
            newheader.save()

            newitems = models.PRitem.objects.filter(PP_Number=PP_Number)
            for newitem in newitems:
                newitem.PP_Number = New_PP_Number
                newitem.pk = None
                newitem.save()
    newprheader = models.PRheader.objects.get(PP_Number=New_PP_Number)
    itemlist = list(models.PRitem.objects.filter(PP_Number=New_PP_Number).order_by('id'))
    approval = models.Approval.objects.get(
            User=request.user.username, Supervisor=prheader.User_Name)
    if prheader.Budget_No is not None :
        bud = models.Budget.objects.get(Budget_No = prheader.Budget_No)
        if approval.DivHead is None and 'PROJECT' in bud.Budget_User:
                approval.DivHead = 'HENDRO WITJAKSONO'
                approval.DivHead_email = 'hendro.witjaksono@aski.co.id'
    revision = models.HistoryApproval.objects.get(PP_Number=ID)
    if request.method == "POST":
        print(request.POST)
        models.activity_log(user = request.user.username,PP_Number=New_PP_Number,activity=request.POST).save()
        if 'Delete' in request.POST:
            print("Delete")
            models.PRitem.objects.filter(PP_Number = New_PP_Number, Nama_Barang = request.POST["Delete"]).delete()

        elif 'save' in request.POST:
            print("Save")
            models.PRitem.objects.filter(PP_Number = New_PP_Number, Nama_Barang = request.POST["Nama_BarangEdit"]).update(Jumlah_Order = request.POST["Jumlah_OrderEdit"],Harga_Satuan = request.POST["Harga_SatuanEdit"],Harga_Total = request.POST["Harga_TotalEdit"],Tgl_Kedatangan = request.POST["Tgl_KedatanganEdit"],Cost_Center = request.POST["Cost_CenterEdit"],Note = request.POST["NoteEdit"])
        elif 'add' in request.POST:
            pritem = forms.PRitem(request.POST)
            if pritem.is_valid() and models.PRitem.objects.filter(PP_Number=request.POST['PP_Number'], Nama_Barang=request.POST['Nama_Barang'], Note=request.POST['Note']).count() == 0:
                pritem.save()
        elif 'Budget' in request.POST:
            saveitem = forms.PRitem(request.POST)
            if saveitem.is_valid() and models.PRitem.objects.filter(PP_Number=request.POST['PP_Number'], Nama_Barang=request.POST['Nama_Barang'], Note=request.POST['Note']).count() == 0:
                saveitem.save()
            else:
                print(saveitem.errors)
        elif 'upload' in request.POST:
            print("attachment")
            
            headersave = forms.PRheader(
                request.POST, request.FILES, instance=newprheader)
            if headersave.is_valid():
                headersave.save()
            else:
                print(headersave.errors)
        elif 'Finish' in request.POST:
            print("Finish")
            
            headersave = forms.PRheader(
                request.POST, request.FILES, instance=newprheader)
            if headersave.is_valid():
                headersave.Submit = datetime.datetime.now()
                newprheader.Submit = datetime.datetime.now()
                headersave.save()
            else:
                print(headersave.errors)
            counter = 0
            contain = ''
            for item in itemlist:
                counter += 1
                contain += '''<tr style="height: 30px; font-size:12px;">
                        <td style="border: 1px solid black;">'''+str(counter)+'''</td>
                        <td style="border: 1px solid black;">'''+xstr(item.Expense)+'''</td>
                        <td style="border: 1px solid black;">'''+xstr(item.Jenis_Barang)+'''</td>
                        <td style="border: 1px solid black;">'''+xstr(item.Kode_Barang)+'''</td>
                        <td style="border: 1px solid black; text-align: left;padding-left: 5px;width:15%;">'''+item.Nama_Barang+" "+xstr(item.Detail_Spec)+'''</td>
                        <td style="border: 1px solid black;">'''+str(item.Jumlah_Order)+'''</td>
                        <td style="border: 1px solid black;">'''+str(item.Unit_Order)+'''</td>
                        <td style="border: 1px solid black;">'''+xstr(item.Harga_Satuan)+" "+xstr(item.Currency)+'''</td>
                        <td style="border: 1px solid black;">'''+xstr(item.Harga_Total)+" "+xstr(item.Currency)+'''</td>
                        <td style="border: 1px solid black;">'''+xstr(item.Tgl_Kedatangan)+'''</td>
                        <td style="border: 1px solid black;">'''+xstr(item.Cost_Center)+'''</td>
                        <td style="border: 1px solid black;">'''+xstr(item.Asset_No_GL_Account)+'''</td>
                        <td style="border: 1px solid black;">'''+xstr(item.Minimal_Stock)+'''</td>
                        <td style="border: 1px solid black;">'''+xstr(item.Actual_Stock)+'''</td>
                        <td style="border: 1px solid black;">'''+xstr(item.Average_Usage)+'''</td>
                        <td style="border: 1px solid black;"></td>
                        <td style="border: 1px solid black;"></td>
                        <td style="border: 1px solid black;">'''+xstr(item.Note)+'''</td>
                    </tr>'''

            if approval.DivHead is None:
                apptable = """
                            <table style="border: 1px solid black; font-size: 12px;text-align: center;border-collapse: collapse;" >
                                <tbody >
                                    <tr style="height:20px;">
                                        <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: center;">Pemesan</td>
                                        <td colspan="3" style="border: 1px solid black;width: 230px;text-align: center;vertical-align: center;">Disetujui/Mengetahui</td>
                                        <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: center;">Purchasing</td>
                                    </tr>
                                    <tr style="height:65px;">
                                        <td style="padding:10px;border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: center;font-style: italic;color: green;">Created """+str(newprheader.Submit.strftime("%d/%m/%Y %H:%M:%S"))+"""</td>
                                        <td style="padding:10px;text-align: center;vertical-align: center;font-style: italic;color: green;" id="DEPH"></td>
                                        <td style="padding:10px;text-align: center;vertical-align: center;font-style: italic;color: green;" id="FIN"></td>
                                        <td style="padding:10px;text-align: center;vertical-align: center;font-style: italic;color: green;" id="DIR"></td>
                                        <td style="padding:10px;border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: center;font-style: italic;color: green;"></td>
                                    </tr>
                                    <tr style="height:15px;">
                                        <td style="border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">"""+newprheader.User_Name.title()+"""</td>
                                        <td style="text-align: center;vertical-align: bottom;">"""+approval.DeptHead.title()+"""</td>
                                        <td style="text-align: center;vertical-align: bottom;">"""+approval.Finance.title()+"""</td>
                                        <td style="text-align: center;vertical-align: bottom;">"""+approval.Direktur.title()+"""</td>
                                        <td style="border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">"""+approval.Purchase.title()+"""</td>
                                    </tr>
                                    <tr style="height:20px;">
                                        <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: center;">User</td>
                                        <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: center;">Dept Head</td>
                                        <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: center;">Fin&Acc</td>
                                        <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: center;">Direktur</td>
                                        <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: center;">Purchasing</td>
                                    </tr>
                                </tbody>
                            </table>
                            """
            elif approval.DeptHead is None:
                apptable = """
                        <table style="border: 1px solid black; font-size: 12px;text-align: center;border-collapse: collapse;" >
                            <tbody >
                                <tr style="height:20px;">
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: center;">Pemesan</td>
                                    <td colspan="3" style="border: 1px solid black;width: 230px;text-align: center;vertical-align: center;">Disetujui/Mengetahui</td>
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: center;">Purchasing</td>
                                </tr>
                                <tr style="height:65px;">
                                    <td style="padding:10px;border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: center;font-style: italic;color: green;">Created """+str(prheader.Submit.strftime("%d/%m/%Y %H:%M:%S"))+"""</td>
                                    <td style="padding:10px;text-align: center;vertical-align: center;font-style: italic;color: green;" id="DIVH"></td>
                                    <td style="padding:10px;text-align: center;vertical-align: center;font-style: italic;color: green;" id="FIN"></td>
                                    <td style="padding:10px;text-align: center;vertical-align: center;font-style: italic;color: green;" id="DIR"></td>
                                    <td style="padding:10px;border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: center;font-style: italic;color: green;"></td>
                                </tr>
                                <tr style="height:15px;">
                                    <td style="border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">"""+prheader.User_Name.title()+"""</td>
                                    <td style="text-align: center;vertical-align: bottom;">"""+approval.DivHead.title()+"""</td>
                                    <td style="text-align: center;vertical-align: bottom;">"""+approval.Finance.title()+"""</td>
                                    <td style="text-align: center;vertical-align: bottom;">"""+approval.Direktur.title()+"""</td>
                                    <td style="border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">"""+approval.Purchase.title()+"""</td>
                                </tr>
                                <tr style="height:20px;">
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: center;">User</td>
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: center;">Div Head</td>
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: center;">Fin&Acc</td>
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: center;">Pres Dir</td>
                                    <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: center;">Purchasing</td>
                                </tr>
                            </tbody>
                        </table>
                        """
            else:
                apptable = """
                            <table style="border: 1px solid black; font-size: 12px;text-align: center;border-collapse: collapse;" >
                                <tbody >
                                    <tr style="height:20px;">
                                        <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: center;">Pemesan</td>
                                        <td colspan="4" style="border: 1px solid black;width: 230px;text-align: center;vertical-align: center;">Disetujui/Mengetahui</td>
                                        <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: center;">Purchasing</td>
                                    </tr>
                                    <tr style="height:65px;">
                                        <td style="padding:10px;border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: center;font-style: italic;color: green;">Created """+str(prheader.Submit.strftime("%d/%m/%Y %H:%M:%S"))+"""</td>
                                        <td style="padding:10px;text-align: center;vertical-align: center;font-style: italic;color: green;" id="DEPH"></td>
                                        <td style="padding:10px;text-align: center;vertical-align: center;font-style: italic;color: green;" id="DIVH"></td>
                                        <td style="padding:10px;text-align: center;vertical-align: center;font-style: italic;color: green;" id="FIN"></td>
                                        <td style="padding:10px;text-align: center;vertical-align: center;font-style: italic;color: green;" id="DIR"></td>
                                        <td style="padding:10px;border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: center;font-style: italic;color: green;"></td>
                                    </tr>
                                    <tr style="height:15px;">
                                        <td style="border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">"""+newprheader.User_Name.title()+"""</td>
                                        <td style="text-align: center;vertical-align: bottom;">"""+approval.DeptHead.title()+"""</td>
                                        <td style="text-align: center;vertical-align: bottom;">"""+approval.DivHead.title()+"""</td>
                                        <td style="text-align: center;vertical-align: bottom;">"""+approval.Finance.title()+"""</td>
                                        <td style="text-align: center;vertical-align: bottom;">"""+approval.Direktur.title()+"""</td>
                                        <td style="border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">"""+approval.Purchase.title()+"""</td>
                                    </tr>
                                    <tr style="height:20px;">
                                        <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: center;">User</td>
                                        <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: center;">Dept Head</td>
                                        <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: center;">Div Head</td>
                                        <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: center;">Fin&Acc</td>
                                        <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: center;">Direktur</td>
                                        <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: center;">Purchasing</td>
                                    </tr>
                                </tbody>
                            </table>
                            """
            #SPV = models.EmailList.objects.get(Email = request.POST['SPV_Email'])
            email_body = """\
                <html>
                <head style="margin-bottom: 0px;">Dear Mr/Ms """ + approval.DeptHead.title() + """,</head>
                <body>
                <p style="margin-bottom: 0px;margin-top: 0px;">This purchase request needs your approval </>
                
                <center><h3 style="margin: 0px;padding: 0px;">Purchase Request</h3></center>
                <hr >
                <table style= "font-size: x-small;">
                    <tr>
                        <td style ="width: 140px;">Company</td>
                        <td>: """+newprheader.Company+"""</td>
                    </tr>
                    <tr>
                        <td>Bussiness Area</td>
                        <td>: """+newprheader.Bussiness_Area+"""</td>
                    </tr>
                    <tr>
                        <td>Date Created</td>
                        <td>: """+str(newprheader.Date_Created)+"""</td>
                    </tr>
                    <tr>
                        <td>Jenis PP </td>
                        <td>: """+newprheader.Jenis_PP+"""</td>
                    </tr>
                    <tr>
                        <td>PP Number</td>
                        <td>: """+newprheader.PP_Number+"""</td>
                    </tr>
                    <tr>
                        <td>User</td>
                        <td>: """+newprheader.User_Name+"""</td>
                    </tr>
                </table>
        
                <table  style="border: 1px solid black; font-size: 14px;text-align: center;border-collapse: collapse;font-weight: normal;">
                        <thead style="border: 1px solid black;">
                            <tr style="border: 1px solid black; height: 50px; word-break: normal;">
                                <th rowspan="2" style="padding: 5px; border: 1px solid black;font-weight: normal;">No</th>
                                <th rowspan="2" style="padding: 5px;border: 1px solid black;font-weight: normal;">A* (Exp)</th>
                                <th rowspan="2" style="padding: 5px;border: 1px solid black;font-weight: normal;">I* (Jenis)</th>
                                <th rowspan="2" style="padding: 5px;border: 1px solid black;font-weight: normal;">Kode Barang</th>
                                <th rowspan="2" style="padding: 5px;border: 1px solid black;font-weight: normal;">Nama Barang / Deskripsi Service</th>
                                <th colspan="2" style="padding: 5px;border: 1px solid black;font-weight: normal;">Dipesan</th>
                                <th colspan="2" style="padding: 5px;border: 1px solid black;font-weight: normal;">Perkiraan Harga</th>
                                <th rowspan="2" style="padding: 5px;border: 1px solid black;font-weight: normal;">Tanggal Kedatangan</th>
                                <th colspan="2" style="padding: 5px;border: 1px solid black; word-break: keep-all;font-weight: normal;">Account Assignment</th>
                                <th rowspan="2" style="padding: 5px;border: 1px solid black;font-weight: normal; transform: rotate(-90deg); width: 1%; vertical-align: middle; ">Min Stock</th>
                                <th rowspan="2" style="padding: 5px;border: 1px solid black; font-weight: normal;transform: rotate(-90deg); width: 1%; vertical-align: middle; ">Act Stock</th>
                                <th rowspan="2" style="padding: 5px;border: 1px solid black; font-weight: normal;transform: rotate(-90deg); width: 1%; vertical-align: middle; ">Avg Usage</th>
                                <th rowspan="2" style="padding: 5px;border: 1px solid black; font-weight: normal;transform: rotate(-90deg); width: 1%; vertical-align: middle; ">Budget</th>
                                <th rowspan="2" style="padding: 5px;border: 1px solid black; font-weight: normal;transform: rotate(-90deg); width: 1%; vertical-align: middle; ">Un-Budget</th>
                                <th rowspan="2" style="padding: 5px;border: 1px solid black; width: 100px;font-weight: normal;">Catatan</th>
                            </tr>
                            <tr style="height:50px">
                                <th style="padding: 5px;border: 1px solid black;font-weight: normal;">Jumlah</th>
                                <th style="padding: 5px;border: 1px solid black;font-weight: normal;">UoM</th>
                                <th style="padding: 5px;border: 1px solid black;font-weight: normal;">Satuan</th>
                                <th style="padding: 5px;border: 1px solid black;font-weight: normal;">Total</th>
                                <th style="padding: 5px;border: 1px solid black;font-weight: normal;">Cost Center</th>
                                <th style="padding: 5px;border: 1px solid black;font-weight: normal;">Asset No./GL Account</th>
                            </tr>
                        </thead>
                        <tbody>
                        """+contain+"""
                        </tbody>
                </table>
                <br>
                <table>
                <tr>
                <td style="width:75%;">
                """+apptable+"""
                
                </td>
                
                <td style="vertical-align: top;border: 1px solid black;">
                    <table style="font-size: 12px;width:100%;">
                    <tr>
                    <td style ="width:40%;"></td>
                    <td colspan="3" style="text-align: right;"> Khusus PP Asset(ZRAT)</td>
                    </tr>
                    <tr>
                    <td>Budget No</td>
                    <td>:</td>
                    <td>"""+xdotstr(newprheader.Budget_No)+"""<td>
                    <td style ="width:10%;"></td>
                    </tr>
                    <tr>
                    <td>Budget</td>
                    <td>:</td>
                    <td style="text-align: right;">"""+xdotstr(newprheader.Budget_Rp)+"""<td>
                    <td style ="width:10%;"></td>
                    </tr>
                    <tr>
                    <td>PP diproses</td>
                    <td>:</td>
                    <td style="text-align: right;border-bottom: 1px solid black;">"""+xdotstr(newprheader.PP_diProses)+"""<td>
                    <td style ="width:10%;"></td>
                    </tr>
                    <tr>
                    <td>Sisa</td>
                    <td>:</td>
                    <td style="text-align: right;">"""+xdotstr(newprheader.Sisa_Budget)+"""<td>
                    <td style ="width:10%;"></td>
                    </tr>
                    <tr>
                    <td>PP diajukan</td>
                    <td>:</td>
                    <td style="text-align: right;border-bottom: 1px solid black;">"""+xdotstr(newprheader.PP_diAjukan)+"""<td>
                    <td style ="width:10%;"></td>
                    </tr>
                    <tr>
                    <td>Sisa</td>
                    <td>:</td>
                    <td style="text-align: right;">"""+xdotstr(newprheader.Sisa_Final)+"""<td>
                    <td style ="width:10%;"></td>
                    </tr>
                    </table>
                </td>
                </tr>
                </table>
                <h6 style="margin:0px;font-size:12px;font-weight:normal;">(*) Kolom 'A' (Expense) ditandai 'F' untuk internal order, 'K' untuk cost center, 'P' untuk Project, dan 'A' untuk asset.</h6>
                <h6 style="margin:0px;font-size:12px;font-weight:normal;">(*) Kolom 'I' (Jenis Barang) : K = Konsinyasi, L = Subcontracting, D = Service.</h6>																				
                <h6 style="margin:0px;font-size:12px;font-weight:normal;">(*) "Catatan" dapat menunjukkan keterangan forecasting, tempat pengiriman spesifik, lokasi asset, dan lainnya.</h6>
                <br>
                <hr>
                 <h6 style="margin:0px;font-size:12px;font-weight:normal;">Revision Note by """+revision.Approval_By+""" : """+ revision.Comment.replace("Need Revise Purchase Request with ID "+PP_Number,"").replace("Revision Message: ","")+"""</h6>
                <hr>
                <p> Please give your response by click approval button bellow and then click send button. A response at your earliest convenience would be much appreciated. </p>
                <table width="100%" cellspacing="0" cellpadding="0">
                    <tr>
                        <td>
                            <table cellspacing="0" cellpadding="0">
                                <tr>
                                    <td style="border-radius: 2px;width : 150px;text-align: center;" bgcolor="#4bf542">
                                        <a href="mailto:online.approval@aski.component.astra.co.id?subject=Approve:"""+newprheader.PP_Number+"""&body=Approve Purchase Request with ID """+newprheader.PP_Number+""" " target="_blank" style="padding: 8px 12px; border: 1px solid #4bf542;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #ffffff;text-decoration: none;font-weight:bold;display: inline-block;">
                                            APPROVE             
                                        </a>
                                    </td>
                                    <td>&nbsp;&nbsp;</td>
                                    <td style="border-radius: 2px;width: 150px;text-align: center;" bgcolor="#ED2939">
                                        <a href="mailto:online.approval@aski.component.astra.co.id?subject=Reject:"""+newprheader.PP_Number+"""&body=Reject  Purchase Request with ID """+newprheader.PP_Number+""" %0DReject Message:" target="_blank" style="padding: 8px 12px; border: 1px solid #ED2939;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #ffffff;text-decoration: none;font-weight:bold;display: inline-block;">
                                            REJECT             
                                        </a>
                                    </td>
                                    <td>&nbsp;&nbsp;</td>
                                    <td style="border-radius: 2px;width: 150px;text-align: center;" bgcolor="#ebde34">
                                        <a href="mailto:online.approval@aski.component.astra.co.id?subject=Revise:"""+newprheader.PP_Number+"""&body=Need Revise Purchase Request with ID """+newprheader.PP_Number+""" %0DRevision Message:" target="_blank" style="padding: 8px 12px; border: 1px solid #ebde34;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #000000;text-decoration: none;font-weight:bold;display: inline-block;">
                                            REVISE             
                                        </a>
                                    </td>
                                    <td>&nbsp;&nbsp;</td>
                                    <td style="border-radius: 2px;width: 150px;text-align: center;" bgcolor="#cccccc">
                                        <a href="mailto:"""+newprheader.User_Email+"""?subject=Ask User:"""+newprheader.PP_Number+"""&body=Ask User about Purchase Request with ID """+newprheader.PP_Number+""" %0DAsk User Message: " target="_blank" style="padding: 8px 12px; border: 1px solid #cccccc;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #000000;text-decoration: none;font-weight:bold;display: inline-block;">
                                            ASK USER             
                                        </a>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
                
                <br>
                <i>This email is automatically generated by Online Approval System PT Astra Komponen Indonesia<i>


                </body>
                </html>
                """

            mailattach = EmailMessage(
                'Purchase Request Online Approval: ' + request.POST['PP_Number'],
                body=email_body,
                from_email=settings.EMAIL_HOST_USER,
                to=[request.POST['Dept_Head_Email']],

            )
            mailattach.content_subtype = "html"

            if len(str(prheader.Attachment1))>1:
                mailattach.attach_file(
                    'Media/'+str(prheader.Attachment1))
            if len(str(prheader.Attachment2))>1:
                mailattach.attach_file(
                    'Media/'+str(prheader.Attachment2))
            if len(str(prheader.Attachment3))>1:
                mailattach.attach_file(
                    'Media/'+str(prheader.Attachment3))

            mailattach.send()

            email = models.Send(htmlmessage=email_body,
                                mailfrom='online.approval@aski.component.astra.co.id',
                                mailto=request.POST['Dept_Head_Email'],
                                PP_Number=request.POST['PP_Number'],
                                mailheader='Purchase Request Online Approval: ' + request.POST['PP_Number'])
            email.save()
            models.PRheader.objects.filter(
                PP_Number=request.POST['PP_Number']).update(PR_Status="Created")

            models.PRheader.objects.filter(PP_Number=PP_Number).update(PR_Status="Revised")
            return listPP(request)

            
    
    context = {
        'Judul': 'Revise Purchase Request',
        'PP_Number': PP_Number,
        'New_PP_Number': New_PP_Number,
        'PRheader': newprheader,
        'PRheaderform': forms.PRheader(instance=newprheader),
        'formPRitem' : forms.PRitem(),
        'ItemSelect': itemselect,
        'itemlist': list(models.PRitem.objects.filter(PP_Number=New_PP_Number).order_by('id')),
        'Approval': approval,
        'revision': revision,
        'CostCenter' : list(models.CostCenter.objects.all()),
    }
    return render(request, 'purchaserequest/RevisePR.html', context)

@login_required
@user_passes_test(is_memberadditem)
def newitem(request):
    print(request.POST)
    if 'add' in request.POST:
        form = forms.ItemList(request.POST)
        if form.is_valid():
            form.save()
        else:
            print(form.errors)
        models.activity_log(user = request.user.username,PP_Number="",activity=request.POST).save()

    if 'delete' in request.POST:
        models.ItemList.objects.filter(
            Nama_Barang=request.POST["DeleteItem"]).delete()
        models.activity_log(user = request.user.username,PP_Number="",activity=request.POST).save()
    context = {
        'Judul': 'Add Purchase Request Item',
        'itemlist': list(models.ItemList.objects.all()),
        'formitem': forms.ItemList()
    }
    return render(request, 'purchaserequest/newitem.html', context)


def exportbudget(request):
    resource = resources.Budget()
    dataset = resource.export()
    response = HttpResponse(dataset.xls, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="budget.xls"'
    models.activity_log(user = request.user.username,PP_Number="",activity="export budget").save()
    return response

def exportcostcenter(request):
    resource = resources.CostCenter()
    dataset = resource.export()
    response = HttpResponse(dataset.xls, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="costcenter.xls"'
    models.activity_log(user = request.user.username,PP_Number="",activity="export cost center").save()
    return response

def exportitem(request):
    resource = resources.ItemList()
    dataset = resource.export()
    response = HttpResponse(dataset.xls, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="itemlist.xls"'
    models.activity_log(user = request.user.username,PP_Number="",activity="export item list").save()
    return response

def exportbudgetusage(request):
    resource = resources.PRheader()
    dataset = resource.export(models.PRheader.objects.all().exclude(Budget_No = None).exclude(PR_Status = None))
    response = HttpResponse(dataset.xls, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="budgetusage.xls"'
    models.activity_log(user = request.user.username,PP_Number="",activity="export budget usage").save()
    return response

def exportfinishedPR(request):
    PRlist= list(models.PRheader.objects.filter(PR_Status = "Finished").only("PP_Number"))
    print(PRlist)
    resource = resources.PRitem()
    dataset = resource.export(models.PRitem.objects.filter(PP_Number__in=PRlist))
    response = HttpResponse(dataset.xls, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="listPRitem.xls"'
    models.activity_log(user = request.user.username,PP_Number="",activity="export PR item list").save()
    return response

def exportlistfinishedPR(request):
    resource = resources.PRheader()
    dataset = resource.export(models.PRheader.objects.filter(PR_Status = "Finished"))
    response = HttpResponse(dataset.xls, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="listPRheader.xls"'
    models.activity_log(user = request.user.username,PP_Number="",activity="export PR item list").save()
    return response

@login_required
@user_passes_test(is_admin)
def email(request):

    if request.method == "POST":
        print(request.POST)
        mailattach = EmailMessage(
                request.POST['header'],
                body=request.POST['messagebody'],
                from_email=settings.EMAIL_HOST_USER,
                to=[request.POST['emailto']],

            )
        mailattach.content_subtype = "html"

        if len(str(request.POST['attach1']))>1:
                mailattach.attach_file(
                    'Media/'+str(request.POST['attach1']))
        if len(str(request.POST['attach2']))>1:
                mailattach.attach_file(
                    'Media/'+str(request.POST['attach2']))
        if len(str(request.POST['attach3']))>1:
                mailattach.attach_file(
                    'Media/'+str(request.POST['attach3']))
        mailattach.send()

    context = {
        'Judul': 'Email',

    }
    return render(request, 'purchaserequest/Email.html', context)

def Generate(PP_Number):
    print(PP_Number)
    prheader = models.PRheader.objects.get(PP_Number=PP_Number)
    itemlist = list(models.PRitem.objects.filter(PP_Number=PP_Number).order_by('id'))
    approval = models.Approval.objects.get(Supervisor_email=prheader.SPV_Email, User = PP_Number.replace("ASKIPP","").split("rev", 1)[0][:-5])
    if prheader.Budget_No is not None :
            bud = models.Budget.objects.get(Budget_No = prheader.Budget_No)
            if approval.DivHead is None and 'PROJECT' in bud.Budget_User:
                approval.DivHead = 'HENDRO WITJAKSONO'
                approval.DivHead_email = 'hendro.witjaksono@aski.co.id'

    watermark = ""
    for x in range(100):
        watermark += PP_Number+" "+prheader.PR_Number+" "
    counter = 0
    contain = ''
    for item in itemlist:
        counter += 1
        contain += '''<tr style="height: 30px; font-size:12px;">
                <td style="border: 1px solid black;">'''+str(counter)+'''</td>
                <td style="border: 1px solid black;">'''+xstr(item.Expense)+'''</td>
                <td style="border: 1px solid black;">'''+xstr(item.Jenis_Barang)+'''</td>
                <td style="border: 1px solid black;">'''+xstr(item.Kode_Barang)+'''</td>
                <td style="border: 1px solid black; text-align: left;padding-left: 5px;width:15%;">'''+item.Nama_Barang+" "+xstr(item.Detail_Spec)+'''</td>
                <td style="border: 1px solid black;">'''+str(item.Jumlah_Order)+'''</td>
                <td style="border: 1px solid black;">'''+str(item.Unit_Order)+'''</td>
                <td style="border: 1px solid black;">'''+xstr(item.Harga_Satuan)+" "+xstr(item.Currency)+'''</td>
                <td style="border: 1px solid black;">'''+xstr(item.Harga_Total)+" "+xstr(item.Currency)+'''</td>
                <td style="border: 1px solid black;">'''+xstr(item.Tgl_Kedatangan)+'''</td>
                <td style="border: 1px solid black;">'''+xstr(item.Cost_Center)+'''</td>
                <td style="border: 1px solid black;">'''+xstr(item.Asset_No_GL_Account)+'''</td>
                <td style="border: 1px solid black;">'''+xstr(item.Minimal_Stock)+'''</td>
                <td style="border: 1px solid black;">'''+xstr(item.Actual_Stock)+'''</td>
                <td style="border: 1px solid black;">'''+xstr(item.Average_Usage)+'''</td>
                <td style="border: 1px solid black;"></td>
                <td style="border: 1px solid black;"></td>
                <td style="border: 1px solid black;">'''+xstr(item.Note)+'''</td>
            </tr>'''

    if approval.DivHead is None:
        apptable = """
                    <table style="border: 1px solid black; font-size: 12px;text-align: center;border-collapse: collapse;" >
                        <tbody >
                            <tr style="height:10px;">
                                <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Pemesan</td>
                                <td colspan="3" style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Disetujui/Mengetahui</td>
                                <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Purchasing</td>
                            </tr>
                            <tr style="height:40px;">
                                <td style="padding:20px;border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;">Created """+str(prheader.Submit.strftime("%d/%m/%Y %H:%M:%S"))+"""</td>
                                <td style="padding:20px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="DEPH">Approved """ + str(prheader.Dept_Head_Approval_Date.strftime("%d/%m/%Y %H:%M:%S")) + """</td>
                                <td style="padding:20px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="FIN">Approved """ + str(prheader.Finance_Approval_Date.strftime("%d/%m/%Y %H:%M:%S")) + """</td>
                                <td style="padding:20px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="DIR">Approved """ + str(prheader.Direktur_Approval_Date.strftime("%d/%m/%Y %H:%M:%S")) + """</td>
                                <td style="padding:20px;border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;">Approved """ + str(prheader.Purchase_Approval_Date.strftime("%d/%m/%Y %H:%M:%S")) + """</td>
                            </tr>
                            <tr style="height:20px;">
                                <td style="border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">"""+prheader.User_Name.title()+"""</td>
                                <td style="text-align: center;vertical-align: bottom;">"""+approval.DeptHead.title()+"""</td>
                                <td style="text-align: center;vertical-align: bottom;">"""+approval.Finance.title()+"""</td>
                                <td style="text-align: center;vertical-align: bottom;">"""+approval.Direktur.title()+"""</td>
                                <td style="border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">"""+approval.Purchase.title()+"""</td>
                            </tr>
                            <tr style="height:10px;">
                                <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">User</td>
                                <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Dept Head</td>
                                <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Fin&Acc</td>
                                <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Pres Dir</td>
                                <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Purchasing</td>
                            </tr>
                        </tbody>
                    </table>
                    """
    elif approval.DeptHead is None:
        apptable = """
                    <table style="border: 1px solid black; font-size: 12px;text-align: center;border-collapse: collapse;" >
                        <tbody >
                            <tr style="height:10px;">
                                <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Pemesan</td>
                                <td colspan="3" style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Disetujui/Mengetahui</td>
                                <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Purchasing</td>
                            </tr>
                            <tr style="height:40px;">
                                <td style="padding:20px;border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;">Created """+str(prheader.Submit.strftime("%d/%m/%Y %H:%M:%S"))+"""</td>
                                <td style="padding:20px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="DIVH">Approved """ + str(prheader.Div_Head_Approval_Date.strftime("%d/%m/%Y %H:%M:%S")) + """</td>
                                <td style="padding:20px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="FIN">Approved """ + str(prheader.Finance_Approval_Date.strftime("%d/%m/%Y %H:%M:%S")) + """</td>
                                <td style="padding:20px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="DIR">Approved """ + str(prheader.Direktur_Approval_Date.strftime("%d/%m/%Y %H:%M:%S")) + """</td>
                                <td style="padding:20px;border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;">Approved """ + str(prheader.Purchase_Approval_Date.strftime("%d/%m/%Y %H:%M:%S")) + """</td>
                            </tr>
                            <tr style="height:20px;">
                                <td style="border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">"""+prheader.User_Name.title()+"""</td>
                                <td style="text-align: center;vertical-align: bottom;">"""+approval.DivHead.title()+"""</td>
                                <td style="text-align: center;vertical-align: bottom;">"""+approval.Finance.title()+"""</td>
                                <td style="text-align: center;vertical-align: bottom;">"""+approval.Direktur.title()+"""</td>
                                <td style="border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">"""+approval.Purchase.title()+"""</td>
                            </tr>
                            <tr style="height:10px;">
                                <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">User</td>
                                <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Div Head</td>
                                <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Fin&Acc</td>
                                <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Pres Dir</td>
                                <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Purchasing</td>
                            </tr>
                        </tbody>
                    </table>
                    """
    else:
        apptable = """
                    <table style="border: 1px solid black; font-size: 12px;text-align: center;border-collapse: collapse;" >
                        <tbody >
                            <tr style="height:10px;">
                                <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Pemesan</td>
                                <td colspan="4" style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Disetujui/Mengetahui</td>
                                <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Purchasing</td>
                            </tr>
                            <tr style="height:40px;">
                                <td style="padding:20px;border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;">Created """+str(prheader.Submit.strftime("%d/%m/%Y %H:%M:%S"))+"""</td>
                                <td style="padding:20px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="DEPH">Approved """ + str(prheader.Dept_Head_Approval_Date.strftime("%d/%m/%Y %H:%M:%S")) + """</td>
                                <td style="padding:20px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="DIVH">Approved """ + str(prheader.Div_Head_Approval_Date.strftime("%d/%m/%Y %H:%M:%S")) + """</td>
                                <td style="padding:20px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="FIN">Approved """ + str(prheader.Finance_Approval_Date.strftime("%d/%m/%Y %H:%M:%S")) + """</td>
                                <td style="padding:20px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="DIR">Approved """ + str(prheader.Direktur_Approval_Date.strftime("%d/%m/%Y %H:%M:%S")) + """</td>
                                <td style="padding:20px;border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;">Approved """ + str(prheader.Purchase_Approval_Date.strftime("%d/%m/%Y %H:%M:%S")) + """</td>
                            </tr>
                            <tr style="height:20px;">
                                <td style="border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">"""+prheader.User_Name.title()+"""</td>
                                <td style="text-align: center;vertical-align: bottom;">"""+approval.DeptHead.title()+"""</td>
                                <td style="text-align: center;vertical-align: bottom;">"""+approval.DivHead.title()+"""</td>
                                <td style="text-align: center;vertical-align: bottom;">"""+approval.Finance.title()+"""</td>
                                <td style="text-align: center;vertical-align: bottom;">"""+approval.Direktur.title()+"""</td>
                                <td style="border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">"""+approval.Purchase.title()+"""</td>
                            </tr>
                            <tr style="height:10px;">
                                <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">User</td>
                                <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Dept Head</td>
                                <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Div Head</td>
                                <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Fin&Acc</td>
                                <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Pres Dir</td>
                                <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Purchasing</td>
                            </tr>
                        </tbody>
                    </table>
                    """
    email_body = """\
        <html>
        <head>
            <meta name="pdfkit-page-size" content="A4"/>
            <meta name="pdfkit-orientation" content="Landscape"/>
        </head>
    
        <body style="font-family:'Palatino Linotype'">
        <div id="watermark" style="min-height: 80vh;">
        <table style= "font-size: small;">
            <tr>
                <td style ="width: 140px;"><b>Company</b></td>
                <td>: """+prheader.Company+"""</td>
                <td style ="width: 400px;"></td>
                <td><b>Bussiness Area</b></td>
                <td>: """+prheader.Bussiness_Area+"""</td>
                <td style ="width: 50px;"></td>
                <td>No Doc</td>
                <td>: FR-FACT.01-003</td>
            </tr>
            <tr>
                <td>Date Created</td>
                <td>: """+str(prheader.Date_Created)+"""</td>
                <td style ="width: 400px;"></td>
                <td></td>
                <td></td>
                <td></td>
                <td>Revision</td>
                <td>: 0</td>
            </tr>
            <tr>
                <td></td>
                <td></td>
                <td style ="width: 400px;"></td>
                <td></td>
                <td></td>
                <td></td>
                <td>Effective Start</td>
                <td>: 15 June 2020</td>
            </tr>
        </table>
        <center><h3 style="margin: 0px;padding: 0px;">Permintaan Pembelian</h3></center>
        <hr >
            <table style= "font-size: small;">
            <tr>
                <td style ="width: 140px;">Jenis PP </td>
                <td>: """+prheader.Jenis_PP+"""</td>
            </tr>
            <tr>
                <td>PP Number</td>
                <td>: """+prheader.PP_Number+"""</td>
            </tr>
            <tr>
                <td>Pemesan</td>
                <td>: """+prheader.User_Name+"""</td>
            </tr>
            <tr>
                <td>PR Number</td>
                <td>: """+prheader.PR_Number+"""</td>
                <td style ="width: 600px;"></td>
                <td>PR Date</td>
                <td>: """+str(prheader.PR_Date.strftime("%Y-%m-%d"))+"""</td>
            </tr>
        </table>
        <br>
        <table  style="border: 1px solid black; font-size: small;text-align: center;border-collapse: collapse;font-weight: normal;">
                <thead style="border: 1px solid black;">
                    <tr style="border: 1px solid black; height: 50px; word-break: normal;">
                        <th rowspan="2" style="padding: 5px; border: 1px solid black;font-weight: normal;">No</th>
                        <th rowspan="2" style="padding: 5px;border: 1px solid black;font-weight: normal;">A* (Exp)</th>
                        <th rowspan="2" style="padding: 5px;border: 1px solid black;font-weight: normal;">I* (Jenis)</th>
                        <th rowspan="2" style="padding: 5px;border: 1px solid black;font-weight: normal;">Kode Barang</th>
                        <th rowspan="2" style="padding: 5px;border: 1px solid black;font-weight: normal;">Nama Barang / Deskripsi Service</th>
                        <th colspan="2" style="padding: 5px;border: 1px solid black;font-weight: normal;">Dipesan</th>
                        <th colspan="2" style="padding: 5px;border: 1px solid black;font-weight: normal;">Perkiraan Harga</th>
                        <th rowspan="2" style="padding: 5px;border: 1px solid black;font-weight: normal;">Tanggal Kedatangan</th>
                        <th colspan="2" style="padding: 5px;border: 1px solid black; word-break: keep-all;font-weight: normal;">Account Assignment</th>
                        <th rowspan="2" style="padding: 5px;border: 1px solid black;font-weight: normal; transform: rotate(-90deg); width: 1%; vertical-align: middle; ">Min Stock</th>
                        <th rowspan="2" style="padding: 5px;border: 1px solid black; font-weight: normal;transform: rotate(-90deg); width: 1%; vertical-align: middle; ">Act Stock</th>
                        <th rowspan="2" style="padding: 5px;border: 1px solid black; font-weight: normal;transform: rotate(-90deg); width: 1%; vertical-align: middle; ">Avg Usage</th>
                        <th rowspan="2" style="padding: 5px;border: 1px solid black; font-weight: normal;transform: rotate(-90deg); width: 1%; vertical-align: middle; ">Budget</th>
                        <th rowspan="2" style="padding: 5px;border: 1px solid black; font-weight: normal;transform: rotate(-90deg); width: 1%; vertical-align: middle; ">Un-Budget</th>
                        <th rowspan="2" style="padding: 5px;border: 1px solid black; width: 100px;font-weight: normal;">Catatan</th>
                    </tr>
                    <tr style="height:50px">
                        <th style="padding: 5px;border: 1px solid black;font-weight: normal;">Jumlah</th>
                        <th style="padding: 5px;border: 1px solid black;font-weight: normal;">UoM</th>
                        <th style="padding: 5px;border: 1px solid black;font-weight: normal;">Satuan</th>
                        <th style="padding: 5px;border: 1px solid black;font-weight: normal;">Total</th>
                        <th style="padding: 5px;border: 1px solid black;font-weight: normal;">Cost Center</th>
                        <th style="padding: 5px;border: 1px solid black;font-weight: normal;">Asset No./GL Account</th>
                    </tr>
                </thead>
                <tbody>
                """+contain+"""
                </tbody>
        </table>
        <br>

        <table>
        <tr>
        <td style="width:70%;">
        """+apptable+"""
        
        </td>
        <td style="width:2%;"></td>
        <td style="vertical-align: top;border: 1px solid black;">
                            <table style="font-size: 12px;width:100%;">
            <tr>
            <td style ="width:40%;"></td>
            <td colspan="3" style="text-align: right;"> Khusus PP Asset(ZRAT)</td>
            </tr>
            <tr>
            <td>Budget No</td>
            <td>:</td>
            <td>"""+xdotstr(prheader.Budget_No)+"""<td>
            <td style ="width:10%;"></td>
            </tr>
            <tr>
            <td>Budget</td>
            <td>:</td>
            <td style="text-align: right;">"""+xdotstr(prheader.Budget_Rp)+"""<td>
            <td style ="width:10%;"></td>
            </tr>
            <tr>
            <td>PP diproses</td>
            <td>:</td>
            <td style="text-align: right;border-bottom: 1px solid black;">"""+xdotstr(prheader.PP_diProses)+"""<td>
            <td style ="width:10%;"></td>
            </tr>
            <tr>
            <td>Sisa</td>
            <td>:</td>
            <td style="text-align: right;">"""+xdotstr(prheader.Sisa_Budget)+"""<td>
            <td style ="width:10%;"></td>
            </tr>
            <tr>
            <td>PP diajukan</td>
            <td>:</td>
            <td style="text-align: right;border-bottom: 1px solid black;">"""+xdotstr(prheader.PP_diAjukan)+"""<td>
            <td style ="width:10%;"></td>
            </tr>
            <tr>
            <td>Sisa</td>
            <td>:</td>
            <td style="text-align: right;">"""+xdotstr(prheader.Sisa_Final)+"""<td>
            <td style ="width:10%;"></td>
            </tr>
            </table>
        </td>
        </tr>
        </table>
        <h6 style="margin:0px;font-size:x-small;font-weight:normal;">(*) Kolom 'A' (Expense) ditandai 'F' untuk internal order, 'K' untuk cost center, 'P' untuk Project, dan 'A' untuk asset.</h6>
        <h6 style="margin:0px;font-size:x-small;font-weight:normal;">(*) Kolom 'I' (Jenis Barang) : K = Konsinyasi, L = Subcontracting, D = Service.</h6>																				
        <h6 style="margin:0px;font-size:x-small;font-weight:normal;">(*) "Catatan" dapat menunjukkan keterangan forecasting, tempat pengiriman spesifik, lokasi asset, dan lainnya.</h6>
        <br>


            <h4>"""+watermark+"""</h4>

        </div>

        <style>
        #watermark {
            position: relative;
            overflow: hidden;
        }

        #watermark h4 {
            position: absolute;
            top: -50%;
            left: -50%;
            display: block;
            width: 150%;
            height: 150%;
            z-index:-1;
            color: #ffffcc;
            opacity: 1;
            line-height: 3em;
            letter-spacing: 2px;
            font-size: 30px;
            pointer-events: none;
            -webkit-transform: rotate(-45deg);
            -moz-transform: rotate(-45deg);
        }
        </style>

        </body>
        <footer>
        <hr>
        <i style ="font-size:small;">This document is automatically generated by Online Approval System PT Astra Komponen Indonesia.<i>
        </footer>

        
        </html>
        """

    config = pdfkit.configuration(
        wkhtmltopdf='C:\Program Files\wkhtmltopdf\\bin\wkhtmltopdf.exe')
    pdfkit.from_string(email_body, "Media\Document\\"+PP_Number +
                        "-"+prheader.PR_Number+".pdf", configuration=config)
    models.PRheader.objects.filter(
        PP_Number=PP_Number).update(PR_Status="Finished")

def pdf(request, ID):
    Generate(ID)
    return HttpResponse("it works!")

@login_required
@user_passes_test(is_memberPRMRP)
def listPRMRP(request):
    ListPR = models.MRPheader.objects.filter(PR_Status__isnull=False).order_by("-id")
    context = {
        'Judul': 'List Purchase Request from MRP',
        'ListPR': ListPR
    }
    return render(request, 'purchaserequest/ListPRMRP.html', context)

@login_required
@user_passes_test(is_memberaddprno)
def createPRMRP(request):
    ListItem = []
    HeadItem = []
    
    PP_Number = 'ASKIPPREGULER' + str(models.MRPheader.objects.filter(
            PP_Number__contains="REGULER", PR_Status__isnull=False).exclude(PP_Number__contains='rev').count()+1).zfill(5)
    if (models.MRPheader.objects.filter(PP_Number = PP_Number).exists()):
        MRPheaderform = forms.MRPheader(instance=models.MRPheader.objects.get(PP_Number = PP_Number))
    else :
        MRPheaderform = forms.MRPheader()
        MRPheaderform["PP_Number"].initial = PP_Number
        MRPheaderform["Bussiness_Area"].initial = 'AK'
    approval = list(models.Approval.objects.filter(
            User=request.user.username))
    data = serializers.serialize(
            "json", models.Approval.objects.filter(User=request.user.username))
    status = "create"

    if request.method == "POST":
        if 'MRP_Item' in request.FILES:
            if (models.MRPheader.objects.filter(PP_Number = PP_Number).exists()):
                MRPheaderformpost = forms.MRPheader(request.POST,request.FILES,instance=models.MRPheader.objects.get(PP_Number = PP_Number))
            else :
                MRPheaderformpost = forms.MRPheader(request.POST,request.FILES)
            
            if MRPheaderformpost.is_valid():
                MRPheaderformpost.save()
            else :
                print(MRPheaderformpost.errors) 
            print(request.FILES)
        
            data = get_data(request.FILES['MRP_Item'])
            ListItem = data['Sheet1']
            print(ListItem)
            HeadItem = models.MRPheader.objects.get(PP_Number = PP_Number)
            status = "confirm"
        if 'back' in request.POST:
            redirect ("/PR/CreatePRMRP/")
        if 'finish' in request.POST:
            Data = models.MRPheader.objects.get(PP_Number = request.POST["PP_Number"])
            row1 = ""
            row2 = ""
            row3 = ""
            row4 = ""
            if Data.Div_Head_Name is not None:
                row1 = """<td style="width:15%;">Approved by</td>"""
                row2 = """<td id="DivHead"></td>"""
                row3 = """<td>"""+Data.Div_Head_Name+"""</td>"""
                row4 = """<td>Div Head</td>"""

            data = get_data('Media/'+str(Data.MRP_Item))
            ListItem = data['Sheet1']
            print(ListItem)

            itemTable = ""
            for Item in ListItem:
                itemTable += "<tr>"
                for I in Item :
                    itemTable += "<td>"+str(I)+"</td>"
                itemTable += "</tr>"

            GenerateMRP(request.POST["PP_Number"])

            email_body = """
                <html>
                    <head style="margin-bottom: 0px;">Dear Mr/Ms """ + Data.SPV_Name.title() + """,</head>
                        <body>
                        <p style="margin-bottom: 0px;margin-top: 0px;">This Purchase Request needs your approval </>
                        <hr>
                        <style>
            
                        .table-header {
                            table-layout: auto;
                            border: 1px solid #dee2e6;
                            width: 100%;
                            font-size: small;
                        }
                        .table-header td {
                            white-space: nowrap;
                            margin-left: 8px;
                            margin-right: 8px;
                        }

                        .table-approve {
                            border: 1px solid #dee2e6;
                            border-collapse: collapse;
                            padding: 5px;
                            font-size: small;
                        }
                        .table-approve tr th,
                        .table-approve tr td {
                            border: 1px  solid #dee2e6;
                        }
                        </style>
                            <table class="table-approve" style="width:100%;text-align: center;">
                            <tr>
                            <td style="width:200px;"><h1>ASKI</h1></td>
                            <td><h2>PURCHASE REQUEST REGULER</h2></td>
                            <td style="text-align: left;width:200px;">
                            <div>No Doc &nbsp&nbsp&nbsp&nbsp: FR-FACT.01-003</div>
                            <div>Revision &nbsp: 0</div>
                            <div>Eff. Start &nbsp: 01 Mar 2021</div>
                            </td>
                            </tr>
                            </table>  
                            <br>

                            <table class="table-header" width = "100%">
                            <tr>
                            <td width = "5%">Company</td>
                            <td>: """+Data.Company+"""</td>
                            
                            </tr>
                            <tr>
                            <td>Bussiness Area</td>
                            <td>: """+Data.Bussiness_Area+"""</td>
                            </tr>
                            <tr>
                            <td>Date Created</td>
                            <td>: """+str(Data.Date_Created)+"""</td>
                            </tr>
                            <tr>
                            <td>PP Number</td>
                            <td>: """+Data.PP_Number+"""</td>
                            </tr>
                            <tr>
                            <td>PP Type</td>
                            <td>: """+Data.PP_Type+"""</td>
                            </tr>
                            
                            </table>

                            <h4>Item PR</h4>
                            <p>terlampir.</p>

                            <h4>Approval</h4>
                            <table class="table-approve" style="white-space: nowrap;text-align: center;">
                                <tr>
                                    <td style="width:15%;">Create by</td>
                                    <td style="width:15%;">Approved by</td>
                                    <td style="width:15%;">Approved by</td>
                                    """+ row1 +"""
                                    <td style="width:15%;">Approved by</td>
                                    <td style="width:15%;">Approved by</td>
                                </tr>
                                <tr style="height:100px;">
                                    <td id="User"><div>Created</div><div>"""+datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S").replace(" ","</div><div>")+"""</div></td>
                                    <td id="SPV"></td>
                                    <td id="DeptHead"></td>
                                    """+ row2 +"""
                                    <td id="Direktur"></td>
                                    <td id="Purchase"></td>
                                </tr>
                                <tr>
                                    <td>"""+Data.User_Name+"""</td>
                                    <td>"""+Data.SPV_Name+"""</td>
                                    <td>"""+Data.Dept_Head_Name+"""</td>
                                    """+ row3 +"""
                                    <td>"""+Data.Direktur_Name+"""</td>
                                    <td>"""+Data.Purchase_Name+"""</td>
                                </tr>
                                <tr>
                                <td>User</td>
                                <td>Supervisor</td>
                                <td>Dept Head</td>
                                """+ row4 +"""
                                <td>Direktur</td>
                                <td>Purchase</td>
                                </tr>
                            </table>

                        <br>
                        <hr>
                        <p> Please give your response by click approval button bellow and then click send button. A response at your earliest convenience would be much appreciated. </p>
                        <table width="100%" cellspacing="0" cellpadding="0">
                            <tr>
                                <td>
                                    <table cellspacing="0" cellpadding="0">
                                        <tr>
                                            <td style="border-radius: 2px;width : 150px;text-align: center;" bgcolor="#4bf542">
                                                <a href="mailto:online.approval@aski.component.astra.co.id?subject=Approve: """+ Data.PP_Number+"""&body=Approve Purchase Request with ID """+ Data.PP_Number+""" %0DApproval Message:" target="_blank" style="padding: 8px 12px; border: 1px solid #4bf542;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #ffffff;text-decoration: none;font-weight:bold;display: inline-block;">
                                                    APPROVE             
                                                </a>
                                            </td>
                                            <td>&nbsp;&nbsp;</td>
                                            <td style="border-radius: 2px;width: 150px;text-align: center;" bgcolor="#ED2939">
                                                <a href="mailto:online.approval@aski.component.astra.co.id?subject=Reject: """+ Data.PP_Number+"""&body=Reject  Purchase Request with ID """+ Data.PP_Number+"""  %0DReject Message:" target="_blank" style="padding: 8px 12px; border: 1px solid #ED2939;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #ffffff;text-decoration: none;font-weight:bold;display: inline-block;">
                                                    REJECT             
                                                </a>
                                            </td>
                                            <td>&nbsp;&nbsp;</td>
                                            <td style="border-radius: 2px;width: 150px;text-align: center;" bgcolor="#ebde34">
                                                <a href="mailto:online.approval@aski.component.astra.co.id?subject=Revise: """+Data.PP_Number+"""&body=Need Revise Purchase Request with ID """+Data.PP_Number+""" %0DRevision Message:" target="_blank" style="padding: 8px 12px; border: 1px solid #ebde34;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #000000;text-decoration: none;font-weight:bold;display: inline-block;">
                                                    REVISE             
                                                </a>
                                            </td>
                                            <td>&nbsp;&nbsp;</td>
                                            <td style="border-radius: 2px;width: 150px;text-align: center;" bgcolor="#cccccc">
                                                <a href="mailto:"""+Data.User_Email+"""?subject=Ask User: """+ Data.PP_Number+"""&body=Ask User about Purchase Request with ID """+ Data.PP_Number+"""  %0DAsk User Message: " target="_blank" style="padding: 8px 12px; border: 1px solid #cccccc;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #000000;text-decoration: none;font-weight:bold;display: inline-block;">
                                                    ASK USER             
                                                </a>
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                        </table>
                        
                        <br>
                        <i>This email is automatically generated by Online Approval System PT Astra Komponen Indonesia<i>


                        </body>
                        </html>
                
                """

            mailattach = EmailMessage(
                'Purchase Request Reguler Online Approval: ' + Data.PP_Number,
                body=email_body,
                from_email=settings.EMAIL_HOST_USER,
                to=[Data.SPV_Email],
            )
            mailattach.content_subtype = "html"
            mailattach.attach_file("Media\Document\\"+Data.PP_Number +".pdf")
            if len(str(Data.Attachment1))> 5:
                mailattach.attach_file(
                    'Media/'+str(Data.Attachment1))
            if len(str(Data.Attachment2))> 5:
                mailattach.attach_file(
                    'Media/'+str(Data.Attachment2))
            mailattach.send()

                   
            email = models.Send(htmlmessage=email_body,
                            mailfrom='online.approval@aski.component.astra.co.id',
                            mailto=Data.SPV_Email,
                            PP_Number=Data.PP_Number,
                            mailheader='Purchase Request Online Approval: ' + Data.PP_Number)
       
            email.save()
            
            models.MRPheader.objects.filter(PP_Number = Data.PP_Number).update(PR_Status = "Created")

            return redirect ("/PR/ListPRMRP/")

    context = {
        'Judul': 'Create Purchase Request from MRP',
        'ListItem' : ListItem,
        'HeadItem' : HeadItem,
        'MRPHeaderForm' : MRPheaderform, 
        'Status' : status,
        'Approval' : approval,
        'Data': data
    }
    return render(request, 'purchaserequest/CreatePRMRP.html', context)

@login_required
@user_passes_test(is_memberPRMRP)
def detailPRMRP(request,ID):
    PR =  models.MRPheader.objects.get(PP_Number = ID)
    data = get_data('Media/'+str(PR.MRP_Item))
    ListItem = data['Sheet1']
 
    context = {
        'Judul': 'Detail Purchase Request from MRP',
        'HeadItem' : PR,
        'ListItem' : ListItem,
    }
    return render(request, 'purchaserequest/DetailPRMRP.html', context)

def GenerateMRP(ID):

    watermark = ""
    for x in range(1000):
        watermark += ID + " "
    Data = models.MRPheader.objects.get(PP_Number = ID)
    row1 = ""
    row2 = ""
    row3 = ""
    row4 = ""
    if Data.Div_Head_Name is not None:
        row1 = """<td style="width:15%;">Approved by</td>"""
        row2 = """<td id="DivHead"><div>"""+Data.Div_Head_Approval_Status+"""</div><div>"""+ Data.Div_Head_Approval_Date.strftime("%d-%m-%Y %H:%M:%S").replace(" ","</div><div>")+"""</div></td>""" if Data.Div_Head_Approval_Status is not None else """<td></td>"""
        row3 = """<td>"""+Data.Div_Head_Name.title()+"""</td>"""
        row4 = """<td>Div Head</td>"""

    Create = """<div>Created</div><div>"""+Data.Submit.strftime("%d-%m-%Y %H:%M:%S").replace(" ","</div><div>")+"""</div>""" if Data.Submit is not None else """ """
    SPVap = """<div>"""+Data.SPV_Approval_Status+"""</div><div>"""+ Data.SPV_Approval_Date.strftime("%d-%m-%Y %H:%M:%S").replace(" ","</div><div>")+"""</div>""" if Data.SPV_Approval_Status is not None else """ """
    Deptap = """<div>"""+Data.Dept_Head_Approval_Status+"""</div><div>"""+ Data.Dept_Head_Approval_Date.strftime("%d-%m-%Y %H:%M:%S").replace(" ","</div><div>")+"""</div>""" if Data.Dept_Head_Approval_Status is not None else """ """
    Dirap = """<div>"""+Data.Direktur_Approval_Status+"""</div><div>"""+ Data.Direktur_Approval_Date.strftime("%d-%m-%Y %H:%M:%S").replace(" ","</div><div>")+"""</div>""" if Data.Direktur_Approval_Status is not None else """ """
    Purcap = """<div>"""+Data.Purchase_Approval_Status+"""</div><div>"""+ Data.Purchase_Approval_Date.strftime("%d-%m-%Y %H:%M:%S").replace(" ","</div><div>")+"""</div>""" if Data.Purchase_Approval_Status is not None else """ """
    data = get_data('Media/'+str(Data.MRP_Item))
    ListItem = data['Sheet1']
    print(ListItem)

    itemTable = ""
    for Item in ListItem:
        itemTable += "<tr>"
        for I in Item :
            itemTable += "<td>"+str(I)+"</td>"
        itemTable += "</tr>"

    pdf_html = """
    <html>
        <head >
            <meta name="pdfkit-page-size" content="A4"/>
            <meta name="pdfkit-orientation" content="Portrait"/>
        </head>
        <body style="font-family:'Palatino Linotype'">
        <div id="watermark" style="min-height: 80vh;">
            <style>
    
                .table-header {
                    table-layout: auto;
                    border: 1px solid #dee2e6;
                    width: 100%;
                    font-size: small;
                }
                .table-header td {
                    white-space: nowrap;
                    margin-left: 8px;
                    margin-right: 8px;
                }

                .table-approve {
                    border: 1px solid #dee2e6;
                    border-collapse: collapse;
                    padding: 5px;
                    font-size: small;
                }
                .table-approve tr th,
                .table-approve tr td {
                    border: 1px  solid #dee2e6;
                }

                #watermark {
                        position: relative;
                        overflow: hidden;
                    }

                    #watermark h4 {
                        position: absolute;
                        top: -50%;
                        left: -100%;
                        width: 400%;
                        height: 200%;
                        z-index:-1;
                       color: #ffffcc;
                        line-height: 2em;
                        letter-spacing: 2px;
                        font-size: 75px;
                        pointer-events: none;
                        -webkit-transform: rotate(-5deg);
                        -moz-transform: rotate(-5deg);
                    }
                </style>

            <table class="table-approve" style="width:100%;text-align: center;">
            <tr>
            <td><img width="60px" src="http://127.0.0.1:8000/static/image/ASKI.png"/></td>
            <td><h2>PURCHASE REQUEST REGULER</h2></td>
            <td style="text-align: left;width:200px;">
            <div>No Doc &nbsp&nbsp&nbsp&nbsp: FR-FACT.01-003</div>
            <div>Revision &nbsp: 0</div>
            <div>Eff. Start &nbsp: 01 Mar 2021</div>
            </td>
            </tr>
            </table>
            <br>

                    <table class="table-header" width = "100%">
                    <tr>
                    <td width = "5%">Company</td>
                    <td>: """+Data.Company+"""</td>
                    
                    </tr>
                    <tr>
                    <td>Bussiness Area</td>
                    <td>: """+Data.Bussiness_Area+"""</td>
                    </tr>
                    <tr>
                    <td>Date Created</td>
                    <td>: """+str(Data.Date_Created)+"""</td>
                    </tr>
                    <tr>
                    <td>PP Number</td>
                    <td>: """+Data.PP_Number+"""</td>
                    </tr>
                    <tr>
                    <td>PP Type</td>
                    <td>: """+Data.PP_Type+"""</td>
                    </tr>
                    <tr>
                    <td>MRP Month</td>
                    <td>: """+Data.MRP_Month+"""</td>
                    </tr>
                    
                    </table>

                    <h5>Item PR</h5>

                    <table class="table-approve" style="width:100%;text-align: center;">
                    """+itemTable+"""
                    </table>
                
                  

                    <h5>Approval</h5>
                    <div>
                    <table class="table-approve" style="text-align: center;text-size: small;">
                        <tr>
                            <td style="width:15%;">Create by</td>
                            <td style="width:15%;">Approved by</td>
                            <td style="width:15%;">Approved by</td>
                            """+ row1 +"""
                            <td style="width:15%;">Approved by</td>
                            <td style="width:15%;">Approved by</td>
                        </tr>
                        <tr style="height:100px;">
                            <td id="User">"""+Create+"""</td>
                            <td id="SPV">"""+SPVap+"""</td>
                            <td id="DeptHead">"""+Deptap+"""</td>
                            """+ row2 +"""
                            <td id="Direktur">"""+Dirap+"""</td>
                            <td id="Purchase">"""+Purcap+"""</td>
                        </tr>
                        <tr>
                            <td>"""+Data.User_Name.title()+"""</td>
                            <td>"""+Data.SPV_Name.title()+"""</td>
                            <td>"""+Data.Dept_Head_Name.title()+"""</td>
                            """+ row3 +"""
                            <td>"""+Data.Direktur_Name.title()+"""</td>
                            <td>"""+Data.Purchase_Name.title()+"""</td>
                        </tr>
                        <tr>
                        <td>User</td>
                        <td>Supervisor</td>
                        <td>Dept Head</td>
                        """+ row4 +"""
                        <td>Direktur</td>
                        <td>Purchase</td>
                        </tr>
                    </table>
                    </div>
                      <hr>
                     <i>This document is automatically generated by Online Approval System PT Astra Komponen Indonesia<i>
              
                       <h4>"""+watermark+"""</h4>
                </div>
        </body>
    </html>
    """
    config = pdfkit.configuration(
            wkhtmltopdf='C:\Program Files\wkhtmltopdf\\bin\wkhtmltopdf.exe')
    pdfkit.from_string(pdf_html, "Media\Document\\"+Data.PP_Number +
                            ".pdf", configuration=config)
    pdfkit.from_string("<html>test</html>", "Media\\Document\\test.pdf", configuration=config)
    

def approvalMRP(request,ID):
    GenerateMRP(ID)
    return HttpResponse("it works!")


@login_required
@user_passes_test(is_memberaddprno)
def reviseMRP(request,ID):
    PP_Number = ID
    prheader = models.MRPheader.objects.get(PP_Number=ID)
    
    if 'rev' not in PP_Number:
        New_PP_Number = PP_Number + "rev1"
    else :
        New_PP_Number = PP_Number.split('rev', 1)[0] + "rev" + str(int(PP_Number.split('rev', 1)[1])+1)


    if request.method == "GET":
        if not models.MRPheader.objects.filter(PP_Number = New_PP_Number).exists():
            newheader = models.MRPheader.objects.get(PP_Number=PP_Number)
            newheader.PP_Number = New_PP_Number
            newheader.pk = None
            newheader.SPV_Approval_Date = None
            newheader.SPV_Approval_Status = None
            newheader.Dept_Head_Approval_Date = None
            newheader.Dept_Head_Approval_Status = None
            newheader.Div_Head_Approval_Date = None
            newheader.Div_Head_Approval_Status = None
            newheader.Direktur_Approval_Date = None
            newheader.Direktur_Approval_Status = None
            newheader.PR_Status = None
            newheader.Approval_Message = None
            newheader.save()
        
      

    if 'save' in request.POST:
        print(request.POST)
        headerSave = forms.MRPheader(request.POST,request.FILES, instance=models.MRPheader.objects.get(PP_Number=New_PP_Number))
        
        if headerSave.is_valid():
            headerSave.save()
        else :
            print(headerSave.errors)

    
    if 'finish' in request.POST:
            Data = models.MRPheader.objects.get(PP_Number = New_PP_Number)
            row1 = ""
            row2 = ""
            row3 = ""
            row4 = ""
            if Data.Div_Head_Name is not None:
                row1 = """<td style="width:15%;">Approved by</td>"""
                row2 = """<td id="DivHead"></td>"""
                row3 = """<td>"""+Data.Div_Head_Name+"""</td>"""
                row4 = """<td>Div Head</td>"""

            data = get_data('Media/'+str(Data.MRP_Item))
            ListItem = data['Sheet1']
            print(ListItem)

            itemTable = ""
            for Item in ListItem:
                itemTable += "<tr>"
                for I in Item :
                    itemTable += "<td>"+str(I)+"</td>"
                itemTable += "</tr>"

            GenerateMRP(request.POST["PP_Number"])

            email_body = """
                <html>
                    <head style="margin-bottom: 0px;">Dear Mr/Ms """ + Data.SPV_Name.title() + """,</head>
                        <body>
                        <p style="margin-bottom: 0px;margin-top: 0px;">This Purchase Request needs your approval </>
                        <hr>
                        <style>
            
                        .table-header {
                            table-layout: auto;
                            border: 1px solid #dee2e6;
                            width: 100%;
                            font-size: small;
                        }
                        .table-header td {
                            white-space: nowrap;
                            margin-left: 8px;
                            margin-right: 8px;
                        }

                        .table-approve {
                            border: 1px solid #dee2e6;
                            border-collapse: collapse;
                            padding: 5px;
                            font-size: small;
                        }
                        .table-approve tr th,
                        .table-approve tr td {
                            border: 1px  solid #dee2e6;
                        }
                        </style>
                            <table class="table-approve" style="width:100%;text-align: center;">
                            <tr>
                            <td style="width:200px;"><h1>ASKI</h1></td>
                            <td><h2>PURCHASE REQUEST REGULER</h2></td>
                            <td style="text-align: left;width:200px;">
                            <div>No Doc &nbsp&nbsp&nbsp&nbsp: FR-FACT.01-002</div>
                            <div>Revision &nbsp: 0</div>
                            <div>Eff. Start &nbsp: 01 Mar 2021</div>
                            </td>
                            </tr>
                            </table>  
                            <br>

                            <table class="table-header" width = "100%">
                            <tr>
                            <td width = "5%">Company</td>
                            <td>: """+Data.Company+"""</td>
                            
                            </tr>
                            <tr>
                            <td>Bussiness Area</td>
                            <td>: """+Data.Bussiness_Area+"""</td>
                            </tr>
                            <tr>
                            <td>Date Created</td>
                            <td>: """+str(Data.Date_Created)+"""</td>
                            </tr>
                            <tr>
                            <td>PP Number</td>
                            <td>: """+Data.PP_Number+"""</td>
                            </tr>
                            <tr>
                            <td>PP Type</td>
                            <td>: """+Data.PP_Type+"""</td>
                            </tr>
                            
                            </table>

                            <h4>Item PR</h4>
                            <p>terlampir.</p>

                            <h4>Approval</h4>
                            <table class="table-approve" style="white-space: nowrap;text-align: center;">
                                <tr>
                                    <td style="width:15%;">Create by</td>
                                    <td style="width:15%;">Approved by</td>
                                    <td style="width:15%;">Approved by</td>
                                    """+ row1 +"""
                                    <td style="width:15%;">Approved by</td>
                                    <td style="width:15%;">Approved by</td>
                                </tr>
                                <tr style="height:100px;">
                                    <td id="User"><div>Created</div><div>"""+datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S").replace(" ","</div><div>")+"""</div></td>
                                    <td id="SPV"></td>
                                    <td id="DeptHead"></td>
                                    """+ row2 +"""
                                    <td id="Direktur"></td>
                                    <td id="Purchase"></td>
                                </tr>
                                <tr>
                                    <td>"""+Data.User_Name+"""</td>
                                    <td>"""+Data.SPV_Name+"""</td>
                                    <td>"""+Data.Dept_Head_Name+"""</td>
                                    """+ row3 +"""
                                    <td>"""+Data.Direktur_Name+"""</td>
                                    <td>"""+Data.Purchase_Name+"""</td>
                                </tr>
                                <tr>
                                <td>User</td>
                                <td>Supervisor</td>
                                <td>Dept Head</td>
                                """+ row4 +"""
                                <td>Direktur</td>
                                <td>Purchase</td>
                                </tr>
                            </table>

                        <br>
                        <hr>
                        <p> Please give your response by click approval button bellow and then click send button. A response at your earliest convenience would be much appreciated. </p>
                        <table width="100%" cellspacing="0" cellpadding="0">
                            <tr>
                                <td>
                                    <table cellspacing="0" cellpadding="0">
                                        <tr>
                                            <td style="border-radius: 2px;width : 150px;text-align: center;" bgcolor="#4bf542">
                                                <a href="mailto:online.approval@aski.component.astra.co.id?subject=Approve: """+ Data.PP_Number+"""&body=Approve Purchase Request with ID """+ Data.PP_Number+""" %0DApproval Message:" target="_blank" style="padding: 8px 12px; border: 1px solid #4bf542;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #ffffff;text-decoration: none;font-weight:bold;display: inline-block;">
                                                    APPROVE             
                                                </a>
                                            </td>
                                            <td>&nbsp;&nbsp;</td>
                                            <td style="border-radius: 2px;width: 150px;text-align: center;" bgcolor="#ED2939">
                                                <a href="mailto:online.approval@aski.component.astra.co.id?subject=Reject: """+ Data.PP_Number+"""&body=Reject  Purchase Request with ID """+ Data.PP_Number+"""  %0DReject Message:" target="_blank" style="padding: 8px 12px; border: 1px solid #ED2939;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #ffffff;text-decoration: none;font-weight:bold;display: inline-block;">
                                                    REJECT             
                                                </a>
                                            </td>
                                            <td>&nbsp;&nbsp;</td>
                                            <td style="border-radius: 2px;width: 150px;text-align: center;" bgcolor="#ebde34">
                                                <a href="mailto:online.approval@aski.component.astra.co.id?subject=Revise: """+Data.PP_Number+"""&body=Need Revise Purchase Request with ID """+Data.PP_Number+""" %0DRevision Message:" target="_blank" style="padding: 8px 12px; border: 1px solid #ebde34;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #000000;text-decoration: none;font-weight:bold;display: inline-block;">
                                                    REVISE             
                                                </a>
                                            </td>
                                            <td>&nbsp;&nbsp;</td>
                                            <td style="border-radius: 2px;width: 150px;text-align: center;" bgcolor="#cccccc">
                                                <a href="mailto:"""+Data.User_Email+"""?subject=Ask User: """+ Data.PP_Number+"""&body=Ask User about Purchase Request with ID """+ Data.PP_Number+"""  %0DAsk User Message: " target="_blank" style="padding: 8px 12px; border: 1px solid #cccccc;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #000000;text-decoration: none;font-weight:bold;display: inline-block;">
                                                    ASK USER             
                                                </a>
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                        </table>
                        
                        <br>
                        <i>This email is automatically generated by Online Approval System PT Astra Komponen Indonesia<i>


                        </body>
                        </html>
                
                """

            mailattach = EmailMessage(
                'Purchase Request Reguler Online Approval: ' + Data.PP_Number,
                body=email_body,
                from_email=settings.EMAIL_HOST_USER,
                to=[Data.SPV_Email],
            )
            mailattach.content_subtype = "html"
            mailattach.attach_file("Media\Document\\"+Data.PP_Number +".pdf")
            if len(str(Data.Attachment1))> 5:
                mailattach.attach_file(
                    'Media/'+str(Data.Attachment1))
            if len(str(Data.Attachment2))> 5:
                mailattach.attach_file(
                    'Media/'+str(Data.Attachment2))
            mailattach.send()

                   
            email = models.Send(htmlmessage=email_body,
                            mailfrom='online.approval@aski.component.astra.co.id',
                            mailto=Data.SPV_Email,
                            PP_Number=Data.PP_Number,
                            mailheader='Purchase Request Online Approval: ' + Data.PP_Number)
       
            email.save()
            
            models.MRPheader.objects.filter(PP_Number = Data.PP_Number).update(PR_Status = "Created")
            models.MRPheader.objects.filter(PP_Number = PP_Number).update(PR_Status = "Revised")

            return redirect ("/PR/ListPRMRP/")

    newprheader = models.MRPheader.objects.get(PP_Number=New_PP_Number)
    data = get_data('Media/'+str(newprheader.MRP_Item))
    ListItem = data['Sheet1']
    MRPheaderform = forms.MRPheader(instance=models.MRPheader.objects.get(PP_Number = New_PP_Number))                    
    
    context = {
        'Judul': 'Revise Purchase Request MRP',
        'PP_Number': PP_Number,
        'New_PP_Number': New_PP_Number,
        'HeadItem': newprheader,
        'ListItem' : ListItem,
        'MRPForm' : MRPheaderform,
 
        'Data': data
    }
    return render(request, 'purchaserequest/ReviseMRP.html', context)
