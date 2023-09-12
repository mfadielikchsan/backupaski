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

# Create your views here.
def is_memberaddasset(user):
    return user.groups.filter(name='Allow_Add_Asset').exists()

def is_membercreatesp(user):
    return user.groups.filter(name='Allow_Create_SP').exists()

def is_memberseeprice(user):
    return user.groups.filter(Q(name='Allow_Add_Asset') | Q(name='Allow_Create_SP')).exists()

def is_admin(user):
    return user.groups.filter(name='Admin').exists()


class datacreate(APIView):
    def post(self, request, format=None):
        print(request.POST)
        SPItem =forms.PriceItem(request.POST)
        if SPItem.is_valid():
            SPItem.save()
        else :
            print(SPItem.errors)

        datatable = {
           'Data' : 'Test'
        }
        return Response(datatable)

# CREATE SP
@login_required
@user_passes_test(is_membercreatesp)
def create(request):
    if request.method == "GET":
        Mode = 'Item'
    if request.method == "POST":
        print(request.POST)
        if 'Finish' in request.POST :
           
            Mode = 'Finish' 
            if models.SellingPrice.objects.filter(SP_Number=request.POST['SP_Number']).exists():
                SP = forms.SellingPrice(request.POST, request.FILES,instance=models.SellingPrice.objects.get(SP_Number=request.POST['SP_Number']))
            else:
                SP = forms.SellingPrice(request.POST, request.FILES)
            SP.fields['User_Submit'].initial = datetime.datetime.now()
            if SP.is_valid():
                SP.save()
            else:
                print(SP.errors)
            approval = models.Approval.objects.get(User=request.user.username)
            SPItem = models.PriceItem.objects.filter(SP_Number=request.POST['SP_Number'])
            ListItem = list(models.PriceItem.objects.filter(SP_Number=request.POST['SP_Number']).order_by('No'))
            SPItem = forms.PriceItem()
            sellingPrice = models.SellingPrice.objects.get(SP_Number=request.POST['SP_Number'])
            counter = 0
            contain = ''
            for item in ListItem:
                counter += 1
                contain += '''<tr style="height: 30px; font-size:12px; border-collapse: collapse;">
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.Type)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.Material_No)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.Material_Description)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.Customer_Material)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.Old_Price)+''',-</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.Old_Depreciation)+''',-</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.Old_Total)+''',-</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.Old_UoM)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.Old_Valid_From)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.New_Price)+''',-</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.New_Depreciation)+''',-</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.New_Total)+''',-</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.New_UoM)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.New_Valid_From)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.Ratio_Variance)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.Note)+'''</td>
                </tr>'''
            if approval.Dept_Head == None:
                apptable = """
                        <table style="font-size: 12px;text-align: center;border: 1px solid black;border-collapse: collapse;" >
                            <tbody>
                                <tr style="height:10px;border: 1px solid black;border-collapse: collapse;">
                                    <td style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Created By</td>
                                    <td style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Checked By</td>
                                    <td colspan="2" style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 460px;text-align: center;vertical-align: bottom;">Approved By</td>
                                    <td style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">SAP Input By</td>
                                    <td style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Confirmed By</td>
                                </tr>
                                <tr style="height:40px;border: 1px solid black;border-collapse: collapse;">
                                    <td style="border: 1px solid black;border-collapse: collapse;padding:20px;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="User">Created """ + str(sellingPrice.User_Submit.strftime("%Y-%m-%d %H:%M:%S")) + """</td>
                                    <td style="border: 1px solid black;border-collapse: collapse;padding:20px;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="SPV"></td>
                                    <td style="border: 1px solid black;border-collapse: collapse;padding:20px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="DIV"></td>
                                    <td style="border: 1px solid black;border-collapse: collapse;padding:20px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="PRDIR"></td>
                                    <td style="border: 1px solid black;border-collapse: collapse;padding:20px;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="ACC"></td>
                                    <td style="border: 1px solid black;border-collapse: collapse;padding:20px;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="DEPTACC"></td>
                                </tr>
                                <tr style="height:20px;border: 1px solid black;border-collapse: collapse;">
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">""" + approval.User_Name.title() + """</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">""" + approval.SPV.title() + """</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">""" + approval.Div_Head.title() + """</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">""" + approval.PresDirektur.title() + """</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">""" + approval.Acc.title() + """</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">""" + approval.Dept_Acc.title() + """</td>
                                </tr>
                                <tr style="height:10px;border: 1px solid black;border-collapse: collapse;">
                                <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Marketing Admin</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Marketing SPV</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Bussiness Dev Div Head</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">President Director</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Finance SPV</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Finance Dept Head</td>
                                </tr>
                            </tbody>
                        </table>
                        """
            else :
                apptable = """
                        <table style="font-size: 12px;text-align: center;border: 1px solid black;border-collapse: collapse;" >
                            <tbody>
                                <tr style="height:10px;border: 1px solid black;border-collapse: collapse;">
                                    <td style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Created By</td>
                                    <td style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Checked By</td>
                                    <td style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Checked By</td>
                                    <td colspan="2" style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 460px;text-align: center;vertical-align: bottom;">Approved By</td>
                                    <td style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">SAP Input By</td>
                                    <td style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Confirmed By</td>
                                </tr>
                                <tr style="height:40px;border: 1px solid black;border-collapse: collapse;">
                                    <td style="border: 1px solid black;border-collapse: collapse;padding:20px;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="User">Created """ + str(sellingPrice.User_Submit.strftime("%Y-%m-%d %H:%M:%S")) + """</td>
                                    <td style="border: 1px solid black;border-collapse: collapse;padding:20px;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="SPV"></td>
                                    <td style="border: 1px solid black;border-collapse: collapse;padding:20px;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="DEPT"></td>
                                    <td style="border: 1px solid black;border-collapse: collapse;padding:20px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="DIV"></td>
                                    <td style="border: 1px solid black;border-collapse: collapse;padding:20px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="PRDIR"></td>
                                    <td style="border: 1px solid black;border-collapse: collapse;padding:20px;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="ACC"></td>
                                    <td style="border: 1px solid black;border-collapse: collapse;padding:20px;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="DEPTACC"></td>
                                </tr>
                                <tr style="height:20px;border: 1px solid black;border-collapse: collapse;">
                                <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">""" + approval.User_Name.title() + """</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">""" + approval.SPV.title() + """</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">""" + approval.Dept_Head.title() + """</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">""" + approval.Div_Head.title() + """</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">""" + approval.PresDirektur.title() + """</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">""" + approval.Acc.title() + """</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">""" + approval.Dept_Acc.title() + """</td>
                                </tr>
                                <tr style="height:10px;border: 1px solid black;border-collapse: collapse;">
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Marketing Admin</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Marketing SPV</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Marketing Dept Head</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Bussiness Dev Div Head</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">President Director</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Finance SPV</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Finance Dept Head</td>
                                </tr>
                            </tbody>
                        </table>
                        """
            Superior = approval.SPV.title()
            email_body = """\
                <html>
                <head style="margin-bottom: 0px;">Dear Mr/Ms """ + Superior  + """,</head>
                <body>
                <p style="margin-bottom: 0px;margin-top: 0px;">This Selling Price needs your approval </>
                <hr>
                <table style="font-size: x-small; width: 100%">
                    <tr>
                        <td rowspan="3" style="width: 15%;  text-align: center; border-bottom: 1px solid black;"><h1>ASKI</h1></td>
                        <td rowspan="3" style="text-align: center;  border-bottom: 1px solid black;">
                            <h3>PEMBUATAN HARGA PENJUALAN di SAP</h3>
                        </td>
                        <td style="width: 10%;">No. Document</td>
                        <td style="text-align: center;">:</td>
                        <td style="text-align: center; width: 10%;">FR-FACT.02.001</td>
                    </tr>
                    <tr>
                        <td>Revision</td>
                        <td style="text-align: center;">:</td>
                        <td style="text-align: center;">0</td>
                    </tr>
                    <tr>
                        <td style="border-bottom: 1px solid black;">Effective Start</td>
                        <td style="text-align: center; border-bottom: 1px solid black;">:</td>
                        <td style="text-align: center; border-bottom: 1px solid black;">25 Agustus 2022</td>
                    </tr>
                </table>
                <br> 
                <table style="width: 100%; font-size: 12px;">
                    <tr>
                    <td style="width: 10%;white-space: nowrap;">Cust Code</td>
                    <td>:</td>
                    <td>"""+str(sellingPrice.Cust_Code)+"""</td>
                    </tr>
                    <tr>
                    <td style="width: 10%;white-space: nowrap;">Cust Name</td>
                    <td>:</td>
                    <td>"""+str(sellingPrice.Cust_Name)+"""</td>
                    </tr>
                    <tr>
                    <td style="width: 10%;white-space: nowrap;">Dist Channel</td>
                    <td>:</td>
                    <td>"""+str(sellingPrice.Dist_Channel)+"""</td>
                    </tr>
                    <tr>
                    <td style="width: 10%;white-space: nowrap;">Submit Date</td>
                    <td>:</td>
                    <td>"""+str(sellingPrice.Submit_Date.strftime("%Y-%m-%d"))+"""</td>
                    </tr>
                    <tr>
                    <td style="width: 10%;white-space: nowrap;">No</td>
                    <td>:</td>
                    <td>"""+str(sellingPrice.SP_Number)+"""</td>
                    </tr>
                    <tr>
                    <td style="width: 10%;white-space: nowrap;">Product Status</td>
                    <td>:</td>
                    <td>"""+str(sellingPrice.Product_Status)+"""</td>
                    </tr>
                </table>

                <br>
                <table style="width: 100%; border-collapse: collapse; font-size: 12px;text-align: center">
                <thead>
                    <tr style=" height: 50px; word-break: normal; border: 1px solid">
                        <th rowspan="2" style="vertical-align: middle; border: 1px solid ">Type</th>
                        <th rowspan="2" style="vertical-align: middle; border: 1px solid">Material No</th>
                        <th rowspan="2" style="vertical-align: middle; border: 1px solid">Material Description</th>
                        <th rowspan="2" style="vertical-align: middle; border: 1px solid">Customer Material</th>
                        <th colspan="5" style="border: 1px solid">Old Price</th>
                        <th colspan="5" style="border: 1px solid">New Price</th>
                        <th rowspan="2" style="vertical-align: middle; border: 1px solid">Ratio</th>
                        <th rowspan="2" style="vertical-align: middle; border: 1px solid">Note</th>
                    </tr>
                    <tr style="border: 1px solid">
                        <th style="padding: 5px; border: 1px solid">Price</th>
                        <th style="padding: 5px; border: 1px solid">Depreciation</th>
                        <th style="padding: 5px; border: 1px solid">Total</th>
                        <th style="padding: 5px; border: 1px solid">UoM</th>
                        <th style="padding: 5px; border: 1px solid">Valid From</th>
                        <th style="padding: 5px; border: 1px solid">Price</th>
                        <th style="padding: 5px; border: 1px solid">Depreciation</th>
                        <th style="padding: 5px; border: 1px solid">Total</th>
                        <th style="padding: 5px; border: 1px solid">UoM</th>
                        <th style="padding: 5px; border: 1px solid">Valid From</th>
                    </tr>
                </thead>
                <tbody>
                """+contain+"""
                </tbody>
                </table>
                <br>
                
                        """+apptable+"""
                
                <br>
                <hr>
                <p> Please give your response by click approval button bellow and then click send button. A response at your earliest convenience would be much appreciated. </p>
                <table width="100%" cellspacing="0" cellpadding="0">
                    <tr>
                        <td>
                            <table cellspacing="0" cellpadding="0">
                                <tr>
                                    <td style="border-radius: 2px;width : 150px;text-align: center;" bgcolor="#4bf542">
                                        <a href="mailto:online.approval@aski.component.astra.co.id?subject=Approve: """+str(sellingPrice.SP_Number)+"""&body=Selling Price Request with ID """+str(sellingPrice.SP_Number)+""" %0DApproval Message:" target="_blank" style="padding: 8px 12px; border: 1px solid #4bf542;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #ffffff;text-decoration: none;font-weight:bold;display: inline-block;">
                                            APPROVE             
                                        </a>
                                    </td>
                                    <td>&nbsp;&nbsp;</td>
                                    <td style="border-radius: 2px;width: 150px;text-align: center;" bgcolor="#ED2939">
                                        <a href="mailto:online.approval@aski.component.astra.co.id?subject=Reject: """+str(sellingPrice.SP_Number)+"""&body=Reject Selling Price Request with ID """+str(sellingPrice.SP_Number)+""" %0DReject Message:" target="_blank" style="padding: 8px 12px; border: 1px solid #ED2939;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #ffffff;text-decoration: none;font-weight:bold;display: inline-block;">
                                            REJECT             
                                        </a>
                                    </td>
                                    <td>&nbsp;&nbsp;</td>
                                    <td style="border-radius: 2px;width: 150px;text-align: center;" bgcolor="#ebde34">
                                        <a href="mailto:online.approval@aski.component.astra.co.id?subject=Revise: """+str(sellingPrice.SP_Number)+"""&body=Need Revise Selling Price Request with ID """+str(sellingPrice.SP_Number)+""" %0DRevision Message:" target="_blank" style="padding: 8px 12px; border: 1px solid #ebde34;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #000000;text-decoration: none;font-weight:bold;display: inline-block;">
                                            REVISE             
                                        </a>
                                    </td>
                                    <td>&nbsp;&nbsp;</td>
                                    <td style="border-radius: 2px;width: 150px;text-align: center;" bgcolor="#cccccc">
                                        <a href="mailto:"""+str(sellingPrice.SPV_Email)+"""?subject=Ask User: """+str(sellingPrice.SP_Number)+"""&body=Ask User about Selling Price Request with ID """+str(sellingPrice.SP_Number)+""" %0DAsk User Message: " target="_blank" style="padding: 8px 12px; border: 1px solid #cccccc;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #000000;text-decoration: none;font-weight:bold;display: inline-block;">
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
            Superior_Email = approval.SPV_Email
            mailattach = EmailMessage(
                'Selling Price Online Approval: ' + 
                request.POST['SP_Number'],
                body=email_body, from_email=settings.EMAIL_HOST_USER, 
                to=[Superior_Email],
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

            email = models.Send(
                htmlmessage=email_body,
                mailfrom='online.approval@aski.component.astra.co.id',
                mailto=Superior_Email,
                SP_Number=request.POST['SP_Number'],
                mailheader='Selling Price Online Approval: ' + request.POST['SP_Number'])
            email.save()

            models.SellingPrice.objects.filter(SP_Number=request.POST['SP_Number']).update(Status="Created")

            return redirect("/SP/ListSP/")

        elif 'Back' in request.POST:
            Mode = 'Item'
        elif 'Next' in request.POST:
            Mode ='Header'
        elif 'Delete' in request.POST:
            Mode = 'Item'
            models.PriceItem.objects.filter(id = request.POST['Delete']).delete()
        else:
            Mode = 'Item'
            SPItem = forms.PriceItem(request.POST)
            if SPItem.is_valid():
                SPItem.save()
            else :
                print(SPItem.errors)
    SP = forms.SellingPrice()
    SP.fields['User_Submit'].initial = datetime.datetime.now()
    SPItem =forms.PriceItem()
    SPItem.fields['Old_Depreciation'].initial = SPItem.fields['New_Depreciation'].initial = '0'
    SP.fields['SP_Number'].initial = SPItem.fields['SP_Number'].initial = 'ASKISELLINGPRICE' + request.user.username + str(models.SellingPrice.objects.filter(
    SP_Number__contains="SELLINGPRICE" + request.user.username, Status__isnull=False).exclude(SP_Number__contains='rev').count()+1).zfill(5)
    
    SPItem.fields['No'].initial = models.PriceItem.objects.filter( SP_Number = SPItem.fields['SP_Number'].initial).count() + 1
    
    approval = list(models.Approval.objects.filter(User=request.user.username))
    ListItem = models.PriceItem.objects.filter( SP_Number = SPItem.fields['SP_Number'].initial).order_by('No')

    data = serializers.serialize( "json", models.Approval.objects.filter(User = request.user))

    context={
        'Mode': Mode,
        'SPForm' : SP,
        'SPItemForm' : SPItem,
        'ListItem' : ListItem,
        'Judul' : 'Create SAP Selling Price Approval Request',
        'Data': data,
        'Approval': approval,
    }
    return render(request, 'sellingprice/Create.html',context)

# Create SP from CSV
@login_required
@user_passes_test(is_membercreatesp)
def createSP(request):
    ListItem = []
    SP_Number = 'ASKISELLINGPRICE' + request.user.username + str(models.SellingPrice.objects.filter(SP_Number__contains="SELLINGPRICE" + request.user.username, Status__isnull=False).exclude(
            SP_Number__contains='rev').count() + 1).zfill(5)
    
    SP = forms.SellingPrice()
    SP.fields['User_Submit'].initial = datetime.datetime.now()
    SPItem = forms.PriceItem()
    SP.fields['SP_Number'].initial = SP_Number
    approval = list(models.Approval.objects.filter(User=request.user.username))
    data = serializers.serialize("json", models.Approval.objects.filter(User=request.user))

    if request.method == 'POST':
        if 'SP_Item' in request.FILES:
            item = pd.read_excel(request.FILES['SP_Item'], skiprows=5)
            ListItem = item.values.tolist()
            print(ListItem)
            header = pd.read_excel(request.FILES['SP_Item'], skiprows=2)
            print(header.loc[header.index[0]])
            cust_code = header._get_value(0, 'Cust_No')
            print(cust_code)
            cust_name = header._get_value(0, 'Cust_Name')
            print(cust_name)
            dist_channel = header._get_value(0, 'Dist_Channel')
            print(dist_channel)
            product_status = header._get_value(0, 'Product_Status')
            print(product_status)
            SP.fields['Cust_Name'].initial = cust_name
            SP.fields['Cust_Code'].initial = cust_code
            SP.fields['Dist_Channel'].initial = dist_channel
            SP.fields['Product_Status'].initial = product_status
        if 'upload' in request.POST:
            print(request.POST)
            item = pd.read_excel(request.FILES['SP_Item'], skiprows=5)
            item['Price_Old'] = (item['Price_Old'].map('{:,.0f}'.format))
            item['Depresiasi_Old'] = item['Depresiasi_Old'].fillna(0).map('{:,.0f}'.format)
            item['UoM_Old'] = item['UoM_Old'].fillna('-')
            item['Total_Old'] = (item['Total_Old'].map('{:,.0f}'.format))
            item['Valid From_Old'] = item['Valid From_Old'].replace({pd.NaT: '-'}).str.replace('-', '.')
            item['Price_New'] = (item['Price_New'].map('{:,.0f}'.format))
            item['Depresiasi_New'] = item['Depresiasi_New'].fillna(0).map('{:,.0f}'.format)
            item['Total_New'] = (item['Total_New'].map('{:,.0f}'.format))
            item['Valid From_New'] = item['Valid From_New'].replace({pd.NaT: '-'}).str.replace('-', '.')
            item['Ratio Variance'] = item['Ratio Variance'].transform(lambda x: '{:,.2%}'.format(x)).str.replace('nan%', '-').str.replace('.', ',')
            item['Note'] = item['Note'].fillna('-')
            new_item = item.dropna(axis = 0, subset=['TYPE'])
            print(new_item)
            ListItem = new_item.values.tolist()
            print(ListItem)
            if (models.PriceItem.objects.filter(SP_Number = SP_Number).exists()):
                models.PriceItem.objects.filter(SP_Number = SP_Number).delete()
                for row in ListItem:
                    item = models.PriceItem(
                        SP_Number=SP_Number,
                        No= models.PriceItem.objects.filter(SP_Number=SP_Number).count() + 1,
                        Type=row[0],
                        Material_No=row[1],
                        Material_Description=row[2],
                        Customer_Material=row[3],
                        Old_Price=row[4],
                        Old_Depreciation=row[5],
                        Old_Total=row[6],
                        Old_UoM=row[7],
                        Old_Valid_From=row[8],
                        New_Price=row[9],
                        New_Depreciation=row[10],
                        New_Total=row[11],
                        New_UoM=row[12],
                        New_Valid_From=row[13],
                        Ratio_Variance=row[14],
                        Note=row[15]
                    )
                    item.save()
            else:
                for row in ListItem:
                    item = models.PriceItem(
                        SP_Number=SP_Number,
                        No= models.PriceItem.objects.filter(SP_Number=SP_Number).count() + 1,
                        Type=row[0],
                        Material_No=row[1],
                        Material_Description=row[2],
                        Customer_Material=row[3],
                        Old_Price=row[4],
                        Old_Depreciation=row[5],
                        Old_Total=row[6],
                        Old_UoM=row[7],
                        Old_Valid_From=row[8],
                        New_Price=row[9],
                        New_Depreciation=row[10],
                        New_Total=row[11],
                        New_UoM=row[12],
                        New_Valid_From=row[13],
                        Ratio_Variance=row[14],
                        Note=row[15]
                    )
                    item.save()
        if 'Finish' in request.POST and request.POST['Cust_Name'] != '':
            print(request.POST)
            if (models.SellingPrice.objects.filter(SP_Number = SP_Number).exists()):
                SPform = forms.SellingPrice(request.POST, request.FILES, instance=models.SellingPrice.objects.get(SP_Number=SP_Number))
            else:
                SPform = forms.SellingPrice(request.POST, request.FILES)
            if SPform.is_valid():
                SPform.save()
            else:
                print(SPform.errors)
            approval = models.Approval.objects.get(User=request.user.username)
            ListItem = list(models.PriceItem.objects.filter(SP_Number=request.POST['SP_Number']).order_by('No'))
            SP = models.SellingPrice.objects.get(SP_Number=request.POST['SP_Number'])
            counter = 0
            contain = ''
            for item in ListItem:
                counter += 1
                contain += '''<tr style="height: 30px; font-size:12px; border-collapse: collapse;">
                                <td style="border: 1px solid black; border-collapse: collapse;">''' + str(item.Type) + '''</td>
                                <td style="border: 1px solid black; border-collapse: collapse;">''' + str(item.Material_No) + '''</td>
                                <td style="border: 1px solid black; border-collapse: collapse;">''' + str(item.Material_Description) + '''</td>
                                <td style="border: 1px solid black; border-collapse: collapse;">''' + str(item.Customer_Material) + '''</td>
                                <td style="border: 1px solid black; border-collapse: collapse;">''' + str(item.Old_Price) + ''',-</td>
                                <td style="border: 1px solid black; border-collapse: collapse;">''' + str(item.Old_Depreciation) + ''',-</td>
                                <td style="border: 1px solid black; border-collapse: collapse;">''' + str(item.Old_Total) + ''',-</td>
                                <td style="border: 1px solid black; border-collapse: collapse;">''' + str(item.Old_UoM) + '''</td>
                                <td style="border: 1px solid black; border-collapse: collapse;">''' + str(item.Old_Valid_From) + '''</td>
                                <td style="border: 1px solid black; border-collapse: collapse;">''' + str(item.New_Price) + ''',-</td>
                                <td style="border: 1px solid black; border-collapse: collapse;">''' + str(item.New_Depreciation) + ''',-</td>
                                <td style="border: 1px solid black; border-collapse: collapse;">''' + str(item.New_Total) + ''',-</td>
                                <td style="border: 1px solid black; border-collapse: collapse;">''' + str(item.New_UoM) + '''</td>
                                <td style="border: 1px solid black; border-collapse: collapse;">''' + str(item.New_Valid_From) + '''</td>
                                <td style="border: 1px solid black; border-collapse: collapse;">''' + str(item.Ratio_Variance) + '''</td>
                                <td style="border: 1px solid black; border-collapse: collapse;">''' + str(item.Note) + '''</td>
                            </tr>'''
            if approval.Dept_Head == None:
                apptable = """
                        <table style="font-size: 12px;text-align: center;border: 1px solid black;border-collapse: collapse;" >
                            <tbody>
                                <tr style="height:10px;border: 1px solid black;border-collapse: collapse;">
                                    <td style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Created By</td>
                                    <td style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Checked By</td>
                                    <td colspan="2" style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 460px;text-align: center;vertical-align: bottom;">Approved By</td>
                                    <td style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">SAP Input By</td>
                                    <td style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Confirmed By</td>
                                </tr>
                                <tr style="height:40px;border: 1px solid black;border-collapse: collapse;">
                                    <td style="border: 1px solid black;border-collapse: collapse;padding:20px;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="User">Created """ + str(SP.User_Submit.strftime("%Y-%m-%d %H:%M:%S")) + """</td>
                                    <td style="border: 1px solid black;border-collapse: collapse;padding:20px;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="SPV"></td>
                                    <td style="border: 1px solid black;border-collapse: collapse;padding:20px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="DIV"></td>
                                    <td style="border: 1px solid black;border-collapse: collapse;padding:20px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="PRDIR"></td>
                                    <td style="border: 1px solid black;border-collapse: collapse;padding:20px;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="ACC"></td>
                                    <td style="border: 1px solid black;border-collapse: collapse;padding:20px;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="DEPTACC"></td>
                                </tr>
                                <tr style="height:20px;border: 1px solid black;border-collapse: collapse;">
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">""" + approval.User_Name.title() + """</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">""" + approval.SPV.title() + """</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">""" + approval.Div_Head.title() + """</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">""" + approval.PresDirektur.title() + """</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">""" + approval.Acc.title() + """</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">""" + approval.Dept_Acc.title() + """</td>
                                </tr>
                                <tr style="height:10px;border: 1px solid black;border-collapse: collapse;">
                                <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Marketing Admin</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Marketing SPV</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Bussiness Dev Div Head</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">President Director</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Finance SPV</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Finance Dept Head</td>
                                </tr>
                            </tbody>
                        </table>
                        """
            else :
                apptable = """
                        <table style="font-size: 12px;text-align: center;border: 1px solid black;border-collapse: collapse;" >
                            <tbody>
                                <tr style="height:10px;border: 1px solid black;border-collapse: collapse;">
                                    <td style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Created By</td>
                                    <td style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Checked By</td>
                                    <td style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Checked By</td>
                                    <td colspan="2" style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 460px;text-align: center;vertical-align: bottom;">Approved By</td>
                                    <td style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">SAP Input By</td>
                                    <td style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Confirmed By</td>
                                </tr>
                                <tr style="height:40px;border: 1px solid black;border-collapse: collapse;">
                                    <td style="border: 1px solid black;border-collapse: collapse;padding:20px;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="User">Created """ + str(SP.User_Submit.strftime("%Y-%m-%d %H:%M:%S")) + """</td>
                                    <td style="border: 1px solid black;border-collapse: collapse;padding:20px;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="SPV"></td>
                                    <td style="border: 1px solid black;border-collapse: collapse;padding:20px;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="DEPT"></td>
                                    <td style="border: 1px solid black;border-collapse: collapse;padding:20px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="DIV"></td>
                                    <td style="border: 1px solid black;border-collapse: collapse;padding:20px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="PRDIR"></td>
                                    <td style="border: 1px solid black;border-collapse: collapse;padding:20px;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="ACC"></td>
                                    <td style="border: 1px solid black;border-collapse: collapse;padding:20px;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="DEPTACC"></td>
                                </tr>
                                <tr style="height:20px;border: 1px solid black;border-collapse: collapse;">
                                <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">""" + approval.User_Name.title() + """</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">""" + approval.SPV.title() + """</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">""" + approval.Dept_Head.title() + """</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">""" + approval.Div_Head.title() + """</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">""" + approval.PresDirektur.title() + """</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">""" + approval.Acc.title() + """</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">""" + approval.Dept_Acc.title() + """</td>
                                </tr>
                                <tr style="height:10px;border: 1px solid black;border-collapse: collapse;">
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Marketing Admin</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Marketing SPV</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Marketing Dept Head</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Bussiness Dev Div Head</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">President Director</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Finance SPV</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Finance Dept Head</td>
                                </tr>
                            </tbody>
                        </table>
                        """
            Superior = approval.SPV.title()
            email_body = """\
                        <html>
                        <head style="margin-bottom: 0px;">Dear Mr/Ms """ + Superior + """,</head>
                        <body>
                        <p style="margin-bottom: 0px;margin-top: 0px;">This Selling Price needs your approval </>
                        <hr>
                        <table style="font-size: x-small; width: 100%">
                            <tr>
                                <td rowspan="3" style="width: 15%;  text-align: center; border-bottom: 1px solid black;"><h1>ASKI</h1></td>
                                <td rowspan="3" style="text-align: center;  border-bottom: 1px solid black;">
                                    <h3>PEMBUATAN HARGA PENJUALAN di SAP</h3>
                                </td>
                                <td style="width: 10%;">No. Document</td>
                                <td style="text-align: center;">:</td>
                                <td style="text-align: center; width: 10%;">FR-FACT.02.001</td>
                            </tr>
                            <tr>
                                <td>Revision</td>
                                <td style="text-align: center;">:</td>
                                <td style="text-align: center;">0</td>
                            </tr>
                            <tr>
                                <td style="border-bottom: 1px solid black;">Effective Start</td>
                                <td style="text-align: center; border-bottom: 1px solid black;">:</td>
                                <td style="text-align: center; border-bottom: 1px solid black;">25 Agustus 2022</td>
                            </tr>
                        </table>
                        <br>
                        <table style="width: 100%; font-size: 12px;">
                            <tr>
                            <td style="width: 10%;white-space: nowrap;">Cust Code</td>
                            <td>:</td>
                            <td>""" + str(SP.Cust_Code) + """</td>
                            </tr>
                            <tr>
                            <td style="width: 10%;white-space: nowrap;">Cust Name</td>
                            <td>:</td>
                            <td>""" + str(SP.Cust_Name) + """</td>
                            </tr>
                            <tr>
                            <td style="width: 10%;white-space: nowrap;">Dist Channel</td>
                            <td>:</td>
                            <td>""" + str(SP.Dist_Channel) + """</td>
                            </tr>
                            <tr>
                            <td style="width: 10%;white-space: nowrap;">Submit Date</td>
                            <td>:</td>
                            <td>""" + str(SP.Submit_Date.strftime("%Y-%m-%d")) + """</td>
                            </tr>
                            <tr>
                            <td style="width: 10%;white-space: nowrap;">No</td>
                            <td>:</td>
                            <td>""" + str(SP.SP_Number) + """</td>
                            </tr>
                            <tr>
                            <td style="width: 10%;white-space: nowrap;">Product Status</td>
                            <td>:</td>
                            <td>"""+str(SP.Product_Status)+"""</td>
                            </tr>
                        </table>
                        <br>
                        <table style="width: 100%; border-collapse: collapse; font-size: 12px;text-align: center">
                        <thead>
                            <tr style=" height: 50px; word-break: normal; border: 1px solid">
                                <th rowspan="2" style="vertical-align: middle; border: 1px solid ">Type</th>
                                <th rowspan="2" style="vertical-align: middle; border: 1px solid">Material No</th>
                                <th rowspan="2" style="vertical-align: middle; border: 1px solid">Material Description</th>
                                <th rowspan="2" style="vertical-align: middle; border: 1px solid">Customer Material</th>
                                <th colspan="5" style="border: 1px solid">Old Price</th>
                                <th colspan="5" style="border: 1px solid">New Price</th>
                                <th rowspan="2" style="vertical-align: middle; border: 1px solid">Ratio</th>
                                <th rowspan="2" style="vertical-align: middle; border: 1px solid">Note</th>
                            </tr>
                            <tr style="border: 1px solid">
                                <th style="padding: 5px; border: 1px solid">Price</th>
                                <th style="padding: 5px; border: 1px solid">Depreciation</th>
                                <th style="padding: 5px; border: 1px solid">Total</th>
                                <th style="padding: 5px; border: 1px solid">UoM</th>
                                <th style="padding: 5px; border: 1px solid">Valid From</th>
                                <th style="padding: 5px; border: 1px solid">Price</th>
                                <th style="padding: 5px; border: 1px solid">Depreciation</th>
                                <th style="padding: 5px; border: 1px solid">Total</th>
                                <th style="padding: 5px; border: 1px solid">UoM</th>
                                <th style="padding: 5px; border: 1px solid">Valid From</th>
                            </tr>
                        </thead>
                        <tbody >
                        """ + contain + """
                        </tbody>
                        </table>
                        <br>
                    
                                """ + apptable + """

                        <br>
                        <hr>
                        <p> Please give your response by click approval button bellow and then click send button. A response at your earliest convenience would be much appreciated. </p>
                        <table width="100%" cellspacing="0" cellpadding="0" >
                            <tr>
                                <td>
                                    <table cellspacing="0" cellpadding="0">
                                        <tr>
                                            <td style="border-radius: 2px;width : 150px;text-align: center;" bgcolor="#4bf542">
                                                <a href="mailto:online.approval@aski.component.astra.co.id?subject=Approve: """ + str(SP.SP_Number) + """&body=Selling Price Request with ID """ + str(SP.SP_Number) + """ %0DApproval Message:" target="_blank" style="padding: 8px 12px; border: 1px solid #4bf542;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #ffffff;text-decoration: none;font-weight:bold;display: inline-block;">
                                                    APPROVE
                                                </a>
                                            </td>
                                            <td>&nbsp;&nbsp;</td>
                                            <td style="border-radius: 2px;width: 150px;text-align: center;" bgcolor="#ED2939">
                                                <a href="mailto:online.approval@aski.component.astra.co.id?subject=Reject: """ + str(SP.SP_Number) + """&body=Reject Selling Price Request with ID """ + str(SP.SP_Number) + """ %0DReject Message:" target="_blank" style="padding: 8px 12px; border: 1px solid #ED2939;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #ffffff;text-decoration: none;font-weight:bold;display: inline-block;">
                                                    REJECT
                                                </a>
                                            </td>
                                            <td>&nbsp;&nbsp;</td>
                                            <td style="border-radius: 2px;width: 150px;text-align: center;" bgcolor="#ebde34">
                                                <a href="mailto:online.approval@aski.component.astra.co.id?subject=Revise: """ + str(SP.SP_Number) + """&body=Need Revise Selling Price Request with ID """ + str(SP.SP_Number) + """ %0DRevision Message:" target="_blank" style="padding: 8px 12px; border: 1px solid #ebde34;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #000000;text-decoration: none;font-weight:bold;display: inline-block;">
                                                    REVISE
                                                </a>
                                            </td>
                                            <td>&nbsp;&nbsp;</td>
                                            <td style="border-radius: 2px;width: 150px;text-align: center;" bgcolor="#cccccc">
                                                <a href="mailto:""" + str(SP.SPV_Email) + """?subject=Ask User: """ + str(SP.SP_Number) + """&body=Ask User about Selling Price Request with ID """ + str(SP.SP_Number) + """ %0DAsk User Message: " target="_blank" style="padding: 8px 12px; border: 1px solid #cccccc;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #000000;text-decoration: none;font-weight:bold;display: inline-block;">
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
            Superior_Email = approval.SPV_Email
            mailattach = EmailMessage(
                'Selling Price Online Approval: ' + 
                request.POST['SP_Number'],
                body=email_body, from_email=settings.EMAIL_HOST_USER, 
                to=[Superior_Email],
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
                mailto=Superior_Email,
                SP_Number=request.POST['SP_Number'],
                mailheader='Selling Price Online Approval: ' + request.POST['SP_Number'])
            email.save()

            models.SellingPrice.objects.filter(SP_Number=request.POST['SP_Number']).update(Status="Created")
            return redirect("/SP/ListSP/")

    Context = {
        'Judul': 'Create SAP Selling Price Approval Request',
        'SPForm': SP,
        'SPItem': SPItem,
        'ListItem': ListItem,
        'SP_Number': SP_Number,
        'Data': data,
        'Approval': approval,
    }
    return render(request, 'sellingprice/CreateSP.html', Context)

#MONITORING SP
@login_required
@user_passes_test(is_memberseeprice)
def listSP(request):
    if (request.user.username == "admin"):
        ListSP = models.SellingPrice.objects.filter(Status__isnull=False).order_by("-id")
        ListSPItem = models.PriceItem.objects.order_by("-id")
    elif (request.user.username == "FINANCE" or request.user.username == "ADMINFINANCE" ):
        ListSP = models.SellingPrice.objects.filter(Status__isnull=False).order_by("-id")
        ListSPItem = models.PriceItem.objects.order_by("-id")
    elif (request.user.username == "MARKETAUTO"):
        ListSP = models.SellingPrice.objects.filter(SP_Number__contains=request.user.username).filter(Status__isnull=False).order_by("-id")
        ListSPItem = models.PriceItem.objects.filter(SP_Number__contains=request.user.username).order_by("-id")
    elif (request.user.username == "MARKETNONAUTO"):
        ListSP = models.SellingPrice.objects.filter(SP_Number__contains=request.user.username).filter(Status__isnull=False).order_by("-id")
        ListSPItem = models.PriceItem.objects.filter(SP_Number__contains=request.user.username).order_by("-id")
    else:
        ListSP = models.SellingPrice.objects.filter(SP_Number__contains=request.user.username).filter(Status__isnull=False).order_by("-id")
        ListSPItem = models.PriceItem.objects.order_by("-id")
    context = {
        'Judul': 'List Selling Price Request',
        'ListSP': ListSP,
        'ListSPItem' : ListSPItem
    }
    return render(request, 'sellingprice/listSP.html', context)


#DETAIL MONITIRING SP
@login_required
@user_passes_test(is_memberseeprice)
def detail(request, ID):
    SP_Number = ID

    SP = models.SellingPrice.objects.get(SP_Number=ID)
    itemlist = list(models.PriceItem.objects.filter(SP_Number=ID))
    # approval = models.Approval.objects.get(SPV_Email=SP.SPV_Email)

    # if request.method == "POST":
    #     models.activity_log(user = request.user.username,SP_Number=SP_Number,activity=request.POST).save()
    #     SPform = forms.SellingPrice(
    #         request.POST, request.FILES, instance=SP)
    #     if SPform.is_valid():
    #         SPform.save()
    #     else:
    #         print(SPform.errors)
    # else:
    #     SPform = forms.SellingPrice(instance=SP)

    context = {
        'Judul': 'Detail Selling Price Request',
        'SP_Number': SP_Number,
        'SP': SP,
        # 'SPform': SPform,
        'itemlist': itemlist,
        # 'approval': approval,
    }
    return render(request, 'sellingprice/detailSP.html', context)


# REVISE SP
@login_required
@user_passes_test(is_membercreatesp)
def revise(request, ID):
    SP_Number = ID

    SP = models.SellingPrice.objects.get(SP_Number=ID)
    spitem = forms.PriceItem()
    approval = models.Approval.objects.get(User=request.user.username)
    if 'rev' not in SP_Number:
        New_SP_Number = SP_Number + "rev1"
    else:
        New_SP_Number = SP_Number.split('rev', 1)[0] + "rev" + str(int(SP_Number.split('rev', 1)[1])+1)
    spitem.fields['SP_Number'].initial = New_SP_Number
    spitem.fields['No'].initial = models.PriceItem.objects.filter(SP_Number = spitem.fields['SP_Number'].initial).count() + 1
    if request.method == "GET" :
        if not models.SellingPrice.objects.filter(SP_Number = New_SP_Number).exists():
            newSP = models.SellingPrice.objects.get(SP_Number = SP_Number)
            newSP.SP_Number = New_SP_Number
            newSP.pk = None
            newSP.Dept_Head_Approval_Date = None
            newSP.Dept_Head_Approval_Status = None
            newSP.Dept_Acc_Confirm_Status = None
            newSP.Div_Head_Approval_Date = None
            newSP.Div_Head_Approval_Status = None
            newSP.PresDirektur_Approval_Date = None
            newSP.PresDirektur_Approval_Status = None
            newSP.Status = None
            newSP.Message = None
            newSP.save()

            newitems = models.PriceItem.objects.filter(SP_Number=SP_Number)
            for newitem in newitems:
                newitem.SP_Number = New_SP_Number
                newitem.pk = None
                newitem.save()
    newSP = models.SellingPrice.objects.get(SP_Number = New_SP_Number)
    itemlist = list(models.PriceItem.objects.filter(SP_Number=New_SP_Number).order_by('id'))
    if request.method == "POST":
        print(request.POST)
        models.activity_log(user=request.user)
        if 'Delete' in request.POST:
            models.PriceItem.objects.filter(SP_Number = New_SP_Number, id = request.POST["Delete"]).delete()
        elif 'save' in request.POST:
            models.PriceItem.objects.filter(SP_Number = New_SP_Number, Material_Description = request.POST["Material_Description_Edit"]).update(Type=request.POST['TypeEdit'], 
            Material_No=request.POST['Material_No_Edit'], Material_Description=request.POST['Material_Description_Edit'], Customer_Material=request.POST['Customer_Material_Edit'], Old_Price=request.POST['Old_Price_Edit'],
            Old_Depreciation =request.POST['Old_Depreciation_Edit'], Old_Total=request.POST['Old_Total_Edit'], Old_UoM=request.POST['Old_UoM_Edit'], Old_Valid_From=request.POST['Old_Valid_From_Edit'],
            New_Price=request.POST['New_Price_Edit'], New_Depreciation=request.POST['New_Depreciation_Edit'], New_Total=request.POST['New_Total_Edit'], New_UoM=request.POST['New_UoM_Edit'],
            New_Valid_From=request.POST['New_Valid_From_Edit'], Note=request.POST['NoteEdit'], Ratio_Variance=request.POST['Ratio_Variance_Edit'])
        elif 'add' in request.POST:
            spitemsave = forms.PriceItem(request.POST)
            if spitemsave.is_valid() and models.PriceItem.objects.filter(SP_Number=request.POST['SP_Number'], Material_Description=request.POST['Material_Description'], Note=request.POST['Note']).count() == 0:
                spitemsave.save()
            else:
                print(spitemsave.errors)
        elif 'upload' in request.POST:
            print("attachment")
            SPsave = forms.SellingPrice(request.POST, request.FILES, instance=newSP)
            if SPsave.is_valid():
                SPsave.save()
            else:
                print(SPsave.errors)
        elif 'Finish' in request.POST:
            print("Finish")
            SPsave = forms.SellingPrice(request.POST, request.FILES, instance=newSP)
            if SPsave.is_valid():
                SPsave.User_Submit = datetime.datetime.now()
                newSP.User_Submit = datetime.datetime.now()
                SPsave.save()
            else:
                print(SPsave.errors)
            counter = 0
            contain = ''
            for item in itemlist:
                counter += 1
                contain += '''<tr style="height: 30px; font-size:12px; border-collapse: collapse;">
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.Type)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.Material_No)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.Material_Description)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.Customer_Material)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.Old_Price)+''',-</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.Old_Depreciation)+''',-</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.Old_Total)+''',-</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.Old_UoM)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.Old_Valid_From)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.New_Price)+''',-</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.New_Depreciation)+''',-</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.New_Total)+''',-</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.New_UoM)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.New_Valid_From)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.Ratio_Variance)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.Note)+'''</td>
                </tr>'''
            if approval.Dept_Head == None:
                apptable = """
                        <table style="font-size: 12px;text-align: center;border: 1px solid black;border-collapse: collapse;" >
                            <tbody>
                                <tr style="height:10px;border: 1px solid black;border-collapse: collapse;">
                                    <td style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Created By</td>
                                    <td style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Checked By</td>
                                    <td colspan="2" style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 460px;text-align: center;vertical-align: bottom;">Approved By</td>
                                    <td style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">SAP Input By</td>
                                    <td style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Confirmed By</td>
                                </tr>
                                <tr style="height:40px;border: 1px solid black;border-collapse: collapse;">
                                    <td style="border: 1px solid black;border-collapse: collapse;padding:20px;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="User">Created """ + str(SP.User_Submit.strftime("%Y-%m-%d %H:%M:%S")) + """</td>
                                    <td style="border: 1px solid black;border-collapse: collapse;padding:20px;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="SPV"></td>
                                    <td style="border: 1px solid black;border-collapse: collapse;padding:20px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="DIV"></td>
                                    <td style="border: 1px solid black;border-collapse: collapse;padding:20px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="PRDIR"></td>
                                    <td style="border: 1px solid black;border-collapse: collapse;padding:20px;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="ACC"></td>
                                    <td style="border: 1px solid black;border-collapse: collapse;padding:20px;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="DEPTACC"></td>
                                </tr>
                                <tr style="height:20px;border: 1px solid black;border-collapse: collapse;">
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">""" + approval.User_Name.title() + """</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">""" + approval.SPV.title() + """</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">""" + approval.Div_Head.title() + """</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">""" + approval.PresDirektur.title() + """</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">""" + approval.Acc.title() + """</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">""" + approval.Dept_Acc.title() + """</td>
                                </tr>
                                <tr style="height:10px;border: 1px solid black;border-collapse: collapse;">
                                <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Marketing Admin</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Marketing SPV</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Bussiness Dev Div Head</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">President Director</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Finance SPV</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Finance Dept Head</td>
                                </tr>
                            </tbody>
                        </table>
                        """
            else :
                apptable = """
                        <table style="font-size: 12px;text-align: center;border: 1px solid black;border-collapse: collapse;" >
                            <tbody>
                                <tr style="height:10px;border: 1px solid black;border-collapse: collapse;">
                                    <td style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Created By</td>
                                    <td style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Checked By</td>
                                    <td style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Checked By</td>
                                    <td colspan="2" style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 460px;text-align: center;vertical-align: bottom;">Approved By</td>
                                    <td style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">SAP Input By</td>
                                    <td style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Confirmed By</td>
                                </tr>
                                <tr style="height:40px;border: 1px solid black;border-collapse: collapse;">
                                    <td style="border: 1px solid black;border-collapse: collapse;padding:20px;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="User">Created """ + str(SP.User_Submit.strftime("%Y-%m-%d %H:%M:%S")) + """</td>
                                    <td style="border: 1px solid black;border-collapse: collapse;padding:20px;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="SPV"></td>
                                    <td style="border: 1px solid black;border-collapse: collapse;padding:20px;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="DEPT"></td>
                                    <td style="border: 1px solid black;border-collapse: collapse;padding:20px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="DIV"></td>
                                    <td style="border: 1px solid black;border-collapse: collapse;padding:20px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="PRDIR"></td>
                                    <td style="border: 1px solid black;border-collapse: collapse;padding:20px;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="ACC"></td>
                                    <td style="border: 1px solid black;border-collapse: collapse;padding:20px;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="DEPTACC"></td>
                                </tr>
                                <tr style="height:20px;border: 1px solid black;border-collapse: collapse;">
                                <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">""" + approval.User_Name.title() + """</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">""" + approval.SPV.title() + """</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">""" + approval.Dept_Head.title() + """</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">""" + approval.Div_Head.title() + """</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">""" + approval.PresDirektur.title() + """</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">""" + approval.Acc.title() + """</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">""" + approval.Dept_Acc.title() + """</td>
                                </tr>
                                <tr style="height:10px;border: 1px solid black;border-collapse: collapse;">
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Marketing Admin</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Marketing SPV</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Marketing Dept Head</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Bussiness Dev Div Head</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">President Director</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Finance SPV</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Finance Dept Head</td>
                                </tr>
                            </tbody>
                        </table>
                        """
            Superior = approval.SPV.title()
            email_body = """\
                <html>
                <head style="margin-bottom: 0px;">Dear Mr/Ms """ + Superior  + """,</head>
                <body>
                <p style="margin-bottom: 0px;margin-top: 0px;">This Selling Price needs your approval </>
                <hr>
                <table style="font-size: x-small; width: 100%">
                    <tr>
                        <td rowspan="3" style="width: 15%;  text-align: center; border-bottom: 1px solid black;"><h1>ASKI</h1></td>
                        <td rowspan="3" style="text-align: center;  border-bottom: 1px solid black;">
                            <h3>PEMBUATAN HARGA PENJUALAN di SAP</h3>
                        </td>
                        <td style="width: 10%;">No. Document</td>
                        <td style="text-align: center;">:</td>
                        <td style="text-align: center; width: 10%;">FR-FACT.02.001</td>
                    </tr>
                    <tr>
                        <td>Revision</td>
                        <td style="text-align: center;">:</td>
                        <td style="text-align: center;">0</td>
                    </tr>
                    <tr>
                        <td style="border-bottom: 1px solid black;">Effective Start</td>
                        <td style="text-align: center; border-bottom: 1px solid black;">:</td>
                        <td style="text-align: center; border-bottom: 1px solid black;">25 Agustus 2022</td>
                    </tr>
                </table>
                <br> 
                <table style="width: 100%; font-size: x-small;">
                    <tr>
                    <td style="width: 10%;white-space: nowrap;">Cust Code</td>
                    <td>:</td>
                    <td>"""+str(newSP.Cust_Code)+"""</td>
                    </tr>
                    <tr>
                    <td style="width: 10%;white-space: nowrap;">Cust Name</td>
                    <td>:</td>
                    <td>"""+str(newSP.Cust_Name)+"""</td>
                    </tr>
                    <tr>
                    <td style="width: 10%;white-space: nowrap;">Dist Channel</td>
                    <td>:</td>
                    <td>"""+str(newSP.Dist_Channel)+"""</td>
                    </tr>
                    <tr>
                    <td style="width: 10%;white-space: nowrap;">Submit Date</td>
                    <td>:</td>
                    <td>"""+str(newSP.Submit_Date.strftime("%Y-%m-%d"))+"""</td>
                    </tr>
                    <tr>
                    <td style="width: 10%;white-space: nowrap;">No</td>
                    <td>:</td>
                    <td>"""+str(newSP.SP_Number)+"""</td>
                    </tr>
                    <tr>
                    <td style="width: 10%;white-space: nowrap;">Product Status</td>
                    <td>:</td>
                    <td>"""+str(SP.Product_Status)+"""</td>
                    </tr>
                </table>

                <br>
                <table style="width: 100%; border-collapse: collapse; font-size: 12px;text-align: center">
                <thead>
                    <tr style=" height: 50px; word-break: normal; border: 1px solid">
                        <th rowspan="2" style="vertical-align: middle; border: 1px solid ">Type</th>
                        <th rowspan="2" style="vertical-align: middle; border: 1px solid">Material No</th>
                        <th rowspan="2" style="vertical-align: middle; border: 1px solid">Material Description</th>
                        <th rowspan="2" style="vertical-align: middle; border: 1px solid">Customer Material</th>
                        <th colspan="5" style="border: 1px solid">Old Price</th>
                        <th colspan="5" style="border: 1px solid">New Price</th>
                        <th rowspan="2" style="vertical-align: middle; border: 1px solid">Ratio</th>
                        <th rowspan="2" style="vertical-align: middle; border: 1px solid">Note</th>
                    </tr>
                    <tr style="border: 1px solid">
                        <th style="padding: 5px; border: 1px solid">Price</th>
                        <th style="padding: 5px; border: 1px solid">Depreciation</th>
                        <th style="padding: 5px; border: 1px solid">Total</th>
                        <th style="padding: 5px; border: 1px solid">UoM</th>
                        <th style="padding: 5px; border: 1px solid">Valid From</th>
                        <th style="padding: 5px; border: 1px solid">Price</th>
                        <th style="padding: 5px; border: 1px solid">Depreciation</th>
                        <th style="padding: 5px; border: 1px solid">Total</th>
                        <th style="padding: 5px; border: 1px solid">UoM</th>
                        <th style="padding: 5px; border: 1px solid">Valid From</th>
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
                </tr>
                </table>
                <br>
                <hr>
                 <h6 style="margin:0px;font-size:12px;font-weight:normal;">Revision Note: """+ SP.Message.replace("Need Revise Selling Price Request with ID "+SP_Number,"").replace("Revision Message: ","")+"""</h6>
                <hr>
                <p> Please give your response by click approval button bellow and then click send button. A response at your earliest convenience would be much appreciated. </p>
                <table width="100%" cellspacing="0" cellpadding="0">
                    <tr>
                        <td>
                            <table cellspacing="0" cellpadding="0">
                                <tr>
                                    <td style="border-radius: 2px;width : 150px;text-align: center;" bgcolor="#4bf542">
                                        <a href="mailto:online.approval@aski.component.astra.co.id?subject=Approve: """+str(newSP.SP_Number)+"""&body= Selling Price Request with ID """+str(newSP.SP_Number)+""" %0DApproval Message:" target="_blank" style="padding: 8px 12px; border: 1px solid #4bf542;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #ffffff;text-decoration: none;font-weight:bold;display: inline-block;">
                                            APPROVE             
                                        </a>
                                    </td>
                                    <td>&nbsp;&nbsp;</td>
                                    <td style="border-radius: 2px;width: 150px;text-align: center;" bgcolor="#ED2939">
                                        <a href="mailto:online.approval@aski.component.astra.co.id?subject=Reject: """+str(newSP.SP_Number)+"""&body=Reject Selling Price Request with ID """+str(newSP.SP_Number)+""" %0DReject Message:" target="_blank" style="padding: 8px 12px; border: 1px solid #ED2939;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #ffffff;text-decoration: none;font-weight:bold;display: inline-block;">
                                            REJECT             
                                        </a>
                                    </td>
                                    <td>&nbsp;&nbsp;</td>
                                    <td style="border-radius: 2px;width: 150px;text-align: center;" bgcolor="#ebde34">
                                        <a href="mailto:online.approval@aski.component.astra.co.id?subject=Revise: """+str(newSP.SP_Number)+"""&body=Need Revise Selling Price Request with ID """+str(newSP.SP_Number)+""" %0DRevision Message:" target="_blank" style="padding: 8px 12px; border: 1px solid #ebde34;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #000000;text-decoration: none;font-weight:bold;display: inline-block;">
                                            REVISE             
                                        </a>
                                    </td>
                                    <td>&nbsp;&nbsp;</td>
                                    <td style="border-radius: 2px;width: 150px;text-align: center;" bgcolor="#cccccc">
                                        <a href="mailto:"""+str(SP.SPV_Email)+"""?subject=Ask User: """+str(newSP.SP_Number)+"""&body=Ask User about Selling Price Request with ID """+str(newSP.SP_Number)+""" %0DAsk User Message: " target="_blank" style="padding: 8px 12px; border: 1px solid #cccccc;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #000000;text-decoration: none;font-weight:bold;display: inline-block;">
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


            Superior_Email = approval.SPV_Email
            mailattach = EmailMessage(
                'Selling Price Online Approval: ' + 
                request.POST['SP_Number'],
                body=email_body, from_email=settings.EMAIL_HOST_USER, 
                to=[Superior_Email],
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

            email = models.Send(
                htmlmessage=email_body,
                mailfrom='online.approval@aski.component.astra.co.id',
                mailto=Superior_Email,
                SP_Number=request.POST['SP_Number'],
                mailheader='Selling Price Online Approval: ' + request.POST['SP_Number'])
            email.save()
            models.SellingPrice.objects.filter(SP_Number=request.POST['SP_Number']).update(Status="Created")

            models.SellingPrice.objects.filter(SP_Number=SP_Number).update(Status="Revised")
            return redirect("/SP/ListSP/")
        
    context = {
        'Judul': 'Revise Selling Price Request',
        'SP_Number': SP_Number,
        'New_SP_Number': New_SP_Number,
        'SP': newSP,
        'SPform': forms.SellingPrice(instance=newSP),
        'SPItemForm' : spitem,
        'itemlist': list(models.PriceItem.objects.filter(SP_Number=New_SP_Number).order_by('id')),
        'Approval': approval,
    } 
    return render(request, 'sellingprice/reviseSP.html', context)


# LIST INPUT
@login_required
@user_passes_test(is_memberaddasset)
def listinput(request):
    listinputCheck = models.SellingPrice.objects.filter(Status='FinanceCheck').order_by("-id")
    listDone = models.SellingPrice.objects.filter(Acc_Input_Status='Input').order_by("-id")
    context = {
        'Judul': 'List Checking Selling Price Request',
        'listinput': listinputCheck,
        'listdone' : listDone
    }
    return render(request, 'sellingprice/listinput.html', context)


# EMAIL REQUEST
@login_required
@user_passes_test(is_memberaddasset)
def check(request, ID):
    SP_Number = ID
    SP = models.SellingPrice.objects.get(SP_Number=ID)
    SPform = forms.SellingPrice(instance=SP)

    # approval = models.Approval.objects.get(User=request.user.username)
    itemlist = list(models.PriceItem.objects.filter(SP_Number=SP_Number))
    if request.method == "POST":
        models.activity_log(user = request.user.username, SP_Number=SP_Number, activity=request.POST).save()
        if 'revision' in request.POST:
            models.SellingPrice.objects.filter(SP_Number = SP_Number).update(Status = 'NeedRevise', Message = request.POST['revisemessage'])
            return listinput(request)
        if 'upload' in request.POST:
            print(request.POST)
            SPform = forms.SellingPrice(request.POST, request.FILES, instance=SP)
            if SPform.is_valid():
                SPform.save()
            else:
                print(SPform.errors)
        if 'finish' in request.POST:
            print(request.POST)
            models.SellingPrice.objects.filter(SP_Number=SP_Number).update(Acc_Input_Date=datetime.datetime.now(), Acc_Input_Status= 'Input')
            SP = models.SellingPrice.objects.get(SP_Number=ID)
            itemlist = list(models.PriceItem.objects.filter(SP_Number=SP_Number))
            # approval = models.Approval.objects.get(User=request.user.username)
            counter = 0
            contain = ''
            for item in itemlist:
                counter += 1
                contain += '''<tr style="height: 30px; font-size:12px; border-collapse: collapse;">
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.Type)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.Material_No)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.Material_Description)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.Customer_Material)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.Old_Price)+''',-</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.Old_Depreciation)+''',-</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.Old_Total)+''',-</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.Old_UoM)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.Old_Valid_From)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.New_Price)+''',-</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.New_Depreciation)+''',-</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.New_Total)+''',-</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.New_UoM)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.New_Valid_From)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.Ratio_Variance)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.Note)+'''</td>
                </tr>'''
            if SP.Dept_Head == None :
                apptable = """
                        <table style="font-size: 12px;text-align: center;border: 1px solid black;border-collapse: collapse;" >
                            <tbody>
                                <tr style="height:10px;border: 1px solid black;border-collapse: collapse;">
                                    <td style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Created By</td>
                                    <td colspan="2" style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 460px;text-align: center;vertical-align: bottom;">Approved By</td>
                                    <td style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">SAP Input By</td>
                                    <td style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Confirmed By</td>
                                </tr>
                                    <tr style="height:40px;">
                                        <td style="padding:20px;border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="SPV">Created """+str(SP.User_Submit.strftime("%Y-%m-%d %H:%M:%S"))+"""</td>
                                        <td style="padding:20px;border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="DIV">"""+str(SP.Div_Head_Approval_Status)+" "+str(SP.Div_Head_Approval_Date.strftime("%Y-%m-%d %H:%M:%S"))+"""</td>
                                        <td style="padding:20px;border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="PRDIR">"""+str(SP.PresDirektur_Approval_Status)+" "+str(SP.PresDirektur_Approval_Date.strftime("%Y-%m-%d %H:%M:%S"))+"""</td>
                                        <td style="padding:20px;border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="ACC">"""+str(SP.Acc_Input_Status)+" "+str(SP.Acc_Input_Date.strftime("%Y-%m-%d %H:%M:%S"))+"""</td>
                                        <td style="padding:20px;border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="DEPTACC"></td>
                                    </tr>
                               <tr style="height:20px;border: 1px solid black;border-collapse: collapse;">
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">""" + SP.SPV.title() + """</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">""" + SP.Div_Head.title() + """</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">""" + SP.PresDirektur.title() + """</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">""" + SP.Acc.title() + """</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">""" + SP.Dept_Acc.title() + """</td>
                                </tr>
                                <tr style="height:10px;border: 1px solid black;border-collapse: collapse;">
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Marketing SPV</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Bussiness Dev Div Head</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">President Director</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Finance SPV</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Finance Dept Head</td>
                                </tr>
                            </tbody>
                        </table>           
                        """

            else :
                apptable = """
                        <table style="font-size: 12px;text-align: center;border: 1px solid black;border-collapse: collapse;" >
                            <tbody>
                                <tr style="height:10px;border: 1px solid black;border-collapse: collapse;">
                                    <td style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Created By</td>
                                    <td style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Checked By</td>
                                    <td colspan="2" style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 460px;text-align: center;vertical-align: bottom;">Approved By</td>
                                    <td style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">SAP Input By</td>
                                    <td style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Confirmed By</td>
                                </tr>
                                    <tr style="height:40px;">
                                        <td style="padding:20px;border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="SPV">Created """+str(SP.User_Submit.strftime("%Y-%m-%d %H:%M:%S"))+"""</td>
                                        <td style="padding:20px;border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="DEPT">"""+str(SP.Dept_Head_Approval_Status)+" "+str(SP.Dept_Head_Approval_Date.strftime("%Y-%m-%d %H:%M:%S"))+"""</td>
                                        <td style="padding:20px;border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="DIV">"""+str(SP.Div_Head_Approval_Status)+" "+str(SP.Div_Head_Approval_Date.strftime("%Y-%m-%d %H:%M:%S"))+"""</td>
                                        <td style="padding:20px;border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="PRDIR">"""+str(SP.PresDirektur_Approval_Status)+" "+str(SP.PresDirektur_Approval_Date.strftime("%Y-%m-%d %H:%M:%S"))+"""</td>
                                        <td style="padding:20px;border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="ACC">"""+str(SP.Acc_Input_Status)+" "+str(SP.Acc_Input_Date.strftime("%Y-%m-%d %H:%M:%S"))+"""</td>
                                        <td style="padding:20px;border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="DEPTACC"></td>
                                    </tr>
                               <tr style="height:20px;border: 1px solid black;border-collapse: collapse;">
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">""" + SP.SPV.title() + """</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">""" + SP.Dept_Head.title() + """</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">""" + SP.Div_Head.title() + """</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">""" + SP.PresDirektur.title() + """</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">""" + SP.Acc.title() + """</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">""" + SP.Dept_Acc.title() + """</td>
                                </tr>
                                <tr style="height:10px;border: 1px solid black;border-collapse: collapse;">
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Marketing SPV</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Marketing Dept Head</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Bussiness Dev Div Head</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">President Director</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Finance SPV</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Finance Dept Head</td>
                                </tr>
                            </tbody>
                        </table>           
                        """
  
            Superior = SP.Dept_Acc.title()
            email_body = """\
                <html>
                <head style="margin-bottom: 0px;">Dear Mr/Ms """ + Superior  + """,</head>
                <body>
                <p style="margin-bottom: 0px;margin-top: 0px;">This Selling Price needs your approval </>
                <hr>
                <table style="font-size: x-small width: 100%">
                    <tr>
                        <td rowspan="3" style="width: 15%;  border-bottom: 1px solid black;"><h1>ASKI</h1></td>
                        <td rowspan="3" style="text-align: center;  border-bottom: 1px solid black;">
                            <h3>PEMBUATAN HARGA PENJUALAN di SAP</h3>
                        </td>
                        <td style="width: 8%;">No. Document</td>
                        <td style="text-align: center;">:</td>
                        <td style="text-align: center; width: 10%;">FR-FACT.02.001</td>
                    </tr>
                    <tr>
                        <td>Revision</td>
                        <td style="text-align: center;">:</td>
                        <td style="text-align: center;">0</td>
                    </tr>
                    <tr>
                        <td style="border-bottom: 1px solid black;">Effective Start</td>
                        <td style="text-align: center; border-bottom: 1px solid black;">:</td>
                        <td style="text-align: center; border-bottom: 1px solid black;">25 Agustus 2022</td>
                    </tr>
                </table>

                <br>
                <table style="width: 100%; font-size: x-small;">
                    <tr>
                    <td style="width: 10%;white-space: nowrap;">Cust Code</td>
                    <td>:</td>
                    <td>"""+str(SP.Cust_Code)+"""</td>
                    </tr>
                    <tr>
                    <td style="width: 10%;white-space: nowrap;">Cust Name</td>
                    <td>:</td>
                    <td>"""+str(SP.Cust_Name)+"""</td>
                    </tr>
                    <tr>
                    <td style="width: 10%;white-space: nowrap;">Dist Channel</td>
                    <td>:</td>
                    <td>"""+str(SP.Dist_Channel)+"""</td>
                    </tr>
                    <tr>
                    <td style="width: 10%;white-space: nowrap;">Submit Date</td>
                    <td>:</td>
                    <td>"""+str(SP.Submit_Date.strftime("%Y-%m-%d"))+"""</td>
                    </tr>
                    <tr>
                    <td style="width: 10%;white-space: nowrap;">No</td>
                    <td>:</td>
                    <td>"""+str(SP.SP_Number)+"""</td>
                    </tr>
                    <tr>
                    <td style="width: 10%;white-space: nowrap;">Product Status</td>
                    <td>:</td>
                    <td>"""+str(SP.Product_Status)+"""</td>
                    </tr>
                </table>
                <br>
                <table style="width: 100%; border-collapse: collapse; font-size: 12px;text-align: center">
                <thead>
                    <tr style=" height: 50px; word-break: normal; border: 1px solid">
                        <th rowspan="2" style="vertical-align: middle; border: 1px solid">Type</th>
                        <th rowspan="2" style="vertical-align: middle; border: 1px solid">Material No</th>
                        <th rowspan="2" style="vertical-align: middle; border: 1px solid">Material Description</th>
                        <th rowspan="2" style="vertical-align: middle; border: 1px solid">Customer Material</th>
                        <th colspan="5" style="border: 1px solid">Old Price</th>
                        <th colspan="5" style="border: 1px solid">New Price</th>
                        <th rowspan="2" style="vertical-align: middle; border: 1px solid">Ratio</th>
                        <th rowspan="2" style="vertical-align: middle; border: 1px solid">Note</th>
                    </tr>
                    <tr style="border: 1px solid">
                        <th style="padding: 5px; border: 1px solid">Price</th>
                        <th style="padding: 5px; border: 1px solid">Depreciation</th>
                        <th style="padding: 5px; border: 1px solid">Total</th>
                        <th style="padding: 5px; border: 1px solid">UoM</th>
                        <th style="padding: 5px; border: 1px solid">Valid From</th>
                        <th style="padding: 5px; border: 1px solid">Price</th>
                        <th style="padding: 5px; border: 1px solid">Depreciation</th>
                        <th style="padding: 5px; border: 1px solid">Total</th>
                        <th style="padding: 5px; border: 1px solid">UoM</th>
                        <th style="padding: 5px; border: 1px solid">Valid From</th>
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
                                        <a href="mailto:online.approval@aski.component.astra.co.id?subject=Approve: """+str(SP.SP_Number)+"""&body= Selling Price Request with ID """+str(SP.SP_Number)+""" %0DApproval Message:" target="_blank" style="padding: 8px 12px; border: 1px solid #4bf542;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #ffffff;text-decoration: none;font-weight:bold;display: inline-block;">
                                            APPROVE           
                                        </a>
                                    </td>
                                    <td>&nbsp;&nbsp;</td>
                                    <td style="border-radius: 2px;width: 150px;text-align: center;" bgcolor="#ED2939">
                                        <a href="mailto:online.approval@aski.component.astra.co.id?subject=Reject: """+str(SP.SP_Number)+"""&body=Reject Selling Price Request with ID """+str(SP.SP_Number)+""" %0DReject Message:" target="_blank" style="padding: 8px 12px; border: 1px solid #ED2939;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #ffffff;text-decoration: none;font-weight:bold;display: inline-block;">
                                            REJECT          
                                        </a>
                                    </td>
                                    <td>&nbsp;&nbsp;</td>
                                    <td style="border-radius: 2px;width: 150px;text-align: center;" bgcolor="#ebde34">
                                        <a href="mailto:online.approval@aski.component.astra.co.id?subject=Revise: """+str(SP.SP_Number)+"""&body=Need Revise Selling Price Request with ID """+str(SP.SP_Number)+""" %0DRevision Message:" target="_blank" style="padding: 8px 12px; border: 1px solid #ebde34;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #000000;text-decoration: none;font-weight:bold;display: inline-block;">
                                            REVISE       
                                        </a>
                                    </td>
                                    <td>&nbsp;&nbsp;</td>
                                    <td style="border-radius: 2px;width: 150px;text-align: center;" bgcolor="#cccccc">
                                        <a href="mailto:"""+str(SP.SPV_Email)+"""?subject=Ask User: """+str(SP.SP_Number)+"""&body=Ask User about Selling Price Request with ID """+str(SP.SP_Number)+""" %0DAsk User Message: " target="_blank" style="padding: 8px 12px; border: 1px solid #cccccc;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #000000;text-decoration: none;font-weight:bold;display: inline-block;">
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
                'Selling Price Online Approval: ' + 
                SP_Number,
                body=email_body, from_email=settings.EMAIL_HOST_USER, 
                to=[SP.Dept_Acc_Email],
            )

            mailattach.content_subtype = "html"
            if len(str(SP.Attachment1))>1:
                mailattach.attach_file(
                    'Media/'+str(SP.Attachment1))
            if len(str(SP.Attachment2))>1:
                mailattach.attach_file(
                    'Media/'+str(SP.Attachment2))
            if len(str(SP.Attachment3))>1:
                mailattach.attach_file(
                    'Media/'+str(SP.Attachment3))
            if len(str(SP.Attachment4))>1:
                mailattach.attach_file(
                    'Media/'+str(SP.Attachment4))
                
            # if 'Input1' in request.FILES:
            #     mailattach.attach_file(
            #         'Media/Uploads/'+str(request.FILES['Input1']).replace(' ', '_'))
            # if 'Input2' in request.FILES:
            #     mailattach.attach_file(
            #         'Media/Uploads/'+str(request.FILES['Input2']).replace(' ', '_'))
            if len(str(SP.Input1))>1:
                mailattach.attach_file(
                    'Media/'+str(SP.Input1))
            if len(str(SP.Input2))>1:
                mailattach.attach_file(
                    'Media/'+str(SP.Input2))

            mailattach.send()

            # email = models.Send(
            #     htmlmessage=email_body,
            #     mailfrom='online.approval@aski.component.astra.co.id',
            #     mailto=[SP.Dept_Acc_Email],
            #     SP_Number=SP_Number,
            #     mailheader='Selling Price Online Approval: ' + SP_Number)
            # email.save()

            models.SellingPrice.objects.filter(SP_Number=SP_Number).update(Status="Waiting Confirmation")
            return redirect("/SP/ListInput/")
    context = {
        'Judul': 'Detail Checking Selling Price Request',
        'SP': SP,
        'SPform': SPform,
        'itemlist': itemlist,
        # 'approval': approval,
    }
    return render(request, 'sellingprice/detailinput.html', context)

def Generate(ID):
    SP_Number = ID

    SP = models.SellingPrice.objects.get(SP_Number=SP_Number)
    itemlist = list(models.PriceItem.objects.filter(SP_Number=SP_Number).order_by('id'))
    watermark = ""
    for x in range(100):
        watermark += SP_Number+" "
    counter = 0
    contain = ''
    for item in itemlist:
        counter += 1
        contain += '''<tr style="height: 30px; font-size:12px; border-collapse: collapse;">
                    <td style="border: 1px solid black; border-collapse: collapse; padding: 5px;">'''+str(item.Type)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse; padding: 5px;">'''+str(item.Material_No)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse; padding: 5px;">'''+str(item.Material_Description)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse; padding: 5px;">'''+str(item.Customer_Material)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse; text-align: right; padding: 5px;">'''+str(item.Old_Price)+''',-</td>
                    <td style="border: 1px solid black; border-collapse: collapse; text-align: center; padding: 5px;">'''+str(item.Old_Depreciation)+''',-</td>
                    <td style="border: 1px solid black; border-collapse: collapse;text-align: right; padding: 5px;">'''+str(item.Old_Total)+''',-</td>
                    <td style="border: 1px solid black; border-collapse: collapse; text-align: center; padding: 5px;">'''+str(item.Old_UoM)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse; text-align: center; padding: 5px;">'''+str(item.Old_Valid_From)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse; text-align: right; padding: 5px;">'''+str(item.New_Price)+''',-</td>
                    <td style="border: 1px solid black; border-collapse: collapse; text-align: center; padding: 5px;">'''+str(item.New_Depreciation)+''',-</td>
                    <td style="border: 1px solid black; border-collapse: collapse; text-align: right; padding: 5px;">'''+str(item.New_Total)+''',-</td>
                    <td style="border: 1px solid black; border-collapse: collapse; text-align: center; padding: 5px;">'''+str(item.New_UoM)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse; text-align: center; padding: 5px;">'''+str(item.New_Valid_From)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse; text-align: center; padding: 5px;">'''+str(item.Ratio_Variance)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse; text-align: center; padding: 5px;">'''+str(item.Note)+'''</td>
                </tr>'''
    if SP.Dept_Head == None :
        apptable = """
                <table style="border: 1px solid black; font-size: 12px;text-align: center;border-collapse: collapse;">
                    <tbody>
                        <tr style="height:10px;">
                            <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Created By</td>
                            <td colspan="2" style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Approved By</td>
                            <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">SAP Input By</td>
                            <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Confirmed By</td>
                        </tr>
                        <tr style="height:40px;">
                            <td style="padding:20px;border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="SPV">Created """+str(SP.User_Submit.strftime("%Y-%m-%d %H:%M:%S"))+"""</td>
                            <td style="padding:20px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="DIV">"""+str(SP.Div_Head_Approval_Status)+' '+str(SP.Div_Head_Approval_Date.strftime("%Y-%m-%d %H:%M:%S"))+"""</td>
                            <td style="padding:20px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="PRDIR">"""+str(SP.PresDirektur_Approval_Status)+' '+str(SP.PresDirektur_Approval_Date.strftime("%Y-%m-%d %H:%M:%S"))+"""</td>
                            <td style="padding:20px;border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="ACC">"""+str(SP.Acc_Input_Status)+' '+str(SP.Acc_Input_Date.strftime("%Y-%m-%d %H:%M:%S"))+"""</td>
                            <td style="padding:20px;border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="DEPTACC">"""+str(SP.Dept_Acc_Confirm_Status)+' '+str(SP.Dept_Acc_Confirm_Date.strftime("%Y-%m-%d %H:%M:%S"))+"""</td>
                        </tr>
                        <tr style="height:20px;">
                            <td style="border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">"""+SP.SPV.title()+"""</td>
                            <td style="text-align: center;vertical-align: bottom;">"""+SP.Div_Head.title()+"""</td>
                            <td style="text-align: center;vertical-align: bottom;">"""+SP.PresDirektur.title()+"""</td>
                            <td style="border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">"""+SP.Acc.title()+"""</td>
                            <td style="border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">"""+SP.Dept_Acc.title()+"""</td>
                        </tr>
                        <tr style="height:10px;">
                            <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Marketing SPV</td>
                            <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Bussiness Dev Div Head</td>
                            <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Pres Director</td>
                            <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Finance SPV</td>
                            <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Finance Dept Head</td>
                        </tr>
                    </tbody>
                </table>
                """
    else :
        apptable = """
                <table style="border: 1px solid black; font-size: 12px;text-align: center;border-collapse: collapse;">
                    <tbody>
                        <tr style="height:10px;">
                            <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Created By</td>
                            <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Checked By</td>
                            <td colspan="2" style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Approved By</td>
                            <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">SAP Input By</td>
                            <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Confirmed By</td>
                        </tr>
                        <tr style="height:40px;">
                            <td style="padding:20px;border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="SPV">Created """+str(SP.User_Submit.strftime("%Y-%m-%d %H:%M:%S"))+"""</td>
                            <td style="padding:20px;border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="DEPT">"""+str(SP.Dept_Head_Approval_Status)+' '+str(SP.Dept_Head_Approval_Date.strftime("%Y-%m-%d %H:%M:%S"))+"""</td>
                            <td style="padding:20px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="DIV">"""+str(SP.Div_Head_Approval_Status)+' '+str(SP.Div_Head_Approval_Date.strftime("%Y-%m-%d %H:%M:%S"))+"""</td>
                            <td style="padding:20px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="PRDIR">"""+str(SP.PresDirektur_Approval_Status)+' '+str(SP.PresDirektur_Approval_Date.strftime("%Y-%m-%d %H:%M:%S"))+"""</td>
                            <td style="padding:20px;border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="ACC">"""+str(SP.Acc_Input_Status)+' '+str(SP.Acc_Input_Date.strftime("%Y-%m-%d %H:%M:%S"))+"""</td>
                            <td style="padding:20px;border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="DEPTACC">"""+str(SP.Dept_Acc_Confirm_Status)+' '+str(SP.Dept_Acc_Confirm_Date.strftime("%Y-%m-%d %H:%M:%S"))+"""</td>
                        </tr>
                        <tr style="height:20px;">
                            <td style="border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">"""+SP.SPV.title()+"""</td>
                            <td style="border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">"""+SP.Dept_Head.title()+"""</td>
                            <td style="text-align: center;vertical-align: bottom;">"""+SP.Div_Head.title()+"""</td>
                            <td style="text-align: center;vertical-align: bottom;">"""+SP.PresDirektur.title()+"""</td>
                            <td style="border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">"""+SP.Acc.title()+"""</td>
                            <td style="border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">"""+SP.Dept_Acc.title()+"""</td>
                        </tr>
                        <tr style="height:10px;">
                            <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Marketing SPV</td>
                            <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Marketing Dept Head</td>
                            <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Bussiness Dev Div Head</td>
                            <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Pres Director</td>
                            <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Finance SPV</td>
                            <td style="border: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;">Finance Dept Head</td>
                        </tr>
                    </tbody>
                </table>
                """
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
                        <h2>PEMBUATAN HARGA PENJUALAN di SAP</h2>
                    </td>
                    <td style="width: 7%;">No. Document</td>
                    <td style="text-align: center;">:</td>
                    <td style="text-align: center; width: 7%;">FR-FACT.02.001</td>
                </tr>
                <tr>
                    <td>Revision</td>
                    <td style="text-align: center;">:</td>
                    <td style="text-align: center;">0</td>
                </tr>
                <tr>
                    <td>Effective Start</td>
                    <td style="text-align: center;">:</td>
                    <td style="text-align: center;">25 Agustus 2022</td>
                </tr>
            </table>
            <br>
            <table style="width: 100%; font-size: small;">
                <tr>
                <td style="width: 10%;">Cust Code</td>
                <td>:</td>
                <td>"""+str(SP.Cust_Code)+"""</td>
                </tr>
                <tr>
                <td style="width: 10%;">Cust Name</td>
                <td>:</td>
                <td>"""+str(SP.Cust_Name)+"""</td>
                </tr>
                <tr>
                <td style="width: 10%;">Dist Channel</td>
                <td>:</td>
                <td>"""+str(SP.Dist_Channel)+"""</td>
                </tr>
                <tr>
                <td style="width: 10%;">Submit Date</td>
                <td>:</td>
                <td>"""+str(SP.Submit_Date.strftime("%Y-%m-%d"))+"""</td>
                </tr>
                <tr>
                <td style="width: 10%;">No</td>
                <td>:</td>
                <td>"""+str(SP.SP_Number)+"""</td>
                </tr>
                <tr>
                <td style="width: 10%;">Product Status</td>
                <td>:</td>
                <td>"""+str(SP.Product_Status)+"""</td>
                </tr>
            </table>
        <table class="table-approve" style="width: 100%;">
        <thead>
            <tr style=" height: 50px; word-break: normal; border: 1px solid">
                <th rowspan="2" style="vertical-align: middle;">Type</th>
                <th rowspan="2" style="vertical-align: middle;">Material No</th>
                <th rowspan="2" style="vertical-align: middle;">Material Description</th>
                <th rowspan="2" style="vertical-align: middle; padding: 5px;">Customer Material</th>
                <th colspan="5">Old Price</th>
                <th colspan="5">New Price</th>
                <th rowspan="2" style="vertical-align: middle;">Ratio</th>
                <th rowspan="2" style="vertical-align: middle;">Note</th>
            </tr>
            <tr style="font-size: 12px;text-align: center;font-weight: normal; border: 1px solid">
                <th style="padding: 5px;">Price</th>
                <th style="padding: 5px;">Depreciation</th>
                <th style="padding: 5px;">Total</th>
                <th style="padding: 5px;">UoM</th>
                <th style="padding: 5px;">Valid From</th>
                <th style="padding: 5px;">Price</th>
                <th style="padding: 5px;">Depreciation</th>
                <th style="padding: 5px;">Total</th>
                <th style="padding: 5px;">UoM</th>
                <th style="padding: 5px;">Valid From</th>
            </tr>
        </thead>
        <tbody>
            """+contain+"""
        </tbody>
        </table>
        <br>
        <table>
            """+apptable+"""
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
    pdfkit.from_string(email_body, "Media\Price\\"+SP_Number +".pdf", configuration=config)
    models.SellingPrice.objects.filter(SP_Number=SP_Number).update(Status="Finished")

def pdf(request, ID):
    Generate(ID)
    return HttpResponse("it works!")

@login_required
@user_passes_test(is_memberaddasset)
def exportSPList (request):
    resource = resources.SellingPrice()
    dataset = resource.export()
    response = HttpResponse(dataset.xls, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="listSellingPrice.xls"'
    models.activity_log(user = request.user.username,SP_Number="",activity="export SP item list").save()
    return response

@login_required
@user_passes_test(is_memberaddasset)
def exportDetail(request,ID):
    SP_Number = ID
    resource = resources.PriceItem()
    dataset = resource.export(models.PriceItem.objects.filter(SP_Number=SP_Number))
    response = HttpResponse(dataset.xls, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=" Price_Item_'+ SP_Number +'.xls"'
    models.activity_log(user = request.user.username,SP_Number="",activity="export SP item list").save()
    return response