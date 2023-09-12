from django.shortcuts import render
from . import forms
from . import models
from PurchaseRequest import models as PRModels
from Entertainment import models as BEModels
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.core import serializers
from django.shortcuts import redirect
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.http import HttpResponse
from . import resources

import datetime
import pdfkit

# Create your views here.

def is_memberaddasset(user):
    return user.groups.filter(name='Allow_Add_Asset').exists()

@login_required
@user_passes_test(is_memberaddasset)
def listApproved (request):
    if request.method == 'POST':
        print(request.POST)
        models.BonSementara.objects.filter(
            BS_Number=request.POST["BS_Number_Closing"]).update(BS_Status = "Closing By Finance - "+ request.POST["Note_Closing"])

    ListBS = models.BonSementara.objects.filter(
            BS_Status = 'Approved').order_by('-BS_Number')
    ListFP = models.Penyelesaian.objects.filter(
                FP_Status = 'Approved').order_by('-FP_Number')
    ListFPCheck = models.Penyelesaian.objects.filter(
                FP_Status = 'FinanceCheck').order_by('-FP_Number')
    ListBSOpen = models.BonSementara.objects.filter(
                BS_Status = 'Finished').order_by('-BS_Number')

    

    context = {
        'Judul': 'List Bon Sementara & Payment Request Approved',
        'ListBS' : ListBS,
        'ListFP' : ListFP,
        'ListFPCheck' : ListFPCheck,
        'ListBSOpen' : ListBSOpen,
        
    }
    return render(request, 'bonmerah/listAP.html', context)

@login_required
def listBS (request):

    if (request.user.username == "admin"):
        ListBS = models.BonSementara.objects.all().exclude(BS_Status = None).order_by('-BS_Number')
    elif (request.user.username == "ADMINFINANCE"):
        ListBS = models.BonSementara.objects.all().exclude(BS_Status = None).order_by('-BS_Number')
    else :
        ListBS = models.BonSementara.objects.filter(
            BS_Number__contains=request.user.username).exclude(BS_Status = None).order_by('-BS_Number')

    
    context = {
        'Judul': 'List Bon Sementara',
        'ListBS' : ListBS,
    }
    return render(request, 'bonmerah/listBS.html', context)

@login_required
def CreateBS(request):
    
    BS = forms.BonSementara()
    BS.fields['BS_Number'].initial = 'ASKITEMPBON'+request.user.username + str(models.BonSementara.objects.filter(
            BS_Number__contains=request.user.username, BS_Status__isnull=False).exclude(BS_Number__contains='rev').count()+1).zfill(5)
    approval = list(PRModels.Approval.objects.filter(
            User=request.user.username))
    data = serializers.serialize(
            "json", PRModels.Approval.objects.filter(User=request.user.username))
    today = datetime.datetime.now().strftime("%d/%m/%Y")

    ListBSOpen = models.BonSementara.objects.filter(BS_Number__contains=request.user.username,
                BS_Status = 'Finished').order_by('-BS_Number').count()
    if ListBSOpen >= 10:
        return HttpResponse(f"<h4>Your departement {request.user.username} temporary disabled for creating Petty Cash Request,</h4><h4>Please close your petty cash request currently open!</h4> <h4>There is {ListBSOpen} petty cash request still opened.</h4>" )
        

    if request.method == "POST" :
        print(request.POST)
        if models.BonSementara.objects.filter(BS_Number =request.POST["BS_Number"].title() ).exists():
            saveBS= forms.BonSementara(request.POST,instance=models.BonSementara.objects.get(BS_Number =request.POST["BS_Number"]))
        else :
            saveBS= forms.BonSementara(request.POST)
        if saveBS.is_valid():
            saveBS.save()

            email_body = """
            <html>
                   <head style="margin-bottom: 0px;">Dear Mr/Ms """ + request.POST["DeptHead"] + """,</head>
                    <body>
                    <p style="margin-bottom: 0px;margin-top: 0px;">This temporary bon request needs your approval </>
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
                        <td><h1>ASKI</h1></td>
                        <td><h2>TEMPORARY BON</h2></td>
                        <td style="text-align: left;width:200px;">
                        <div>No Doc &nbsp&nbsp&nbsp&nbsp: FR-FACT.01-002</div>
                        <div>Revision &nbsp: 0</div>
                        <div>Eff. Start &nbsp: 01 Mar 2021</div>
                        </td>
                        </tr>
                        </table>
                    <p style="text-align: center;">Harus dipertanggung jawabkan paling lambat 2 (dua) hari</p>
                    <table class="table-header">
                        <tr>
                        <td width="1%" >BS Number</td>
                        <td width="1%" >:</td>
                        <td width="98%"> """+ request.POST["BS_Number"]+"""</td>
                        </tr>
                        <tr>
                        <td width="1%" >Paid By</td>
                        <td width="1%" >:</td>
                        <td width="98%"> """+ request.POST["PaidBy"]+"""</td>
                        </tr>
                        </table>

                            <br>
                            <table class="table-approve" style="width: 100%;">
                                <tr>
                                    <th>Date Created</th>
                                    <th>Temporary Bon Note</th>
                                    <th>Value</th>
                                </tr>
                                <tr style ="min-height: 200px;">
                                    <td style ="text-align:center;">

                                        <div style="min-height: 100px;">"""+ datetime.datetime.now().strftime("%d-%m-%Y")+"""</div>
                                    </td>
                                    <td style="text-align: left;"><div>"""+request.POST["Note"].replace("\n","</div><div>")+"""</div></td>
                                    <td style ="text-align:center;"> Rp. """+ request.POST["Jumlah"]+""",-</td>
                                </tr>
                                <tr >
                                    <td colspan="3">
                                        <h4 style="text-align: left;">Terbilang</h4>
                                        <div style="text-align: left;margin-left: 20px;">"""+ request.POST["Terbilang"]+"""</div>
                                    </td>
                                </tr>
                    
                            </table>
                    
                        


                        <h4>Approval</h4>
                        <table class="table-approve" style="white-space: nowrap;text-align: center;">
                            <tr>
                                <td style="width:25%;">Received by</td>
                                <td style="width:25%;">Approved by</td>
                                <td style="width:25%;">Approved by</td>
                                <td style="width:25%;">Created by</td>
                            </tr>
                            <tr style="height:100px;">
                                <td></td>
                                <td id="Finance"></td>
                                <td id="DeptHead"></td>
                                <td id="User"><div>Created</div><div>"""+datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S").replace(" ","</div><div>")+"""</div></td>
                            </tr>
                            <tr>
                                <td></td>
                                <td>"""+ request.POST["Finance"]+"""</td>
                                <td>"""+ request.POST["DeptHead"]+"""</td>
                                <td>"""+ request.POST["User_Name"]+"""</td>
                            </tr>
                            <tr>
                            <td style="width:25%;">Receiver</td>
                            <td style="width:25%;">Finance</td>
                            <td style="width:25%;">Dept/Div Head</td>
                            <td style="width:25%;">User</td>
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
                                            <a href="mailto:online.approval@aski.component.astra.co.id?subject=Approve: """+ request.POST["BS_Number"]+"""&body=Approve Temporary Bon with ID """+ request.POST["BS_Number"]+""" %0DApproval Message:" target="_blank" style="padding: 8px 12px; border: 1px solid #4bf542;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #ffffff;text-decoration: none;font-weight:bold;display: inline-block;">
                                                APPROVE             
                                            </a>
                                        </td>
                                        <td>&nbsp;&nbsp;</td>
                                        <td style="border-radius: 2px;width: 150px;text-align: center;" bgcolor="#ED2939">
                                            <a href="mailto:online.approval@aski.component.astra.co.id?subject=Reject: """+ request.POST["BS_Number"]+"""&body=Reject  Temporary Bon with ID """+ request.POST["BS_Number"]+"""  %0DReject Message:" target="_blank" style="padding: 8px 12px; border: 1px solid #ED2939;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #ffffff;text-decoration: none;font-weight:bold;display: inline-block;">
                                                REJECT             
                                            </a>
                                        </td>
                                        <td>&nbsp;&nbsp;</td>
                                        <td style="border-radius: 2px;width: 150px;text-align: center;" bgcolor="#cccccc">
                                            <a href="mailto:"""+request.POST["User_Email"]+"""?subject=Ask User: """+ request.POST["BS_Number"]+"""&body=Ask User about Temporary Bon with ID """+ request.POST["BS_Number"]+"""  %0DAsk User Message: " target="_blank" style="padding: 8px 12px; border: 1px solid #cccccc;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #000000;text-decoration: none;font-weight:bold;display: inline-block;">
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
                'Bon Sementara Online Approval: ' + request.POST['BS_Number'],
                body=email_body,
                from_email=settings.EMAIL_HOST_USER,
                to=[request.POST['DeptHead_Email']],
            )
            mailattach.content_subtype = "html"
            mailattach.send()

            models.Send(htmlmessage=email_body,
                            mailfrom='online.approval@aski.component.astra.co.id',
                            mailto=request.POST['DeptHead_Email'],
                            Number=request.POST['BS_Number'],
                            mailheader='Bon Sementara Online Approval: ' + request.POST['BS_Number']).save()
            models.BonSementara.objects.filter(
            BS_Number=request.POST['BS_Number']).update(BS_Status="Created")

            return redirect('/BS/ListBS/')

        else :
            print(saveBS.errors)

    context = {
        'Judul': 'Create Bon Sementara',
        'BS' : BS,
        'Approval' : approval,
        'Data': data,
        'today': today
    }
    return render(request, 'bonmerah/CreateBS.html', context)

@login_required
def DetailBS(request,ID):

    if request.method == 'POST':
        print(request.POST)
        models.BonSementara.objects.filter(BS_Number = ID).update(Receiver_Name = request.POST["ReceiveBy"],Received_Date = datetime.datetime.now())
        GenerateBS(ID)
    BS = models.BonSementara.objects.get(BS_Number = ID)
    context = {
        'Judul': 'Bon Sementara',
        'BS' : BS,
    }
    return render(request, 'bonmerah/DetailBS.html', context)

@login_required
def listFP (request):
    if (request.user.username == "admin"):
       ListFP = models.Penyelesaian.objects.all().exclude(FP_Status = None).order_by('-FP_Number')
    elif (request.user.username == "ADMINFINANCE"):
        ListFP = models.Penyelesaian.objects.all().exclude(FP_Status = None).order_by('-FP_Number')
    else :
        ListFP = models.Penyelesaian.objects.filter(
                FP_Number__contains=request.user.username).exclude(FP_Status = None).order_by('-FP_Number')
    context = {
        'Judul': 'List Payment Request',
        'ListFP' : ListFP,
    }
    return render(request, 'bonmerah/listFP.html', context)

@login_required
def CreateFP(request,ID):
    FP = forms.Penyelesaian()
    FP.fields['FP_Number'].initial = 'ASKIPAYREQ'+request.user.username + str(models.Penyelesaian.objects.filter(
            FP_Number__contains=request.user.username, FP_Status__isnull=False).exclude(FP_Number__contains='rev').count()+1).zfill(5)
    costcenter = list(PRModels.CostCenter.objects.all())
    entertainment = list(BEModels.Entertainment.objects.filter(Status='Finished', BE_Number__contains=request.user.username))
    approval = list(PRModels.Approval.objects.filter(
            User=request.user.username))
    data = serializers.serialize(
            "json", PRModels.Approval.objects.filter(User=request.user.username))
    FP.fields['Dept'].initial = request.user
    FP.fields['Reference'].initial = ID
    if request.method == "POST" :
        print(request.POST)
        if models.Penyelesaian.objects.filter(FP_Number =request.POST["FP_Number"] ).exists():
            saveFP= forms.Penyelesaian(request.POST,request.FILES,instance=models.Penyelesaian.objects.get(FP_Number =request.POST["FP_Number"]))
        else :
            saveFP= forms.Penyelesaian(request.POST,request.FILES)
        if saveFP.is_valid():
            saveFP.save()

            email_body = """
            <html>
                   <head style="margin-bottom: 0px;">Dear Mr/Ms """ + request.POST["DeptHead"].title() + """,</head>
                    <body>
                    <p style="margin-bottom: 0px;margin-top: 0px;">This payment request needs your approval </>
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
                        <td><h1>ASKI</h1></td>
                        <td><h2>PAYMENT REQUEST</h2></td>
                        <td style="text-align: left;width:200px;">
                        <div>No Doc &nbsp&nbsp&nbsp&nbsp: FR-FACT.01-004</div>
                        <div>Revision &nbsp: 0</div>
                        <div>Eff. Start &nbsp: 01 Mar 2021</div>
                        </td>
                        </tr>
                        </table>
                        <br>

                        <table class="table-header" >
                            <tr >
                                <td width="8%" >Bussiness Unit</td>
                                <td width="2%">:</td>
                                <td width="90%">""" + request.POST["Bussiness_Unit"]+ """</td>
                            </tr>
                            <tr>
                                <td>Div / Dept</td>
                                <td>:</td>
                                <td>""" + request.POST["Dept"]+ """</td>
                            </tr>
                            <tr>
                                <td>User</td>
                                <td>:</td>
                                <td>""" + request.POST["User_Name"]+ """
                                </td>
                            </tr>
                            <tr>
                                <td>Cost Center</td>
                                <td>:</td>
                                <td>""" + request.POST["CostCenter"]+ """
                                </td>
                            </tr>
                            <tr>
                                <td>Note</td>
                                <td>:</td>
                                <td>""" + request.POST["Note"]+ """</td>
                            </tr>
                            <tr>
                                <td>Paid by</td>
                                <td>:</td>
                                <td>""" + request.POST["PaidBy"]+ """</td>
                            </tr>
                            <tr>
                                <td>PayReq Number</td>
                                <td>:</td>
                                <td>""" + request.POST["FP_Number"]+ """</td>
                            </tr>
                            <tr>
                                <td>Temp Bon Reference</td>
                                <td>:</td>
                                <td>""" + request.POST["Reference"]+ """</td>
                            </tr>

                        </table>
               
                 
                            <br>
                            <table class="table-header" >
                                <tr>
                                <td width="8%">Paid to</td>
                                <td width="2%">:</td>
                                <td width="90%">""" + request.POST["PaidTo"]+ """</td>
                                </tr>
                                <tr>
                                    <td style="vertical-align: top;">Description
                                    <div> </div>
                                    <div> </div>
                                    <div> </div>
                                    <div> </div>
                                    <div> </div>
                                    <div> </div>
                                    <div> </div>
                                    <div> </div>
                                    </td>
                                    <td style="vertical-align: top;">:</td>
                                    <td vertical-align: top;"><div>"""+request.POST["Description"].replace("\n","</div><div>")+"""</div></td>
                                </tr>
                                <tr>
                                    <td>Amount</td>
                                    <td>:</td>
                                    <td>
                                    <div>Rp. """ + request.POST["Amount"]+ """,-</div>
                                   
                                    </td>
                                </tr>
                                <tr>
                                    <td>Says</td>
                                    <td>:</td>
                                    <td>""" + request.POST["Says"]+ """</td>
                                </tr>
                            </table>
                    
                        


                        <h4>Approval</h4>
                        <table class="table-approve" style="white-space: nowrap;text-align: center;width:90%;">
                            <tr>
                                <td style="width:20%;">Received by</td>
                                <td style="width:20%;">Payment Approved by</td>
                                <td style="width:20%;">Request Approved by</td>
                                <td style="width:20%;">Request Approved by</td>
                                <td style="width:20%;">Created by</td>
                            </tr>
                            <tr style="height:100px;">
                                <td></td>
                                <td id="DirFinance"></td>
                                <td id="Finance"></td>
                                <td id="DeptHead"></td>
                                <td id="User"><div>Created</div><div>"""+datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S").replace(" ","</div><div>")+"""</div></td>
                            </tr>
                            <tr>
                                <td></td>
                                <td>"""+ request.POST["Dir_Finance"]+"""</td>
                                <td>"""+ request.POST["Finance"]+"""</td>
                                <td>"""+ request.POST["DeptHead"]+"""</td>
                                <td>"""+ request.POST["User_Name"]+"""</td>
                            </tr>
                            <tr>
                            <td>Receiver</td>
                            <td>Direktur</td>
                            <td>Finance</td>
                            <td>Dept/Div Head</td>
                            <td>User</td>
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
                                            <a href="mailto:online.approval@aski.component.astra.co.id?subject=Approve: """+ request.POST["FP_Number"]+"""&body=Approve Payment Request with ID """+ request.POST["FP_Number"]+""" %0DApproval Message:" target="_blank" style="padding: 8px 12px; border: 1px solid #4bf542;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #ffffff;text-decoration: none;font-weight:bold;display: inline-block;">
                                                APPROVE             
                                            </a>
                                        </td>
                                        <td>&nbsp;&nbsp;</td>
                                        <td style="border-radius: 2px;width: 150px;text-align: center;" bgcolor="#ED2939">
                                            <a href="mailto:online.approval@aski.component.astra.co.id?subject=Reject: """+ request.POST["FP_Number"]+"""&body=Reject  Payment Request with ID """+ request.POST["FP_Number"]+"""  %0DReject Message:" target="_blank" style="padding: 8px 12px; border: 1px solid #ED2939;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #ffffff;text-decoration: none;font-weight:bold;display: inline-block;">
                                                REJECT             
                                            </a>
                                        </td>
                                        <td>&nbsp;&nbsp;</td>
                                        <td style="border-radius: 2px;width: 150px;text-align: center;" bgcolor="#cccccc">
                                            <a href="mailto:"""+request.POST["User_Email"]+"""?subject=Ask User: """+ request.POST["FP_Number"]+"""&body=Ask User about Payment Request with ID """+ request.POST["FP_Number"]+"""  %0DAsk User Message: " target="_blank" style="padding: 8px 12px; border: 1px solid #cccccc;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #000000;text-decoration: none;font-weight:bold;display: inline-block;">
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
                'Payment Request Online Approval: ' + request.POST['FP_Number'],
                body=email_body,
                from_email=settings.EMAIL_HOST_USER,
                to=[request.POST['DeptHead_Email']],
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
            if 'Attachment4' in request.FILES:
                mailattach.attach_file(
                    'Media/Uploads/'+str(request.FILES['Attachment4']).replace(' ', '_'))
            if 'Attachment5' in request.FILES:
                mailattach.attach_file(
                    'Media/Uploads/'+str(request.FILES['Attachment5']).replace(' ', '_'))
            if  request.POST['Entertainment'] != '':
                mailattach.attach_file(
                    'Media/Entertaint/'+str(request.POST['Entertainment']).replace(' ', '_')+'.pdf')

            mailattach.send()

            models.Send(htmlmessage=email_body,
                            mailfrom='online.approval@aski.component.astra.co.id',
                            mailto=request.POST['DeptHead_Email'],
                            Number=request.POST['FP_Number'],
                            mailheader='Payment Request Online Approval: ' + request.POST['FP_Number']).save()
            models.Penyelesaian.objects.filter(
            FP_Number=request.POST['FP_Number']).update(FP_Status="Created")

            return redirect('/BS/ListFP/')
        else :
            print(saveFP.errors)

    context = {
        'Judul': 'Create Form Payment Request',
        'FP' : FP,
        'Approval' : approval,
        'Data': data,
        'CostCenter': costcenter,
        'Entertainment': entertainment,
    }
    return render(request, 'bonmerah/CreateFP.html', context)

@login_required
def DetailFP(request,ID):
    if request.method == 'POST':
        print(request.POST)
        if 'ChangeCost' in request.POST:
            models.Penyelesaian.objects.filter(FP_Number = ID).update(CostCenter = request.POST['CostCenter'])
        if 'Amount' in request.POST:
            models.Penyelesaian.objects.filter(FP_Number = ID).update(Amount = request.POST['Amount'])
        if 'Says' in request.POST:
            models.Penyelesaian.objects.filter(FP_Number = ID).update(Says = request.POST['Says'])
        if 'reject' in request.POST:
            models.Penyelesaian.objects.filter(FP_Number = ID).update(Reject_Message = request.POST['rejectmessage'],FP_Status = 'Rejected')
            return redirect ("/BS/ListFA/")
        if 'Save' in request.POST:
            models.Penyelesaian.objects.filter(FP_Number = ID).update(Receiver_Name = request.POST["ReceiveBy"],Received_Date = datetime.datetime.now())
            GenerateFP(ID)
        if 'finish' in request.POST:
            FP = models.Penyelesaian.objects.get(FP_Number = ID)
            email_body = """
            <html>
                   <head style="margin-bottom: 0px;">Dear Mr/Ms """ + FP.Finance.title() + """,</head>
                    <body>
                    <p style="margin-bottom: 0px;margin-top: 0px;">This payment request needs your approval </>
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
                        <td><h1>ASKI</h1></td>
                        <td><h2>PAYMENT REQUEST</h2></td>
                        <td style="text-align: left;width:200px;">
                        <div>No Doc &nbsp&nbsp&nbsp&nbsp: FR-FACT.01-004</div>
                        <div>Revision &nbsp: 0</div>
                        <div>Eff. Start &nbsp: 01 Mar 2021</div>
                        </td>
                        </tr>
                        </table>
                        <br>

                        <table class="table-header" >
                            <tr >
                                <td width="8%" >Bussiness Unit</td>
                                <td width="2%">:</td>
                                <td width="90%">""" + FP.Bussiness_Unit+ """</td>
                            </tr>
                            <tr>
                                <td>Div / Dept</td>
                                <td>:</td>
                                <td>""" + FP.Dept+ """</td>
                            </tr>
                            <tr>
                                <td>User</td>
                                <td>:</td>
                                <td>""" + FP.User_Name+ """
                                </td>
                            </tr>
                            <tr>
                                <td>Cost Center</td>
                                <td>:</td>
                                <td>""" + FP.CostCenter+ """
                                </td>
                            </tr>
                            <tr>
                                <td>Note</td>
                                <td>:</td>
                                <td>""" + FP.Note+ """</td>
                            </tr>
                            <tr>
                                <td>Paid by</td>
                                <td>:</td>
                                <td>""" + FP.PaidBy+ """</td>
                            </tr>
                            <tr>
                                <td>PayReq Number</td>
                                <td>:</td>
                                <td>""" + FP.FP_Number+ """</td>
                            </tr>

                        </table>
               
                 
                            <br>
                            <table class="table-header" >
                                <tr>
                                <td width="8%">Paid to</td>
                                <td width="2%">:</td>
                                <td width="90%">""" + FP.PaidTo+ """</td>
                                </tr>
                                <tr>
                                    <td style="vertical-align: top;">Description
                                    <div> </div>
                                    <div> </div>
                                    <div> </div>
                                    <div> </div>
                                    <div> </div>
                                    <div> </div>
                                    <div> </div>
                                    <div> </div>
                                    </td>
                                    <td style="vertical-align: top;">:</td>
                                    <td vertical-align: top;"><div>"""+FP.Description.replace("\n","</div><div>")+"""</div></td>
                                </tr>
                                <tr>
                                    <td>Amount</td>
                                    <td>:</td>
                                    <td>
                                    <div>Rp. """ + FP.Amount+ """,-</div>
                                   
                                    </td>
                                </tr>
                                <tr>
                                    <td>Says</td>
                                    <td>:</td>
                                    <td>""" + FP.Says+ """</td>
                                </tr>
                            </table>
                    
                        


                        <h4>Approval</h4>
                        <table class="table-approve" style="white-space: nowrap;text-align: center;width:90%;">
                            <tr>
                                <td style="width:20%;">Received by</td>
                                <td style="width:20%;">Payment Approved by</td>
                                <td style="width:20%;">Request Approved by</td>
                                <td style="width:20%;">Request Approved by</td>
                                <td style="width:20%;">Created by</td>
                            </tr>
                            <tr style="height:100px;">
                                <td></td>
                                <td id="DirFinance"></td>
                                <td id="Finance"></td>
                                <td id="DeptHead"><div>"""+FP.DeptHead_Approval+"""</div><div>"""+FP.DeptHead_Approval_Date.strftime("%d-%m-%Y %H:%M:%S").replace(" ","</div><div>")+"""</div></td>
                                <td id="User"><div>Created</div><div>"""+FP.Date_Created.strftime("%d-%m-%Y %H:%M:%S").replace(" ","</div><div>")+"""</div></td>
                            </tr>
                            <tr>
                                <td></td>
                                <td>"""+ FP.Dir_Finance+"""</td>
                                <td>"""+ FP.Finance+"""</td>
                                <td>"""+ FP.DeptHead+"""</td>
                                <td>"""+ FP.User_Name+"""</td>
                            </tr>
                            <tr>
                            <td>Receiver</td>
                            <td>Direktur</td>
                            <td>Finance</td>
                            <td>Dept/Div Head</td>
                            <td>User</td>
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
                                            <a href="mailto:online.approval@aski.component.astra.co.id?subject=Approve: """+ FP.FP_Number+"""&body=Approve Payment Request with ID """+ FP.FP_Number+""" %0DApproval Message:" target="_blank" style="padding: 8px 12px; border: 1px solid #4bf542;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #ffffff;text-decoration: none;font-weight:bold;display: inline-block;">
                                                APPROVE             
                                            </a>
                                        </td>
                                        <td>&nbsp;&nbsp;</td>
                                        <td style="border-radius: 2px;width: 150px;text-align: center;" bgcolor="#ED2939">
                                            <a href="mailto:online.approval@aski.component.astra.co.id?subject=Reject: """+ FP.FP_Number+"""&body=Reject  Payment Request with ID """+ FP.FP_Number+"""  %0DReject Message:" target="_blank" style="padding: 8px 12px; border: 1px solid #ED2939;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #ffffff;text-decoration: none;font-weight:bold;display: inline-block;">
                                                REJECT             
                                            </a>
                                        </td>
                                        <td>&nbsp;&nbsp;</td>
                                        <td style="border-radius: 2px;width: 150px;text-align: center;" bgcolor="#cccccc">
                                            <a href="mailto:"""+FP.User_Email+"""?subject=Ask User: """+ FP.FP_Number+"""&body=Ask User about Payment Request with ID """+ FP.FP_Number+"""  %0DAsk User Message: " target="_blank" style="padding: 8px 12px; border: 1px solid #cccccc;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #000000;text-decoration: none;font-weight:bold;display: inline-block;">
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
                'Payment Request Online Approval: ' + FP.FP_Number,
                body=email_body,
                from_email=settings.EMAIL_HOST_USER,
                to=[FP.Finance_Email],
            )
            mailattach.content_subtype = "html"

            if len(str(FP.Attachment1))> 5:
                mailattach.attach_file(
                    'Media/'+str(FP.Attachment1))
            if len(str(FP.Attachment2))> 5:
                mailattach.attach_file(
                    'Media/'+str(FP.Attachment2))
            if len(str(FP.Attachment3))> 5:
                mailattach.attach_file(
                    'Media/'+str(FP.Attachment3))
            if len(str(FP.Attachment4))> 5:
                mailattach.attach_file(
                    'Media/'+str(FP.Attachment4))
            if len(str(FP.Attachment5))> 5:
                mailattach.attach_file(
                    'Media/'+str(FP.Attachment5))

            mailattach.send()

            models.Penyelesaian.objects.filter(
            FP_Number=FP.FP_Number).update(FP_Status="Approval")



            return redirect ("/BS/ListFA/")
        
    FP = models.Penyelesaian.objects.get(FP_Number = ID)
    costcenter = list(PRModels.CostCenter.objects.all())
    
    context = {
        'Judul': 'Payment Request',
        'FP' : FP,
        'CostCenter': costcenter
    }
    return render(request, 'bonmerah/DetailFP.html', context)


def GenerateBS(ID):
    BS = models.BonSementara.objects.get(BS_Number = ID)
    watermark = ""
    for x in range(100):
        watermark += ID + " "
    email_body = """
            <html>
                <head >
                    <meta name="pdfkit-page-size" content="A5"/>
                    <meta name="pdfkit-orientation" content="Landscape"/>
                </head>
                    <body style="font-family:'Palatino Linotype'">
                    <div id="watermark" style="min-height: 80vh;">
                    <hr>


                        <table class="table-approve" style="width:100%;text-align: center;">
                        <tr>
                        <td><img width="60px" src="http://127.0.0.1:8000/static/image/ASKI.png"/></td>
                        <td><h2>TEMPORARY BON</h2></td>
                        <td style="text-align: left;width:200px;">
                        <div>No Doc &nbsp&nbsp&nbsp&nbsp: FR-FACT.01-002</div>
                        <div>Revision &nbsp: 0</div>
                        <div>Eff. Start &nbsp: 01 Mar 2021</div>
                        </td>
                        </tr>
                        </table>
                    <p style="text-align: center;">Harus dipertanggung jawabkan paling lambat 2 (dua) hari</p>
                    <table class="table-header">
                        <tr>
                        <td width="1%" >BS Number</td>
                        <td width="1%" >:</td>
                        <td width="98%"> """+ BS.BS_Number +"""</td>
                        </tr>
                        <tr>
                        <td width="1%" >Paid By</td>
                        <td width="1%" >:</td>
                        <td width="98%"> """+ BS.PaidBy +"""</td>
                        </tr>
                        </table>

                            
                            <table class="table-approve" style="width: 100%;margin-top:2px;">
                                <tr>
                                    <th>Date Created</th>
                                    <th>Temporary Bon Note</th>
                                    <th>Value</th>
                                </tr>
                                <tr >
                                    <td style ="text-align:center;padding-top:50px;padding-bottom:50px;">

                                        <div >"""+ BS.Date_Created.strftime("%d-%m-%Y")+"""</div>
                                    </td>
                                    <td style="text-align: left;"><div>"""+BS.Note.replace("\n","</div><div>")+"""</div></td>
                                    <td style ="text-align:center;"> Rp. """+ BS.Jumlah+""",-</td>
                                </tr>
                                <tr >
                                    <td colspan="3">
                                        <p style="text-align: left;">Terbilang : """+ BS.Terbilang+"""</p>
                                    </td>
                                </tr>
                    
                            </table>
                    
                        

             
                        <table class="table-approve" style="white-space: nowrap;text-align: center;margin-top:2px;">
                            <tr>
                                <td style="width:25%;">Received by</td>
                                <td style="width:25%;">Approved by</td>
                                <td style="width:25%;">Approved by</td>
                                <td style="width:25%;">Created by</td>
                            </tr>
                            <tr style="height:90px;">
                                <td><div>Received</div><div>"""+BS.Received_Date.strftime("%d-%m-%Y %H:%M:%S").replace(" ","</div><div>")+"""</div></td>
                                <td id="Finance"><div>"""+BS.Finance_Approval+"""</div><div>"""+BS.Finance_Approval_Date.strftime("%d-%m-%Y %H:%M:%S").replace(" ","</div><div>")+"""</div></td>
                                <td id="DeptHead"><div>"""+BS.DeptHead_Approval+"""</div><div>"""+BS.DeptHead_Approval_Date.strftime("%d-%m-%Y %H:%M:%S").replace(" ","</div><div>")+"""</div></td>
                                <td id="User"><div>Created</div><div>"""+BS.Date_Created.strftime("%d-%m-%Y %H:%M:%S").replace(" ","</div><div>")+"""</div></td>
                            </tr>
                            <tr>
                                <td>"""+ BS.Receiver_Name+"""</td>
                                <td>"""+ BS.Finance+"""</td>
                                <td>"""+ BS.DeptHead+"""</td>
                                <td>"""+ BS.User_Name+"""</td>
                            </tr>
                            <tr>
                            <td style="width:25%;">Receiver</td>
                            <td style="width:25%;">Finance</td>
                            <td style="width:25%;">Dept/Div Head</td>
                            <td style="width:25%;">User</td>
                            </tr>
                        </table>

                    
                    <hr>
                     <i>This document is automatically generated by Online Approval System PT Astra Komponen Indonesia<i>
              
                       <h4>"""+watermark+"""</h4>

                </div>           
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
                        left: -50%;
                        width: 200%;
                        height: 200%;
                        z-index:-1;
                       color: #ffffcc;
                        line-height: 3em;
                        letter-spacing: 2px;
                        font-size: 30px;
                        pointer-events: none;
                        -webkit-transform: rotate(-45deg);
                        -moz-transform: rotate(-45deg);
                    }
                    </style>
                    </body>
                    </html>
            
            """
    config = pdfkit.configuration(
            wkhtmltopdf='C:\Program Files\wkhtmltopdf\\bin\wkhtmltopdf.exe')
    pdfkit.from_string(email_body, "Media\Document\\"+ID +
                            ".pdf", configuration=config)
    models.BonSementara.objects.filter(
            BS_Number=ID).update(BS_Status="Finished")


def GenerateFP(ID):
    FP = models.Penyelesaian.objects.get(FP_Number = ID)
    watermark = ""
    for x in range(100):
        watermark += ID + " "
    attachment = ""
    if len(str(FP.Attachment1))>5:
        attachment += """<img height = "300px" src="http://127.0.0.1:8000/Media/"""+str(FP.Attachment1)+""""/>"""
    if len(str(FP.Attachment2))>5:
        attachment += """<img height = "300px"  src="http://127.0.0.1:8000/Media/"""+str(FP.Attachment2)+""""/>"""
    if len(str(FP.Attachment3))>5:
        attachment += """<img height = "300px"  src="http://127.0.0.1:8000/Media/"""+str(FP.Attachment3)+""""/>"""
    if len(str(FP.Attachment4))>5:
        attachment += """<img height = "300px"  src="http://127.0.0.1:8000/Media/"""+str(FP.Attachment4)+""""/>"""
    if len(str(FP.Attachment5))>5:
        attachment += """<img height = "300px"  src="http://127.0.0.1:8000/Media/"""+str(FP.Attachment5)+""""/>"""




    email_body = """
            <html>
                <head >
                    <meta name="pdfkit-page-size" content="A5"/>
                    <meta name="pdfkit-orientation" content="Landscape"/>
                </head>
                    <body style="font-family:'Palatino Linotype'">
                    <div id="watermark" style="min-height: 80vh;">
                    <hr>


                        <table class="table-approve" style="width:100%;text-align: center;margin-bottom:2px;">
                        <tr>
                        <td><img width="60px" src="http://127.0.0.1:8000/static/image/ASKI.png"/></td>
                        <td><h2>Payment Request</h2></td>
                        <td style="text-align: left;width:200px;">
                        <div>No Doc &nbsp&nbsp&nbsp&nbsp: FR-FACT.01-004</div>
                        <div>Revision &nbsp: 0</div>
                        <div>Eff. Start &nbsp: 01 Mar 2021</div>
                        </td>
                        </tr>
                        </table>
                    <table class="table-header" style="margin-bottom:2px;" >
                            <tr >
                                <td width="8%" >Bussiness Unit</td>
                                <td width="2%">:</td>
                                <td width="40%">""" + FP.Bussiness_Unit+ """</td>
                                <td width="8%">Note</td>
                                <td width="2%">:</td>
                                <td width="40%">""" + FP.Note+ """</td>
                            </tr>
                            <tr>
                                <td>Div / Dept</td>
                                <td>:</td>
                                <td>""" + FP.Dept+ """</td>
                                <td>Paid by</td>
                                <td>:</td>
                                <td>""" + FP.PaidBy+ """</td>
                            </tr>
                            <tr>
                                <td>User</td>
                                <td>:</td>
                                <td>""" + FP.User_Name+ """
                                </td>
                                <td>PayReq Number</td>
                                <td>:</td>
                                <td>""" + FP.FP_Number+ """</td>
                            </tr>
                            <tr>
                                <td>Cost Center</td>
                                <td>:</td>
                                <td>""" + FP.CostCenter+ """
                                </td>
                                <td>Temp Bon Reference</td>
                                <td>:</td>
                                <td>""" + FP.Reference+ """</td>
                            </tr>

                        </table>
               
                 
                       
                            <table class="table-header" style="margin-bottom:2px;">
                                <tr>
                                <td width="8%">Paid to</td>
                                <td width="2%">:</td>
                                <td width="90%">""" + FP.PaidTo+ """</td>
                                </tr>
                                <tr>
                                    <td style="vertical-align: top;padding-bottom: 100px;">Description
                                  
                                    </td>
                                    <td style="vertical-align: top;">:</td>
                                    <td vertical-align: top;"><div>"""+FP.Description.replace("\n","</div><div>")+"""</div></td>
                                </tr>
                                <tr>
                                    <td>Amount</td>
                                    <td>:</td>
                                    <td>
                                    <div>Rp. """ + FP.Amount + """,-</div>
                                   
                                    </td>
                                </tr>
                                <tr>
                                    <td>Says</td>
                                    <td>:</td>
                                    <td>""" + FP.Says+ """</td>
                                </tr>
                            </table>
                    
                        


                        <h4>Approval</h4>
                        <table class="table-approve" style="text-align: center;width:100%;">
                            <tr>
                                <td style="width:20%;">Received by</td>
                                <td style="width:20%;">Payment Approved by</td>
                                <td style="width:20%;">Request Approved by</td>
                                <td style="width:20%;">Request Approved by</td>
                                <td style="width:20%;">Created by</td>
                            </tr>
                            <tr style="height:80px;">
                                <td><div>Received</div><div>"""+FP.Received_Date.strftime("%d-%m-%Y %H:%M:%S").replace(" ","</div><div>")+"""</div></td>
                                <td id="DirFinance"><div>"""+FP.Dir_Finance_Approval+"""</div><div>"""+FP.Dir_Finance_Approval_Date.strftime("%d-%m-%Y %H:%M:%S").replace(" ","</div><div>")+"""</div></td>
                                <td id="Finance"><div>"""+FP.Finance_Approval+"""</div><div>"""+FP.Finance_Approval_Date.strftime("%d-%m-%Y %H:%M:%S").replace(" ","</div><div>")+"""</div></td>
                                <td id="DeptHead"><div>"""+FP.DeptHead_Approval+"""</div><div>"""+FP.DeptHead_Approval_Date.strftime("%d-%m-%Y %H:%M:%S").replace(" ","</div><div>")+"""</div></td>
                                <td id="User"><div>Created</div><div>"""+FP.Date_Created.strftime("%d-%m-%Y %H:%M:%S").replace(" ","</div><div>")+"""</div></td>
                            </tr>
                            <tr>
                                <td>"""+ FP.Receiver_Name+"""</td>
                                <td>"""+ FP.Dir_Finance+"""</td>
                                <td>"""+ FP.Finance+"""</td>
                                <td>"""+ FP.DeptHead+"""</td>
                                <td>"""+ FP.User_Name+"""</td>
                            </tr>
                            <tr>
                            <td>Receiver</td>
                            <td>Direktur</td>
                            <td>Finance</td>
                            <td>Dept/Div Head</td>
                            <td>User</td>
                            </tr>
                        </table>

        

                    
                    <hr>
                     <i>This document is automatically generated by Online Approval System PT Astra Komponen Indonesia<i>
              
                       <h4>"""+watermark+"""</h4>

                </div>           
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
                        left: -50%;
                        width: 200%;
                        height: 200%;
                        z-index:-1;
                       color: #ffffcc;
                        line-height: 3em;
                        letter-spacing: 2px;
                        font-size: 30px;
                        pointer-events: none;
                        -webkit-transform: rotate(-45deg);
                        -moz-transform: rotate(-45deg);
                    }
                    </style>

                    """+attachment+"""
                    </body>
                    </html>
            
            """
    config = pdfkit.configuration(
            wkhtmltopdf='C:\Program Files\wkhtmltopdf\\bin\wkhtmltopdf.exe')
    pdfkit.from_string(email_body, "Media\Document\\"+ID +
                            ".pdf", configuration=config)
    models.Penyelesaian.objects.filter(
            FP_Number=ID).update(FP_Status="Finished")
    if (len(FP.Reference)>5):
        models.BonSementara.objects.filter(
            BS_Number=FP.Reference).update(BS_Status="Closed")

def exportbon(request):
    resource = resources.BonSementara()
    dataset = resource.export()
    response = HttpResponse(dataset.xls, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="bon sementara.xls"'
    #models.activity_log(user = request.user.username,PP_Number="",activity="export budget").save()
    return response