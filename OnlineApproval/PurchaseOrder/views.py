from ast import Delete
import os
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from PyPDF2 import PdfFileWriter, PdfFileReader
from . import forms
from . import models
from django.core import serializers
from django.shortcuts import redirect
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
import datetime
from django.http import HttpResponse
import pdfkit
import shutil
from pdfminer.layout import LAParams, LTTextBox
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.clickjacking import xframe_options_sameorigin
import pyodbc
from . import resources
import requests 

# Create your views here.



def SQLWrite(query):
    print(query)
    cnn = pyodbc.connect('DRIVER={SQL Server};PORT=port;SERVER=10.14.81.30;PORT=1433;DATABASE=ASKICTR;UID=askictr;PWD=D1msum@1000')
    sqlcursor = cnn.cursor()
    sqlcursor.execute(query)
    sqlcursor.commit()

def is_membercreatePO(user):
    return user.groups.filter(name='Allow_Create_PO').exists()


@login_required
@user_passes_test(is_membercreatePO)
def create(request):
    if request.method == "GET":
        PO = forms.POData()
        PO.fields['PO_Admin'].initial = request.user.username
        PO.fields['Revision_Status'].initial = 0
        approval = list(models.POApproval.objects.filter(Admin = request.user))
        data = serializers.serialize(
            "json", models.POApproval.objects.filter(Admin = request.user))

    elif request.method == "POST":
        if (models.POData.objects.filter(PO_Number=request.POST["PO_Number"]).exists()):
            context = {
                'Error': 'WARNING!! \n PO ' + request.POST["PO_Number"] + ' sudah pernah disubmit sebelumnya, lakukan revise untuk merevisi PO yang sudah pernah di submit.'
            }
            return render(request, 'purchaseorder/Error.html', context)

        else:
            PO = forms.POData(request.POST, request.FILES)

        if PO.is_valid():
            PO.save()
            POData = models.POData.objects.get(
                PO_Number=request.POST["PO_Number"])


            Note = ""
            if POData.Note is not None:
                Note = """
                <tr>
                <td>Note</td>
                <td>: """+POData.Note+"""</td>
                </tr>
                """

            if POData.PO_Admin_Email == POData.PO_SPV_Email and POData.PO_PresDirektur is not None and POData.PO_Direktur is not None:
                approval = """
                            <table class="table-approve" style="white-space: nowrap;text-align: center;">
                                <tr>
                                    <td style="width:15%;">Create by</td>
                                    <td style="width:15%;">Approved by</td>
                                    <td style="width:15%;">Approved by</td>
                                    <td style="width:15%;">Approved by</td>

                                </tr>
                                <tr style="height:100px;">
                                    <td ><div>Created</div><div>"""+datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S").replace(" ", "</div><div>")+"""</div></td>
                                    <td id="Dept Head"></td>
                                    <td id="Direktur"></td>
                                    <td id="Pres Direktur"></td>
                                </tr>
                                <tr>
                                    <td>"""+POData.PO_SPV+"""</td>
                                    <td>"""+POData.PO_Dept_Head+"""</td>
                                    <td>"""+POData.PO_Direktur+"""</td>
                                    <td>"""+POData.PO_PresDirektur+"""</td>
                                </tr>
                                <tr>
                                <td>Supervisor</td>
                                <td>Dept Head</td>
                                <td>Direktur</td>
                                <td>Presiden Direktur</td>
                                </tr>
                            </table>
                """
            elif POData.PO_Admin_Email == POData.PO_SPV_Email and POData.PO_PresDirektur is None and POData.PO_Direktur is not None:
                approval = """
                            <table class="table-approve" style="white-space: nowrap;text-align: center;">
                                <tr>
                                    <td style="width:15%;">Create by</td>
                                    <td style="width:15%;">Approved by</td>
                                    <td style="width:15%;">Approved by</td>
                                </tr>
                                <tr style="height:100px;">
                                    <td ><div>Created</div><div>"""+datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S").replace(" ", "</div><div>")+"""</div></td>
                                    <td id="Dept Head"></td>
                                    <td id="Direktur"></td>
                                </tr>
                                <tr>
                                    <td>"""+POData.PO_SPV+"""</td>
                                    <td>"""+POData.PO_Dept_Head+"""</td>
                                    <td>"""+POData.PO_Direktur+"""</td>
                                </tr>
                                <tr>
                                <td>Supervisor</td>
                                <td>Dept Head</td>
                                <td>Direktur</td>
                                </tr>
                            </table>
                """
            elif POData.PO_Admin_Email == POData.PO_SPV_Email and POData.PO_PresDirektur is not None and POData.PO_Direktur is None:
                approval = """
                            <table class="table-approve" style="white-space: nowrap;text-align: center;">
                                <tr>
                                    <td style="width:15%;">Create by</td>
                                    <td style="width:15%;">Approved by</td>
                                    <td style="width:15%;">Approved by</td>
                                </tr>
                                <tr style="height:100px;">
                                    <td ><div>Created</div><div>"""+datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S").replace(" ", "</div><div>")+"""</div></td>
                                    <td id="Dept Head"></td>
                                    <td id="Pres Direktur"></td>
                                </tr>
                                <tr>
                                    <td>"""+POData.PO_SPV+"""</td>
                                    <td>"""+POData.PO_Dept_Head+"""</td>
                                    <td>"""+POData.PO_PresDirektur+"""</td>
                                </tr>
                                <tr>
                                <td>Supervisor</td>
                                <td>Dept Head</td>
                                <td>Presiden Direktur</td>
                                </tr>
                            </table>
                """
            elif POData.PO_PresDirektur is not None and POData.PO_Direktur is not None:
                approval = """
                            <table class="table-approve" style="white-space: nowrap;text-align: center;">
                                <tr>
                                    <td style="width:15%;">Create by</td>
                                    <td style="width:15%;">Approved by</td>
                                    <td style="width:15%;">Approved by</td>
                                    <td style="width:15%;">Approved by</td>
                                    <td style="width:15%;">Approved by</td>

                                </tr>
                                <tr style="height:100px;">
                                    <td id="User"><div>Created</div><div>"""+datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S").replace(" ", "</div><div>")+"""</div></td>
                                    <td id="Supervisor"></td>
                                    <td id="Dept Head"></td>
                                    <td id="Direktur"></td>
                                    <td id="Pres Direktur"></td>
                                </tr>
                                <tr>
                                    <td>"""+POData.PO_Admin+"""</td>
                                    <td>"""+POData.PO_SPV+"""</td>
                                    <td>"""+POData.PO_Dept_Head+"""</td>
                                    <td>"""+POData.PO_Direktur+"""</td>
                                    <td>"""+POData.PO_PresDirektur+"""</td>
                                </tr>
                                <tr>
                                <td>Admin</td>
                                <td>Supervisor</td>
                                <td>Dept Head</td>
                                <td>Direktur</td>
                                <td>Presiden Direktur</td>
                                </tr>
                            </table>
                """
            elif POData.PO_PresDirektur is None and POData.PO_Direktur is not None:
                approval = """
                            <table class="table-approve" style="white-space: nowrap;text-align: center;">
                                <tr>
                                    <td style="width:15%;">Create by</td>
                                    <td style="width:15%;">Approved by</td>
                                    <td style="width:15%;">Approved by</td>
                                    <td style="width:15%;">Approved by</td>
                                </tr>
                                <tr style="height:100px;">
                                    <td id="User"><div>Created</div><div>"""+datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S").replace(" ", "</div><div>")+"""</div></td>
                                    <td id="Supervisor"></td>
                                    <td id="Dept Head"></td>
                                    <td id="Pres Direktur"></td>
                                </tr>
                                <tr>
                                    <td>"""+POData.PO_Admin+"""</td>
                                    <td>"""+POData.PO_SPV+"""</td>
                                    <td>"""+POData.PO_Dept_Head+"""</td>
                                    <td>"""+POData.PO_Direktur+"""</td>
                                </tr>
                                <tr>
                                <td>Admin</td>
                                <td>Supervisor</td>
                                <td>Dept Head</td>
                                <td>Direktur</td>
                                </tr>
                            </table>
                """
            elif POData.PO_PresDirektur is not None and POData.PO_Direktur is None:
                approval = """
                            <table class="table-approve" style="white-space: nowrap;text-align: center;">
                                <tr>
                                    <td style="width:15%;">Create by</td>
                                    <td style="width:15%;">Approved by</td>
                                    <td style="width:15%;">Approved by</td>
                                    <td style="width:15%;">Approved by</td>
                                </tr>
                                <tr style="height:100px;">
                                    <td id="User"><div>Created</div><div>"""+datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S").replace(" ", "</div><div>")+"""</div></td>
                                    <td id="Supervisor"></td>
                                    <td id="Dept Head"></td>
                                    <td id="Direktur"></td>
                                </tr>
                                <tr>
                                    <td>"""+POData.PO_Admin+"""</td>
                                    <td>"""+POData.PO_SPV+"""</td>
                                    <td>"""+POData.PO_Dept_Head+"""</td>
                                    <td>"""+POData.PO_PresDirektur+"""</td>
                                </tr>
                                <tr>
                                <td>Admin</td>
                                <td>Supervisor</td>
                                <td>Dept Head</td>
                                <td>Presiden Direktur</td>
                                </tr>
                            </table>
                """
            email_body = """
            <html>
                   <head style="margin-bottom: 0px;">Dear Mr/Ms """ + request.POST["PO_SPV"] + """,</head>
                    <body>
                    <p style="margin-bottom: 0px;margin-top: 0px;">This purchase order needs your approval </>
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
                            <td><h2>PURCHASE ORDER APPROVAL</h2></td>
                            <td style="text-align: left;width:200px;">
                            <div>No Doc &nbsp&nbsp&nbsp&nbsp: FR-FACT.01-003</div>
                            <div>Revision &nbsp: 0</div>
                            <div>Eff. Start &nbsp: 01 Mei 2022</div>
                            </td>
                            </tr>
                            </table>
                            <br>

                            <table class="table-header" width = "100%">
                            <tr>
                            <td width = "5%">Company</td>
                            <td>: PT Astra Komponen Indonesia</td>
                            </tr>
                            <tr>
                            <td>PO Number</td>
                            <td>: """+str(POData.PO_Number)+"""</td>
                            </tr>
                            <tr>
                            <td>PO Date</td>
                            <td>: """+POData.PO_Date+"""</td>
                            </tr>
                                                        <tr>
                            <td>Revision</td>
                            <td>: """+str(POData.Revision_Status)+"""</td>
                            </tr>
                            <tr>
                            <td>Vendor Number</td>
                            <td>: """+str(POData.Vendor_Number)+"""</td>
                            </tr>
                            <tr>
                            <td>Vendor Name</td>
                            <td>: """+POData.Vendor_Name+"""</td>
                            </tr>

                            """+ Note +"""


                            </table>

                            <h4>Document PO</h4>
                            <p>Attached.</p>

                            <h4>Approval</h4>
                           """+approval+"""

                        <br>
                        <hr>
                        <p> Please give your response by click approval button bellow and then click send button. A response at your earliest convenience would be much appreciated. </p>
                        <table width="100%" cellspacing="0" cellpadding="0">
                            <tr>
                                <td>
                                    <table cellspacing="0" cellpadding="0">
                                        <tr>
                                            <td style="border-radius: 2px;width : 150px;text-align: center;" bgcolor="#4bf542">
                                                <a href="mailto:online.approval@aski.component.astra.co.id?subject=Approve: PO""" + request.POST["PO_Number"]+"""Rev""" + str(request.POST['Revision_Status'])+"""&body=Approve Purchase Order with ID """ + request.POST["PO_Number"]+""" Rev""" + str(request.POST['Revision_Status'])+""" %0DApproval Message:" target="_blank" style="padding: 8px 12px; border: 1px solid #4bf542;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #ffffff;text-decoration: none;font-weight:bold;display: inline-block;">
                                                    APPROVE
                                                </a>
                                            </td>
                                            <td>&nbsp;&nbsp;</td>
                                            <td style="border-radius: 2px;width: 150px;text-align: center;" bgcolor="#ED2939">
                                                <a href="mailto:online.approval@aski.component.astra.co.id?subject=Reject: PO""" + request.POST["PO_Number"]+"""Rev""" + str(request.POST['Revision_Status'])+"""&body=Reject  Purchase Order with ID """ + request.POST["PO_Number"]+""" Rev""" + str(request.POST['Revision_Status'])+"""  %0DReject Message:" target="_blank" style="padding: 8px 12px; border: 1px solid #ED2939;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #ffffff;text-decoration: none;font-weight:bold;display: inline-block;">
                                                    REJECT
                                                </a>
                                            </td>
                                            <td>&nbsp;&nbsp;</td>
                                            <td style="border-radius: 2px;width: 150px;text-align: center;" bgcolor="#ebde34">
                                                <a href="mailto:online.approval@aski.component.astra.co.id?subject=Revise: PO"""+request.POST["PO_Number"]+"""Rev""" + str(request.POST['Revision_Status'])+"""&body=Need Revise Purchase Order with ID """+request.POST["PO_Number"]+""" Rev""" + str(request.POST['Revision_Status'])+""" %0DRevision Message:" target="_blank" style="padding: 8px 12px; border: 1px solid #ebde34;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #000000;text-decoration: none;font-weight:bold;display: inline-block;">
                                                    REVISE
                                                </a>
                                            </td>
                                            <td>&nbsp;&nbsp;</td>
                                            <td style="border-radius: 2px;width: 150px;text-align: center;" bgcolor="#cccccc">
                                                <a href="mailto:"""+request.POST["PO_Admin_Email"]+"""?subject=Ask User: PO""" + request.POST["PO_Number"]+"""Rev""" + str(request.POST['Revision_Status'])+"""&body=Ask User about Purchase Order with ID """ + request.POST["PO_Number"]+""" Rev""" + str(request.POST['Revision_Status'])+"""  %0DAsk User Message: " target="_blank" style="padding: 8px 12px; border: 1px solid #cccccc;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #000000;text-decoration: none;font-weight:bold;display: inline-block;">
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
            if POData.PO_Admin_Email == POData.PO_SPV_Email :
                models.POData.objects.filter(PO_Number=request.POST['PO_Number']).update(PO_SPV_Approval_Date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), PO_SPV_Approval_Status = 'Approved')
                mailattach = EmailMessage(
                    'Purchase Order Online Approval: ' +
                        request.POST['PO_Number'] + """Rev""" +
                            str(request.POST['Revision_Status']),
                    body=email_body,
                    from_email=settings.EMAIL_HOST_USER,
                    to=[request.POST['PO_Dept_Head_Email']],
                )
            else :
                mailattach = EmailMessage(
                    'Purchase Order Online Approval: ' +
                        request.POST['PO_Number'] + """Rev""" +
                            str(request.POST['Revision_Status']),
                    body=email_body,
                    from_email=settings.EMAIL_HOST_USER,
                    to=[request.POST['PO_SPV_Email']],
                )
            mailattach.content_subtype = "html"

            shutil.copy("Media\\"+str(POData.PO_Before_Approval),
            str("Media\\UnsignedPO\\PO "+str(POData.PO_Number) +"rev"+str(POData.Revision_Status)+".pdf"))
          
            mailattach.attach_file("Media\\UnsignedPO\\PO "+str(POData.PO_Number) +"rev"+str(POData.Revision_Status)+".pdf")

            if len(str(POData.PO_Attachment1)) > 5:
                mailattach.attach_file('Media/'+str(POData.PO_Attachment1))
            if len(str(POData.PO_Attachment2)) > 5:
                mailattach.attach_file('Media/'+str(POData.PO_Attachment2))
            if len(str(POData.PO_Attachment3)) > 5:
                mailattach.attach_file('Media/'+str(POData.PO_Attachment3))
            if len(str(POData.PO_Attachment4)) > 5:
                mailattach.attach_file('Media/'+str(POData.PO_Attachment4))

            mailattach.send()

            if POData.PO_Admin_Email == POData.PO_SPV_Email :
                 models.Send(htmlmessage=email_body,
                            mailfrom='online.approval@aski.component.astra.co.id',
                            mailto=request.POST['PO_Dept_Head_Email'],
                            PO_Number=request.POST['PO_Number']+"Rev" + str(request.POST['Revision_Status']),
                            mailheader='Purchase Order Online Approval: ' + request.POST['PO_Number']+"""Rev"""+ str(request.POST['Revision_Status'])).save()
 
            else :
                models.Send(htmlmessage=email_body,
                            mailfrom='online.approval@aski.component.astra.co.id',
                            mailto=request.POST['PO_SPV_Email'],
                            PO_Number=request.POST['PO_Number']+"Rev" + str(request.POST['Revision_Status']),
                            mailheader='Purchase Order Online Approval: ' + request.POST['PO_Number']+"""Rev"""+ str(request.POST['Revision_Status'])).save()           
            models.POData.objects.filter(
            PO_Number=request.POST['PO_Number']).update(PO_Status="Created")

            return redirect('/PO/ListPO/')
        else :
            print(PO.errors)
            context={
                'Error': PO.errors
            }
            return render(request, 'purchaseorder/Error.html',context)


    context={
        'POForm' : PO,
        'Judul' : 'Create Purchase Order Approval Request',
        'Approval' : approval,
        'Data': data,

    }
    return render(request, 'purchaseorder/CreatePO.html',context)

@login_required
@user_passes_test(is_membercreatePO)
def listPO (request):

    POData = models.POData.objects.all().order_by('-id')
    if request.method == "POST":
        #print(request.POST)
        data = dict(request.POST)
        data.pop('csrfmiddlewaretoken')
        data.pop('table_length')
        for key in data.keys():
            var = key.split("rev", 2)
            value = str(data[key])[2:][:-2]
            if (len(value) > 0):
                print(var[0][2:])
                print(var[1])
                models.POData.objects.filter(PO_Number=var[0][2:], Revision_Status =  var[1]).update(
                    User_Note=value)

    context={
        'Judul' : 'List Purchase Order Approval',
        'POData' : POData,   
    }
    return render(request, 'purchaseorder/ListPO.html',context)

@login_required
@user_passes_test(is_membercreatePO)
@xframe_options_sameorigin
def detailPO(request,po_number,revision):

   
    if request.method == "POST":
        print(request.POST)
        models.POData.objects.filter(PO_Number = request.POST["PONumber"], Revision_Status = request.POST["Revision"]).update(PO_Status = "Canceled by "+ str(request.user))
        SQLWrite(f"update dbo.release_PO set Status = 'Canceled by {str(request.user)}' , Modified_Date =  GetDate() where PO_Number = '{request.POST['PONumber']}'  and Revision =  '{request.POST['Revision']}' ")



    POData = models.POData.objects.get(PO_Number = po_number, Revision_Status = revision)

    context={
        'Judul' : 'Detail Purchase Order Approval',
        'POData' : POData,
    }
    return render(request, 'purchaseorder/DetailPO.html',context)


    
def exportlistPO(request):
    resource = resources.ListPO()
    dataset = resource.export(models.POData.objects.all())
    response = HttpResponse(dataset.xls, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="listPO.xls"'
    #models.activity_log(user = request.user.username,PP_Number="",activity="export PO").save()
    return response


@login_required
@user_passes_test(is_membercreatePO)
def revisePO(request,po_number,revision):

    POData = models.POData.objects.get(PO_Number = po_number, Revision_Status = revision)

    if request.method == "GET":
        PO = forms.POData()
        PO.fields['PO_Admin'].initial = request.user.username
        PO.fields['Revision_Status'].initial = int(revision)+1
        approval = list(models.POApproval.objects.filter(Admin = request.user))
        data = serializers.serialize(
            "json", models.POApproval.objects.filter(Admin = request.user))
    elif request.method == "POST":
        print(request.POST)
        PO = forms.POData(request.POST,request.FILES)

        if PO.is_valid():
            PO.save()
            POData = models.POData.objects.get(PO_Number = request.POST["PO_Number"],Revision_Status = request.POST["Revision_Status"])
            
            
            Note = ""
            if POData.Note is not None:
                Note = """
                <tr>
                <td>Note</td>
                <td>: """+POData.Note+"""</td>
                </tr>
                """

            if POData.PO_Admin_Email == POData.PO_SPV_Email and POData.PO_PresDirektur is not None and POData.PO_Direktur is not None:
                approval = """
                            <table class="table-approve" style="white-space: nowrap;text-align: center;">
                                <tr>
                                    <td style="width:15%;">Create by</td>
                                    <td style="width:15%;">Approved by</td>
                                    <td style="width:15%;">Approved by</td>
                                    <td style="width:15%;">Approved by</td>

                                </tr>
                                <tr style="height:100px;">
                                    <td ><div>Created</div><div>"""+datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S").replace(" ", "</div><div>")+"""</div></td>
                                    <td id="Dept Head"></td>
                                    <td id="Direktur"></td>
                                    <td id="Pres Direktur"></td>
                                </tr>
                                <tr>
                                    <td>"""+POData.PO_SPV+"""</td>
                                    <td>"""+POData.PO_Dept_Head+"""</td>
                                    <td>"""+POData.PO_Direktur+"""</td>
                                    <td>"""+POData.PO_PresDirektur+"""</td>
                                </tr>
                                <tr>
                                <td>Supervisor</td>
                                <td>Dept Head</td>
                                <td>Direktur</td>
                                <td>Presiden Direktur</td>
                                </tr>
                            </table>
                """
            elif POData.PO_Admin_Email == POData.PO_SPV_Email and POData.PO_PresDirektur is None and POData.PO_Direktur is not None:
                approval = """
                            <table class="table-approve" style="white-space: nowrap;text-align: center;">
                                <tr>
                                    <td style="width:15%;">Create by</td>
                                    <td style="width:15%;">Approved by</td>
                                    <td style="width:15%;">Approved by</td>
                                </tr>
                                <tr style="height:100px;">
                                    <td ><div>Created</div><div>"""+datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S").replace(" ", "</div><div>")+"""</div></td>
                                    <td id="Dept Head"></td>
                                    <td id="Direktur"></td>
                                </tr>
                                <tr>
                                    <td>"""+POData.PO_SPV+"""</td>
                                    <td>"""+POData.PO_Dept_Head+"""</td>
                                    <td>"""+POData.PO_Direktur+"""</td>
                                </tr>
                                <tr>
                                <td>Supervisor</td>
                                <td>Dept Head</td>
                                <td>Direktur</td>
                                </tr>
                            </table>
                """
            elif POData.PO_Admin_Email == POData.PO_SPV_Email and POData.PO_PresDirektur is not None and POData.PO_Direktur is None:
                approval = """
                            <table class="table-approve" style="white-space: nowrap;text-align: center;">
                                <tr>
                                    <td style="width:15%;">Create by</td>
                                    <td style="width:15%;">Approved by</td>
                                    <td style="width:15%;">Approved by</td>
                                </tr>
                                <tr style="height:100px;">
                                    <td ><div>Created</div><div>"""+datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S").replace(" ", "</div><div>")+"""</div></td>
                                    <td id="Dept Head"></td>
                                    <td id="Pres Direktur"></td>
                                </tr>
                                <tr>
                                    <td>"""+POData.PO_SPV+"""</td>
                                    <td>"""+POData.PO_Dept_Head+"""</td>
                                    <td>"""+POData.PO_PresDirektur+"""</td>
                                </tr>
                                <tr>
                                <td>Supervisor</td>
                                <td>Dept Head</td>
                                <td>Presiden Direktur</td>
                                </tr>
                            </table>
                """
            elif POData.PO_PresDirektur is not None and POData.PO_Direktur is not None:
                approval = """
                            <table class="table-approve" style="white-space: nowrap;text-align: center;">
                                <tr>
                                    <td style="width:15%;">Create by</td>
                                    <td style="width:15%;">Approved by</td>
                                    <td style="width:15%;">Approved by</td>
                                    <td style="width:15%;">Approved by</td>
                                    <td style="width:15%;">Approved by</td>

                                </tr>
                                <tr style="height:100px;">
                                    <td id="User"><div>Created</div><div>"""+datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S").replace(" ", "</div><div>")+"""</div></td>
                                    <td id="Supervisor"></td>
                                    <td id="Dept Head"></td>
                                    <td id="Direktur"></td>
                                    <td id="Pres Direktur"></td>
                                </tr>
                                <tr>
                                    <td>"""+POData.PO_Admin+"""</td>
                                    <td>"""+POData.PO_SPV+"""</td>
                                    <td>"""+POData.PO_Dept_Head+"""</td>
                                    <td>"""+POData.PO_Direktur+"""</td>
                                    <td>"""+POData.PO_PresDirektur+"""</td>
                                </tr>
                                <tr>
                                <td>Admin</td>
                                <td>Supervisor</td>
                                <td>Dept Head</td>
                                <td>Direktur</td>
                                <td>Presiden Direktur</td>
                                </tr>
                            </table>
                """
            elif POData.PO_PresDirektur is None and POData.PO_Direktur is not None:
                approval = """
                            <table class="table-approve" style="white-space: nowrap;text-align: center;">
                                <tr>
                                    <td style="width:15%;">Create by</td>
                                    <td style="width:15%;">Approved by</td>
                                    <td style="width:15%;">Approved by</td>
                                    <td style="width:15%;">Approved by</td>
                                </tr>
                                <tr style="height:100px;">
                                    <td id="User"><div>Created</div><div>"""+datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S").replace(" ", "</div><div>")+"""</div></td>
                                    <td id="Supervisor"></td>
                                    <td id="Dept Head"></td>
                                    <td id="Pres Direktur"></td>
                                </tr>
                                <tr>
                                    <td>"""+POData.PO_Admin+"""</td>
                                    <td>"""+POData.PO_SPV+"""</td>
                                    <td>"""+POData.PO_Dept_Head+"""</td>
                                    <td>"""+POData.PO_Direktur+"""</td>
                                </tr>
                                <tr>
                                <td>Admin</td>
                                <td>Supervisor</td>
                                <td>Dept Head</td>
                                <td>Direktur</td>
                                </tr>
                            </table>
                """
            elif POData.PO_PresDirektur is not None and POData.PO_Direktur is None:
                approval = """
                            <table class="table-approve" style="white-space: nowrap;text-align: center;">
                                <tr>
                                    <td style="width:15%;">Create by</td>
                                    <td style="width:15%;">Approved by</td>
                                    <td style="width:15%;">Approved by</td>
                                    <td style="width:15%;">Approved by</td>
                                </tr>
                                <tr style="height:100px;">
                                    <td id="User"><div>Created</div><div>"""+datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S").replace(" ", "</div><div>")+"""</div></td>
                                    <td id="Supervisor"></td>
                                    <td id="Dept Head"></td>
                                    <td id="Direktur"></td>
                                </tr>
                                <tr>
                                    <td>"""+POData.PO_Admin+"""</td>
                                    <td>"""+POData.PO_SPV+"""</td>
                                    <td>"""+POData.PO_Dept_Head+"""</td>
                                    <td>"""+POData.PO_PresDirektur+"""</td>
                                </tr>
                                <tr>
                                <td>Admin</td>
                                <td>Supervisor</td>
                                <td>Dept Head</td>
                                <td>Presiden Direktur</td>
                                </tr>
                            </table>
                """            
            email_body = """
            <html>
                   <head style="margin-bottom: 0px;">Dear Mr/Ms """ + request.POST["PO_SPV"] + """,</head>
                    <body>
                    <p style="margin-bottom: 0px;margin-top: 0px;">This purchase order needs your approval </>
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
                            <td><h2>PURCHASE ORDER APPROVAL</h2></td>
                            <td style="text-align: left;width:200px;">
                            <div>No Doc &nbsp&nbsp&nbsp&nbsp: FR-FACT.01-003</div>
                            <div>Revision &nbsp: 0</div>
                            <div>Eff. Start &nbsp: 01 Mei 2022</div>
                            </td>
                            </tr>
                            </table>  
                            <br>

                            <table class="table-header" width = "100%">
                            <tr>
                            <td width = "5%">Company</td>
                            <td>: PT Astra Komponen Indonesia</td>
                            </tr>
                            <tr>
                            <td>PO Number</td>
                            <td>: """+str(POData.PO_Number)+"""</td>
                            </tr>
                            <tr>
                            <td>PO Date</td>
                            <td>: """+POData.PO_Date+"""</td>
                            </tr>
                            <tr>
                            <td>Revision</td>
                            <td>: """+str(POData.Revision_Status)+"""</td>
                            </tr>
                            <tr>
                            <td>Revision Message</td>
                            <td>: """+str(POData.Revise_Message)+"""</td>
                            </tr>
                            <tr>
                            <td>Vendor Number</td>
                            <td>: """+str(POData.Vendor_Number)+"""</td>
                            </tr>   
                            <tr>
                            <td>Vendor Name</td>
                            <td>: """+POData.Vendor_Name+"""</td>
                            </tr>   

                            """+Note+"""

                         
                            </table>

                            <h4>Document PO</h4>
                            <p>Attached.</p>

                            <h4>Approval</h4>
                           """+approval+""" 

                        <br>
                        <hr>
                        <p> Please give your response by click approval button bellow and then click send button. A response at your earliest convenience would be much appreciated. </p>
                        <table width="100%" cellspacing="0" cellpadding="0">
                            <tr>
                                <td>
                                    <table cellspacing="0" cellpadding="0">
                                        <tr>
                                            <td style="border-radius: 2px;width : 150px;text-align: center;" bgcolor="#4bf542">
                                                <a href="mailto:online.approval@aski.component.astra.co.id?subject=Approve: PO"""+ request.POST["PO_Number"]+"""Rev"""+ str(request.POST['Revision_Status'])+"""&body=Approve Purchase Order with ID """+ request.POST["PO_Number"]+""" Rev"""+ str(request.POST['Revision_Status'])+""" %0DApproval Message:" target="_blank" style="padding: 8px 12px; border: 1px solid #4bf542;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #ffffff;text-decoration: none;font-weight:bold;display: inline-block;">
                                                    APPROVE             
                                                </a>
                                            </td>
                                            <td>&nbsp;&nbsp;</td>
                                            <td style="border-radius: 2px;width: 150px;text-align: center;" bgcolor="#ED2939">
                                                <a href="mailto:online.approval@aski.component.astra.co.id?subject=Reject: PO"""+ request.POST["PO_Number"]+"""Rev"""+ str(request.POST['Revision_Status'])+"""&body=Reject  Purchase Order with ID """+ request.POST["PO_Number"]+""" Rev"""+ str(request.POST['Revision_Status'])+"""  %0DReject Message:" target="_blank" style="padding: 8px 12px; border: 1px solid #ED2939;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #ffffff;text-decoration: none;font-weight:bold;display: inline-block;">
                                                    REJECT             
                                                </a>
                                            </td>
                                            <td>&nbsp;&nbsp;</td>
                                            <td style="border-radius: 2px;width: 150px;text-align: center;" bgcolor="#ebde34">
                                                <a href="mailto:online.approval@aski.component.astra.co.id?subject=Revise: PO"""+request.POST["PO_Number"]+"""Rev"""+ str(request.POST['Revision_Status'])+"""&body=Need Revise Purchase Order with ID """+request.POST["PO_Number"]+""" Rev"""+ str(request.POST['Revision_Status'])+""" %0DRevision Message:" target="_blank" style="padding: 8px 12px; border: 1px solid #ebde34;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #000000;text-decoration: none;font-weight:bold;display: inline-block;">
                                                    REVISE             
                                                </a>
                                            </td>
                                            <td>&nbsp;&nbsp;</td>
                                            <td style="border-radius: 2px;width: 150px;text-align: center;" bgcolor="#cccccc">
                                                <a href="mailto:"""+request.POST["PO_Admin_Email"]+"""?subject=Ask User: PO"""+ request.POST["PO_Number"]+"""Rev"""+ str(request.POST['Revision_Status'])+"""&body=Ask User about Purchase Order with ID """+ request.POST["PO_Number"]+""" Rev"""+ str(request.POST['Revision_Status'])+"""  %0DAsk User Message: " target="_blank" style="padding: 8px 12px; border: 1px solid #cccccc;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #000000;text-decoration: none;font-weight:bold;display: inline-block;">
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

            if POData.PO_Admin_Email == POData.PO_SPV_Email :
                models.POData.objects.filter(PO_Number=request.POST['PO_Number']).update(PO_SPV_Approval_Date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), PO_SPV_Approval_Status = 'Approved')
                mailattach = EmailMessage(
                    'Purchase Order Online Approval: ' +
                        request.POST['PO_Number'] + """Rev""" +
                            str(request.POST['Revision_Status']),
                    body=email_body,
                    from_email=settings.EMAIL_HOST_USER,
                    to=[request.POST['PO_Dept_Head_Email']],
                )
            else :
                mailattach = EmailMessage(
                    'Purchase Order Online Approval: ' +
                        request.POST['PO_Number'] + """Rev""" +
                            str(request.POST['Revision_Status']),
                    body=email_body,
                    from_email=settings.EMAIL_HOST_USER,
                    to=[request.POST['PO_SPV_Email']],
                )
            mailattach.content_subtype = "html"

            shutil.copy("Media\\"+str(POData.PO_Before_Approval),
            str("Media\\UnsignedPO\\PO "+str(POData.PO_Number) +"rev"+str(POData.Revision_Status)+".pdf"))

            mailattach.attach_file("Media\\UnsignedPO\\PO "+str(POData.PO_Number) +"rev"+str(POData.Revision_Status)+".pdf")
            mailattach.attach_file("Media\\UnsignedPO\\PO "+str(POData.PO_Number) +"rev"+str(POData.Revision_Status-1)+".pdf")

            

            if len(str(POData.PO_Attachment1))> 5:
                mailattach.attach_file('Media/'+str(POData.PO_Attachment1))
            if len(str(POData.PO_Attachment2))> 5:
                mailattach.attach_file('Media/'+str(POData.PO_Attachment2))
            if len(str(POData.PO_Attachment3))> 5:
                mailattach.attach_file('Media/'+str(POData.PO_Attachment3))
            if len(str(POData.PO_Attachment4))> 5:
                mailattach.attach_file('Media/'+str(POData.PO_Attachment4))
                                                                
            mailattach.send()
            if POData.PO_Admin_Email == POData.PO_SPV_Email :
                 models.Send(htmlmessage=email_body,
                            mailfrom='online.approval@aski.component.astra.co.id',
                            mailto=request.POST['PO_Dept_Head_Email'],
                            PO_Number=request.POST['PO_Number']+"Rev" + str(request.POST['Revision_Status']),
                            mailheader='Purchase Order Online Approval: ' + request.POST['PO_Number']+"""Rev"""+ str(request.POST['Revision_Status'])).save()
 
            else :
                models.Send(htmlmessage=email_body,
                            mailfrom='online.approval@aski.component.astra.co.id',
                            mailto=request.POST['PO_SPV_Email'],
                            PO_Number=request.POST['PO_Number']+"Rev" + str(request.POST['Revision_Status']),
                            mailheader='Purchase Order Online Approval: ' + request.POST['PO_Number']+"""Rev"""+ str(request.POST['Revision_Status'])).save()
            
            models.POData.objects.filter(
            PO_Number=request.POST['PO_Number'], Revision_Status = POData.Revision_Status).update(PO_Status="Created")
            models.POData.objects.filter(
            PO_Number=request.POST['PO_Number'], Revision_Status = POData.Revision_Status-1).update(PO_Status="Revised")
            SQLWrite(f"update dbo.release_PO set Status = 'Revised by {str(request.user)}' , Modified_Date =  GetDate() where PO_Number = '{request.POST['PO_Number']}'  and Revision =  '{POData.Revision_Status-1}' ")


            return redirect('/PO/ListPO/')
        else :
            print(PO.errors)
            context={
                'Error': PO.errors
            }
            return render(request, 'purchaseorder/Error.html',context)

    context={
        'Judul' : 'Revise Purchase Order',
        'POData' : POData,
        'POForm' : PO,
        'Approval' : approval,
        'Data': data,
    }
    return render(request, 'purchaseorder/RevisePO.html',context)


def pdf(request, ID):
    generatePO(ID)
    sendPO(ID)
    return HttpResponse("it works!")

def send(request, ID):
    sendPO(ID)
    return HttpResponse(f"Send PO {ID} to portal completed!")

def sendPO(ID):
    PO_Number = ID.split('rev')[0]
    Revision = ID.split('rev')[1]
    url = "http://10.14.55.183:8080/apigateway/api/v1/1086455/upload"
    header = {
        'username':'ASKI_admin1',
        'role':'admin'
    }
    file = {'file': open(f"Media\\SignedPO\\PO {ID}.pdf", 'rb')}
    body = {
        'filename':'PO '+ID,
        'category[1088553_2]':"",
        'category[1088553_5]':"Active",
        'category[1088553_6]':"PT Astra Komponen Indonesia",
        'category[1088553_7]':"PT Astra Komponen Indonesia",
        'category[1088553_8]':"",
        'category[1088553_9]':"",
        'category[1088553_10]':"",
        'category[1088553_12]':"PO",
        'category[1088553_13]':ID,
        'category[1088553_14]':"2023-01-30"
    }

    r = requests.put(url=url, headers=header,files=file, data=body)
    print(r.text)
    

    if 'error' in r.text :
        models.POData.objects.filter(
            PO_Number=PO_Number, Revision_Status = Revision).update(PO_Status="Finished|PortalError")
    else : 
        print(r.json()['id']) 
        SQLWrite(f"Update dbo.release_PO Set DDMS_id = {r.json()['id']}, version = {r.json()['version']} where PO_Number = {PO_Number} and Revision = {Revision}")
        models.POData.objects.filter(
            PO_Number=PO_Number, Revision_Status = Revision).update(PO_Status="Finished|PortalSuccess")



    


def generatePO(ID):
    PO_Number = ID.split('rev')[0]
    Revision = ID.split('rev')[1]
    POData = models.POData.objects.get(PO_Number = PO_Number, Revision_Status = Revision)
    print('Generate ' + ID)

    
    watermark_html = """
    <head>
    <meta name="pdfkit-page-size" content="A4"/>
    </head>
    <body>
    <br>
    <br>
    <br>
    <br>
    <br>
    <br>
    <br>
    <br>
    <br>
    <br>
    <br>
    <br>
    <br>
    <br>
        <h4>PO """+PO_Number+"""&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</h4>
        <h4>DIGITALLY SIGNED</h4>

        <div style ="font-size:10px;top:auto;bottom: 0px;position: absolute;width: 100%; text-align:center;"><div><i>Purchase Order """+PO_Number+""" Revision """+Revision+""" </i></div><div><i> This Document Automatically Generated by PT Astra Komponen Indonesia Online Approval System</i></div>
    
    <style>
        h4 {
      
            margin-left: auto;
            margin-right:auto;
            width : 100%;
            text-align: center;
            vertical-align: baseline;
            color: #CCF8F5;
            opacity: 1;
            letter-spacing: 2px;
            font-size: 80px;
            pointer-events: none;
            -webkit-transform: rotate(-45deg);
            -moz-transform: rotate(-45deg);
            
        }
        </style>
    </body>
    
    """

    print(POData.PO_PresDirektur)
    if POData.PO_PresDirektur is not None:
        if(POData.PO_PresDirektur_Approval_Status == 'Approved'):
            ttd = POData.PO_PresDirektur.upper()
            ttd_time = str(POData.PO_PresDirektur_Approval_Date.strftime("%d-%m-%Y %H:%M:%S"))
            ttd_time_sql = str(POData.PO_PresDirektur_Approval_Date.strftime("%Y-%m-%d %H:%M:%S"))
           
    else :
        if(POData.PO_Direktur_Approval_Status == 'Approved'):
            ttd = POData.PO_Direktur.upper()
            ttd_time = str(POData.PO_Direktur_Approval_Date.strftime("%d-%m-%Y %H:%M:%S"))
            ttd_time_sql = str(POData.PO_Direktur_Approval_Date.strftime("%Y-%m-%d %H:%M:%S"))
            
    config = pdfkit.configuration(
            wkhtmltopdf='C:\Program Files\wkhtmltopdf\\bin\wkhtmltopdf.exe')
    pdfkit.from_string(watermark_html, "Media\\SignedPO\\watermark.pdf", configuration=config)

    # watermarktemp = """
    #         <head>
    #         <meta name="pdfkit-page-size" content="A4"/>
    #         </head>
    #         <body>
    #         <div style="top:0px;bottom:auto;position: absolute;">*</div>
    #         <div style="top:auto;bottom:800px;position: absolute;">**</div>
    #         <div style="top:auto;bottom:0px;position: absolute;">*</div>

    #         </body>

    #         """

    # pdfkit.from_string(watermarktemp, "Media\\SignedPO\\watermarktemp.pdf", configuration=config)
   
    

    output = PdfFileWriter()
    input1 = PdfFileReader(open("Media\\"+str(POData.PO_Before_Approval), "rb"))
    pages = input1.numPages

    # watermark_temp = PdfFileReader(open(r"Media\\SignedPO\\watermarktemp.pdf", "rb"))
    # watermark_temppage = watermark_temp.getPage(0)
    # watermark_temppage.mergePage(input1.getPage(pages-1))
    # output.addPage(watermark_temppage)
    # outputTemp = open("Media\SignedPO\POTemp.pdf", "wb")
    # output.write(outputTemp)
    # outputTemp.close()

    fp = open("Media\\"+str(POData.PO_Before_Approval), "rb")
    rsrcmgr = PDFResourceManager()
    laparams = LAParams()
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    pages1 = PDFPage.get_pages(fp)
    print(ttd)
    ttd_pos = 0
    for page in pages1:
        print('Processing next page...')
        interpreter.process_page(page)
        layout = device.get_result()
        for lobj in layout:
            if isinstance(lobj, LTTextBox):
                x, y, text = lobj.bbox[0], lobj.bbox[3], lobj.get_text()
                #print('At %r is text: %s' % ((x, y), text))
                if ttd in text :
                    print('At %r is text: %s' % ((x, y), text))
                    ttd_pos =  y


    print(ttd_pos)

    fp.close()


    if (ttd_pos> 0):
            watermarkfull_html = """
            <head>
            <meta name="pdfkit-page-size" content="A4"/>
            </head>
            <body>
                <div id = "approval">
                <div style ="font-size:14px;color:#111111;font-style: bold;"><div>Purchase Order """+PO_Number+""" Digitally Signed  </div><div>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"""+ttd_time+"""</div></div>
                </div>
                            <style>
                            #approval {
                                position: absolute;
                                top:auto;
                                bottom: """+str(((int(ttd_pos)-43)*10/6)+50)+"""px;
                                
                            }
                            .table-approve {

                                border: 1px solid #5DA1B7;
                                border-collapse: collapse;
                                font-size: 12px;
                                table-layout: fixed;
                            }
                            .table-approve tr th,
                            .table-approve tr td {
                                border: 1px  solid #5DA1B7;
                                font-size: 12px;
                                padding: 2px;
                                min-width : 130px;
                                color: #5DA1B7;
                            }
                            </style>
            </body>
            
            """
            pdfkit.from_string(watermarkfull_html, "Media\\SignedPO\\watermarkfull.pdf", configuration=config)

    

    for i in range (pages):
        input_page = input1.getPage(i)
        if pages == i+1 :
            watermark = PdfFileReader(open(r"Media\\SignedPO\\watermark.pdf", "rb"))
            watermark_page = watermark.getPage(0)
            watermark_page.mergePage(input_page)
            ap = open(r"Media\\SignedPO\\watermarkfull.pdf", "rb")
            app = PdfFileReader(ap)
            app_page = app.getPage(0)
            watermark_page.mergePage(app_page)
            
        else :
            watermark = PdfFileReader(open(r"Media\\SignedPO\\watermark.pdf", "rb"))
            watermark_page = watermark.getPage(0)
            watermark_page.mergePage(input_page)
        output.addPage(watermark_page)
    outputStream = open("Media\SignedPO\PO "+ID+".pdf", "wb")
    output.addMetadata(
            {
                "/Title" : "PO" + ID,
                "/Author": "DIGITAL ASKI",
                "/Producer": "PT Astra Komponen Indonesia Online Approval System",
                "/Application": "Digital Online Approval System",
            }
        )
    output.write(outputStream)
    ap.close()
    outputStream.close()
    if os.path.exists("Media\\SignedPO\\watermarkfull.pdf"): os.remove("Media\\SignedPO\\watermarkfull.pdf")
    
    
    models.POData.objects.filter(
            PO_Number=PO_Number, Revision_Status = Revision).update(PO_Status="Finished")


    SQLWrite(f"Insert into dbo.release_PO (PO_Number,PO_Date,Revision,Vendor_Number,Vendor_Name,PDF_File,Approval_Date,Status,Release_Date) values ('{PO_Number}','{POData.PO_Date}','{Revision}','{POData.Vendor_Number}','{POData.Vendor_Name}','PO {PO_Number}rev{Revision}.pdf','{ttd_time_sql}','Released',GetDate())")



    # for i in range(10):
    #     print(i)
    #     watermarkfull_html = """
    #         <head>
    #         <meta name="pdfkit-page-size" content="A4"/>
    #         </head>
    #         <body>
    #             <div id = "approval">

    #             <div style ="font-size:14px;color:#111111;font-style: bold;  ">TEST POSISI</div>
    #             </div>
    #                         <style>
    #                         #approval {
    #                             position: absolute;
    #                             top: """+str(i*200)+"""px;
    #                             bottom:auto;
    #                         }
    #                         .table-approve {

    #                             border: 1px solid #5DA1B7;
    #                             border-collapse: collapse;
    #                             font-size: 12px;
    #                             table-layout: fixed;
    #                         }
    #                         .table-approve tr th,
    #                         .table-approve tr td {
    #                             border: 1px  solid #5DA1B7;
    #                             font-size: 12px;
    #                             padding: 2px;
    #                             min-width : 130px;
    #                             color: #5DA1B7;
    #                         }
    #                         </style>
    #         </body>
            
    #         """
    #     pdfkit.from_string(watermarkfull_html, "Media\\SignedPO\\watermarkfull"+str(i)+".pdf", configuration=config)
    #     fp = open("Media\\SignedPO\\watermarkfull"+str(i)+".pdf", "rb")
    #     rsrcmgr = PDFResourceManager()
    #     laparams = LAParams()
    #     device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    #     interpreter = PDFPageInterpreter(rsrcmgr, device)
    #     pages1 = PDFPage.get_pages(fp)
    #     #print(ttd)
    #     ttd_pos = 0
    #     for page in pages1:
    #         print('Processing next page...')
    #         interpreter.process_page(page)
    #         layout = device.get_result()
    #         for lobj in layout:
    #             if isinstance(lobj, LTTextBox):
    #                 x, y, text = lobj.bbox[0], lobj.bbox[3], lobj.get_text()
    #                 if "TEST POSISI" in text :
    #                     print('At %r is text: %s' % ((x, y), text))
    #                     ttd_pos =  y


    #     print(ttd_pos)

