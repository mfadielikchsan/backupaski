from ast import Delete
import os
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from PyPDF2 import PdfFileWriter, PdfFileReader
from . import forms
from . import models
from . import resources
from django.core import serializers
from django.shortcuts import redirect
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.views import generic
from rest_framework.views import APIView
from rest_framework.response import Response
import datetime
from django.http import HttpResponse
import pdfkit
from pyexcel_xlsx import get_data
from django.contrib.auth.decorators import user_passes_test
import json
import pandas as pd
import numpy as np
from django.db.models import Q
from xlsx2html import xlsx2html
import xlsxwriter
from io import BytesIO
from django.core.files.storage import FileSystemStorage
from django.core.files.storage import default_storage

# Create your views here.

def is_membercreatePP(user):
    return user.groups.filter(name='Allow_Create_PO').exists()

def is_memberaddasset(user):
    return user.groups.filter(name='Allow_Add_Asset').exists()

@login_required
@user_passes_test(is_membercreatePP)
def create(request):
    PP_Number = 'ASKIPURCHASINGPRICE'+ str(models.PurchasingPrice.objects.filter(PP_Number__contains="PURCHASINGPRICE" , Status__isnull=False).exclude(
            PP_Number__contains='rev').count() + 1).zfill(5)
    PP = forms.PurchasingPrice()
    PP.fields['Submit'].initial = datetime.datetime.now()
    PP.fields['PP_Number'].initial = PP_Number
    
    approval = list(models.Approval.objects.filter(User=request.user.username))
    data = serializers.serialize("json", models.Approval.objects.filter(User=request.user))
    Note = ''
    if request.method == 'POST':
        print(request.POST)
        if 'upload' in request.POST:
            print(request.FILES)

            items = pd.read_excel(request.FILES['PP_Item'],sheet_name=0, skiprows=4)
            # items['Old Delivery'] = items['Old Delivery'].dt.strftime('%b %Y')
            # items['New Delivery'] = items['New Delivery'].dt.strftime('%b %Y')
            items['Old Price'] = items['Old Price'].map('{:,}'.format)
            items['New Price'] = items['New Price'].map('{:,}'.format)
            
            items['Ratio Variance'] = items['Ratio Variance'].transform(lambda x: '{:,.2%}'.format(x)).str.replace('nan%', '-').str.replace('.', ',')

            print(items)
            models.PP_Item.objects.filter(PP_Number = PP_Number).delete()
            for item in items.values.tolist() :
                PP.fields['Vendor'].initial = item[1]
                models.PP_Item(
                    PP_Number = PP_Number,
                    Vend_Code = item[0],
                    Vend_Name = item[1],
                    Material = item[2],
                    Material_Desc = item[3],   
                    Qty = item[4],
                    UoM = item[5],
                    Currency = item[6],
                    Old_Price = item[7],
                    Old_Delivery = item[8],  
                    New_Price = item[9],
                    New_Delivery = item[10],
                    Ratio = item[11]
                ).save()

            # note = pd.read_excel(request.FILES['PP_Item'],sheet_name=1, skiprows=0)
            # print(note.to_html())
            out_stream = xlsx2html(request.FILES['PP_Item'],sheet=1)
            out_stream.seek(0)
            # print(out_stream.read())
            Note = str(out_stream.read()).split('<body>')[1].split('</body>')[0]
            PP.fields['Note'].initial = Note
            print(Note)

            excel = request.FILES['PP_Item']
            filename = default_storage.save("Uploads/"+PP_Number+".xlsx", excel)

        elif 'Finish' in request.POST:
            # print(request.POST)
            if (models.PurchasingPrice.objects.filter(PP_Number = PP_Number).exists()):
                PPform = forms.PurchasingPrice(request.POST, request.FILES, instance=models.PurchasingPrice.objects.get(PP_Number=PP_Number))
            else:
                PPform = forms.PurchasingPrice(request.POST, request.FILES)
            if PPform.is_valid():
                PPform.save()
                PPHead = models.PurchasingPrice.objects.get(PP_Number=PP_Number)
                PPItem = models.PP_Item.objects.filter(PP_Number=PP_Number)
                contain = ''
                for item in PPItem:
                    contain += '''<tr style="height: 30px; font-size:12px; border-collapse: collapse;">
                        <td style="border: 1px solid black; border-collapse: collapse;">''' + str(item.Vend_Code) + '''</td>
                        <td style="border: 1px solid black; border-collapse: collapse;">''' + str(item.Vend_Name) + '''</td>
                        <td style="border: 1px solid black; border-collapse: collapse;">''' + str(item.Material) + '''</td>
                        <td style="border: 1px solid black; border-collapse: collapse;">''' + str(item.Material_Desc) + '''</td>
                        <td style="border: 1px solid black; border-collapse: collapse;">''' + str(item.Qty) + '''</td>
                        <td style="border: 1px solid black; border-collapse: collapse;">''' + str(item.UoM) + '''</td>
                        <td style="border: 1px solid black; border-collapse: collapse;">''' + str(item.Currency) +' '+ str(item.Old_Price)+ '''</td>
                        <td style="border: 1px solid black; border-collapse: collapse;">''' + str(item.Old_Delivery) + '''</td>
                        <td style="border: 1px solid black; border-collapse: collapse;">''' + str(item.Currency) +' '+ str(item.New_Price)+ '''</td>
                        <td style="border: 1px solid black; border-collapse: collapse;">''' + str(item.New_Delivery) + '''</td>
                        <td style="border: 1px solid black; border-collapse: collapse;">''' + str(item.Ratio) + '''</td>
                    </tr>'''
                email_body = """\
                        <html>
                        <head style="margin-bottom: 0px;">Dear Mr/Ms """ + PPHead.SPV.title() + """,</head>
                        <body>
                        <p style="margin-bottom: 0px;margin-top: 0px;">This Purchasing Price needs your approval </>
                        <hr>
                        <table style="font-size: x-small; width: 100%">
                            <tr>
                                <td rowspan="3" style="width: 15%;  text-align: center; border-bottom: 1px solid black;"><h1>ASKI</h1></td>
                                <td rowspan="3" style="text-align: center;  border-bottom: 1px solid black;">
                                    <h3>PERUBAHAN/PERSETUJUAN HARGA PEMBELIAN</h3>
                                </td>
                                <td style="width: 10%;">No. Document</td>
                                <td style="text-align: center;">:</td>
                                <td style="text-align: center; width: 10%;">FR-PURC.01-006</td>
                            </tr>
                            <tr>
                                <td>Revision</td>
                                <td style="text-align: center;">:</td>
                                <td style="text-align: center;">0</td>
                            </tr>
                            <tr>
                                <td style="border-bottom: 1px solid black;">Effective Start</td>
                                <td style="text-align: center; border-bottom: 1px solid black;">:</td>
                                <td style="text-align: center; border-bottom: 1px solid black;">09-Jan-14</td>
                            </tr>
                        </table>
                        <br>
                        <table style="width: 100%; font-size: 12px;">
                            <tr>
                            <td style="width: 10%;white-space: nowrap;">Purchasing Price Number</td>
                            <td>:</td>
                            <td>""" + str(PPHead.PP_Number) + """</td>
                            </tr>
                            <tr>
                            <td style="width: 10%;white-space: nowrap;">Part Type</td>
                            <td>:</td>
                            <td>""" + str(PPHead.Type) + """</td>
                            </tr>
                            
                        </table>
                        <br>
                        <table style="width: 100%; border-collapse: collapse; font-size: 12px;text-align: center">
                        <thead>
                            <tr style="border: 1px solid">
                                <th  style="padding: 5px; border: 1px solid">Vendor Code</th>
                                <th  style="padding: 5px; border: 1px solid">Vendor Name</th>
                                <th  style="padding: 5px; border: 1px solid">Material No</th>
                                <th  style="padding: 5px; border: 1px solid">Material Description</th>
                                <th  style="padding: 5px; border: 1px solid">Qty</th>
                                <th  style="padding: 5px; border: 1px solid">UoM</th>
                                <th  style="padding: 5px; border: 1px solid">Old Price</th>
                                <th  style="padding: 5px; border: 1px solid">Old Delivery </th>
                                <th  style="padding: 5px; border: 1px solid">New Price</th>
                                <th  style="padding: 5px; border: 1px solid">New Delivery </th>
                                <th  style="padding: 5px; border: 1px solid">Ratio Variance </th>
                            </tr>
                        </thead>
                        <tbody >
                        """ + contain + """
                        </tbody>
                        </table>
                        <br>
                        <H6>Note :</H6>
                        """ + PPHead.Note + """
                        <br>
                    
                        <table style="font-size: 12px;text-align: center;border: 1px solid black;border-collapse: collapse;" >
                            <tbody>
                                <tr style="height:10px;border: 1px solid black;border-collapse: collapse;">
                                    <td style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 12,5%;text-align: center;vertical-align: bottom;">Created By</td>
                                    <td style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 12,5%;text-align: center;vertical-align: bottom;">Checked By</td>
                                    <td style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 12,5%;text-align: center;vertical-align: bottom;">Checked By</td>
                                    <td style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 12,5%;text-align: center;vertical-align: bottom;">Approved By</td>
                                    <td style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 12,5%;text-align: center;vertical-align: bottom;">Approved By</td>
                                    <td style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 12,5%;text-align: center;vertical-align: bottom;">Approved By</td>
                                    <td style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 12,5%;text-align: center;vertical-align: bottom;">Input By</td>
                                    <td style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 12,5%;text-align: center;vertical-align: bottom;">Confirm By</td>
                                </tr>
                                <tr style="height:40px;border: 1px solid black;border-collapse: collapse;">
                                    <td style="border: 1px solid black;border-collapse: collapse;padding:20px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="Admin">Created """ + str(PPHead.Submit.strftime("%Y-%m-%d %H:%M:%S")) + """</td>
                                    <td style="border: 1px solid black;border-collapse: collapse;padding:20px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="SPV"></td>
                                    <td style="border: 1px solid black;border-collapse: collapse;padding:20px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="DEPT"></td>
                                    <td style="border: 1px solid black;border-collapse: collapse;padding:20px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="MKT"></td>
                                    <td style="border: 1px solid black;border-collapse: collapse;padding:20px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="DIV"></td>
                                    <td style="border: 1px solid black;border-collapse: collapse;padding:20px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="PRESDIR"></td>
                                    <td style="border: 1px solid black;border-collapse: collapse;padding:20px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="FIN"></td>
                                    <td style="border: 1px solid black;border-collapse: collapse;padding:20px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="FIN_DEPT"></td>
                                </tr>
                                <tr style="height:20px;border: 1px solid black;border-collapse: collapse;">
                                <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">""" + PPHead.Admin.title() + """</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">""" + PPHead.SPV.title() + """</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">""" + PPHead.Dept_Head.title() + """</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">""" + PPHead.Mkt_Head.title() + """</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">""" + PPHead.Div_Head.title() + """</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">""" + PPHead.PresDirektur.title() + """</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">""" + PPHead.Fin.title() + """</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">""" + PPHead.Dept_Fin.title() + """</td>
                                </tr>
                                <tr style="height:10px;border: 1px solid black;border-collapse: collapse;">
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">Purchasing Admin</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">Purchasing SPV</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">Purchasing Dept Head</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">Marketing Dept Head</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">Administration Div Head</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">President Director</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">Finance SPV</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">Finance Dept Head</td>
                                </tr>
                            </tbody>
                        </table>
                        <br>
                        <hr>
                        <p> Please give your response by click approval button bellow and then click send button. A response at your earliest convenience would be much appreciated. </p>
                        <table width="100%" cellspacing="0" cellpadding="0" >
                            <tr>
                                <td>
                                    <table cellspacing="0" cellpadding="0">
                                        <tr>
                                            <td style="border-radius: 2px;width : 150px;text-align: center;" bgcolor="#4bf542">
                                                <a href="mailto:online.approval@aski.component.astra.co.id?subject=Approve: """ + str(PPHead.PP_Number) + """&body=Purchasing Price Request with ID """ + str(PPHead.PP_Number) + """ %0DApproval Message:" target="_blank" style="padding: 8px 12px; border: 1px solid #4bf542;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #ffffff;text-decoration: none;font-weight:bold;display: inline-block;">
                                                    APPROVE
                                                </a>
                                            </td>
                                            <td>&nbsp;&nbsp;</td>
                                            <td style="border-radius: 2px;width: 150px;text-align: center;" bgcolor="#ED2939">
                                                <a href="mailto:online.approval@aski.component.astra.co.id?subject=Reject: """ + str(PPHead.PP_Number) + """&body=Purchasing Selling Price Request with ID """ + str(PPHead.PP_Number) + """ %0DReject Message:" target="_blank" style="padding: 8px 12px; border: 1px solid #ED2939;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #ffffff;text-decoration: none;font-weight:bold;display: inline-block;">
                                                    REJECT
                                                </a>
                                            </td>
                                            <td>&nbsp;&nbsp;</td>
                                            <td style="border-radius: 2px;width: 150px;text-align: center;" bgcolor="#ebde34">
                                                <a href="mailto:online.approval@aski.component.astra.co.id?subject=Revise: """ + str(PPHead.PP_Number) + """&body=Need Revise Purchasing Price Request with ID """ + str(PPHead.PP_Number) + """ %0DRevision Message:" target="_blank" style="padding: 8px 12px; border: 1px solid #ebde34;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #000000;text-decoration: none;font-weight:bold;display: inline-block;">
                                                    REVISE
                                                </a>
                                            </td>
                                            <td>&nbsp;&nbsp;</td>
                                            <td style="border-radius: 2px;width: 150px;text-align: center;" bgcolor="#cccccc">
                                                <a href="mailto:""" + str(PPHead.Admin_Email) + """?subject=Ask User: """ + str(PPHead.PP_Number) + """&body=Ask User about Purchasing Price Request with ID """ + str(PPHead.PP_Number) + """ %0DAsk User Message: " target="_blank" style="padding: 8px 12px; border: 1px solid #cccccc;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #000000;text-decoration: none;font-weight:bold;display: inline-block;">
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
                'Purchasing Price Online Approval: ' + 
                PP_Number,
                body=email_body, from_email=settings.EMAIL_HOST_USER, 
                to=[PPHead.SPV_Email],
                )
                mailattach.content_subtype = "html"
                if 'Attachment1' in request.FILES:
                    mailattach.attach_file(
                        'Media/Uploads/' + str(request.FILES['Attachment1']).replace(' ', '_'))
                if 'Attachment2' in request.FILES:
                    mailattach.attach_file(
                        'Media/Uploads/' + str(request.FILES['Attachment2']).replace(' ', '_'))
                if 'Attachment3' in request.FILES:
                    mailattach.attach_file(
                        'Media/Uploads/' + str(request.FILES['Attachment3']).replace(' ', '_'))
                if 'Attachment4' in request.FILES:
                    mailattach.attach_file(
                        'Media/Uploads/' + str(request.FILES['Attachment4']).replace(' ', '_'))
                mailattach.send()

                email = models.Send(
                    htmlmessage=email_body,
                    mailfrom='online.approval@aski.component.astra.co.id',
                    mailto=PPHead.SPV_Email,
                    PP_Number=PP_Number,
                    mailheader='Purchasing Price Online Approval: ' + PP_Number)
                email.save()

                models.PurchasingPrice.objects.filter(PP_Number=PP_Number).update(Status="Created")
                return redirect("/PP/ListPP/")

            else:
                print(PPform.errors)
                return HttpResponse(PPform.errors)

    if request.method == 'GET':
        models.PP_Item.objects.filter(PP_Number = PP_Number).delete()
    PPItem = models.PP_Item.objects.filter(PP_Number=PP_Number)
    context={
        'Judul': 'Create SAP Purchasing Price Approval Request',
        'PPForm' : PP,
        'PPItem' : PPItem,
        'PP_Number' : PP_Number,
        'Note' : Note,
        'Data': data,
    }
    return render(request, 'purchasingprice/Create.html',context)

@login_required
@user_passes_test(is_membercreatePP)
def listPP(request):
    ListPP = models.PurchasingPrice.objects.filter(Status__isnull=False).order_by("-id")
    ListPPItem = models.PP_Item.objects.order_by("-id")

    context={
        'ListPP':ListPP,
        'ListPPItem' : ListPPItem
    }
    return render(request, 'purchasingprice/ListPP.html',context)

@login_required
@user_passes_test(is_membercreatePP)
def detail(request, PP_Number):
    PP = models.PurchasingPrice.objects.get(PP_Number=PP_Number)
    PPItem = models.PP_Item.objects.filter(PP_Number=PP_Number).order_by("-id")

    context={
        'PP_Number': PP_Number,
        'PP':PP,
        'PPItem' : PPItem
    }
    return render(request, 'purchasingprice/Detail.html',context)

@login_required
@user_passes_test(is_membercreatePP)
def revise(request, PP_Number):
    NewPP_Number = PP_Number.split('rev')[0] + 'rev' + str(models.PurchasingPrice.objects.filter(PP_Number__contains = PP_Number.split('rev')[0]).exclude(Status = None).count() )
    PP = forms.PurchasingPrice()
    PP.fields['Submit'].initial = datetime.datetime.now()
    PP.fields['PP_Number'].initial = NewPP_Number
    Revise_Request = models.PurchasingPrice.objects.get(PP_Number=PP_Number).Revise_Request
    
    approval = list(models.Approval.objects.filter(User=request.user.username))
    data = serializers.serialize("json", models.Approval.objects.filter(User=request.user))
    Note = ''
    olditem = models.PurchasingPrice.objects.filter(PP_Number=PP_Number).values_list('Vendor', 'Attn1', 'Attn2', 'Vendor_Email', 'QuotDate', 'ConfNote')
    for item in olditem:
        PP.fields['Vendor'].initial = item[0]
        PP.fields['Attn1'].initial = item[1]
        PP.fields['Attn2'].initial = item[2]
        PP.fields['Vendor_Email'].initial = item[3]
        PP.fields['QuotDate'].initial = item[4]
        PP.fields['ConfNote'].initial = item[5]
        
    if request.method == 'POST':
        print(request.POST)
        if 'upload' in request.POST:
            print(request.FILES)
            items = pd.read_excel(request.FILES['PP_Item'],sheet_name=0, skiprows=4)
            items['Old Price'] = items['Old Price'].map('{:,}'.format)
            items['New Price'] = items['New Price'].map('{:,}'.format)
            items['Ratio Variance'] = items['Ratio Variance'].transform(lambda x: '{:,.2%}'.format(x)).str.replace('nan%', '-').str.replace('.', ',')

            print(items)
            models.PP_Item.objects.filter(PP_Number = NewPP_Number).delete()
            for item in items.values.tolist() :
                PP.fields['Vendor'].initial = item[1]
                models.PP_Item(
                    PP_Number = NewPP_Number,
                    Vend_Code = item[0],
                    Vend_Name = item[1],
                    Material = item[2],
                    Material_Desc = item[3],   
                    Qty = item[4],
                    UoM = item[5],
                    Currency = item[6],
                    Old_Price = item[7],
                    Old_Delivery = item[8],  
                    New_Price = item[9],
                    New_Delivery = item[10],
                    Ratio = item[11]
                ).save()

            # note = pd.read_excel(request.FILES['PP_Item'],sheet_name=1, skiprows=0)
            # print(note.to_html())
            out_stream = xlsx2html(request.FILES['PP_Item'],sheet=1)
            out_stream.seek(1)
            Note = str(out_stream.read()).split('<body>')[1].split('</body>')[0]
            PP.fields['Note'].initial = Note
            print(Note)
        elif 'Finish' in request.POST:
            # print(request.POST)
            if (models.PurchasingPrice.objects.filter(PP_Number = NewPP_Number).exists()):
                PPform = forms.PurchasingPrice(request.POST, request.FILES, instance=models.PurchasingPrice.objects.get(PP_Number=NewPP_Number))
            else:
                PPform = forms.PurchasingPrice(request.POST, request.FILES)
            if PPform.is_valid():
                PPform.save()
                PPHead = models.PurchasingPrice.objects.get(PP_Number=NewPP_Number)
                PPItem = models.PP_Item.objects.filter(PP_Number=NewPP_Number)
                contain = ''
                for item in PPItem:
                    contain += '''<tr style="height: 30px; font-size:12px; border-collapse: collapse;">
                        <td style="border: 1px solid black; border-collapse: collapse;">''' + str(item.Vend_Code) + '''</td>
                        <td style="border: 1px solid black; border-collapse: collapse;">''' + str(item.Vend_Name) + '''</td>
                        <td style="border: 1px solid black; border-collapse: collapse;">''' + str(item.Material) + '''</td>
                        <td style="border: 1px solid black; border-collapse: collapse;">''' + str(item.Material_Desc) + '''</td>
                        <td style="border: 1px solid black; border-collapse: collapse;">''' + str(item.Qty) + '''</td>
                        <td style="border: 1px solid black; border-collapse: collapse;">''' + str(item.UoM) + '''</td>
                        <td style="border: 1px solid black; border-collapse: collapse;">''' + str(item.Currency) +' '+ str(item.Old_Price)+ '''</td>
                        <td style="border: 1px solid black; border-collapse: collapse;">''' + str(item.Old_Delivery) + '''</td>
                        <td style="border: 1px solid black; border-collapse: collapse;">''' + str(item.Currency) +' '+ str(item.New_Price)+ '''</td>
                        <td style="border: 1px solid black; border-collapse: collapse;">''' + str(item.New_Delivery) + '''</td>
                        <td style="border: 1px solid black; border-collapse: collapse;">''' + str(item.Ratio) + '''</td>

                    </tr>'''
                email_body = """\
                        <html>
                        <head style="margin-bottom: 0px;">Dear Mr/Ms """ + PPHead.SPV.title() + """,</head>
                        <body>
                        <p style="margin-bottom: 0px;margin-top: 0px;">This Purchasing Price needs your approval </>
                        <hr>
                        <table style="font-size: x-small; width: 100%">
                            <tr>
                                <td rowspan="3" style="width: 15%;  text-align: center; border-bottom: 1px solid black;"><h1>ASKI</h1></td>
                                <td rowspan="3" style="text-align: center;  border-bottom: 1px solid black;">
                                    <h3>PERUBAHAN/PERSETUJUAN HARGA PEMBELIAN</h3>
                                </td>
                                <td style="width: 10%;">No. Document</td>
                                <td style="text-align: center;">:</td>
                                <td style="text-align: center; width: 10%;">FR-PURC.01-006</td>
                            </tr>
                            <tr>
                                <td>Revision</td>
                                <td style="text-align: center;">:</td>
                                <td style="text-align: center;">0</td>
                            </tr>
                            <tr>
                                <td style="border-bottom: 1px solid black;">Effective Start</td>
                                <td style="text-align: center; border-bottom: 1px solid black;">:</td>
                                <td style="text-align: center; border-bottom: 1px solid black;">09-Jan-14</td>
                            </tr>
                        </table>
                        <br>
                        <table style="width: 100%; font-size: 12px;">
                            <tr>
                            <td style="width: 10%;white-space: nowrap;">Purchasing Price Number</td>
                            <td>:</td>
                            <td>""" + str(PPHead.PP_Number) + """</td>
                            </tr>
                            <tr>
                            <td style="width: 10%;white-space: nowrap;">Part Type</td>
                            <td>:</td>
                            <td>""" + str(PPHead.Type) + """</td>
                            </tr>
                            
                        </table>
                        <br>
                        <table style="width: 100%; border-collapse: collapse; font-size: 12px;text-align: center">
                        <thead>
                            <tr style="border: 1px solid">
                                <th  style="padding: 5px; border: 1px solid">Vendor Code</th>
                                <th  style="padding: 5px; border: 1px solid">Vendor Name</th>
                                <th  style="padding: 5px; border: 1px solid">Material No</th>
                                <th  style="padding: 5px; border: 1px solid">Material Description</th>
                                <th  style="padding: 5px; border: 1px solid">Qty</th>
                                <th  style="padding: 5px; border: 1px solid">UoM</th>
                                <th  style="padding: 5px; border: 1px solid">Old Price</th>
                                <th  style="padding: 5px; border: 1px solid">Old Delivery </th>
                                <th  style="padding: 5px; border: 1px solid">New Price</th>
                                <th  style="padding: 5px; border: 1px solid">New Delivery </th>
                                <th  style="padding: 5px; border: 1px solid">Ratio Variance </th>
                            </tr>
                        </thead>
                        <tbody >
                        """ + contain + """
                        </tbody>
                        </table>
                        <br>
                        <H6>Note :</H6>
                        """ + PPHead.Note + """
                        <br>
                    
                        <table style="font-size: 12px;text-align: center;border: 1px solid black;border-collapse: collapse;" >
                            <tbody>
                                <tr style="height:10px;border: 1px solid black;border-collapse: collapse;">
                                    <td style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 12,5%;text-align: center;vertical-align: bottom;">Created By</td>
                                    <td style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 12,5%;text-align: center;vertical-align: bottom;">Checked By</td>
                                    <td style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 12,5%;text-align: center;vertical-align: bottom;">Checked By</td>
                                    <td style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 12,5%;text-align: center;vertical-align: bottom;">Approved By</td>
                                    <td style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 12,5%;text-align: center;vertical-align: bottom;">Approved By</td>
                                    <td style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 12,5%;text-align: center;vertical-align: bottom;">Approved By</td>
                                    <td style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 12,5%;text-align: center;vertical-align: bottom;">Input By</td>
                                    <td style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 12,5%;text-align: center;vertical-align: bottom;">Confirm By</td>
                                </tr>
                                <tr style="height:40px;border: 1px solid black;border-collapse: collapse;">
                                    <td style="border: 1px solid black;border-collapse: collapse;padding:20px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="Admin">Created """ + str(PPHead.Submit.strftime("%Y-%m-%d %H:%M:%S")) + """</td>
                                    <td style="border: 1px solid black;border-collapse: collapse;padding:20px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="SPV"></td>
                                    <td style="border: 1px solid black;border-collapse: collapse;padding:20px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="DEPT"></td>
                                    <td style="border: 1px solid black;border-collapse: collapse;padding:20px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="MKT"></td>
                                    <td style="border: 1px solid black;border-collapse: collapse;padding:20px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="DIV"></td>
                                    <td style="border: 1px solid black;border-collapse: collapse;padding:20px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="PRESDIR"></td>
                                    <td style="border: 1px solid black;border-collapse: collapse;padding:20px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="FIN"></td>
                                    <td style="border: 1px solid black;border-collapse: collapse;padding:20px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="FIN_DEPT"></td>
                                </tr>
                                <tr style="height:20px;border: 1px solid black;border-collapse: collapse;">
                                <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">""" + PPHead.Admin.title() + """</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">""" + PPHead.SPV.title() + """</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">""" + PPHead.Dept_Head.title() + """</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">""" + PPHead.Mkt_Head.title() + """</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">""" + PPHead.Div_Head.title() + """</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">""" + PPHead.PresDirektur.title() + """</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">""" + PPHead.Fin.title() + """</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">""" + PPHead.Dept_Fin.title() + """</td>
                                </tr>
                                <tr style="height:10px;border: 1px solid black;border-collapse: collapse;">
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">Purchasing Admin</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">Purchasing SPV</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">Purchasing Dept Head</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">Marketing Dept Head</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">Administration Div Head</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">President Director</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">Finance SPV</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">Finance Dept Head</td>
                                </tr>
                            </tbody>
                        </table>
                        <br>
                        <hr>
                         Revision : """+PPHead.Revise_Note+"""
                        <hr>
                        <p> Please give your response by click approval button bellow and then click send button. A response at your earliest convenience would be much appreciated. </p>
                        <table width="100%" cellspacing="0" cellpadding="0" >
                            <tr>
                                <td>
                                    <table cellspacing="0" cellpadding="0">
                                        <tr>
                                            <td style="border-radius: 2px;width : 150px;text-align: center;" bgcolor="#4bf542">
                                                <a href="mailto:online.approval@aski.component.astra.co.id?subject=Approve: """ + str(PPHead.PP_Number) + """&body=Purchasing Price Request with ID """ + str(PPHead.PP_Number) + """ %0DApproval Message:" target="_blank" style="padding: 8px 12px; border: 1px solid #4bf542;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #ffffff;text-decoration: none;font-weight:bold;display: inline-block;">
                                                    APPROVE
                                                </a>
                                            </td>
                                            <td>&nbsp;&nbsp;</td>
                                            <td style="border-radius: 2px;width: 150px;text-align: center;" bgcolor="#ED2939">
                                                <a href="mailto:online.approval@aski.component.astra.co.id?subject=Reject: """ + str(PPHead.PP_Number) + """&body=Purchasing Selling Price Request with ID """ + str(PPHead.PP_Number) + """ %0DReject Message:" target="_blank" style="padding: 8px 12px; border: 1px solid #ED2939;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #ffffff;text-decoration: none;font-weight:bold;display: inline-block;">
                                                    REJECT
                                                </a>
                                            </td>
                                            <td>&nbsp;&nbsp;</td>
                                            <td style="border-radius: 2px;width: 150px;text-align: center;" bgcolor="#ebde34">
                                                <a href="mailto:online.approval@aski.component.astra.co.id?subject=Revise: """ + str(PPHead.PP_Number) + """&body=Need Revise Purchasing Price Request with ID """ + str(PPHead.PP_Number) + """ %0DRevision Message:" target="_blank" style="padding: 8px 12px; border: 1px solid #ebde34;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #000000;text-decoration: none;font-weight:bold;display: inline-block;">
                                                    REVISE
                                                </a>
                                            </td>
                                            <td>&nbsp;&nbsp;</td>
                                            <td style="border-radius: 2px;width: 150px;text-align: center;" bgcolor="#cccccc">
                                                <a href="mailto:""" + str(PPHead.Admin_Email) + """?subject=Ask User: """ + str(PPHead.PP_Number) + """&body=Ask User about Purchasing Price Request with ID """ + str(PPHead.PP_Number) + """ %0DAsk User Message: " target="_blank" style="padding: 8px 12px; border: 1px solid #cccccc;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #000000;text-decoration: none;font-weight:bold;display: inline-block;">
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
                'Purchasing Price Online Approval: ' + 
                NewPP_Number,
                body=email_body, from_email=settings.EMAIL_HOST_USER, 
                to=[PPHead.SPV_Email],
                )
                mailattach.content_subtype = "html"
                if 'Attachment1' in request.FILES:
                    mailattach.attach_file(
                        'Media/Uploads/' + str(request.FILES['Attachment1']).replace(' ', '_'))
                if 'Attachment2' in request.FILES:
                    mailattach.attach_file(
                        'Media/Uploads/' + str(request.FILES['Attachment2']).replace(' ', '_'))
                if 'Attachment3' in request.FILES:
                    mailattach.attach_file(
                        'Media/Uploads/' + str(request.FILES['Attachment3']).replace(' ', '_'))
                if 'Attachment4' in request.FILES:
                    mailattach.attach_file(
                        'Media/Uploads/' + str(request.FILES['Attachment4']).replace(' ', '_'))
                mailattach.send()

                email = models.Send(
                    htmlmessage=email_body,
                    mailfrom='online.approval@aski.component.astra.co.id',
                    mailto=PPHead.SPV_Email,
                    PP_Number=NewPP_Number,
                    mailheader='Purchasing Price Online Approval: ' + NewPP_Number)
                email.save()

                models.PurchasingPrice.objects.filter(PP_Number=NewPP_Number).update(Status="Created")
                models.PurchasingPrice.objects.filter(PP_Number=PP_Number).update(Status="Revised")
                return redirect("/PP/ListPP/")

            else:
                print(PPform.errors)
                return HttpResponse(PPform.errors)

    if request.method == 'GET':
        models.PP_Item.objects.filter(PP_Number = NewPP_Number).delete()
    PPItem = models.PP_Item.objects.filter(PP_Number=NewPP_Number)
    context={
        'Judul': 'Revise SAP Purchasing Price Approval Request',
        'PPForm' : PP,
        'PPItem' : PPItem,
        'PP_Number' : NewPP_Number,
        'OldPP_Number': PP_Number,
        'Note' : Note,
        'Data': data,
        'Revise_Request': Revise_Request
    }
    return render(request, 'purchasingprice/Revise.html',context)

@login_required
@user_passes_test(is_memberaddasset)
def listcheck(request):
    ListPP = models.PurchasingPrice.objects.filter(Status="FinanceCheck").order_by("-id")
    ListPPdone = models.PurchasingPrice.objects.filter(Status__isnull=False, Fin_Input_Status="Done Input").order_by("-id")

    context={
        'ListPP':ListPP,
        'ListPPdone':ListPPdone,
    }
    return render(request, 'purchasingprice/ListCheck.html',context)

@login_required
@user_passes_test(is_memberaddasset)
def check(request, PP_Number):
    PP = models.PurchasingPrice.objects.get(PP_Number=PP_Number)
    PPform = forms.PurchasingPrice(instance=PP)
    PPItem = models.PP_Item.objects.filter(PP_Number=PP_Number).order_by("-id")

    if request.method == "POST":
        models.activity_log(user = request.user.username, PP_Number=PP_Number, activity=request.POST).save()
        if 'revision' in request.POST:
            models.PurchasingPrice.objects.filter(PP_Number = PP_Number).update(Status = 'NeedRevise', Revise_Request = request.POST['revisemessage'])
            return listcheck(request)
        if 'upload' in request.POST:
            print(request.POST)
            PPform = forms.PurchasingPrice(request.POST, request.FILES, instance=PP)
            if PPform.is_valid():
                PPform.save()
            else:
                print(PPform.errors)
        if 'finish' in request.POST:
            print(request.POST)
            models.PurchasingPrice.objects.filter(PP_Number=PP_Number).update(Fin_Input_Status= 'Done Input', Fin_Input_Date= datetime.datetime.now())
            PP = models.PurchasingPrice.objects.get(PP_Number=PP_Number)
            PPItem = models.PP_Item.objects.filter(PP_Number=PP_Number).order_by("-id")
            contain = ''
            for item in PPItem:
                contain += '''<tr style="height: 30px; font-size:12px; border-collapse: collapse;">
                    <td style="border: 1px solid black; border-collapse: collapse;">''' + str(item.Vend_Code) + '''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">''' + str(item.Vend_Name) + '''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">''' + str(item.Material) + '''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">''' + str(item.Material_Desc) + '''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">''' + str(item.Qty) + '''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">''' + str(item.UoM) + '''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">''' + str(item.Currency) +' '+ str(item.Old_Price)+ '''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">''' + str(item.Old_Delivery) + '''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">''' + str(item.Currency) +' '+ str(item.New_Price)+ '''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">''' + str(item.New_Delivery) + '''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">''' + str(item.Ratio) + '''</td>

                </tr>'''
            email_body = """\
                    <html>
                    <head style="margin-bottom: 0px;">Dear Mr/Ms """ + PP.Dept_Fin.title() + """,</head>
                    <body>
                    <p style="margin-bottom: 0px;margin-top: 0px;">This Purchasing Price needs your approval </>
                    <hr>
                    <table style="font-size: x-small; width: 100%">
                        <tr>
                            <td rowspan="3" style="width: 15%;  text-align: center; border-bottom: 1px solid black;"><h1>ASKI</h1></td>
                            <td rowspan="3" style="text-align: center;  border-bottom: 1px solid black;">
                                <h3>PERUBAHAN/PERSETUJUAN HARGA PEMBELIAN</h3>
                            </td>
                            <td style="width: 10%;">No. Document</td>
                            <td style="text-align: center;">:</td>
                            <td style="text-align: center; width: 10%;">FR-PURC.01-006</td>
                        </tr>
                        <tr>
                            <td>Revision</td>
                            <td style="text-align: center;">:</td>
                            <td style="text-align: center;">0</td>
                        </tr>
                        <tr>
                            <td style="border-bottom: 1px solid black;">Effective Start</td>
                            <td style="text-align: center; border-bottom: 1px solid black;">:</td>
                            <td style="text-align: center; border-bottom: 1px solid black;">09-Jan-14</td>
                        </tr>
                    </table>
                    <br>
                    <table style="width: 100%; font-size: 12px;">
                        <tr>
                        <td style="width: 10%;white-space: nowrap;">Purchasing Price Number</td>
                        <td>:</td>
                        <td>""" + str(PP.PP_Number) + """</td>
                        </tr>
                        <tr>
                        <td style="width: 10%;white-space: nowrap;">Part Type</td>
                        <td>:</td>
                        <td>""" + str(PP.Type) + """</td>
                        </tr>
                        
                    </table>
                    <br>
                    <table style="width: 100%; border-collapse: collapse; font-size: 12px;text-align: center">
                    <thead>
                        <tr style="border: 1px solid">
                            <th  style="padding: 5px; border: 1px solid">Vendor Code</th>
                            <th  style="padding: 5px; border: 1px solid">Vendor Name</th>
                            <th  style="padding: 5px; border: 1px solid">Material No</th>
                            <th  style="padding: 5px; border: 1px solid">Material Description</th>
                            <th  style="padding: 5px; border: 1px solid">Qty</th>
                            <th  style="padding: 5px; border: 1px solid">UoM</th>
                            <th  style="padding: 5px; border: 1px solid">Old Price</th>
                            <th  style="padding: 5px; border: 1px solid">Old Delivery </th>
                            <th  style="padding: 5px; border: 1px solid">New Price</th>
                            <th  style="padding: 5px; border: 1px solid">New Delivery </th>
                            <th  style="padding: 5px; border: 1px solid">Ratio Variance </th>
                        </tr>
                    </thead>
                    <tbody >
                    """ + contain + """
                    </tbody>
                    </table>
                    <br>
                    <H6>Note :</H6>
                    """ + PP.Note + """
                    <br>
                
                    <table style="font-size: 12px;text-align: center;border: 1px solid black;border-collapse: collapse;" >
                        <tbody>
                            <tr style="height:10px;border: 1px solid black;border-collapse: collapse;">
                                <td style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 12,5%;text-align: center;vertical-align: bottom;">Created By</td>
                                    <td style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 12,5%;text-align: center;vertical-align: bottom;">Checked By</td>
                                    <td style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 12,5%;text-align: center;vertical-align: bottom;">Checked By</td>
                                    <td style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 12,5%;text-align: center;vertical-align: bottom;">Approved By</td>
                                    <td style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 12,5%;text-align: center;vertical-align: bottom;">Approved By</td>
                                    <td style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 12,5%;text-align: center;vertical-align: bottom;">Approved By</td>
                                    <td style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 12,5%;text-align: center;vertical-align: bottom;">Input By</td>
                                    <td style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 12,5%;text-align: center;vertical-align: bottom;">Confirm By</td>
                            </tr>
                            <tr style="height:40px;border: 1px solid black;border-collapse: collapse;">
                                <td style="border: 1px solid black;border-collapse: collapse;padding:20px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="Admin">Created """ + str(PP.Submit.strftime("%Y-%m-%d %H:%M:%S")) + """</td>
                                <td style="border: 1px solid black;border-collapse: collapse;padding:20px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="SPV">"""+str(PP.SPV_Approval_Status)+" "+str(PP.SPV_Approval_Date.strftime("%Y-%m-%d %H:%M:%S"))+"""</td>
                                <td style="border: 1px solid black;border-collapse: collapse;padding:20px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="DEPT">"""+str(PP.Dept_Head_Approval_Status)+" "+str(PP.Dept_Head_Approval_Date.strftime("%Y-%m-%d %H:%M:%S"))+"""</td>
                                <td style="border: 1px solid black;border-collapse: collapse;padding:20px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="MKT">"""+str(PP.Mkt_Head_Approval_Status)+" "+str(PP.Mkt_Head_Approval_Date.strftime("%Y-%m-%d %H:%M:%S"))+"""</td>
                                <td style="border: 1px solid black;border-collapse: collapse;padding:20px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="DIV">"""+str(PP.Div_Head_Approval_Status)+" "+str(PP.Div_Head_Approval_Date.strftime("%Y-%m-%d %H:%M:%S"))+"""</td>
                                <td style="border: 1px solid black;border-collapse: collapse;padding:20px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="PRESDIR">"""+str(PP.PresDirektur_Approval_Status)+" "+str(PP.PresDirektur_Approval_Date.strftime("%Y-%m-%d %H:%M:%S"))+"""</td>
                                <td style="border: 1px solid black;border-collapse: collapse;padding:20px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="FIN">"""+str(PP.Fin_Input_Status)+" "+str(PP.Fin_Input_Date.strftime("%Y-%m-%d %H:%M:%S"))+"""</td>
                                    <td style="border: 1px solid black;border-collapse: collapse;padding:20px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="FIN_DEPT"></td>
                            </tr>
                            <tr style="height:20px;border: 1px solid black;border-collapse: collapse;">
                            <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">""" + PP.Admin.title() + """</td>
                                <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">""" + PP.SPV.title() + """</td>
                                <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">""" + PP.Dept_Head.title() + """</td>
                                <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">""" + PP.Mkt_Head.title() + """</td>
                                <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">""" + PP.Div_Head.title() + """</td>
                                <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">""" + PP.PresDirektur.title() + """</td>
                                <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">""" + PP.Fin.title() + """</td>
                                <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">""" + PP.Dept_Fin.title() + """</td>
                            </tr>
                            <tr style="height:10px;border: 1px solid black;border-collapse: collapse;">
                                <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">Purchasing Admin</td>
                                <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">Purchasing SPV</td>
                                <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">Purchasing Dept Head</td>
                                <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">Marketing Dept Head</td>
                                <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">Administration Div Head</td>
                                <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">President Director</td>
                                <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">Finance SPV</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">Finance Dept Head</td>
                            </tr>
                        </tbody>
                    </table>
                    <br>
                    <hr>
                    <p> Please give your response by click approval button bellow and then click send button. A response at your earliest convenience would be much appreciated. </p>
                    <table width="100%" cellspacing="0" cellpadding="0" >
                        <tr>
                            <td>
                                <table cellspacing="0" cellpadding="0">
                                    <tr>
                                        <td style="border-radius: 2px;width : 150px;text-align: center;" bgcolor="#4bf542">
                                            <a href="mailto:online.approval@aski.component.astra.co.id?subject=Approve: """ + str(PP.PP_Number) + """&body=Purchasing Price Request with ID """ + str(PP.PP_Number) + """ %0DApproval Message:" target="_blank" style="padding: 8px 12px; border: 1px solid #4bf542;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #ffffff;text-decoration: none;font-weight:bold;display: inline-block;">
                                                APPROVE
                                            </a>
                                        </td>
                                        <td>&nbsp;&nbsp;</td>
                                        <td style="border-radius: 2px;width: 150px;text-align: center;" bgcolor="#ED2939">
                                            <a href="mailto:online.approval@aski.component.astra.co.id?subject=Reject: """ + str(PP.PP_Number) + """&body=Purchasing Selling Price Request with ID """ + str(PP.PP_Number) + """ %0DReject Message:" target="_blank" style="padding: 8px 12px; border: 1px solid #ED2939;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #ffffff;text-decoration: none;font-weight:bold;display: inline-block;">
                                                REJECT
                                            </a>
                                        </td>
                                        <td>&nbsp;&nbsp;</td>
                                        <td style="border-radius: 2px;width: 150px;text-align: center;" bgcolor="#ebde34">
                                            <a href="mailto:online.approval@aski.component.astra.co.id?subject=Revise: """ + str(PP.PP_Number) + """&body=Need Revise Purchasing Price Request with ID """ + str(PP.PP_Number) + """ %0DRevision Message:" target="_blank" style="padding: 8px 12px; border: 1px solid #ebde34;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #000000;text-decoration: none;font-weight:bold;display: inline-block;">
                                                REVISE
                                            </a>
                                        </td>
                                        <td>&nbsp;&nbsp;</td>
                                        <td style="border-radius: 2px;width: 150px;text-align: center;" bgcolor="#cccccc">
                                            <a href="mailto:""" + str(PP.Admin_Email) + """?subject=Ask User: """ + str(PP.PP_Number) + """&body=Ask User about Purchasing Price Request with ID """ + str(PP.PP_Number) + """ %0DAsk User Message: " target="_blank" style="padding: 8px 12px; border: 1px solid #cccccc;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #000000;text-decoration: none;font-weight:bold;display: inline-block;">
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
            'Purchasing Price Online Approval: ' + 
            PP_Number,
            body=email_body, from_email=settings.EMAIL_HOST_USER, 
            to=[PP.Dept_Fin_Email],
            )
            mailattach.content_subtype = "html"
            if len(str(PP.Attachment1))>1:
                mailattach.attach_file(
                    'Media/'+str(PP.Attachment1))
            if len(str(PP.Attachment2))>1:
                mailattach.attach_file(
                    'Media/'+str(PP.Attachment2))
            if len(str(PP.Attachment3))>1:
                mailattach.attach_file(
                    'Media/'+str(PP.Attachment3))
            if len(str(PP.Attachment4))>1:
                mailattach.attach_file(
                    'Media/'+str(PP.Attachment4))
            if len(str(PP.Input1))>1:
                mailattach.attach_file(
                    'Media/'+str(PP.Input1))
            if len(str(PP.Input2))>1:
                mailattach.attach_file(
                    'Media/'+str(PP.Input2))
            
            mailattach.send()

            email = models.Send(
                htmlmessage=email_body,
                mailfrom='online.approval@aski.component.astra.co.id',
                mailto=PP.Dept_Fin_Email,
                PP_Number=PP_Number,
                mailheader='Purchasing Price Online Approval: ' + PP_Number)
            email.save()
            models.PurchasingPrice.objects.filter(PP_Number=PP_Number).update(Status="Input")
            return redirect("/PP/ListCheck/")

    context={
        'PP_Number': PP_Number,
        'PP':PP,
        'PPform': PPform,
        'PPItem' : PPItem
    }
    return render(request, 'purchasingprice/Check.html',context)

def pdf(request,PP_Number):
    PPHead = models.PurchasingPrice.objects.get(PP_Number=PP_Number)
    PPItem = models.PP_Item.objects.filter(PP_Number=PP_Number)
    watermark = ""
    for x in range(100):
        watermark += PP_Number+" "
    watermark2 = '<div style="width:100%;text-align:center;">Digitally Signed</div><div style="width:100%;text-align:center;">'+PP_Number+'</div>'
    contain = ''
    contain2 = ''
    counter = 0
    for item in PPItem:
        counter += 1
        contain += '''<tr style="height: 30px; font-size:12px; border-collapse: collapse;">
            <td style="border: 1px solid black; border-collapse: collapse;">''' + str(item.Vend_Code) + '''</td>
            <td style="border: 1px solid black; border-collapse: collapse;">''' + str(item.Vend_Name) + '''</td>
            <td style="border: 1px solid black; border-collapse: collapse;">''' + str(item.Material) + '''</td>
            <td style="border: 1px solid black; border-collapse: collapse;">''' + str(item.Material_Desc) + '''</td>
            <td style="border: 1px solid black; border-collapse: collapse;">''' + str(item.Qty) + '''</td>
            <td style="border: 1px solid black; border-collapse: collapse;">''' + str(item.UoM) + '''</td>
            <td style="border: 1px solid black; border-collapse: collapse;">''' + str(item.Currency) +' '+ str(item.Old_Price)+ '''</td>
            <td style="border: 1px solid black; border-collapse: collapse;">''' + str(item.Old_Delivery) + '''</td>
            <td style="border: 1px solid black; border-collapse: collapse;">''' + str(item.Currency) +' '+ str(item.New_Price)+ '''</td>
            <td style="border: 1px solid black; border-collapse: collapse;">''' + str(item.New_Delivery) + '''</td>
            <td style="border: 1px solid black; border-collapse: collapse;">''' + str(item.Ratio) + '''</td>

        </tr>'''
        contain2 += '''<tr style="height: 30px; font-size:12px; border-collapse: collapse;">
            <td style="border: 1px solid black; border-collapse: collapse;">''' + str(counter) + '''</td>
            <td style="border: 1px solid black; border-collapse: collapse;">''' + str(item.Material_Desc) + '''</td>
            <td style="border: 1px solid black; border-collapse: collapse;">''' + str(item.Qty) + '''</td>
            <td style="border: 1px solid black; border-collapse: collapse;">''' + str(item.UoM) + '''</td>
            <td style="border: 1px solid black; border-collapse: collapse;">''' + str(item.Currency) +' '+ str(item.Old_Price)+ '''</td>
            <td style="border: 1px solid black; border-collapse: collapse;">''' + str(item.Old_Delivery) + '''</td>
            <td style="border: 1px solid black; border-collapse: collapse;">''' + str(item.Currency) +' '+ str(item.New_Price)+ '''</td>
            <td style="border: 1px solid black; border-collapse: collapse;">''' + str(item.New_Delivery) + '''</td>
        </tr>'''
        

    email_body = """
        <html>
        <head>
            <meta name="pdfkit-page-size" content="A4" />
            <meta name="pdfkit-orientation" content="Landscape" />
        </head>
        <body style="font-family:'Palatino Linotype'">
            <style>
                .table-header {
                    table-layout: auto;
                    border: 1px solid #dee2e6;
                    width: 100%;
                    font-size: small;
                    border-collapse: collapse;
                    align-items: center;
                }

                .table-header td {
                    white-space: nowrap;
                    margin-left: 8px;
                    margin-right: 8px;
                }

                .table-header tr td {
                    border: 1px solid #000000;
                    padding: 5px;
                }

                .table-approve {
                    border: 1px solid #000000;
                    border-collapse: collapse;
                    font-size: small;
                }

                .table-approve tr th,
                .table-approve tr td {
                    border: 1px solid #000000;
                }
            </style>
            <div id="watermark" style="min-height: 80vh;">
            <table class="table-header">
                <tr>
                    <td rowspan="3" style="width: 15%; ">
                        <img src="http://127.0.0.1:8000/static/image/ASKI.png"
                            style="width: 80%;margin-left: auto;margin-right: auto;display: block;" alt="GAMBARR">
                    </td>
                    <td rowspan="3" style="text-align: center; vertical-align: middle;">
                        <h2>PERUBAHAN/PERSETUJUAN HARGA PEMBELIAN</h2>
                    </td>
                    <td style="width: 10%;">No. Document</td>
                    <td style="text-align: center;">:</td>
                    <td style="text-align: center; width: 10%;">FR-PURC.01-006</td>
                </tr>
                <tr>
                    <td>Revision</td>
                    <td style="text-align: center;">:</td>
                    <td style="text-align: center;">0</td>
                </tr>
                <tr>
                    <td style="border-bottom: 1px solid black;">Effective Start</td>
                    <td style="text-align: center; border-bottom: 1px solid black;">:</td>
                    <td style="text-align: center; border-bottom: 1px solid black;">09-Jan-14</td>
                </tr>
            </table>
            <br>
            <table style="width: 100%; font-size: 12px;">
                <tr>
                <td style="width: 10%;white-space: nowrap;">Purchasing Price Number</td>
                <td>:</td>
                <td>""" + str(PPHead.PP_Number) + """</td>
                </tr>
                <tr>
                <td style="width: 10%;white-space: nowrap;">Part Type</td>
                <td>:</td>
                <td>""" + str(PPHead.Type) + """</td>
                </tr>
                
            </table>
            <br>
            <table style="width: 100%; border-collapse: collapse; font-size: 12px;text-align: center">
            <thead>
                <tr style="border: 1px solid">
                    <th  style="padding: 5px; border: 1px solid">Vendor Code</th>
                    <th  style="padding: 5px; border: 1px solid">Vendor Name</th>
                    <th  style="padding: 5px; border: 1px solid">Material No</th>
                    <th  style="padding: 5px; border: 1px solid">Material Description</th>
                    <th  style="padding: 5px; border: 1px solid">Qty</th>
                    <th  style="padding: 5px; border: 1px solid">UoM</th>
                    <th  style="padding: 5px; border: 1px solid">Old Price</th>
                    <th  style="padding: 5px; border: 1px solid">Old Delivery </th>
                    <th  style="padding: 5px; border: 1px solid">New Price</th>
                    <th  style="padding: 5px; border: 1px solid">New Delivery </th>
                    <th  style="padding: 5px; border: 1px solid">Ratio Variance </th>
                </tr>
            </thead>
            <tbody >
            """ + contain + """
            </tbody>
            </table>
            <H6>Note :</H6>
            """ + PPHead.Note + """
            <br>
        
            <table style="font-size: 12px;text-align: center;border: 1px solid black;border-collapse: collapse;" >
                <tbody>
                    <tr style="height:10px;border: 1px solid black;border-collapse: collapse;">
                        <td style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 12,5%;text-align: center;vertical-align: bottom;">Created By</td>
                        <td style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 12,5%;text-align: center;vertical-align: bottom;">Checked By</td>
                        <td style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 12,5%;text-align: center;vertical-align: bottom;">Checked By</td>
                        <td style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 12,5%;text-align: center;vertical-align: bottom;">Approved By</td>
                        <td style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 12,5%;text-align: center;vertical-align: bottom;">Approved By</td>
                        <td style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 12,5%;text-align: center;vertical-align: bottom;">Approved By</td>
                        <td style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 12,5%;text-align: center;vertical-align: bottom;">Iput By</td>
                        <td style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 12,5%;text-align: center;vertical-align: bottom;">Confirm By</td>
                    </tr>
                    <tr style="height:40px;border: 1px solid black;border-collapse: collapse;">
                        <td style="border: 1px solid black;border-collapse: collapse;padding:20px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="Admin">Created """ + str(PPHead.Submit.strftime("%Y-%m-%d %H:%M:%S")) + """</td>
                        <td style="border: 1px solid black;border-collapse: collapse;padding:20px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="SPV"><div>"""+PPHead.SPV_Approval_Status+"""</div><div>""" + str(PPHead.SPV_Approval_Date.strftime("%Y-%m-%d %H:%M:%S")) + """</div></td>
                        <td style="border: 1px solid black;border-collapse: collapse;padding:20px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="DEPT"><div>"""+PPHead.Dept_Head_Approval_Status+"""</div><div>""" + str(PPHead.Dept_Head_Approval_Date.strftime("%Y-%m-%d %H:%M:%S")) + """</div></td>
                        <td style="border: 1px solid black;border-collapse: collapse;padding:20px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="MKT"><div>"""+PPHead.Mkt_Head_Approval_Status+"""</div><div>""" + str(PPHead.Mkt_Head_Approval_Date.strftime("%Y-%m-%d %H:%M:%S")) + """</div></td>
                        <td style="border: 1px solid black;border-collapse: collapse;padding:20px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="DIV"><div>"""+PPHead.Div_Head_Approval_Status+"""</div><div>""" + str(PPHead.Div_Head_Approval_Date.strftime("%Y-%m-%d %H:%M:%S")) + """</div></td>
                        <td style="border: 1px solid black;border-collapse: collapse;padding:20px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="PRESDIR"><div>"""+PPHead.PresDirektur_Approval_Status+"""</div><div>""" + str(PPHead.PresDirektur_Approval_Date.strftime("%Y-%m-%d %H:%M:%S")) + """</div></td>
                        <td style="border: 1px solid black;border-collapse: collapse;padding:20px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="PRESDIR"><div>"""+PPHead.Fin_Input_Status+"""</div><div>""" + str(PPHead.Fin_Input_Date.strftime("%Y-%m-%d %H:%M:%S")) + """</div></td>
                        <td style="border: 1px solid black;border-collapse: collapse;padding:20px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="PRESDIR"><div>"""+PPHead.Dept_Fin_Confirm_Status+"""</div><div>""" + str(PPHead.Dept_Fin_Confirm_Date.strftime("%Y-%m-%d %H:%M:%S")) + """</div></td>
                    </tr>
                    <tr style="height:20px;border: 1px solid black;border-collapse: collapse;">
                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">""" + PPHead.Admin.title() + """</td>
                        <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">""" + PPHead.SPV.title() + """</td>
                        <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">""" + PPHead.Dept_Head.title() + """</td>
                        <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">""" + PPHead.Mkt_Head.title() + """</td>
                        <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">""" + PPHead.Div_Head.title() + """</td>
                        <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">""" + PPHead.PresDirektur.title() + """</td>
                        <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">""" + PPHead.Fin.title() + """</td>
                        <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">""" + PPHead.Dept_Fin.title() + """</td>
                    </tr>
                    <tr style="height:10px;border: 1px solid black;border-collapse: collapse;">
                        <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">Purchasing Admin</td>
                        <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">Purchasing SPV</td>
                        <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">Purchasing Dept Head</td>
                        <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">Marketing Dept Head</td>
                        <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">Administration Div Head</td>
                        <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">President Director</td>
                        <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">Finance SPV</td>
                        <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">Finance Dept Head</td>
                    </tr>
                </tbody>
            </table>
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
    pdfkit.from_string(email_body, "Media\Price\\"+PP_Number +".pdf", configuration=config)

    confirmation = """
        <html>
        <head>
            <meta name="pdfkit-page-size" content="A4" />
            <meta name="pdfkit-orientation" content="Portrait" />
        </head>
        <body style="font-family:'Palatino Linotype'">
            <style>
                .table-header {
                    table-layout: auto;
                    border: 1px solid #dee2e6;
                    width: 100%;
                    font-size: small;
                    border-collapse: collapse;
                    align-items: center;
                }

                .table-header td {
                    white-space: nowrap;
                    margin-left: 8px;
                    margin-right: 8px;
                }

                .table-header tr td {
                    border: 1px solid #000000;
                    padding: 5px;
                }

                .table-approve {
                    border: 1px solid #000000;
                    border-collapse: collapse;
                    font-size: small;
                }

                .table-approve tr th,
                .table-approve tr td {
                    border: 1px solid #000000;
                }
            </style>
            <div id="watermark" style="min-height: 80vh;">
            <table>
                <tr>
                    <td rowspan="3" style="width: 15%; ">
                        <img src="http://127.0.0.1:8000/static/image/ASKI.png"
                            style="width: 100%;margin-left: auto;margin-right: auto;display: block;" alt="GAMBARR">
                    </td>
                    <td rowspan="3" style=" vertical-align: bottom;padding: 20px;">
                    
                        <h2 style="margin-top: 15px;">PT ASTRA KOMPONEN INDONESIA</h2>
                    </td>
                   
                </tr>

            </table>
            <br>
                        <table width ="100%">
                <tr>
                    <td width = "5%">No</td>  
                    <td width = "2%">:</td>
                    <td width = "43%">"""+PP_Number+"""</td>
                    <td width = "15%"></td>
                    <td width = "15%"></td>
                    <td width = "15%"> Bogor, """+str(PPHead.PresDirektur_Approval_Date.strftime("%d %b %Y"))+"""</td>
                </tr>
                <tr>
                    <td>Hal</td>
                    <td>:</td>
                    <td>Confirmation For Part / Material Price Change</td>
                </tr>
                <tr><td><br></td></tr>
                <tr>
                    <td>Messrs</td>
                </tr>
                <tr>
                    <td colspan="3">"""+PPHead.Vendor+"""</td>
                </tr>
                <tr>
                    <td colspan="3"> Att. """+PPHead.Attn1+"""</td>
                </tr>
                """ + ("" if PPHead.Attn2==None else """
                <tr>
                    <td colspan="3">Att."""+PPHead.Attn2+"""</td>
                </tr>
                """ ) + """
                <tr><td><br></td></tr>
                <tr>
                    <td colspan="6">
                        <div>Dear Sir / Madam,</div>
                        <div style="display: flex; ">Regarding quotation on """+PPHead.QuotDate+""", herewith we confirm you for Part / Material as below:</div>
                    </td>
                </tr>
                <tr><td></td></tr>
                <tr>
                    <td colspan="6">
                        <style>
                            #Item tr td{
                                border: 1px solid black;
                                border-collapse: collapse;
                                padding-left: 8px;
                                padding-right: 8px;
                            }
                        </style>
                        <table class="table-header" style="text-align: center;">
                            <tr >
                                <td rowspan="2">No</td>
                                <td rowspan="2">Material Description</td>
                                <td rowspan="2">Per</td>
                                <td rowspan="2">UoM</td>
                                <td colspan="2">Old Price</td>
                                <td colspan="2">New Price</td>
                            </tr>
                            <tr>
                                <td>Price</td>
                                <td>Delivery</td>
                                <td>Price</td>
                                <td>Delivery</td>
                            </tr>
                            """+contain2+"""
                        </table>
                    </td>
                </tr>
                <tr><td><br></td></tr>
                <tr><td colspan="6">Term & Condition :</td></tr>
                <tr>
                    <td colspan="6">
                    <div>
                        """+PPHead.ConfNote.replace('\n','</div><div>')+"""
                    </div>
                    </td>
                </tr>
                <tr><td>
                <br>
                <br>
                <br>
                </td></tr>
                <tr><td colspan="6">
                Thank You
                </td></tr>
                <tr><td colspan="6">
                <table style="width:100%;"> 
                <tr>
                   <td>Yours Faithfully,</td><td style="width:50%;"></td><td></td><td></td><td></td><td></td><td></td><td></td><td>Vendor Confirmation</td>
                </tr>
                  <tr style="height: 100px;font-size: 12px;color: #1A5F7A;">
                   <td><i><Div>Digitally Signed</Div><div>"""+str(PPHead.PresDirektur_Approval_Date.strftime("%Y-%m-%d %H:%M:%S"))+"""</div></i></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td>
                </tr>
                  <tr>
                   <td>"""+PPHead.PresDirektur+"""</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td>Name_________________</td>
                </tr>
                  <tr>
                   <td>President Director</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td>Title___________________</td>
                </tr>
                </table> 


                </td></tr>
                <tr><td><br></td></tr>
                <tr>
                <td colspan="6">
                <i>Please send back this Confirmation letter. If in three days, we aren't received your feedback, we assumed you're accepted it.</i>
                </td>
                </tr>


            </table>

            
            
            



        <br>
            <h4>"""+watermark2+"""</h4>
        </div>
        <style>
            #watermark {
            position: relative;
            overflow: hidden;
            }

            #watermark h4 {
                position: absolute;
                top: 30%;
                left: 30%;
                display: block;
                width: 100%;
                height: 100%;
                z-index:-1;
                color: #ffffcc;
                opacity: 1;
                line-height: 1.5 em;
                letter-spacing: 2px;
                font-size: 60px;
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

    

    pdfkit.from_string(confirmation, "Media\Price\\Confirmation Letter "+PP_Number +".pdf", configuration=config)

    models.PurchasingPrice.objects.filter(PP_Number=PP_Number).update(Status="Finished")




    return HttpResponse('it works!')
