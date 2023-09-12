from django.shortcuts import render
from django.shortcuts import redirect
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from . import models
from . import forms
import datetime
from django.http import HttpResponse
from django.core import serializers
import pandas as pd
import os
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
import xlsxwriter
from io import BytesIO

def is_admin(user):
    return user.groups.filter(name='Admin').exists()

def is_membercreatecapex(user):
    return user.groups.filter(name='Allow_Create_Capex').exists()

def is_memberaddasset(user):
    return user.groups.filter(name='Allow_Add_Asset').exists()

# Create your views here.
@login_required
@user_passes_test(is_membercreatecapex)
def createCP(request):
    ListItem = []
    CP_Number = 'ASKICAPEX' + request.user.username + str(
        models.capex.objects.filter(
            CP_Number__contains=request.user.username, Status__isnull=False).exclude(
            CP_Number__contains='rev').count() + 1).zfill(5)
    CP = forms.Capex()
    CPItem = forms.CapexItem()
    CP.fields['CP_Number'].initial = CP_Number
    CP.fields['SPV_Submit'].initial = datetime.datetime.now()
    approval = list(models.Approval.objects.filter(user=request.user.username))
    data = serializers.serialize("json", models.Approval.objects.filter(user=request.user))

    if request.method == 'POST':
        models.activity_log(user = request.user.username,CP_Number=CP_Number,activity=request.POST).save()
        if 'CP_Form' in request.FILES:
            item = pd.read_excel(request.FILES['CP_Form'])
            ListItem = item.values.tolist()
            print(ListItem)
            item = pd.read_excel(request.FILES['CP_Form'], skiprows=22)
            CP.fields['Business_Unit'].initial = 'Astra Komponen Indonesia'
            CP.fields['Year'].initial = datetime.datetime.today().year +1
            CP.fields['Next_Year1'].initial = datetime.datetime.today().year + 2
            CP.fields['Next_Year2'].initial = datetime.datetime.today().year + 3
            CP.fields['Sum_Year'].initial = item['Year'].sum()
            CP.fields['Sum_NextYear1'].initial = item['Next_Year1'].sum()
            CP.fields['Sum_NextYear2'].initial = item['Next_Year2'].sum()

        if 'upload' in request.POST:
            if (models.capex.objects.filter(CP_Number__contains= request.user.username).filter(Year=datetime.date.today().year + 1, Status='Finished').exists()):
                print ("Capital Expenditure Request Form " + str(datetime.date.today().year+1 ) + " telah dibuat!")
                return redirect("/CP/Create/")
            else:
                print(request.POST)
                item = pd.read_excel(request.FILES['CP_Form'], skiprows=22)
                item['PROJECT'] = item['PROJECT'].fillna('-')
                item['Prioritas'] = item['Prioritas'].fillna('-')
                item['Alasan'] = item['Alasan'].fillna('-')
                item['Remarks'] = item['Remarks'].fillna('-')
                item['Year'] = item['Year'].fillna(0).map('{:,.0f}'.format).str.replace(',', '.')
                item['Next_Year1'] = item['Next_Year1'].fillna(0).map('{:,.0f}'.format).str.replace(',', '.')
                item['Next_Year2'] = item['Next_Year2'].fillna(0).map('{:,.0f}'.format).str.replace(',', '.')
                item['Jan'] = item['Jan'].fillna(0).map('{:,.0f}'.format).str.replace(',', '.')
                item['Feb'] = item['Feb'].fillna(0).map('{:,.0f}'.format).str.replace(',', '.')
                item['Mar'] = item['Mar'].fillna(0).map('{:,.0f}'.format).str.replace(',', '.')
                item['Apr'] = item['Apr'].fillna(0).map('{:,.0f}'.format).str.replace(',', '.')
                item['May'] = item['May'].fillna(0).map('{:,.0f}'.format).str.replace(',', '.')
                item['Jun'] = item['Jun'].fillna(0).map('{:,.0f}'.format).str.replace(',', '.')
                item['Jul'] = item['Jul'].fillna(0).map('{:,.0f}'.format).str.replace(',', '.')
                item['Aug'] = item['Aug'].fillna(0).map('{:,.0f}'.format).str.replace(',', '.')
                item['Sept'] = item['Sept'].fillna(0).map('{:,.0f}'.format).str.replace(',', '.')
                item['Oct'] = item['Oct'].fillna(0).map('{:,.0f}'.format).str.replace(',', '.')
                item['Nov'] = item['Nov'].fillna(0).map('{:,.0f}'.format).str.replace(',', '.')
                item['Dec'] = item['Dec'].fillna(0).map('{:,.0f}'.format).str.replace(',', '.')
                item['Sum_Year'] = item['Sum_Year'].fillna(0).map('{:,.0f}'.format).str.replace(',', '.')
                item['Sum_Next_Year1'] = item['Sum_Next_Year1'].fillna(0).map('{:,.0f}'.format).str.replace(',', '.')
                item['Sum_Next_Year2'] = item['Sum_Next_Year2'].fillna(0).map('{:,.0f}'.format).str.replace(',', '.')
                new_item = item.dropna(subset=['CAPEX_ITEM', 'Asset_Class'])
                news_item = new_item.fillna(0)
                print(news_item)
                ListItem = news_item.values.tolist()
                print(ListItem)
                if (models.cpitem.objects.filter(CP_Number=CP_Number).exists()):
                    models.cpitem.objects.filter(CP_Number=CP_Number).delete()
                    for row in ListItem:
                        item = models.cpitem(
                            CP_Number=CP_Number,
                            No = models.cpitem.objects.filter(CP_Number=CP_Number).count() + 1,
                            CP_Name = row[1],
                            Project = row[2],
                            Asset_Class = row[3],
                            Priority = row[4],
                            Reason = row[5],
                            Remarks = row[6],
                            Jan_payment = row[10],
                            Feb_payment = row[11],
                            Mar_payment = row[12],
                            April_payment = row[13],
                            May_payment = row[14],
                            Jun_payment = row[15],
                            Jul_payment = row[16],
                            Augst_payment = row[17],
                            Sept_payment = row[18],
                            Oct_payment = row[19],
                            Nov_payment = row[20],
                            Dec_payment = row[21],
                            Summary_Current_Year = row[22],
                            Summary_Next_Year1 = row[23],
                            Summary_Next_Year2 = row[24],
                            After_Current_Year = row[22],
                            After_Next_Year1 = row[23],
                            After_Next_Year2 = row[24],
                            Payment_Check1 = row[25],
                            Payment_Check2 = row[26],
                            Payment_Check3 = row[27],
                            Grup = 'Capex'
                        )
                        item.save()
                else:
                    for row in ListItem:
                        item = models.cpitem(
                            CP_Number=CP_Number,
                            No=models.cpitem.objects.filter(CP_Number=CP_Number).count() + 1,
                            CP_Name=row[1],
                            Project=row[2],
                            Asset_Class=row[3],
                            Priority=row[4],
                            Reason=row[5],
                            Remarks=row[6],
                            Jan_payment=row[10],
                            Feb_payment=row[11],
                            Mar_payment=row[12],
                            April_payment=row[13],
                            May_payment=row[14],
                            Jun_payment=row[15],
                            Jul_payment=row[16],
                            Augst_payment=row[17],
                            Sept_payment=row[18],
                            Oct_payment=row[19],
                            Nov_payment=row[20],
                            Dec_payment=row[21],
                            Summary_Current_Year=row[22],
                            Summary_Next_Year1=row[23],
                            Summary_Next_Year2=row[24],
                            After_Current_Year=row[22],
                            After_Next_Year1=row[23],
                            After_Next_Year2=row[24],
                            Payment_Check1=row[25],
                            Payment_Check2=row[26],
                            Payment_Check3=row[27],
                            Grup = 'Capex'
                        )
                        item.save()
        if 'Finish' in request.POST :
            print(request.POST)
            if (models.capex.objects.filter(CP_Number=CP_Number).exists()):
                CPform = forms.Capex(request.POST,instance=models.capex.objects.get(CP_Number=CP_Number))
            else:
                CPform = forms.Capex(request.POST)
            if CPform.is_valid():
                CPform.save()
            else:
                print(CPform.errors)
            ListItem = list(models.cpitem.objects.filter(CP_Number=request.POST['CP_Number']).order_by('id'))
            CP = models.capex.objects.get(CP_Number=request.POST['CP_Number'])
            approval = models.Approval.objects.get(SPV_Email=CP.SPV_Email)
            counter = 0
            contain = ''
            for item in ListItem:
                counter += 1
                contain += '''<tr style="height: 30px; font-size:12px; border-collapse: collapse; ">
                    <td style="border: 1px solid black; border-collapse: collapse; padding: 5px;">'''+str(item.No)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse; padding: 5px; text-align: left; white-space: nowrap;">'''+str(item.CP_Name)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse; padding: 5px; white-space: nowrap;">'''+str(item.Project)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse; padding: 5px; white-space: nowrap;">'''+str(item.Asset_Class)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse; padding: 5px; white-space: nowrap;">'''+str(item.Priority)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse; padding: 5px; white-space: nowrap;">'''+str(item.Reason)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse; padding: 5px; white-space: nowrap;">'''+str(item.Remarks)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.Summary_Current_Year)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.Summary_Next_Year1)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.Summary_Next_Year2)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.Jan_payment)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.Feb_payment)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.Mar_payment)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.April_payment)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.May_payment)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.Jun_payment)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.Jul_payment)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.Augst_payment)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.Sept_payment)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.Oct_payment)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.Nov_payment)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.Dec_payment)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.Summary_Current_Year)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.Summary_Next_Year1)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.Summary_Next_Year2)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.Payment_Check1)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.Payment_Check2)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.Payment_Check3)+'''</td>
                </tr>'''
            if approval.Dept_Head == None:
                apptable = """
                        <table style="font-size: 12px;text-align: center;border: 1px solid black;border-collapse: collapse;" >
                            <tbody >
                                <tr style="height:10px;border: 1px solid black;border-collapse: collapse;">
                                    <th style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Prepared By</th>
                                    <th style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Approved By</th>
                                </tr>
                                <tr style="height:40px; border: 1px solid black;border-collapse: collapse;">
                                    <td style="padding:20px;border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="SPV">Created """ + str(CP.SPV_Submit.strftime("%Y-%m-%d %H:%M:%S")) + """</td>
                                    <td style="padding:20px;text-align: center;vertical-align: bottom;font-style: italic;color: green;border: 1px solid black;border-collapse: collapse;" id="DIV"></td>
                                </tr>
                                <tr style="height:20px; border: 1px solid black;border-collapse: collapse;">
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">""" + approval.SPV.title() + """</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">""" + approval.Div_Head.title() + """</td>
                                </tr>
                                <tr style="height:10px; border: 1px solid black;border-collapse: collapse;">
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Supervisor</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Division Head</td>
                                </tr>
                            </tbody>
                        </table>
                        """
            elif approval.Div_Head == None:
                apptable = """
                        <table style="font-size: 12px;text-align: center;border: 1px solid black;border-collapse: collapse;" >
                            <tbody >
                                <tr style="height:10px;border: 1px solid black;border-collapse: collapse;">
                                    <th style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Prepared By</th>
                                    <th style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Approved By</th>
                                </tr>
                                <tr style="height:40px; border: 1px solid black;border-collapse: collapse;">
                                    <td style="padding:20px;border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="SPV">Created """ + str(CP.SPV_Submit.strftime("%Y-%m-%d %H:%M:%S")) + """</td>
                                    <td style="padding:20px;text-align: center;vertical-align: bottom;font-style: italic;color: green;border: 1px solid black;border-collapse: collapse;" id="DEPT"></td>
                                </tr>
                                <tr style="height:20px; border: 1px solid black;border-collapse: collapse;">
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">""" + approval.SPV.title() + """</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">""" + approval.Dept_Head.title() + """</td>
                                </tr>
                                <tr style="height:10px; border: 1px solid black;border-collapse: collapse;">
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Supervisor</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Department Head</td>
                                </tr>
                            </tbody>
                        </table>
                        """
            else:
                apptable = """
                        <table style="font-size: 12px;text-align: center;border: 1px solid black;border-collapse: collapse;" >
                            <tbody >
                                <tr style="height:10px;border: 1px solid black;border-collapse: collapse;">
                                    <th style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Prepared By</th>
                                    <th colspan="2" style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Approved By</th>
                                </tr>
                                <tr style="height:40px; border: 1px solid black;border-collapse: collapse;">
                                    <td style="padding:20px;border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="SPV">Created """ + str(CP.SPV_Submit.strftime("%Y-%m-%d %H:%M:%S")) + """</td>
                                    <td style="padding:20px;border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="DEPT"></td>
                                    <td style="padding:20px;text-align: center;vertical-align: bottom;font-style: italic;color: green;border: 1px solid black;border-collapse: collapse;" id="DIV"></td>
                                </tr>
                                <tr style="height:20px; border: 1px solid black;border-collapse: collapse;">
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">""" + approval.SPV.title() + """</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">""" + approval.Dept_Head.title() + """</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">""" + approval.Div_Head.title() + """</td>
                                </tr>
                                <tr style="height:10px; border: 1px solid black;border-collapse: collapse;">
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Supervisor</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Department Head</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Division Head</td>
                                </tr>
                            </tbody>
                        </table>
                        """
            if CP.Dept_Head == None:
                Superior = CP.Div_Head.title()
            else:
                Superior = CP.Dept_Head.title()
            email_body = """\
                        <html>
                        <head style="margin-bottom: 0px;">Dear Mr/Ms """ + Superior + """,</head>
                        <body>
                        <p style="margin-bottom: 0px;margin-top: 0px;">This Capital Expenditure needs your approval </>
                        <hr>
                        <table style="font-size: x-small; width: 100%">
                            <tr>
                                <td rowspan="3" style="width: 15%;  text-align: center; border-bottom: 1px solid black;"><h1>ASKI</h1></td>
                                <td rowspan="3" style="text-align: center;  border-bottom: 1px solid black;">
                                    <h3>CAPITAL EXPENDITURE REQUEST FORM</h3>
                                </td>
                            </tr>
                        </table>
                        <br>
                        <table style="width: 100%; font-size: x-small;">
                            <tr>
                            <td style="width: 10%;">Business Unit</td>
                            <td>:</td>
                            <td>""" + str(CP.Business_Unit) + """</td>
                            </tr>
                            <tr>
                            <td style="width: 10%;">Division</td>
                            <td>:</td>
                            <td>""" + str(CP.Division) + """</td>
                            </tr>
                            <tr>
                            <td style="width: 10%;">Department</td>
                            <td>:</td>
                            <td>""" + str(CP.Department) + """</td>
                            </tr>
                        </table>
                        <br>
                        <table style="width: 100%; border-collapse: collapse; font-size: 12px;text-align: center">
                        <thead >
                            <tr style=" height: 50px; word-break: normal; border: 1px solid">
                                <th rowspan="2" style="vertical-align: middle; border: 1px solid; padding: 5px; ">No</th>
                                <th rowspan="2" style="vertical-align: middle; border: 1px solid; padding: 5px; ">Capex Item</th>
                                <th rowspan="2" style="vertical-align: middle; border: 1px solid; padding: 5px; ">Project</th>
                                <th rowspan="2" style="vertical-align: middle; border: 1px solid; padding: 5px; ">Asset Class</th>
                                <th rowspan="2" style="vertical-align: middle; border: 1px solid; padding: 5px; ">Priority</th>
                                <th rowspan="2" style="vertical-align: middle; border: 1px solid; padding: 5px; ">Reason</th>
                                <th rowspan="2" style="vertical-align: middle; border: 1px solid; padding: 5px; ">Remarks</th>
                                <th colspan="3" style="vertical-align: middle; border: 1px solid; padding: 5px; ">Capex Capitalization (in million Rp)</th>
                                <th colspan="15" style="vertical-align: middle; border: 1px solid ">Capex Payment (in a million Rp)</th>
                                <th colspan="3" style="vertical-align: middle; border: 1px solid ">Payment Check</th>
                            </tr>
                            <tr style="border: 1px solid" >
                                <th style="padding: 5px; border: 1px solid">""" + str(CP.Year) + """</th>
                                <th style="padding: 5px; border: 1px solid">""" + str(CP.Next_Year1) + """</th>
                                <th style="padding: 5px; border: 1px solid">""" + str(CP.Next_Year2) + """</th>
                                <th style="padding: 5px; border: 1px solid">Jan</th>
                                <th style="padding: 5px; border: 1px solid">Feb</th>
                                <th style="padding: 5px; border: 1px solid">Mar</th>
                                <th style="padding: 5px; border: 1px solid">Apr</th>
                                <th style="padding: 5px; border: 1px solid">May</th>
                                <th style="padding: 5px; border: 1px solid">Jun</th>
                                <th style="padding: 5px; border: 1px solid">Jul</th>
                                <th style="padding: 5px; border: 1px solid">Aug</th>
                                <th style="padding: 5px; border: 1px solid">Sept</th>
                                <th style="padding: 5px; border: 1px solid">Oct</th>
                                <th style="padding: 5px; border: 1px solid">Nov</th>
                                <th style="padding: 5px; border: 1px solid">Dec</th>
                                <th style="padding: 5px; border: 1px solid">""" + str(CP.Year) + """</th>
                                <th style="padding: 5px; border: 1px solid">""" + str(CP.Next_Year1) + """</th>
                                <th style="padding: 5px; border: 1px solid">""" + str(CP.Next_Year2) + """</th>
                                <th style="padding: 5px; border: 1px solid">""" + str(CP.Year) + """</th>
                                <th style="padding: 5px; border: 1px solid">""" + str(CP.Next_Year1) + """</th>
                                <th style="padding: 5px; border: 1px solid">""" + str(CP.Next_Year2) + """</th>
                            </tr>
                        </thead>
                        <tbody>
                        """ + contain + """
                        </tbody>
                        </table>
                        <br>
                        <table>
                        <tr>
                            <td style="width:75%;">
                                """ + apptable + """
                            </td>
                        </tr>
                        </table>
                        <br>
                        <i>Please, see the attached document for the capex item detail.</i>
                        <br>
                        <hr>
                        <p> Please give your response by click approval button bellow and then click send button. A response at your earliest convenience would be much appreciated. </p>
                        <table width="100%" cellspacing="0" cellpadding="0">
                            <tr>
                                <td>
                                    <table cellspacing="0" cellpadding="0">
                                        <tr>
                                            <td style="border-radius: 2px;width : 150px;text-align: center;" bgcolor="#4bf542">
                                                <a href="mailto:online.approval@aski.component.astra.co.id?subject=Approve: """ + str(CP.CP_Number) + """&body=Approve Capital Expenditure Request with ID """ + str(CP.CP_Number) + """ %0DApproval Message:" target="_blank" style="padding: 8px 12px; border: 1px solid #4bf542;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #ffffff;text-decoration: none;font-weight:bold;display: inline-block;">
                                                    APPROVE
                                                </a>
                                            </td>
                                            <td>&nbsp;&nbsp;</td>
                                            <td style="border-radius: 2px;width: 150px;text-align: center;" bgcolor="#ebde34">
                                                <a href="mailto:online.approval@aski.component.astra.co.id?subject=Revise: """ + str(CP.CP_Number) + """&body=Need Revise Capital Expenditure Request with ID """ + str(CP.CP_Number) + """ %0DRevision Message:" target="_blank" style="padding: 8px 12px; border: 1px solid #ebde34;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #000000;text-decoration: none;font-weight:bold;display: inline-block;">
                                                    REVISE
                                                </a>
                                            </td>
                                            <td>&nbsp;&nbsp;</td>
                                            <td style="border-radius: 2px;width: 150px;text-align: center;" bgcolor="#cccccc">
                                                <a href="mailto:""" + str(CP.SPV_Email) + """?subject=Ask User: """ + str(CP.CP_Number) + """&body=Ask User about Capital Expenditure Request with ID """ + str(CP.CP_Number) + """ %0DAsk User Message: " target="_blank" style="padding: 8px 12px; border: 1px solid #cccccc;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #000000;text-decoration: none;font-weight:bold;display: inline-block;">
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
            filename = str(CP_Number)+".xlsx"
            excelfile = BytesIO()
            wb = xlsxwriter.Workbook(excelfile)
            ws = wb.add_worksheet('Capex')
            formathead = wb.add_format(
                {
                    "bold":1,
                    "border": 1,
                    "align": "center",
            }
            )
            font_style = wb.add_format(
                {
                    "border": 1,
                    "align": "center",
                    "fg_color": "yellow",
                    "bold":1,
            }
            )
            ws.merge_range("A1:AB1", 'PT. ASTRA KOMPONEN INDONESIA', formathead)
            ws.merge_range("A2:AB2", 'CAPITAL EXPENDITURE REQUEST FORM', formathead)
            ws.merge_range("A3:AB3", ' ')
            ws.merge_range("A4:AB4", ' ')

            row_num = 4
            header = ['BUSINESS UNIT', 'DIVISION', 'DEPARTMENT']
            col_num = 0
            for col_nums in range(len(header)):
                col_num += 1
                ws.write(row_num, col_num, header[col_nums], font_style)
            
            row_num = 5
            header_style = wb.add_format(
                {
                    "border": 1,
                    "align": "center",
            }
            )
            header = models.capex.objects.filter(CP_Number=CP_Number).values_list('Business_Unit', 'Division', 'Department')
            col_num = 0
            for row in header:
                for col_nums in range(len(row)):
                    col_num += 1
                    ws.write(row_num, col_num, row[col_nums], header_style)
            

            ws.merge_range("B9:C9", 'Asset Class', font_style)
            ws.merge_range("E9:F9", 'Alasan', font_style)
            ws.merge_range("H9:I9", 'Prioritas', font_style)

            body_style = wb.add_format(
                {
                    "border": 1,
                    "align": "center",
                    "fg_color": "#FF00FF",
            }
            )
            asset_class = (['20', 'Building',],['21','Building Eqp.'], ['30', 'Machinery Eqp'], ['40', 'Transportation'], ['50', 'Office Eqp.'], ['51', 'Furniture & Fixture'], ['60', 'Tools & Eqp.'], ['70', 'Asset under cap.lease'], ['80', 'Mold ISAK 8'])
            row_num = 9
            for row in asset_class:
                row_num +=1
                col_num = 0
                for col_nums in range(len(row)):
                    col_num += 1
                    ws.write(row_num, col_num, row[col_nums], body_style)

            reason = (['1', 'Penambahan'], ['2', 'Penggantian'], ['3', 'Model Baru'], ['4', 'Quality Control'], ['5', 'Local Comp'], ['6', 'Keselamatan Kerja'], ['7', 'Peningkatan Produk'], ['8', 'Others'])
            row = 9
            for row_reason in reason:
                row +=1
                col_num = 3
                for col_nums in range(len(row_reason)):
                    col_num +=1
                    ws.write(row, col_num, row_reason[col_nums], body_style)

            priority = (['H', 'HIGH'], ['M', 'MEDIUM'], ['L', 'Low'])
            row = 9
            for row_priority in priority:
                row +=1
                col_num = 6
                for col_nums in range(len(row_priority)):
                    col_num +=1
                    ws.write(row, col_num, row_priority[col_nums], body_style)

            
            ws.merge_range("A22:A23", 'No', font_style)
            ws.merge_range("B22:B23", 'CAPEX Item', font_style)
            ws.merge_range("C22:C23", 'Project', font_style)
            ws.merge_range("D22:D23", 'Asset Class', font_style)
            ws.merge_range("E22:E23", 'Priority', font_style)
            ws.merge_range("F22:F23", 'Reason', font_style)
            ws.merge_range("G22:G23", 'Remarks', font_style)
            ws.merge_range("H22:J22", 'Capex Capitalization (in million Rp)', font_style)
            ws.merge_range("K22:Y22", 'Capex Payment (in million Rp)', font_style)
            ws.merge_range("Z22:AB22", 'Payment Check', font_style)
            ws.write("H23", str(datetime.datetime.today().year+1), font_style)
            ws.write("I23", str(datetime.datetime.today().year+2), font_style)
            ws.write("J23", str(datetime.datetime.today().year+3), font_style)
            ws.write("K23", 'Jan-'+str(datetime.datetime.today().year+1)+'', font_style)
            ws.write("L23", 'Feb-'+str(datetime.datetime.today().year+1)+'', font_style)
            ws.write("M23", 'Mar-'+str(datetime.datetime.today().year+1)+'', font_style)
            ws.write("N23", 'April-'+str(datetime.datetime.today().year+1)+'', font_style)
            ws.write("O23", 'May-'+str(datetime.datetime.today().year+1)+'', font_style)
            ws.write("P23", 'Jun-'+str(datetime.datetime.today().year+1)+'', font_style)
            ws.write("Q23", 'Jul-'+str(datetime.datetime.today().year+1)+'', font_style)
            ws.write("R23", 'August-'+str(datetime.datetime.today().year+1)+'', font_style)
            ws.write("S23", 'Sept-'+str(datetime.datetime.today().year+1)+'', font_style)
            ws.write("T23", 'Oct-'+str(datetime.datetime.today().year+1)+'', font_style)
            ws.write("U23", 'Nov-'+str(datetime.datetime.today().year+1)+'', font_style)
            ws.write("V23", 'Dec-'+str(datetime.datetime.today().year+1)+'', font_style)
            ws.write("W23", str(datetime.datetime.today().year+1), font_style)
            ws.write("X23", str(datetime.datetime.today().year+2), font_style)
            ws.write("Y23", str(datetime.datetime.today().year+3), font_style)
            ws.write("Z23", str(datetime.datetime.today().year+1), font_style)
            ws.write("AA23", str(datetime.datetime.today().year+2), font_style)
            ws.write("AB23", str(datetime.datetime.today().year+3), font_style)

            ws.set_column('A:A', 4) 
            ws.set_column('B:B', 40)
            ws.set_column('C:C', 19)
            ws.set_column('D:D', 20)
            ws.set_column('E:E', 25)
            ws.set_column('F:F', 20)
            ws.set_column('G:G', 25)
            ws.set_column('H:H', 11)
            ws.set_column('I:I', 11)
            ws.set_column('J:J', 11)


            font_style = wb.add_format(
                {
                    "border": 1,
                    "align": "center",
            }
            )
            cpitem = models.cpitem.objects.filter(CP_Number=CP_Number).order_by('id').values_list('No', 'CP_Name', 'Project', 'Asset_Class', 'Priority', 'Reason', 'Remarks','Summary_Current_Year', 'Summary_Next_Year1', 'Summary_Next_Year2', 'Jan_payment', 'Feb_payment', 'Mar_payment', 'April_payment', 'May_payment', 'Jun_payment', 'Jul_payment', 'Augst_payment', 'Sept_payment', 'Oct_payment', 'Nov_payment', 'Dec_payment', 'Summary_Current_Year', 'Summary_Next_Year1', 'Summary_Next_Year2', 'Payment_Check1', 'Payment_Check2', 'Payment_Check3')
            row_num = 22
            for row in cpitem:
                row_num +=1
                for col_num in range(len(row)):
                    if col_num == 22:
                        ws.write_formula(row_num, col_num, "=SUM(K"+str(row_num+1)+":V"+str(row_num+1)+")", font_style, row[col_num])
                    elif col_num == 23:
                        ws.write_formula(row_num, col_num, "=I"+str(row_num+1)+"", font_style, row[col_num])
                    elif col_num == 24:
                        ws.write_formula(row_num, col_num, "=J"+str(row_num+1)+"", font_style, row[col_num])
                    elif col_num == 25:
                        ws.write_formula(row_num, col_num, '=IF(ROUND(H'+str(row_num+1)+'-W'+str(row_num+1)+',0)=0,"OK","Error")', font_style, row[col_num])
                    elif col_num == 26:
                        ws.write_formula(row_num, col_num, '=IF(ROUND(I'+str(row_num+1)+'-X'+str(row_num+1)+',0)=0,"OK","Error")', font_style, row[col_num])
                    elif col_num == 27:
                        ws.write_formula(row_num, col_num, '=IF(ROUND(J'+str(row_num+1)+'-Y'+str(row_num+1)+',0)=0,"OK","Error")', font_style, row[col_num])
                    else :
                        try :
                            ws.write(row_num, col_num, int(row[col_num].replace('.', '')), font_style)
                        except ValueError:
                            ws.write(row_num, col_num, row[col_num], font_style)
            
            wb.close()
            if CP.Dept_Head == None:
                Superior_Email = CP.Div_Head_Email
            else :
                Superior_Email = CP.Dept_Head_Email
            mailattach = EmailMessage(
                'Capital Expenditure Online Approval: ' +
                request.POST['CP_Number'],
                body=email_body, from_email=settings.EMAIL_HOST_USER,
                to=[Superior_Email],
            )
            mailattach.content_subtype = "html"
            mailattach.attach(filename, excelfile.getvalue(), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            mailattach.send()
            email = models.Send(
                htmlmessage=email_body,
                mailfrom='online.approval@aski.component.astra.co.id',
                mailto=Superior_Email,
                CP_Number=request.POST['CP_Number'],
                mailheader='Capital Expenditure Online Approval: ' + request.POST['CP_Number'])
            email.save()
            models.capex.objects.filter(CP_Number= CP_Number).update(Status="Created")
            models.cpitem.objects.filter(CP_Number= CP_Number).update(Item_Year=datetime.date.today().year + 1, Dept=request.POST['Dept'], PIC=request.POST['PIC'])
            return redirect("/CP/ListDept/")
    context = {
        'Judul': 'Create Capital Expenditure',
        'CPForm': CP,
        'CPItem': CPItem,
        'ListItem': ListItem,
        'CP_Number': CP_Number,
        'approval': approval,
        'Data': data,
    }
    return render(request, 'capitalexpenditure/Create.html', context)

@login_required
@user_passes_test(is_membercreatecapex)
def listCP(request):
    if (request.user.username == "admin"):
        ListCP = models.capex.objects.all()
    else:
        ListCP = models.capex.objects.filter(CP_Number__contains=request.user.username).order_by("-id")
    context = {
        'Judul': 'List Capex Department',
        'listcp': ListCP
    }
    return render(request, 'capitalexpenditure/ListDept.html', context)

@login_required
@user_passes_test(is_membercreatecapex)
def view(request, ID):
    CP_Number = ID
    CP = models.capex.objects.get(CP_Number=ID)
    ListItem = list(models.cpitem.objects.filter(CP_Number=ID).order_by('id'))
    context ={
        'Judul': 'Detail Capital Expenditure',
        'CP': CP,
        'CP_Number': CP_Number,
        'listcpitem': ListItem,
    }
    return render(request, 'capitalexpenditure/ViewDept.html', context)

@login_required
@user_passes_test(is_memberaddasset)
def filter(request):
    CP = models.capex(Year=datetime.date.today().year + 1, Next_Year1=datetime.date.today().year + 2, Next_Year2=datetime.date.today().year + 3  )
    if not (models.capex.objects.filter(Year=datetime.date.today().year + 1, Status='FinanceCheck')).exists():
        ListItem =[]
    else:
        ListItem = models.cpitem.objects.filter(Item_Year = datetime.date.today().year + 1).order_by('Dept')
    data = serializers.serialize("json", models.Approval.objects.filter(user=request.user))
    CPitem = models.cpitem.objects.filter(Item_Year=datetime.datetime.today().year+1)

    if request.method == 'POST':
        if 'Finish' in request.POST:
            models.activity_log(user = request.user.username,CP_Number=datetime.datetime.today().year+1,activity='Capex Filtering').save()
            print(request.POST)
            row = []
            Group = []
            After_Current_Year = []
            After_Next_Year1 = []
            After_Next_Year2 = []
            for data in request.POST.keys():
                if '|' in data:
                    if int(data.split('|')[1]) not in row:
                        row.append(int(data.split('|')[1]))
                    if 'Group' in data:
                        Group.append(request.POST[data])
                    if 'After_Current_Year' in data:
                        After_Current_Year.append(request.POST[data])
                    if 'After_Next_Year1' in data:
                        After_Next_Year1.append(request.POST[data])
                    if 'After_Next_Year2' in data:
                        After_Next_Year2.append(request.POST[data])
                   
            NewData = pd.DataFrame.from_dict({'id': row,
                            'Grup': Group,
                              'After_Current_Year' : After_Current_Year, 
                              'After_Next_Year1':After_Next_Year1,
                              'After_Next_Year2':After_Next_Year2 })
            OldData = pd.DataFrame(list(models.cpitem.objects.filter(Item_Year=datetime.datetime.today().year+1).order_by('id').values('id','Grup', 'After_Current_Year', 'After_Next_Year1', 'After_Next_Year2')))
            Compare = pd.concat([NewData,OldData],keys=["New","Old"]).drop_duplicates(keep=False)

            if len(Compare) > 0 :
                for i in Compare.loc["New"].index:
                    models.cpitem.objects.filter(id=Compare.loc["New"]["id"][i]).update(Grup=Compare.loc["New"]["Grup"][i], After_Current_Year=Compare.loc["New"]["After_Current_Year"][i], 
                                                                                        After_Next_Year1=Compare.loc["New"]["After_Next_Year1"][i], After_Next_Year2=Compare.loc["New"]["After_Next_Year2"][i])
                
                CapexGrup = CPitem.values('Dept','Grup', 'After_Current_Year', 'After_Next_Year1', 'After_Next_Year2')
                df = pd.DataFrame(CapexGrup)
                df['After_Current_Year'] = (df['After_Current_Year'].str.replace('.', '', regex=True)).astype(int)
                df['After_Next_Year1'] = (df['After_Next_Year1'].str.replace('.', '', regex=True)).astype(int)
                df['After_Next_Year2'] = (df['After_Next_Year2'].str.replace('.', '', regex=True)).astype(int)
                df2 = df.groupby(['Dept', 'Grup']).sum()
                for cal,row in df2.iterrows() :
                    print(cal[0],cal[1])
                    if cal[1] == 'Capex':
                        models.capex.objects.filter(Department=cal[0]).update(Sum_Capex_Year = row["After_Current_Year"], Sum_Capex_NextYear1= row['After_Next_Year1'],
                                                                                                             Sum_Capex_NextYear2 = row['After_Next_Year2'])
                    else :
                        models.capex.objects.filter(Department=cal[0]).update(Sum_Expense_Year = row["After_Current_Year"], Sum_Expense_NextYear1= row['After_Next_Year1'], 
                                                                                                                   Sum_Expense_NextYear2 = row['After_Next_Year2'])  
            return redirect("/CP/Summary/")                                                                             
    context = {
        'Judul': 'Filtering Capital Expenditure',
        'CP': CP,
        'ListItem': ListItem,
        'Data': data,
    }
    return render(request, 'capitalexpenditure/Filtering.html', context)

@login_required
@user_passes_test(is_memberaddasset)
def summary(request):
    CP = models.capex(Year=datetime.date.today().year + 1, Next_Year1=datetime.date.today().year + 2, Next_Year2=datetime.date.today().year + 3  )
    if not (models.capex.objects.filter(Year=datetime.date.today().year+1, Status="FinanceCheck", Div_Head_Approval_Status='Approved')).exists():
        listCP = []
        listCPlast = []
        listexpense = []
        listexpenselast = []
        CPtotal =[]
    else:
        CPitem = models.cpitem.objects.filter(Item_Year=datetime.datetime.today().year+1)
        CapexGrup = CPitem.values('Item_Year','Dept','Grup', 'After_Current_Year', 'After_Next_Year1', 'After_Next_Year2')
        df = pd.DataFrame(CapexGrup)
        df['After_Current_Year'] = (df['After_Current_Year'].str.replace('.', '', regex=True)).astype(int)
        df['After_Next_Year1'] = (df['After_Next_Year1'].str.replace('.', '', regex=True)).astype(int)
        df['After_Next_Year2'] = (df['After_Next_Year2'].str.replace('.', '', regex=True)).astype(int)

        summarycapex = df.query("Grup=='Capex'").groupby(['Grup','Dept']).sum(numeric_only=True).reset_index()
        totalcapex = summarycapex.groupby('Grup').sum(numeric_only=True).reset_index()
        data_capex = pd.concat([summarycapex, totalcapex])
        data_capex['After_Current_Year'] = (data_capex['After_Current_Year']).apply(lambda x: "{:,}".format(x).replace(",", "."))
        data_capex['After_Next_Year1'] = (data_capex['After_Next_Year1']).apply(lambda x: "{:,}".format(x).replace(",", "."))
        data_capex['After_Next_Year2'] = (data_capex['After_Next_Year2']).apply(lambda x: "{:,}".format(x).replace(",", "."))
        CPcapex = data_capex.drop('Grup', axis=1).fillna('Capex Total').values.tolist()
        listCP = CPcapex[0:-1]
        listCPlast = CPcapex[len(CPcapex)-1:]

        summaryexpense = df.query("Grup=='Expense'").groupby(['Grup','Dept']).sum(numeric_only=True).reset_index()
        totalexpense = summaryexpense.groupby('Grup').sum(numeric_only=True).reset_index()
        data_expense = pd.concat([summaryexpense,totalexpense])
        data_expense['After_Current_Year'] = (data_expense['After_Current_Year']).apply(lambda x: "{:,}".format(x).replace(",", "."))
        data_expense['After_Next_Year1'] = (data_expense['After_Next_Year1']).apply(lambda x: "{:,}".format(x).replace(",", "."))
        data_expense['After_Next_Year2'] = (data_expense['After_Next_Year2']).apply(lambda x: "{:,}".format(x).replace(",", "."))
        CPexpense = data_expense.drop('Grup', axis=1).fillna('Expense Total').values.tolist()
        listexpense = CPexpense[0:-1]
        listexpenselast = CPexpense[len(CPexpense)-1:]

        grand_total = df.groupby('Item_Year').sum(numeric_only=True).reset_index()
        grand_total['Item_Year'] = 'Grand Total'
        grand_total['After_Current_Year'] = (grand_total['After_Current_Year']).apply(lambda x: "{:,}".format(x).replace(",", "."))
        grand_total['After_Next_Year1'] = (grand_total['After_Next_Year1']).apply(lambda x: "{:,}".format(x).replace(",", "."))
        grand_total['After_Next_Year2'] = (grand_total['After_Next_Year2']).apply(lambda x: "{:,}".format(x).replace(",", "."))
        CPtotal = grand_total.values.tolist()

    if request.method == 'POST':
        if 'Finish' in request.POST:
            ListItem = CPcapex
            Listitem = CPexpense
            ListAll = CPtotal
            countercapex = 0
            containcapex = ''
            for item in ListItem[0:-1]:
                containcapex += '''
                <tr style="height: 30px; font-size:12px; border-collapse: collapse;">
                '''
                for i in item :
                    countercapex += 1
                    containcapex +='''
                    <td style="text-align: center; border: 1px solid black; border-collapse: collapse;">'''+ str(i) +'''</td>
                    '''
                '''
                </tr>
                ''' 
            for item in ListItem[len(ListItem) - 1:]:
                containcapex += '''
                <tr style="height: 30px; font-size:12px; border-collapse: collapse;">
                '''
                for i in item :
                    countercapex += 1
                    containcapex +='''
                    <td style="text-align: center; border: 1px solid black; border-collapse: collapse;font-weight: bold;">'''+ str(i) +'''</td>
                    '''
                '''
                </tr>
                '''

            counterexpense = 0
            containexpense = ''
            for item in Listitem[0:-1]:
                containexpense += '''
                <tr style="height: 30px; font-size:12px; border-collapse: collapse;">
                '''
                for i in item :
                    counterexpense += 1
                    containexpense +='''
                    <td style="text-align: center; border: 1px solid black; border-collapse: collapse;">'''+ str(i) +'''</td>
                    '''
                '''
                </tr>
                ''' 
            for item in Listitem[len(Listitem) - 1:]:
                containexpense += '''
                <tr style="height: 30px; font-size:12px; border-collapse: collapse;">
                '''
                for i in item :
                    counterexpense += 1
                    containexpense +='''
                    <td style="text-align: center; border: 1px solid black; border-collapse: collapse;font-weight: bold;">'''+ str(i) +'''</td>
                    '''
                '''
                </tr>
                '''

            countergrand = 0
            containgrand = ''
            for item in ListAll:
                containgrand += '''
                <tr style="height: 30px; font-size:12px; border-collapse: collapse;">
                '''
                for i in item :
                    countergrand += 1
                    containgrand +='''
                    <td style="text-align: center; border: 1px solid black; border-collapse: collapse; font-weight: bold;">'''+ str(i) +'''</td>
                    '''
                '''
                </tr>
                ''' 
                    
            Superior = 'Prihartanto'
            email_body = """\
                        <html>
                        <head style="margin-bottom: 0px;">Dear Mr """ + Superior + """,</head>
                        <body>
                        <p style="margin-bottom: 0px;margin-top: 0px;">This Capital Expenditure needs your approval </>
                        <hr>
                        <table style="font-size: x-small; width: 100%">
                            <tr>
                                <td rowspan="3" style="width: 15%;  text-align: center; border-bottom: 1px solid black;"><h1>ASKI</h1></td>
                                <td rowspan="3" style="text-align: center;  border-bottom: 1px solid black;">
                                    <h3>CAPITAL EXPENDITURE SUMMARY</h3>
                                </td>
                            </tr>
                        </table>
                        <br>
                        <table style="width: 100%; font-size: x-small;">
                            <tr>
                            <td style="width: 10%;">Business Unit</td>
                            <td>:</td>
                            <td>Astra Komponen Indonesia</td>
                            </tr>
                            <tr>
                            <td style="width: 10%;">Division</td>
                            <td>:</td>
                            <td>ALL</td>
                            </tr>
                            <tr>
                            <td style="width: 10%;">Department</td>
                            <td>:</td>
                            <td>ALL</td>
                            </tr>
                        </table>
                        <br>
                        <div>Summary of Capex</div>
                        <table style="width: 100%; border-collapse: collapse; font-size: 12px;text-align: center">
                            <thead>
                                <tr style=" height: 50px; word-break: normal; border: 1px solid">
                                    <th rowspan="2" style="vertical-align: middle; border: 1px solid ">Department</th>
                                    <th colspan="3" style="vertical-align: middle; border: 1px solid ">Data</th>
                                </tr>
                                <tr>
                                    <td style="padding: 5px; border: 1px solid">Sum of """ + str(datetime.datetime.today().year+1) + """</td>
                                    <td style="padding: 5px; border: 1px solid">Sum of """ + str(datetime.datetime.today().year+2) + """</td>
                                    <td style="padding: 5px; border: 1px solid">Sum of """ + str(datetime.datetime.today().year+3) + """</td>
                                </tr>
                            </thead>
                            <tbody>
                                """+containcapex+"""
                            </tbody>
                        </table>
                        <br>
                        <div>Summary of Expense</div>
                        <table style="width: 100%; border-collapse: collapse; font-size: 12px;text-align: center">
                            <thead>
                                <tr style=" height: 50px; word-break: normal; border: 1px solid">
                                    <th rowspan="2" style="vertical-align: middle; border: 1px solid ">Department</th>
                                    <th colspan="3" style="vertical-align: middle; border: 1px solid ">Data</th>
                                </tr>
                                <tr>
                                    <td style="padding: 5px; border: 1px solid">Sum of """ + str(datetime.datetime.today().year+1) + """</td>
                                    <td style="padding: 5px; border: 1px solid">Sum of """ + str(datetime.datetime.today().year+2) + """</td>
                                    <td style="padding: 5px; border: 1px solid">Sum of """ + str(datetime.datetime.today().year+3) + """</td>
                                </tr>
                            </thead>
                            <tbody>
                                """+containexpense+"""
                            </tbody>
                        </table>
                        <br>
                        <div>Grand Total</div>
                        <table style="width: 100%; border-collapse: collapse; font-size: 12px;text-align: center">
                            <thead>
                                <tr style=" height: 50px; word-break: normal; border: 1px solid">
                                    <th rowspan="2" style="vertical-align: middle; border: 1px solid ">Department</th>
                                    <th colspan="3" style="vertical-align: middle; border: 1px solid ">Data</th>
                                </tr>
                                <tr>
                                    <td style="padding: 5px; border: 1px solid">Sum of """ + str(datetime.datetime.today().year+1) + """</td>
                                    <td style="padding: 5px; border: 1px solid">Sum of """ + str(datetime.datetime.today().year+2) + """</td>
                                    <td style="padding: 5px; border: 1px solid">Sum of """ + str(datetime.datetime.today().year+3) + """</td>
                                </tr>
                            </thead>
                            <tbody>
                                """+containgrand+"""
                            </tbody>
                        </table>
                        <br>
                        <i>Please, see the attached document for the capex item detail from each department.</i>
                        <br>
                        <hr>
                        <p> Please give your response by click approval button bellow and then click send button. A response at your earliest convenience would be much appreciated. </p>
                        <table width="100%" cellspacing="0" cellpadding="0">
                            <tr>
                                <td>
                                    <table cellspacing="0" cellpadding="0">
                                        <tr>
                                            <td style="border-radius: 2px;width : 150px;text-align: center;" bgcolor="#4bf542">
                                                <a href="mailto:online.approval@aski.component.astra.co.id?subject=Approve: ASKICAPEX""" + str(datetime.datetime.today().year+1) + """&body=Approve Capital Expenditure Request with ID ASKICAPEX""" + str(datetime.datetime.today().year+1) + """ %0DApproval Message:" target="_blank" style="padding: 8px 12px; border: 1px solid #4bf542;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #ffffff;text-decoration: none;font-weight:bold;display: inline-block;">
                                                    APPROVE
                                                </a>
                                            </td>
                                            <td>&nbsp;&nbsp;</td>
                                            <td style="border-radius: 2px;width: 150px;text-align: center;" bgcolor="#ebde34">
                                                <a href="mailto:online.approval@aski.component.astra.co.id?subject=Revise: ASKICAPEX""" + str(datetime.datetime.today().year+1) + """&body=Need Revise Capital Expenditure Request with ID ASKICAPEX""" + str(datetime.datetime.today().year+1) + """ %0DRevision Message:" target="_blank" style="padding: 8px 12px; border: 1px solid #ebde34;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #000000;text-decoration: none;font-weight:bold;display: inline-block;">
                                                    REVISE
                                                </a>
                                            </td>
                                            <td>&nbsp;&nbsp;</td>
                                            <td style="border-radius: 2px;width: 150px;text-align: center;" bgcolor="#cccccc">
                                                <a href="mailto:anistaprafitri@aski.component.astra.co.id?subject=Ask User: ASKICAPEX""" + str(datetime.datetime.today().year+1) + """&body=Ask User about Capital Expenditure Request with ID ASKICAPEX""" + str(datetime.datetime.today().year+1) + """ %0DAsk User Message: " target="_blank" style="padding: 8px 12px; border: 1px solid #cccccc;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #000000;text-decoration: none;font-weight:bold;display: inline-block;">
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
            
            filename = "ASKICAPEX"+str(datetime.datetime.today().year+1)+".xls"
            excelfile = BytesIO()
            wb = xlsxwriter.Workbook(excelfile)
            ws = wb.add_worksheet('Capex')
            formathead = wb.add_format(
                {
                    "bold":1,
                    "border": 1,
                    "align": "center",
            }
            )
            font_style = wb.add_format(
                {
                    "border": 1,
                    "align": "center",
                    "fg_color": "yellow",
                    "bold":1,
            }
            )
            ws.merge_range("A1:AN1", 'PT. ASTRA KOMPONEN INDONESIA', formathead)
            ws.merge_range("A2:AN2", 'CAPITAL EXPENDITURE REQUEST FORM', formathead)
            ws.merge_range("A3:AN3", ' ')
            ws.merge_range("A4:AN4", ' ')

            row_num = 4
            header = ['BUSINESS UNIT', 'DIVISION', 'DEPARTMENT']
            col_num = 0
            for col_nums in range(len(header)):
                col_num += 1
                ws.write(row_num, col_num, header[col_nums], font_style)
            
            row_num = 5
            header_style = wb.add_format(
                {
                    "border": 1,
                    "align": "center",
            }
            )
            header = ['ASKI', 'ALL', 'ALL']
            col_num = 0
            for col_nums in range(len(header)):
                col_num += 1
                ws.write(row_num, col_num, header[col_nums], header_style)
            

            ws.merge_range("B9:C9", 'Asset Class', font_style)
            ws.merge_range("E9:F9", 'Alasan', font_style)
            ws.merge_range("H9:I9", 'Prioritas', font_style)

            body_style = wb.add_format(
                {
                    "border": 1,
                    "align": "center",
                    "fg_color": "#FF00FF",
            }
            )
            asset_class = (['20', 'Building',],['21','Building Eqp.'], ['30', 'Machinery Eqp'], ['40', 'Transportation'], ['50', 'Office Eqp.'], ['51', 'Furniture & Fixture'], ['60', 'Tools & Eqp.'], ['70', 'Asset under cap.lease'], ['80', 'Mold ISAK 8'])
            row_num = 9
            for row in asset_class:
                row_num +=1
                col_num = 0
                for col_nums in range(len(row)):
                    col_num += 1
                    ws.write(row_num, col_num, row[col_nums], body_style)

            reason = (['1', 'Penambahan'], ['2', 'Penggantian'], ['3', 'Model Baru'], ['4', 'Quality Control'], ['5', 'Local Comp'], ['6', 'Keselamatan Kerja'], ['7', 'Peningkatan Produk'], ['8', 'Others'])
            row = 9
            for row_reason in reason:
                row +=1
                col_num = 3
                for col_nums in range(len(row_reason)):
                    col_num +=1
                    ws.write(row, col_num, row_reason[col_nums], body_style)

            priority = (['H', 'HIGH'], ['M', 'MEDIUM'], ['L', 'Low'])
            row = 9
            for row_priority in priority:
                row +=1
                col_num = 6
                for col_nums in range(len(row_priority)):
                    col_num +=1
                    ws.write(row, col_num, row_priority[col_nums], body_style)

            
            ws.merge_range("A22:A24", 'No', font_style)
            ws.merge_range("B22:B24", 'CAPEX Item', font_style)
            ws.merge_range("C22:C24", 'Grup', font_style)
            ws.merge_range("D22:D24", 'Dept', font_style)
            ws.merge_range("E22:E24", 'PIC', font_style)
            ws.merge_range("F22:F24", 'Project', font_style)
            ws.merge_range("G22:G24", 'Asset Class', font_style)
            ws.merge_range("H22:H24", 'Priority', font_style)
            ws.merge_range("I22:I24", 'Reason', font_style)
            ws.merge_range("J22:J24", 'Remarks', font_style)
            ws.merge_range("K22:P22", 'Capex Capitalization (in million Rp)', font_style)
            ws.merge_range("Q22:AH22", 'Capex Payment (in million Rp)', font_style)
            ws.merge_range("AI22:AK22", 'Payment Check', font_style)
            ws.merge_range("AL22:AN22", 'Payment Approval', font_style)
            ws.merge_range("K23:L23", str(datetime.datetime.today().year+1), font_style)
            ws.merge_range("M23:N23", str(datetime.datetime.today().year+2), font_style)
            ws.merge_range("O23:P23", str(datetime.datetime.today().year+3), font_style)
            ws.merge_range("AC23:AD23", str(datetime.datetime.today().year+1), font_style)
            ws.merge_range("AE23:AF23", str(datetime.datetime.today().year+2), font_style)
            ws.merge_range("AG23:AH23", str(datetime.datetime.today().year+3), font_style)
            ws.merge_range("Q23:Q24", 'Jan-'+str(datetime.datetime.today().year+1)+'', font_style)
            ws.merge_range("R23:R24", 'Feb-'+str(datetime.datetime.today().year+1)+'', font_style)
            ws.merge_range("S23:S24", 'Mar-'+str(datetime.datetime.today().year+1)+'', font_style)
            ws.merge_range("T23:T24", 'April-'+str(datetime.datetime.today().year+1)+'', font_style)
            ws.merge_range("U23:U24", 'May-'+str(datetime.datetime.today().year+1)+'', font_style)
            ws.merge_range("V23:V24", 'Jun-'+str(datetime.datetime.today().year+1)+'', font_style)
            ws.merge_range("W23:W24", 'Jul-'+str(datetime.datetime.today().year+1)+'', font_style)
            ws.merge_range("X23:X24", 'Aug-'+str(datetime.datetime.today().year+1)+'', font_style)
            ws.merge_range("Y23:Y24", 'Sept-'+str(datetime.datetime.today().year+1)+'', font_style)
            ws.merge_range("Z23:Z24", 'Oct-'+str(datetime.datetime.today().year+1)+'', font_style)
            ws.merge_range("AA23:AA24", 'Nov-'+str(datetime.datetime.today().year+1)+'', font_style)
            ws.merge_range("AB23:AB24", 'Dec-'+str(datetime.datetime.today().year+1)+'', font_style)
            ws.merge_range("AI23:AI24", str(datetime.datetime.today().year+1), font_style)
            ws.merge_range("AJ23:AJ24", str(datetime.datetime.today().year+2), font_style)
            ws.merge_range("AK23:AK24", str(datetime.datetime.today().year+3), font_style)
            ws.merge_range("AL23:AL24", str(datetime.datetime.today().year+1), font_style)
            ws.merge_range("AM23:AM24", str(datetime.datetime.today().year+2), font_style)
            ws.merge_range("AN23:AN24", str(datetime.datetime.today().year+3), font_style)

            ws.set_column('A:A', 4) 
            ws.set_column('B:B', 40)
            ws.set_column('C:C', 15)
            ws.set_column('D:D', 18)
            ws.set_column('E:E', 25)
            ws.set_column('F:F', 20)
            ws.set_column('G:G', 25)
            ws.set_column('H:H', 25)
            ws.set_column('I:I', 25)
            ws.set_column('J:J', 25)
            
            row_num = 23
            columns_7 = ['Before', 'After', 'Before', 'After', 'Before', 'After']
            col_num = 9
            for col_nums in range(len(columns_7)):
                col_num += 1
                ws.write(row_num, col_num, columns_7[col_nums], font_style)

            row_num = 23
            columns_26 = ['Before', 'After', 'Before', 'After', 'Before', 'After']
            col = 27
            for column in range(len(columns_26)):
                col += 1
                ws.write(row_num, col, columns_26[column], font_style)

            font_style = wb.add_format(
                {
                    "border": 1,
                    "align": "center",
            }
            )
            cpitem = models.cpitem.objects.filter(Item_Year=datetime.datetime.today().year+1).order_by('id').values_list('No', 'CP_Name', 'Grup', 'Dept', 'PIC', 'Project', 'Asset_Class', 'Priority', 'Reason', 'Remarks','Summary_Current_Year', 'After_Current_Year', 'Summary_Next_Year1', 'After_Next_Year1','Summary_Next_Year2', 'After_Next_Year2', 'Jan_payment', 'Feb_payment', 'Mar_payment', 'April_payment', 'May_payment', 'Jun_payment', 'Jul_payment', 'Augst_payment', 'Sept_payment', 'Oct_payment', 'Nov_payment', 'Dec_payment', 'Summary_Current_Year', 'After_Current_Year', 'Summary_Next_Year1', 'After_Next_Year1','Summary_Next_Year2', 'After_Next_Year2', 'Payment_Check1', 'Payment_Check2', 'Payment_Check3')
            row_num = 23
            for row in cpitem:
                row_num +=1
                for col_num in range(len(row)+3):
                    if col_num == 28:
                        ws.write_formula(row_num, col_num, "=SUM(Q"+str(row_num+1)+":AB"+str(row_num+1)+")", font_style, row[col_num])
                    elif col_num == 29:
                        ws.write_formula(row_num, col_num, "=L"+str(row_num+1)+"", font_style, row[col_num])
                    elif col_num == 30:
                        ws.write_formula(row_num, col_num, "=M"+str(row_num+1)+"", font_style, row[col_num])
                    elif col_num == 31:
                        ws.write_formula(row_num, col_num, "=N"+str(row_num+1)+"", font_style, row[col_num])
                    elif col_num == 32:
                        ws.write_formula(row_num, col_num, "=O"+str(row_num+1)+"", font_style, row[col_num])
                    elif col_num == 33:
                        ws.write_formula(row_num, col_num, "=P"+str(row_num+1)+"", font_style, row[col_num])
                    elif col_num == 34:
                        ws.write_formula(row_num, col_num, '=IF(ROUND(K'+str(row_num+1)+'-AC'+str(row_num+1)+',0)=0,"OK","Error")', font_style, row[col_num])
                    elif col_num == 35:
                        ws.write_formula(row_num, col_num, '=IF(ROUND(M'+str(row_num+1)+'-AE'+str(row_num+1)+',0)=0,"OK","Error")', font_style, row[col_num])
                    elif col_num == 36:
                        ws.write_formula(row_num, col_num, '=IF(ROUND(O'+str(row_num+1)+'-AG'+str(row_num+1)+',0)=0,"OK","Error")', font_style, row[col_num])
                    elif col_num == 37:
                        ws.write_formula(row_num, col_num, '=IF(ROUND(L'+str(row_num+1)+'-AD'+str(row_num+1)+',0)=0,"OK","Error")', font_style,('OK' if row[11]==row[29] else 'Error'))
                    elif col_num == 38:
                        ws.write_formula(row_num, col_num, '=IF(ROUND(N'+str(row_num+1)+'-AF'+str(row_num+1)+',0)=0,"OK","Error")', font_style, ('OK' if row[13]==row[31] else 'Error'))
                    elif col_num == 39:
                        ws.write_formula(row_num, col_num, '=IF(ROUND(P'+str(row_num+1)+'-AH'+str(row_num+1)+',0)=0,"OK","Error")', font_style, ('OK' if row[15]==row[33] else 'Error'))
                    else :
                        try :
                            ws.write(row_num, col_num, int(row[col_num].replace('.', '')), font_style)
                        except ValueError:
                            ws.write(row_num, col_num, row[col_num], font_style)
            
            wb.close()
            mailattach = EmailMessage(
                'Capital Expenditure Online Approval: ASKICAPEX' +
                str(datetime.datetime.today().year+1),
                body=email_body, from_email=settings.EMAIL_HOST_USER,
                to=['noreply.catu@gmail.com'],
            )
            mailattach.content_subtype = "html"
            mailattach.attach(filename, excelfile.getvalue(), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            mailattach.send()
            email = models.Send(
                htmlmessage=email_body,
                mailfrom='online.approval@aski.component.astra.co.id',
                mailto='noreply.catu@gmail.com',
                CP_Number='ASKICAPEX' + str(datetime.datetime.today().year+1),
                mailheader='Capital Expenditure Online Approval: ASKICAPEX' + str(datetime.datetime.today().year+1))
            email.save()
            models.capex.objects.filter(Year=datetime.datetime.today().year+1).update(Status="Waiting Approval")
            return redirect("/CP/Filter/")
        
    context ={
        'CP': CP,
        'listCP' : listCP,
        'listCPlast' : listCPlast,
        'listexpense': listexpense,
        'listexpenselast': listexpenselast,
        'listtotal': CPtotal,
    }
    return render(request, 'capitalexpenditure/Summary.html', context)

@login_required
@user_passes_test(is_memberaddasset)
def listAll(request):
    ListCP = models.capex.objects.filter(Status__isnull=False).order_by("-id")
    context = {
        'Judul': 'List Capital Expenditure',
        'listcp': ListCP,
    }
    return render(request, 'capitalexpenditure/ListCapex.html', context)

@login_required
@user_passes_test(is_memberaddasset)
def viewAll(request, ID):
    CP_Number = ID
    CP = models.capex.objects.get(CP_Number=ID)
    listcapex = list(models.cpitem.objects.filter(CP_Number=ID, Grup='Capex'))
    listexpense = list(models.cpitem.objects.filter(CP_Number=ID, Grup='Expense'))
    context ={
        'Judul': 'Detail Capital Expenditure',
        'CP': CP,
        'CP_Number': CP_Number,
        'listcapex': listcapex,
        'listexpense': listexpense,
    }
    return render(request, 'capitalexpenditure/View.html', context)

@login_required
@user_passes_test(is_membercreatecapex)
def revise(request, ID):
    CP_Number = ID

    cpitem = forms.CapexItem()
    CP = models.capex.objects.get(CP_Number = CP_Number)
    approval = models.Approval.objects.get(SPV_Email=CP.SPV_Email)
    if request.method == "GET" :
        if models.capex.objects.filter(CP_Number = CP_Number).exists():
            CP.Dept_Head_Approval_Date = None
            CP.Dept_Head_Approval_Status = None
            CP.Div_Head_Approval_Date = None
            CP.Div_Head_Approval_Status = None
            CP.PresDirektur_Approval_Date = None
            CP.PresDirektur_Approval_Status = None
            CP.Status = None
            CP.save()
    cpitem.fields['CP_Number'].initial = CP_Number
    cpitem.fields['No'].initial = models.cpitem.objects.filter(CP_Number = cpitem.fields['CP_Number'].initial).count() + 1
    cpitem.fields['Dept'].initial = CP.Department
    if CP.Dept_Head == None:
        cpitem.fields['PIC'].initial = CP.Div_Head
    else:
        cpitem.fields['PIC'].initial = CP.Dept_Head
    cpitem.fields['Item_Year'].initial = CP.Year
    ListItem = list(models.cpitem.objects.filter(CP_Number=CP_Number).order_by('id'))
    if request.method == "POST":
        print(request.POST)
        models.activity_log(user=request.user)
        if 'Delete' in request.POST:
            models.cpitem.objects.filter(CP_Number = CP_Number, id = request.POST["Delete"]).delete()
        elif 'save' in request.POST:
            models.cpitem.objects.filter(CP_Number = CP_Number, CP_Name=request.POST['NameEdit']).update(Project=request.POST['ProjectEdit'],
            Asset_Class=request.POST['Asset_ClassEdit'], Reason=request.POST['ReasonEdit'], Remarks=request.POST['RemarksEdit'], 
            Summary_Current_Year=request.POST['Summary_Current_YearEdit'], Summary_Next_Year1=request.POST['Summary_Next_Year1Edit'],
            Summary_Next_Year2=request.POST['Summary_Next_Year2Edit'], Jan_payment=request.POST['JanEdit'], Feb_payment=request.POST['FebEdit'], 
            Mar_payment=request.POST['MarEdit'], April_payment=request.POST['AprEdit'], May_payment=request.POST['MayEdit'], Jun_payment=request.POST['JunEdit'],
            Jul_payment=request.POST['JulEdit'], Augst_payment=request.POST['AgsEdit'], Sept_payment=request.POST['SepEdit'], Oct_payment=request.POST['OctEdit'],
            Nov_payment=request.POST['NovEdit'], Dec_payment=request.POST['DecEdit'], Payment_Check1=request.POST['Payment_Check1Edit'], 
            Payment_Check2=request.POST['Payment_Check2Edit'], Payment_Check3=request.POST['Payment_Check3Edit'])
        elif 'add' in request.POST:
            cpitemsave = forms.CapexItem(request.POST)
            if cpitemsave.is_valid() and models.cpitem.objects.filter(CP_Number=request.POST['CP_Number'], CP_Name=request.POST['CP_Name'], Remarks=request.POST['Remarks']).count() == 0:
                cpitemsave.save()
            else:
                print(cpitemsave.errors)
        elif 'Finish' in request.POST:
            print("finish")
            Sum = models.cpitem.objects.filter(CP_Number=CP_Number).values('Summary_Current_Year', 'Summary_Next_Year1', 'Summary_Next_Year2')
            df = pd.DataFrame(Sum)
            df['Summary_Current_Year'] = (df['Summary_Current_Year'].str.replace('.', '', regex=True)).astype(int)
            df['Summary_Next_Year1'] = (df['Summary_Next_Year1'].str.replace('.', '', regex=True)).astype(int)
            df['Summary_Next_Year2'] = (df['Summary_Next_Year2'].str.replace('.', '', regex=True)).astype(int)
            CPsave = forms.Capex(request.POST, instance=CP)
            if CPsave.is_valid():
                CPsave.SPV_Submit = datetime.datetime.now()
                CP.SPV_Submit = datetime.datetime.now()
                CP.Sum_Year = df['Summary_Current_Year'].sum()
                CP.Sum_NextYear1 = df['Summary_Next_Year1'].sum()
                CP.Sum_NextYear2 = df['Summary_Next_Year2'].sum()
                if CP.Revision == None:
                    CP.Revision = 1
                else:
                    CP.Revision = str(int(CP.Revision)+1)
                CPsave.save()
            else:
                print(CPsave.errors)
            CP = models.capex.objects.get(CP_Number = request.POST['CP_Number'])
            counter = 0
            contain = ''
            for item in ListItem:
                counter += 1
                contain += '''<tr style="height: 30px; font-size:12px; border-collapse: collapse; ">
                    <td style="border: 1px solid black; border-collapse: collapse; padding: 5px;">'''+str(counter)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse; padding: 5px; text-align: left; white-space: nowrap;">'''+str(item.CP_Name)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse; padding: 5px; white-space: nowrap;">'''+str(item.Project)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse; padding: 5px; white-space: nowrap;">'''+str(item.Asset_Class)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse; padding: 5px; white-space: nowrap;">'''+str(item.Priority)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse; padding: 5px; white-space: nowrap;">'''+str(item.Reason)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse; padding: 5px; white-space: nowrap;">'''+str(item.Remarks)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.Summary_Current_Year)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.Summary_Next_Year1)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.Summary_Next_Year2)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.Jan_payment)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.Feb_payment)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.Mar_payment)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.April_payment)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.May_payment)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.Jun_payment)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.Jul_payment)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.Augst_payment)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.Sept_payment)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.Oct_payment)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.Nov_payment)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.Dec_payment)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.Summary_Current_Year)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.Summary_Next_Year1)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.Summary_Next_Year2)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.Payment_Check1)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.Payment_Check2)+'''</td>
                    <td style="border: 1px solid black; border-collapse: collapse;">'''+str(item.Payment_Check3)+'''</td>
                </tr>'''
            if approval.Dept_Head == None:
                apptable = """
                        <table style="font-size: 12px;text-align: center;border: 1px solid black;border-collapse: collapse;" >
                            <tbody >
                                <tr style="height:10px;border: 1px solid black;border-collapse: collapse;">
                                    <th style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Prepared By</th>
                                    <th style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Approved By</th>
                                </tr>
                                <tr style="height:40px; border: 1px solid black;border-collapse: collapse;">
                                    <td style="padding:20px;border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="SPV">Created """ + str(CP.SPV_Submit.strftime("%Y-%m-%d %H:%M:%S")) + """</td>
                                    <td style="padding:20px;text-align: center;vertical-align: bottom;font-style: italic;color: green;border: 1px solid black;border-collapse: collapse;" id="DIV"></td>
                                </tr>
                                <tr style="height:20px; border: 1px solid black;border-collapse: collapse;">
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">""" + approval.SPV.title() + """</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">""" + approval.Div_Head.title() + """</td>
                                </tr>
                                <tr style="height:10px; border: 1px solid black;border-collapse: collapse;">
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Supervisor</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Division Head</td>
                                </tr>
                            </tbody>
                        </table>
                        """
            elif approval.Div_Head == None:
                apptable = """
                        <table style="font-size: 12px;text-align: center;border: 1px solid black;border-collapse: collapse;" >
                            <tbody >
                                <tr style="height:10px;border: 1px solid black;border-collapse: collapse;">
                                    <th style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Prepared By</th>
                                    <th style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Approved By</th>
                                </tr>
                                <tr style="height:40px; border: 1px solid black;border-collapse: collapse;">
                                    <td style="padding:20px;border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="SPV">Created """ + str(CP.SPV_Submit.strftime("%Y-%m-%d %H:%M:%S")) + """</td>
                                    <td style="padding:20px;text-align: center;vertical-align: bottom;font-style: italic;color: green;border: 1px solid black;border-collapse: collapse;" id="DEPT"></td>
                                </tr>
                                <tr style="height:20px; border: 1px solid black;border-collapse: collapse;">
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">""" + approval.SPV.title() + """</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">""" + approval.Dept_Head.title() + """</td>
                                </tr>
                                <tr style="height:10px; border: 1px solid black;border-collapse: collapse;">
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Supervisor</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Department Head</td>
                                </tr>
                            </tbody>
                        </table>
                        """
            else:
                apptable = """
                        <table style="font-size: 12px;text-align: center;border: 1px solid black;border-collapse: collapse;" >
                            <tbody >
                                <tr style="height:10px;border: 1px solid black;border-collapse: collapse;">
                                    <th style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Prepared By</th>
                                    <th colspan="2" style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Approved By</th>
                                </tr>
                                <tr style="height:40px; border: 1px solid black;border-collapse: collapse;">
                                    <td style="padding:20px;border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="SPV">Created """ + str(CP.SPV_Submit.strftime("%Y-%m-%d %H:%M:%S")) + """</td>
                                    <td style="padding:20px;border-right: 1px solid black;border-left: 1px solid black;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="DEPT"></td>
                                    <td style="padding:20px;text-align: center;vertical-align: bottom;font-style: italic;color: green;border: 1px solid black;border-collapse: collapse;" id="DIV"></td>
                                </tr>
                                <tr style="height:20px; border: 1px solid black;border-collapse: collapse;">
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">""" + approval.SPV.title() + """</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">""" + approval.Dept_Head.title() + """</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">""" + approval.Div_Head.title() + """</td>
                                </tr>
                                <tr style="height:10px; border: 1px solid black;border-collapse: collapse;">
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Supervisor</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Department Head</td>
                                    <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Division Head</td>
                                </tr>
                            </tbody>
                        </table>
                        """
            if approval.Dept_Head == None:
                Superior = approval.Div_Head.title()
            else:
                Superior = approval.Dept_Head.title()
            email_body = """\
                        <html>
                        <head style="margin-bottom: 0px;">Dear Mr/Ms """ + Superior + """,</head>
                        <body>
                        <p style="margin-bottom: 0px;margin-top: 0px;">This Capital Expenditure needs your approval </>
                        <hr>
                        <table style="font-size: x-small; width: 100%">
                            <tr>
                                <td rowspan="3" style="width: 15%;  text-align: center; border-bottom: 1px solid black;"><h1>ASKI</h1></td>
                                <td rowspan="3" style="text-align: center;  border-bottom: 1px solid black;">
                                    <h3>CAPITAL EXPENDITURE REQUEST FORM</h3>
                                </td>
                            </tr>
                        </table>
                        <br>
                        <table style="width: 100%; font-size: x-small;">
                            <tr>
                            <td style="width: 10%;">Business Unit</td>
                            <td>:</td>
                            <td>""" + str(CP.Business_Unit) + """</td>
                            </tr>
                            <tr>
                            <td style="width: 10%;">Division</td>
                            <td>:</td>
                            <td>""" + str(CP.Division) + """</td>
                            </tr>
                            <tr>
                            <td style="width: 10%;">Department</td>
                            <td>:</td>
                            <td>""" + str(CP.Department) + """</td>
                            </tr>
                        </table>
                        <br>
                        <table style="width: 100%; border-collapse: collapse; font-size: 12px;text-align: center">
                        <thead >
                            <tr style=" height: 50px; word-break: normal; border: 1px solid">
                                <th rowspan="2" style="vertical-align: middle; border: 1px solid; padding: 5px; ">No</th>
                                <th rowspan="2" style="vertical-align: middle; border: 1px solid; padding: 5px; ">Capex Item</th>
                                <th rowspan="2" style="vertical-align: middle; border: 1px solid; padding: 5px; ">Project</th>
                                <th rowspan="2" style="vertical-align: middle; border: 1px solid; padding: 5px; ">Asset Class</th>
                                <th rowspan="2" style="vertical-align: middle; border: 1px solid; padding: 5px; ">Priority</th>
                                <th rowspan="2" style="vertical-align: middle; border: 1px solid; padding: 5px; ">Reason</th>
                                <th rowspan="2" style="vertical-align: middle; border: 1px solid; padding: 5px; ">Remarks</th>
                                <th colspan="3" style="vertical-align: middle; border: 1px solid; padding: 5px; ">Capex Capitalization (in million Rp)</th>
                                <th colspan="15" style="vertical-align: middle; border: 1px solid ">Capex Payment (in a million Rp)</th>
                                <th colspan="3" style="vertical-align: middle; border: 1px solid ">Payment Check</th>
                            </tr>
                            <tr style="border: 1px solid" >
                                <th style="padding: 5px; border: 1px solid">""" + str(CP.Year) + """</th>
                                <th style="padding: 5px; border: 1px solid">""" + str(CP.Next_Year1) + """</th>
                                <th style="padding: 5px; border: 1px solid">""" + str(CP.Next_Year2) + """</th>
                                <th style="padding: 5px; border: 1px solid">Jan</th>
                                <th style="padding: 5px; border: 1px solid">Feb</th>
                                <th style="padding: 5px; border: 1px solid">Mar</th>
                                <th style="padding: 5px; border: 1px solid">Apr</th>
                                <th style="padding: 5px; border: 1px solid">May</th>
                                <th style="padding: 5px; border: 1px solid">Jun</th>
                                <th style="padding: 5px; border: 1px solid">Jul</th>
                                <th style="padding: 5px; border: 1px solid">Aug</th>
                                <th style="padding: 5px; border: 1px solid">Sept</th>
                                <th style="padding: 5px; border: 1px solid">Oct</th>
                                <th style="padding: 5px; border: 1px solid">Nov</th>
                                <th style="padding: 5px; border: 1px solid">Dec</th>
                                <th style="padding: 5px; border: 1px solid">""" + str(CP.Year) + """</th>
                                <th style="padding: 5px; border: 1px solid">""" + str(CP.Next_Year1) + """</th>
                                <th style="padding: 5px; border: 1px solid">""" + str(CP.Next_Year2) + """</th>
                                <th style="padding: 5px; border: 1px solid">""" + str(CP.Year) + """</th>
                                <th style="padding: 5px; border: 1px solid">""" + str(CP.Next_Year1) + """</th>
                                <th style="padding: 5px; border: 1px solid">""" + str(CP.Next_Year2) + """</th>
                            </tr>
                        </thead>
                        <tbody>
                        """ + contain + """
                        </tbody>
                        </table>
                        <br>
                        <table>
                        <tr>
                            <td style="width:75%;">
                                """ + apptable + """
                            </td>
                        </tr>
                        </table>
                        <br>
                        <i>Please, see the attached document for the capex item detail.</i>
                        <br>
                        <hr>
                        <p> Please give your response by click approval button bellow and then click send button. A response at your earliest convenience would be much appreciated. </p>
                        <table width="100%" cellspacing="0" cellpadding="0">
                            <tr>
                                <td>
                                    <table cellspacing="0" cellpadding="0">
                                        <tr>
                                            <td style="border-radius: 2px;width : 150px;text-align: center;" bgcolor="#4bf542">
                                                <a href="mailto:online.approval@aski.component.astra.co.id?subject=Approve: """ + str(CP.CP_Number) + """&body=Approve Capital Expenditure Request with ID """ + str(CP.CP_Number) + """ %0DApproval Message:" target="_blank" style="padding: 8px 12px; border: 1px solid #4bf542;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #ffffff;text-decoration: none;font-weight:bold;display: inline-block;">
                                                    APPROVE
                                                </a>
                                            </td>
                                            <td>&nbsp;&nbsp;</td>
                                            <td style="border-radius: 2px;width: 150px;text-align: center;" bgcolor="#ebde34">
                                                <a href="mailto:online.approval@aski.component.astra.co.id?subject=Revise: """ + str(CP.CP_Number) + """&body=Need Revise Capital Expenditure Request with ID """ + str(CP.CP_Number) + """ %0DRevision Message:" target="_blank" style="padding: 8px 12px; border: 1px solid #ebde34;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #000000;text-decoration: none;font-weight:bold;display: inline-block;">
                                                    REVISE
                                                </a>
                                            </td>
                                            <td>&nbsp;&nbsp;</td>
                                            <td style="border-radius: 2px;width: 150px;text-align: center;" bgcolor="#cccccc">
                                                <a href="mailto:""" + str(CP.SPV_Email) + """?subject=Ask User: """ + str(CP.CP_Number) + """&body=Ask User about Capital Expenditure Request with ID """ + str(CP.CP_Number) + """ %0DAsk User Message: " target="_blank" style="padding: 8px 12px; border: 1px solid #cccccc;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #000000;text-decoration: none;font-weight:bold;display: inline-block;">
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
            filename = str(CP_Number)+".xlsx"
            excelfile = BytesIO()
            wb = xlsxwriter.Workbook(excelfile)
            ws = wb.add_worksheet('Capex')
            formathead = wb.add_format(
                {
                    "bold":1,
                    "border": 1,
                    "align": "center",
            }
            )
            font_style = wb.add_format(
                {
                    "border": 1,
                    "align": "center",
                    "fg_color": "yellow",
                    "bold":1,
            }
            )
            ws.merge_range("A1:AB1", 'PT. ASTRA KOMPONEN INDONESIA', formathead)
            ws.merge_range("A2:AB2", 'CAPITAL EXPENDITURE REQUEST FORM', formathead)
            ws.merge_range("A3:AB3", ' ')
            ws.merge_range("A4:AB4", ' ')

            row_num = 4
            header = ['BUSINESS UNIT', 'DIVISION', 'DEPARTMENT']
            col_num = 0
            for col_nums in range(len(header)):
                col_num += 1
                ws.write(row_num, col_num, header[col_nums], font_style)
            
            row_num = 5
            header_style = wb.add_format(
                {
                    "border": 1,
                    "align": "center",
            }
            )
            header = models.capex.objects.filter(CP_Number=CP_Number).values_list('Business_Unit', 'Division', 'Department')
            col_num = 0
            for row in header:
                for col_nums in range(len(row)):
                    col_num += 1
                    ws.write(row_num, col_num, row[col_nums], header_style)
            

            ws.merge_range("B9:C9", 'Asset Class', font_style)
            ws.merge_range("E9:F9", 'Alasan', font_style)
            ws.merge_range("H9:I9", 'Prioritas', font_style)

            body_style = wb.add_format(
                {
                    "border": 1,
                    "align": "center",
                    "fg_color": "#FF00FF",
            }
            )
            asset_class = (['20', 'Building',],['21','Building Eqp.'], ['30', 'Machinery Eqp'], ['40', 'Transportation'], ['50', 'Office Eqp.'], ['51', 'Furniture & Fixture'], ['60', 'Tools & Eqp.'], ['70', 'Asset under cap.lease'], ['80', 'Mold ISAK 8'])
            row_num = 9
            for row in asset_class:
                row_num +=1
                col_num = 0
                for col_nums in range(len(row)):
                    col_num += 1
                    ws.write(row_num, col_num, row[col_nums], body_style)

            reason = (['1', 'Penambahan'], ['2', 'Penggantian'], ['3', 'Model Baru'], ['4', 'Quality Control'], ['5', 'Local Comp'], ['6', 'Keselamatan Kerja'], ['7', 'Peningkatan Produk'], ['8', 'Others'])
            row = 9
            for row_reason in reason:
                row +=1
                col_num = 3
                for col_nums in range(len(row_reason)):
                    col_num +=1
                    ws.write(row, col_num, row_reason[col_nums], body_style)

            priority = (['H', 'HIGH'], ['M', 'MEDIUM'], ['L', 'Low'])
            row = 9
            for row_priority in priority:
                row +=1
                col_num = 6
                for col_nums in range(len(row_priority)):
                    col_num +=1
                    ws.write(row, col_num, row_priority[col_nums], body_style)

            
            ws.merge_range("A22:A23", 'No', font_style)
            ws.merge_range("B22:B23", 'CAPEX Item', font_style)
            ws.merge_range("C22:C23", 'Project', font_style)
            ws.merge_range("D22:D23", 'Asset Class', font_style)
            ws.merge_range("E22:E23", 'Priority', font_style)
            ws.merge_range("F22:F23", 'Reason', font_style)
            ws.merge_range("G22:G23", 'Remarks', font_style)
            ws.merge_range("H22:J22", 'Capex Capitalization (in million Rp)', font_style)
            ws.merge_range("K22:Y22", 'Capex Payment (in million Rp)', font_style)
            ws.merge_range("Z22:AB22", 'Payment Check', font_style)
            ws.write("H23", str(datetime.datetime.today().year+1), font_style)
            ws.write("I23", str(datetime.datetime.today().year+2), font_style)
            ws.write("J23", str(datetime.datetime.today().year+3), font_style)
            ws.write("K23", 'Jan-'+str(datetime.datetime.today().year+1)+'', font_style)
            ws.write("L23", 'Feb-'+str(datetime.datetime.today().year+1)+'', font_style)
            ws.write("M23", 'Mar-'+str(datetime.datetime.today().year+1)+'', font_style)
            ws.write("N23", 'April-'+str(datetime.datetime.today().year+1)+'', font_style)
            ws.write("O23", 'May-'+str(datetime.datetime.today().year+1)+'', font_style)
            ws.write("P23", 'Jun-'+str(datetime.datetime.today().year+1)+'', font_style)
            ws.write("Q23", 'Jul-'+str(datetime.datetime.today().year+1)+'', font_style)
            ws.write("R23", 'August-'+str(datetime.datetime.today().year+1)+'', font_style)
            ws.write("S23", 'Sept-'+str(datetime.datetime.today().year+1)+'', font_style)
            ws.write("T23", 'Oct-'+str(datetime.datetime.today().year+1)+'', font_style)
            ws.write("U23", 'Nov-'+str(datetime.datetime.today().year+1)+'', font_style)
            ws.write("V23", 'Dec-'+str(datetime.datetime.today().year+1)+'', font_style)
            ws.write("W23", str(datetime.datetime.today().year+1), font_style)
            ws.write("X23", str(datetime.datetime.today().year+2), font_style)
            ws.write("Y23", str(datetime.datetime.today().year+3), font_style)
            ws.write("Z23", str(datetime.datetime.today().year+1), font_style)
            ws.write("AA23", str(datetime.datetime.today().year+2), font_style)
            ws.write("AB23", str(datetime.datetime.today().year+3), font_style)

            ws.set_column('A:A', 4) 
            ws.set_column('B:B', 40)
            ws.set_column('C:C', 19)
            ws.set_column('D:D', 20)
            ws.set_column('E:E', 25)
            ws.set_column('F:F', 20)
            ws.set_column('G:G', 25)
            ws.set_column('H:H', 11)
            ws.set_column('I:I', 11)
            ws.set_column('J:J', 11)


            font_style = wb.add_format(
                {
                    "border": 1,
                    "align": "center",
            }
            )

            cpitem = models.cpitem.objects.filter(CP_Number=CP_Number).order_by('id').values_list('No', 'CP_Name', 'Project', 'Asset_Class', 'Priority', 'Reason', 'Remarks','Summary_Current_Year', 'Summary_Next_Year1', 'Summary_Next_Year2', 'Jan_payment', 'Feb_payment', 'Mar_payment', 'April_payment', 'May_payment', 'Jun_payment', 'Jul_payment', 'Augst_payment', 'Sept_payment', 'Oct_payment', 'Nov_payment', 'Dec_payment', 'Summary_Current_Year', 'Summary_Next_Year1', 'Summary_Next_Year2', 'Payment_Check1', 'Payment_Check2', 'Payment_Check3')
            row_num = 22
            for row in cpitem:
                row_num +=1
                for col_num in range(len(row)):
                    if col_num == 22:
                        ws.write_formula(row_num, col_num, "=SUM(K"+str(row_num+1)+":V"+str(row_num+1)+")", font_style, row[col_num])
                    elif col_num == 23:
                        ws.write_formula(row_num, col_num, "=I"+str(row_num+1)+"", font_style, row[col_num])
                    elif col_num == 24:
                        ws.write_formula(row_num, col_num, "=J"+str(row_num+1)+"", font_style, row[col_num])
                    elif col_num == 25:
                        ws.write_formula(row_num, col_num, '=IF(ROUND(H'+str(row_num+1)+'-W'+str(row_num+1)+',0)=0,"OK","Error")', font_style, row[col_num])
                    elif col_num == 26:
                        ws.write_formula(row_num, col_num, '=IF(ROUND(I'+str(row_num+1)+'-X'+str(row_num+1)+',0)=0,"OK","Error")', font_style, row[col_num])
                    elif col_num == 27:
                        ws.write_formula(row_num, col_num, '=IF(ROUND(J'+str(row_num+1)+'-Y'+str(row_num+1)+',0)=0,"OK","Error")', font_style, row[col_num])
                    else :
                        try :
                            ws.write(row_num, col_num, int(row[col_num].replace('.', '')), font_style)
                        except ValueError:
                            ws.write(row_num, col_num, row[col_num], font_style)
            
            wb.close()
            if approval.Dept_Head == None:
                Superior_Email = approval.Div_Head_Email
            else :
                Superior_Email = approval.Dept_Head_Email
            mailattach = EmailMessage(
                'Capital Expenditure Online Approval: ' +
                request.POST['CP_Number'],
                body=email_body, from_email=settings.EMAIL_HOST_USER,
                to=[Superior_Email],
            )
            mailattach.content_subtype = "html"
            mailattach.attach(filename, excelfile.getvalue(), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            mailattach.send()
            email = models.Send(
                htmlmessage=email_body,
                mailfrom='online.approval@aski.component.astra.co.id',
                mailto=Superior_Email,
                CP_Number=request.POST['CP_Number'],
                mailheader='Capital Expenditure Online Approval: ' + request.POST['CP_Number'])
            email.save()
            models.capex.objects.filter(CP_Number=CP_Number).update(Status="Revised")
            return redirect("/CP/ListDept/")
    context={
        'Judul': 'Revise Capital Expenditure Request ' +CP_Number+ '',
        'CP_Number' : CP_Number,
        'CP': CP,
        'CPForm' : cpitem,
        'CPform': forms.Capex(instance=CP),
        'ListItem': list(models.cpitem.objects.filter(CP_Number=CP_Number).order_by('id')),
    }
    return render(request, 'capitalexpenditure/revise.html', context)

def Generate(ID):
    CP_Number = ID
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    excelfile = os.path.join(BASE_DIR, 'Media/Capex/' + CP_Number+'.xlsx')
    wb = xlsxwriter.Workbook(excelfile)
    ws = wb.add_worksheet('Capex')
    formathead = wb.add_format(
        {
            "bold":1,
            "border": 1,
            "align": "center",
    }
    )
    font_style = wb.add_format(
        {
            "border": 1,
            "align": "center",
            "fg_color": "yellow",
            "bold":1,
    }
    )
    ws.merge_range("A1:AB1", 'PT. ASTRA KOMPONEN INDONESIA', formathead)
    ws.merge_range("A2:AB2", 'CAPITAL EXPENDITURE REQUEST FORM', formathead)
    ws.merge_range("A3:AB3", ' ')
    ws.merge_range("A4:AB4", ' ')

    row_num = 4
    header = ['BUSINESS UNIT', 'DIVISION', 'DEPARTMENT']
    col_num = 0
    for col_nums in range(len(header)):
        col_num += 1
        ws.write(row_num, col_num, header[col_nums], font_style)
    
    row_num = 5
    header_style = wb.add_format(
        {
            "border": 1,
            "align": "center",
    }
    )
    header = models.capex.objects.filter(CP_Number=CP_Number).values_list('Business_Unit', 'Division', 'Department')
    col_num = 0
    for row in header:
        for col_nums in range(len(row)):
            col_num += 1
            ws.write(row_num, col_num, row[col_nums], header_style)
    

    ws.merge_range("B9:C9", 'Asset Class', font_style)
    ws.merge_range("E9:F9", 'Alasan', font_style)
    ws.merge_range("H9:I9", 'Prioritas', font_style)

    body_style = wb.add_format(
        {
            "border": 1,
            "align": "center",
            "fg_color": "#FF00FF",
    }
    )
    asset_class = (['20', 'Building',],['21','Building Eqp.'], ['30', 'Machinery Eqp'], ['40', 'Transportation'], ['50', 'Office Eqp.'], ['51', 'Furniture & Fixture'], ['60', 'Tools & Eqp.'], ['70', 'Asset under cap.lease'], ['80', 'Mold ISAK 8'])
    row_num = 9
    for row in asset_class:
        row_num +=1
        col_num = 0
        for col_nums in range(len(row)):
            col_num += 1
            ws.write(row_num, col_num, row[col_nums], body_style)

    reason = (['1', 'Penambahan'], ['2', 'Penggantian'], ['3', 'Model Baru'], ['4', 'Quality Control'], ['5', 'Local Comp'], ['6', 'Keselamatan Kerja'], ['7', 'Peningkatan Produk'], ['8', 'Others'])
    row = 9
    for row_reason in reason:
        row +=1
        col_num = 3
        for col_nums in range(len(row_reason)):
            col_num +=1
            ws.write(row, col_num, row_reason[col_nums], body_style)

    priority = (['H', 'HIGH'], ['M', 'MEDIUM'], ['L', 'Low'])
    row = 9
    for row_priority in priority:
        row +=1
        col_num = 6
        for col_nums in range(len(row_priority)):
            col_num +=1
            ws.write(row, col_num, row_priority[col_nums], body_style)

    
    ws.merge_range("A22:A23", 'No', font_style)
    ws.merge_range("B22:B23", 'CAPEX Item', font_style)
    ws.merge_range("C22:C23", 'Project', font_style)
    ws.merge_range("D22:D23", 'Asset Class', font_style)
    ws.merge_range("E22:E23", 'Priority', font_style)
    ws.merge_range("F22:F23", 'Reason', font_style)
    ws.merge_range("G22:G23", 'Remarks', font_style)
    ws.merge_range("H22:J22", 'Capex Capitalization (in million Rp)', font_style)
    ws.merge_range("K22:Y22", 'Capex Payment (in million Rp)', font_style)
    ws.merge_range("Z22:AB22", 'Payment Check', font_style)
    ws.write("H23", str(datetime.datetime.today().year+1), font_style)
    ws.write("I23", str(datetime.datetime.today().year+2), font_style)
    ws.write("J23", str(datetime.datetime.today().year+3), font_style)
    ws.write("K23", 'Jan-'+str(datetime.datetime.today().year+1)+'', font_style)
    ws.write("L23", 'Feb-'+str(datetime.datetime.today().year+1)+'', font_style)
    ws.write("M23", 'Mar-'+str(datetime.datetime.today().year+1)+'', font_style)
    ws.write("N23", 'April-'+str(datetime.datetime.today().year+1)+'', font_style)
    ws.write("O23", 'May-'+str(datetime.datetime.today().year+1)+'', font_style)
    ws.write("P23", 'Jun-'+str(datetime.datetime.today().year+1)+'', font_style)
    ws.write("Q23", 'Jul-'+str(datetime.datetime.today().year+1)+'', font_style)
    ws.write("R23", 'August-'+str(datetime.datetime.today().year+1)+'', font_style)
    ws.write("S23", 'Sept-'+str(datetime.datetime.today().year+1)+'', font_style)
    ws.write("T23", 'Oct-'+str(datetime.datetime.today().year+1)+'', font_style)
    ws.write("U23", 'Nov-'+str(datetime.datetime.today().year+1)+'', font_style)
    ws.write("V23", 'Dec-'+str(datetime.datetime.today().year+1)+'', font_style)
    ws.write("W23", str(datetime.datetime.today().year+1), font_style)
    ws.write("X23", str(datetime.datetime.today().year+2), font_style)
    ws.write("Y23", str(datetime.datetime.today().year+3), font_style)
    ws.write("Z23", str(datetime.datetime.today().year+1), font_style)
    ws.write("AA23", str(datetime.datetime.today().year+2), font_style)
    ws.write("AB23", str(datetime.datetime.today().year+3), font_style)

    ws.set_column('A:A', 4) 
    ws.set_column('B:B', 40)
    ws.set_column('C:C', 19)
    ws.set_column('D:D', 20)
    ws.set_column('E:E', 25)
    ws.set_column('F:F', 20)
    ws.set_column('G:G', 25)
    ws.set_column('H:H', 11)
    ws.set_column('I:I', 11)
    ws.set_column('J:J', 11)


    font_style = wb.add_format(
        {
            "border": 1,
            "align": "center",
    }
    )
    cpitem = models.cpitem.objects.filter(CP_Number=CP_Number).order_by('id').values_list('No', 'CP_Name', 'Project', 'Asset_Class', 'Priority', 'Reason', 'Remarks','Summary_Current_Year', 'Summary_Next_Year1', 'Summary_Next_Year2', 'Jan_payment', 'Feb_payment', 'Mar_payment', 'April_payment', 'May_payment', 'Jun_payment', 'Jul_payment', 'Augst_payment', 'Sept_payment', 'Oct_payment', 'Nov_payment', 'Dec_payment', 'Summary_Current_Year', 'Summary_Next_Year1', 'Summary_Next_Year2', 'Payment_Check1', 'Payment_Check2', 'Payment_Check3')
    row_num = 22
    for row in cpitem:
        row_num +=1
        for col_num in range(len(row)):
            if col_num == 22:
                ws.write_formula(row_num, col_num, "=SUM(K"+str(row_num+1)+":V"+str(row_num+1)+")", font_style, row[col_num])
            elif col_num == 23:
                ws.write_formula(row_num, col_num, "=I"+str(row_num+1)+"", font_style, row[col_num])
            elif col_num == 24:
                ws.write_formula(row_num, col_num, "=J"+str(row_num+1)+"", font_style, row[col_num])
            elif col_num == 25:
                ws.write_formula(row_num, col_num, '=IF(ROUND(H'+str(row_num+1)+'-W'+str(row_num+1)+',0)=0,"OK","Error")', font_style, row[col_num])
            elif col_num == 26:
                ws.write_formula(row_num, col_num, '=IF(ROUND(I'+str(row_num+1)+'-X'+str(row_num+1)+',0)=0,"OK","Error")', font_style, row[col_num])
            elif col_num == 27:
                ws.write_formula(row_num, col_num, '=IF(ROUND(J'+str(row_num+1)+'-Y'+str(row_num+1)+',0)=0,"OK","Error")', font_style, row[col_num])
            else :
                try :
                    ws.write(row_num, col_num, int(row[col_num].replace('.', '')), font_style)
                except ValueError:
                    ws.write(row_num, col_num, row[col_num], font_style)
    
    wb.close()

def excel(request, ID):
    Generate(ID)
    return HttpResponse("it works!")

def ExcelDept(request, ID):
    CP_Number = ID
    output = BytesIO()
    wb = xlsxwriter.Workbook(output)
    ws = wb.add_worksheet('Capex')
    formathead = wb.add_format(
        {
            "bold":1,
            "border": 1,
            "align": "center",
    }
    )
    font_style = wb.add_format(
        {
            "border": 1,
            "align": "center",
            "fg_color": "yellow",
            "bold":1,
    }
    )
    ws.merge_range("A1:AL1", 'PT. ASTRA KOMPONEN INDONESIA', formathead)
    ws.merge_range("A2:AL2", 'CAPITAL EXPENDITURE REQUEST FORM', formathead)
    ws.merge_range("A3:AL3", ' ')
    ws.merge_range("A4:AL4", ' ')

    row_num = 4
    header = ['BUSINESS UNIT', 'DIVISION', 'DEPARTMENT']
    col_num = 0
    for col_nums in range(len(header)):
        col_num += 1
        ws.write(row_num, col_num, header[col_nums], font_style)
    
    row_num = 5
    header_style = wb.add_format(
        {
            "border": 1,
            "align": "center",
    }
    )
    header = models.capex.objects.filter(CP_Number=CP_Number).values_list('Business_Unit', 'Division', 'Department')
    col_num = 0
    for row in header:
        for col_nums in range(len(row)):
            col_num += 1
            ws.write(row_num, col_num, row[col_nums], header_style)
    

    ws.merge_range("B9:C9", 'Asset Class', font_style)
    ws.merge_range("E9:F9", 'Alasan', font_style)
    ws.merge_range("H9:I9", 'Prioritas', font_style)

    body_style = wb.add_format(
        {
            "border": 1,
            "align": "center",
            "fg_color": "#FF00FF",
    }
    )
    asset_class = (['20', 'Building',],['21','Building Eqp.'], ['30', 'Machinery Eqp'], ['40', 'Transportation'], ['50', 'Office Eqp.'], ['51', 'Furniture & Fixture'], ['60', 'Tools & Eqp.'], ['70', 'Asset under cap.lease'], ['80', 'Mold ISAK 8'])
    row_num = 9
    for row in asset_class:
        row_num +=1
        col_num = 0
        for col_nums in range(len(row)):
            col_num += 1
            ws.write(row_num, col_num, row[col_nums], body_style)

    reason = (['1', 'Penambahan'], ['2', 'Penggantian'], ['3', 'Model Baru'], ['4', 'Quality Control'], ['5', 'Local Comp'], ['6', 'Keselamatan Kerja'], ['7', 'Peningkatan Produk'], ['8', 'Others'])
    row = 9
    for row_reason in reason:
        row +=1
        col_num = 3
        for col_nums in range(len(row_reason)):
            col_num +=1
            ws.write(row, col_num, row_reason[col_nums], body_style)

    priority = (['H', 'HIGH'], ['M', 'MEDIUM'], ['L', 'Low'])
    row = 9
    for row_priority in priority:
        row +=1
        col_num = 6
        for col_nums in range(len(row_priority)):
            col_num +=1
            ws.write(row, col_num, row_priority[col_nums], body_style)

    
    ws.merge_range("A22:A24", 'No', font_style)
    ws.merge_range("B22:B24", 'CAPEX Item', font_style)
    ws.merge_range("C22:C24", 'Grup', font_style)
    ws.merge_range("D22:D24", 'Project', font_style)
    ws.merge_range("E22:E24", 'Asset Class', font_style)
    ws.merge_range("F22:F24", 'Priority', font_style)
    ws.merge_range("G22:G24", 'Reason', font_style)
    ws.merge_range("H22:H24", 'Remarks', font_style)
    ws.merge_range("I22:N22", 'Capex Capitalization (in million Rp)', font_style)
    ws.merge_range("O22:AF22", 'Capex Payment (in million Rp)', font_style)
    ws.merge_range("AG22:AI22", 'Payment Check', font_style)
    ws.merge_range("AJ22:AL22", 'Payment Approval', font_style)
    ws.merge_range("I23:J23", str(datetime.datetime.today().year+1), font_style)
    ws.merge_range("K23:L23", str(datetime.datetime.today().year+2), font_style)
    ws.merge_range("M23:N23", str(datetime.datetime.today().year+3), font_style)
    ws.merge_range("AA23:AB23", str(datetime.datetime.today().year+1), font_style)
    ws.merge_range("AC23:AD23", str(datetime.datetime.today().year+2), font_style)
    ws.merge_range("AE23:AF23", str(datetime.datetime.today().year+3), font_style)
    ws.merge_range("O23:O24", 'Jan-'+str(datetime.datetime.today().year+1)+'', font_style)
    ws.merge_range("P23:P24", 'Feb-'+str(datetime.datetime.today().year+1)+'', font_style)
    ws.merge_range("Q23:Q24", 'Mar-'+str(datetime.datetime.today().year+1)+'', font_style)
    ws.merge_range("R23:R24", 'April-'+str(datetime.datetime.today().year+1)+'', font_style)
    ws.merge_range("S23:S24", 'May-'+str(datetime.datetime.today().year+1)+'', font_style)
    ws.merge_range("T23:T24", 'Jun-'+str(datetime.datetime.today().year+1)+'', font_style)
    ws.merge_range("U23:U24", 'Jul-'+str(datetime.datetime.today().year+1)+'', font_style)
    ws.merge_range("V23:V24", 'Aug-'+str(datetime.datetime.today().year+1)+'', font_style)
    ws.merge_range("W23:W24", 'Sept-'+str(datetime.datetime.today().year+1)+'', font_style)
    ws.merge_range("X23:X24", 'Oct-'+str(datetime.datetime.today().year+1)+'', font_style)
    ws.merge_range("Y23:Y24", 'Nov-'+str(datetime.datetime.today().year+1)+'', font_style)
    ws.merge_range("Z23:Z24", 'Dec-'+str(datetime.datetime.today().year+1)+'', font_style)
    ws.merge_range("AG23:AG24", str(datetime.datetime.today().year+1), font_style)
    ws.merge_range("AH23:AH24", str(datetime.datetime.today().year+2), font_style)
    ws.merge_range("AI23:AI24", str(datetime.datetime.today().year+3), font_style)
    ws.merge_range("AJ23:AJ24", str(datetime.datetime.today().year+1), font_style)
    ws.merge_range("AK23:AK24", str(datetime.datetime.today().year+2), font_style)
    ws.merge_range("AL23:AL24", str(datetime.datetime.today().year+3), font_style)

    ws.set_column('A:A', 4) 
    ws.set_column('B:B', 40)
    ws.set_column('C:C', 15)
    ws.set_column('D:D', 19)
    ws.set_column('E:E', 25)
    ws.set_column('F:F', 20)
    ws.set_column('G:G', 25)
    ws.set_column('H:H', 25)
    
    row_num = 23
    columns_7 = ['Before', 'After', 'Before', 'After', 'Before', 'After']
    col_num = 7
    for col_nums in range(len(columns_7)):
        col_num += 1
        ws.write(row_num, col_num, columns_7[col_nums], font_style)

    row_num = 23
    columns_26 = ['Before', 'After', 'Before', 'After', 'Before', 'After']
    col = 25
    for column in range(len(columns_26)):
        col += 1
        ws.write(row_num, col, columns_26[column], font_style)

    font_style = wb.add_format(
        {
            "border": 1,
            "align": "center",
    }
    )
    cpitem = models.cpitem.objects.filter(CP_Number=CP_Number).order_by('id').values_list('No', 'CP_Name', 'Grup', 'Project', 'Asset_Class', 'Priority', 'Reason', 'Remarks','Summary_Current_Year', 'After_Current_Year', 'Summary_Next_Year1', 'After_Next_Year1','Summary_Next_Year2', 'After_Next_Year2', 'Jan_payment', 'Feb_payment', 'Mar_payment', 'April_payment', 'May_payment', 'Jun_payment', 'Jul_payment', 'Augst_payment', 'Sept_payment', 'Oct_payment', 'Nov_payment', 'Dec_payment', 'Summary_Current_Year', 'After_Current_Year', 'Summary_Next_Year1', 'After_Next_Year1','Summary_Next_Year2', 'After_Next_Year2', 'Payment_Check1', 'Payment_Check2', 'Payment_Check3')
    row_num = 23
    for row in cpitem:
        row_num +=1
        for col_num in range(len(row)+3):
            if col_num == 26:
                ws.write_formula(row_num, col_num, "=SUM(O"+str(row_num+1)+":Z"+str(row_num+1)+")", font_style, row[col_num])
            elif col_num == 27:
                ws.write_formula(row_num, col_num, "=K"+str(row_num+1)+"", font_style, row[col_num])
            elif col_num == 28:
                ws.write_formula(row_num, col_num, "=M"+str(row_num+1)+"", font_style, row[col_num])
            elif col_num == 29:
                ws.write_formula(row_num, col_num, "=J"+str(row_num+1)+"", font_style, row[col_num])
            elif col_num == 30:
                ws.write_formula(row_num, col_num, "=L"+str(row_num+1)+"", font_style, row[col_num])
            elif col_num == 31:
                ws.write_formula(row_num, col_num, "=N"+str(row_num+1)+"", font_style, row[col_num])
            elif col_num == 32:
                ws.write_formula(row_num, col_num, '=IF(ROUND(I'+str(row_num+1)+'-AA'+str(row_num+1)+',0)=0,"OK","Error")', font_style, row[col_num])
            elif col_num == 33:
                ws.write_formula(row_num, col_num, '=IF(ROUND(K'+str(row_num+1)+'-AC'+str(row_num+1)+',0)=0,"OK","Error")', font_style, row[col_num])
            elif col_num == 34:
                ws.write_formula(row_num, col_num, '=IF(ROUND(M'+str(row_num+1)+'-AE'+str(row_num+1)+',0)=0,"OK","Error")', font_style, row[col_num])
            elif col_num == 35:
                ws.write_formula(row_num, col_num, '=IF(ROUND(J'+str(row_num+1)+'-AB'+str(row_num+1)+',0)=0,"OK","Error")', font_style,('OK' if row[9]==row[27] else 'Error'))
            elif col_num == 36:
                ws.write_formula(row_num, col_num, '=IF(ROUND(L'+str(row_num+1)+'-AD'+str(row_num+1)+',0)=0,"OK","Error")', font_style, ('OK' if row[11]==row[29] else 'Error'))
            elif col_num == 37:
                ws.write_formula(row_num, col_num, '=IF(ROUND(N'+str(row_num+1)+'-AF'+str(row_num+1)+',0)=0,"OK","Error")', font_style, ('OK' if row[13]==row[31] else 'Error'))
            else :
                try :
                    ws.write(row_num, col_num, int(row[col_num].replace('.', '')), font_style)
                except ValueError:
                    ws.write(row_num, col_num, row[col_num], font_style)
    
    wb.close()
    output.seek(0)
    response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename='+CP_Number+'.xlsx'
    return response

