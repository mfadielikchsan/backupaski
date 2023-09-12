from django.shortcuts import render
from django.shortcuts import redirect
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from . import models
from . import forms
import datetime
from django.http import HttpResponse
from django.core import serializers
import pdfkit
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test

# Create your views here.
def is_memberaddasset(user):
    return user.groups.filter(name='Allow_Add_Asset').exists()

def is_membercreatebe(user):
    return user.groups.filter(name='Allow_Create_Entertaint').exists()

def is_memberentertaint(user):
    return user.groups.filter(Q(name='Allow_Add_Asset') | Q(name='Allow_Create_Entertaint')).exists()

def is_admin(user):
    return user.groups.filter(name='Admin').exists()


# Create your views here.
@login_required
@user_passes_test(is_membercreatebe)
def createBE(request):
    BE = forms.Entertainment()
    BE.fields['BE_Number'].initial = 'ASKIENTERTAINMENT' + request.user.username + str(models.Entertainment.objects.filter(
    BE_Number__contains="ENTERTAINMENT"+ request.user.username, Status__isnull=False).exclude(BE_Number__contains='rev').count()+1).zfill(5)
    BE.fields['Tahun_Pajak'].initial = datetime.datetime.today().year
    BE.fields['SPV_Submit'].initial = datetime.datetime.now()
    data = serializers.serialize("json", models.Approval.objects.filter(User=request.user))
    if request.method == 'POST':
        models.activity_log(user = request.user.username,BE_Number=request.POST["BE_Number"],activity=request.POST).save()
        print(request.POST)
        if 'Finish' in request.POST:
            if models.Entertainment.objects.filter(BE_Number= request.POST['BE_Number']).exists():
                BE = forms.Entertainment(request.POST, request.FILES,instance=models.Entertainment.objects.get(BE_Number=request.POST['BE_Number']))
            else:
                BE = forms.Entertainment(request.POST, request.FILES)
            if BE.is_valid():
                BE.save()
            else:
                print(BE.errors)
            print(BE.errors)
            BE = models.Entertainment.objects.get(BE_Number=request.POST['BE_Number'])
            approval = models.Approval.objects.get(User = request.user.username)
            ListItem = list(models.Entertainment.objects.filter(BE_Number=request.POST['BE_Number']))
            counter = 0
            contain = ''
            for item in ListItem:
                counter += 1
                contain += ''' <tr style="height: 30px; font-size:12px; border-collapse: collapse;">
                    <td rowspan="2" style="border: 1px solid black; border-collapse: collapse;padding: 5px; vertical-align: top;">1</td>
                    <td rowspan="2" style="border: 1px solid black; border-collapse: collapse; padding: 5px; vertical-align: top;">'''+str(item.Date)+'''</td>
                    <td rowspan="2" style="border: 1px solid black; border-collapse: collapse; padding: 5px; vertical-align: top; text-align: left;white-space: pre-wrap;"><div>'''+item.Place.replace("\r\n", "</div><div>")+'''</div></td>
                    <td rowspan="2" style="border: 1px solid black; border-collapse: collapse; padding: 5px; vertical-align: top; text-align: left;white-space: pre-wrap;"><div>'''+item.Address.replace("\r\n", "</div><div>")+'''</div></td>
                    <td rowspan="2" style="border: 1px solid black; border-collapse: collapse; padding: 5px; vertical-align: top;">'''+str(item.Type)+'''</td>
                    <td rowspan="2" style="border: 1px solid black; border-collapse: collapse; padding: 5px; vertical-align: top;">Rp. '''+str(item.Jumlah)+'''</td>
                    <td style="padding: 5px; text-align: left; border-top: 1px solid black; border-right: 1px solid black; border-collapse: collapse; vertical-align: top; white-space: pre-wrap;"><diV><b>External</b></diV><div>'''+item.Name_External.replace("\r\n", "</div><div>")+'''</div></td>
                    <td style="padding: 5px; text-align: left; border-top: 1px solid black; border-right: 1px solid black; border-collapse: collapse; vertical-align: top; white-space: pre-wrap;"><diV><b>External</b></diV><div>'''+item.Posisi_External.replace("\r\n", "</div><div>")+'''</div>
                    </td>
                    <td style="padding: 5px; text-align: left; border-top: 1px solid black; border-right: 1px solid black; border-collapse: collapse; vertical-align: top; white-space: pre-wrap;"><diV><b>External</b></diV><div>'''+item.Company_Name_External.replace("\r\n", "</div><div>")+'''</div>
                    </td>
                    <td rowspan="2" style="border: 1px solid black; border-collapse: collapse; padding: 5px; vertical-align: top;">'''+str(item.Company_Type)+'''</td>
                    <td rowspan="2" style="border: 1px solid black; border-collapse: collapse; padding: 5px; vertical-align: top;">'''+str(item.SAP_Number)+'''</td>
                </tr>
                <tr style="height: 30px; font-size:12px; border-collapse: collapse;">
                    <td style="padding: 5px; text-align: left; border-bottom: 1px solid black; border-right: 1px solid black;  border-collapse: collapse; vertical-align: top; white-space: pre-wrap;"><diV><b>Internal</b></diV><div>'''+item.Name_Internal.replace("\r\n", "</div><div>")+'''</div></td>
                    <td style="padding: 5px; text-align: left; border-bottom: 1px solid black; border-right: 1px solid black;  border-collapse: collapse; vertical-align: top; white-space: pre-wrap;"><diV><b>Internal</b></diV><div>'''+item.Posisi_Internal.replace("\r\n", "</div><div>")+'''</div>
                    </td>
                    <td style="padding: 5px; text-align: left; border-bottom: 1px solid black; border-right: 1px solid black;  border-collapse: collapse; vertical-align: top; white-space: pre-wrap;"><diV><b>Internal</b></diV><div>'''+item.Company_Name_Internal.replace("\r\n", "</div><div>")+'''</div>
                    </td>
                </tr>'''
            apptable = """
            <table style="font-size: 12px;text-align: center;border: 1px solid black;border-collapse: collapse;" >
                <tbody >
                    <tr style="height:10px;border: 1px solid black;border-collapse: collapse;">
                        <th style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Prepared By</th>
                        <th colspan="2" style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Approved By</th>
                    </tr>
                    <tr style="height:40px;border: 1px solid black;border-collapse: collapse;">
                        <td style="border: 1px solid black;border-collapse: collapse;padding:20px;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="SPV">Created """ + str(BE.SPV_Submit.strftime("%Y-%m-%d %H:%M:%S")) + """</td>
                        <td style="border: 1px solid black;border-collapse: collapse;padding:20px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="DEPT"></td>
                        <td style="border: 1px solid black;border-collapse: collapse;padding:20px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="PRDIR"></td>
                    </tr>
                    <tr style="height:20px;border: 1px solid black;border-collapse: collapse;">
                        <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">""" + approval.SPV.title() + """</td>
                        <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">""" + approval.Dept_Head.title() + """</td>
                        <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">""" + approval.PresDirektur.title() + """</td>
                    </tr>
                    <tr style="height:10px;border: 1px solid black;border-collapse: collapse;">
                        <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Supervisor</td>
                        <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Department Head</td>
                        <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">President Director</td>
                    </tr>
                </tbody>
            </table>
            """
            Superior = approval.Dept_Head.title()
            email_body = """
            <html>
                <head style="margin-bottom: 0px;">Dear Mr/Ms """ + Superior + """,</head>
                <body>
                <p style="margin-bottom: 0px;margin-top: 0px;">This Nominative List of Entertainment Cost Request needs your approval </>
                <hr>
                <table style="font-size: x-small; width: 100%">
                    <tr >
                        <td rowspan="3" style="width: 15%;  text-align: center; border-bottom: 1px solid black;"><h1>ASKI</h1></td>
                        <td rowspan="3" style="text-align: center;  border-bottom: 1px solid black;">
                            <div><h3>DAFTAR NOMINATIF BIAYA ENTERTAINMENT DAN SEJENISNYA</h3><div>
                            <div><h3>Tahun Pajak :  """ + str(BE.Tahun_Pajak) + """</h3></div>
                        </td>
                    </tr>
                </table>
                <br>
                <table style="width: 100%; font-size: x-small;">
                    <tr>
                    <td style="width: 10%;">Doc Number</td>
                    <td>:</td>
                    <td>""" + str(BE.BE_Number) + """</td>
                    </tr>
                </table>
                <br>
                <table style="width: 100%; border-collapse: collapse; font-size: 12px;text-align: center">
                    <thead>
                        <tr style=" height: 50px; word-break: normal; border: 1px solid">
                            <th rowspan="2" style="vertical-align: middle; border: 1px solid; padding: 5px; ">No</th>
                            <th colspan="4" style="vertical-align: middle; border: 1px solid; padding: 5px; ">Pemberian Entertainment dan Sejenisnya</th>
                            <th colspan="5" style="vertical-align: middle; border: 1px solid; padding: 5px; ">Relasi Usaha yang diberikan Entertainment dan Sejenisnya</th>
                            <th rowspan="2" style="vertical-align: middle; border: 1px solid; padding: 5px; ">No. Document SAP <br>(diisi oleh Fin. Dept)</th>
                        </tr>
                        <tr style="border: 1px solid">
                            <th style="padding: 5px; border: 1px solid;padding: 5px;">Tanggal</th>
                            <th style="padding: 5px; border: 1px solid;padding: 5px;">Tempat</th>
                            <th style="padding: 5px; border: 1px solid;padding: 5px;">Alamat</th>
                            <th style="padding: 5px; border: 1px solid;padding: 5px;">Jenis</th>
                            <th style="padding: 5px; border: 1px solid;padding: 5px;">Jumlah (Rp)</th>
                            <th style="padding: 5px; border: 1px solid;padding: 5px;">Nama</th>
                            <th style="padding: 5px; border: 1px solid;padding: 5px;">Posisi</th>
                            <th style="padding: 5px; border: 1px solid;padding: 5px;">Nama Perusahaan</th>
                            <th style="padding: 5px; border: 1px solid;padding: 5px;">Jenis Usaha</th>
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
                <hr>
                <p> Please give your response by click approval button bellow and then click send button. A response at your earliest convenience would be much appreciated. </p>
                <table width="100%" cellspacing="0" cellpadding="0">
                    <tr>
                        <td>
                            <table cellspacing="0" cellpadding="0">
                                <tr>
                                    <td style="border-radius: 2px;width : 150px;text-align: center;" bgcolor="#4bf542">
                                        <a href="mailto:online.approval@aski.component.astra.co.id?subject=Approve: """ + str(BE.BE_Number) + """&body=Approve Entertainment Request with ID """ + str(BE.BE_Number) + """ %0DApproval Message:" target="_blank" style="padding: 8px 12px; border: 1px solid #4bf542;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #ffffff;text-decoration: none;font-weight:bold;display: inline-block;">
                                            APPROVE
                                        </a>
                                    </td>
                                    <td>&nbsp;&nbsp;</td>
                                    <td style="border-radius: 2px;width: 150px;text-align: center;" bgcolor="#ED2939">
                                        <a href="mailto:online.approval@aski.component.astra.co.id?subject=Reject: """ + str(BE.BE_Number) + """&body=Reject Entertainment Request with ID """ + str(BE.BE_Number) + """ %0DReject Message:" target="_blank" style="padding: 8px 12px; border: 1px solid #ED2939;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #ffffff;text-decoration: none;font-weight:bold;display: inline-block;">
                                            REJECT
                                        </a>
                                    </td>
                                    <td>&nbsp;&nbsp;</td>
                                    <td style="border-radius: 2px;width: 150px;text-align: center;" bgcolor="#ebde34">
                                        <a href="mailto:online.approval@aski.component.astra.co.id?subject=Revise: """ + str(BE.BE_Number) + """&body=Need Revise Entertainment Request with ID """ + str(BE.BE_Number) + """ %0DRevision Message:" target="_blank" style="padding: 8px 12px; border: 1px solid #ebde34;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #000000;text-decoration: none;font-weight:bold;display: inline-block;">
                                            REVISE
                                        </a>
                                    </td>
                                    <td>&nbsp;&nbsp;</td>
                                    <td style="border-radius: 2px;width: 150px;text-align: center;" bgcolor="#cccccc">
                                        <a href="mailto:""" + str(BE.SPV_Email) + """?subject=Ask User: """ + str(BE.BE_Number) + """&body=Ask User about Entertainment Request with ID """ + str(BE.BE_Number) + """ %0DAsk User Message: " target="_blank" style="padding: 8px 12px; border: 1px solid #cccccc;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #000000;text-decoration: none;font-weight:bold;display: inline-block;">
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
                'Entertainment Online Approval: ' +
                request.POST['BE_Number'],
                body=email_body, from_email=settings.EMAIL_HOST_USER,
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
            if 'Attachment4' in request.FILES:
                mailattach.attach_file(
                    'Media/Uploads/'+str(request.FILES['Attachment4']).replace(' ', '_'))
            if 'Attachment5' in request.FILES:
                mailattach.attach_file(
                    'Media/Uploads/'+str(request.FILES['Attachment5']).replace(' ', '_'))
            if 'Attachment6' in request.FILES:
                mailattach.attach_file(
                    'Media/Uploads/'+str(request.FILES['Attachment6']).replace(' ', '_'))
            mailattach.send()

            email = models.Send(
                htmlmessage=email_body,
                mailfrom='online.approval@aski.component.astra.co.id',
                mailto=request.POST['Dept_Head_Email'],
                BE_Number=request.POST['BE_Number'],
                mailheader='Biaya Entertainment Online Approval: ' + request.POST['BE_Number'])
            email.save()
            models.Entertainment.objects.filter(BE_Number=request.POST['BE_Number']).update(Status="Created")
            return redirect("/BE/ListBE/")
                
    context = {
        'Judul': 'Daftar Nominatif Biaya Entertainment dan Sejenisnya',
        'BE': BE,
        'Data': data,
    }
    return render(request, 'entertainment/createBE.html', context)

@login_required
@user_passes_test(is_memberentertaint)
def listBE(request):
    if (request.user.username == "admin"):
        ListBE = models.Entertainment.objects.order_by("-id")
    elif (request.user.username == "FINANCE" or request.user.username == "ADMINFINANCE" ):
        ListBE = models.Entertainment.objects.order_by("-id")
    else:
        ListBE = models.Entertainment.objects.filter(BE_Number__contains=request.user.username).filter(Status__isnull=False).order_by("-id")
    context = {
        'Judul': 'Monitoring Biaya Entertainment',
        'listBE': ListBE,
    }
    return render(request, 'entertainment/list.html', context)

@login_required
@user_passes_test(is_memberentertaint)
def view(request,ID):
    BE_Number = ID
    BE = models.Entertainment.objects.get(BE_Number= ID)
    ListItem = list(models.Entertainment.objects.filter(BE_Number=BE_Number))
    if request.method == "POST":
        models.activity_log(user = request.user.username,BE_Number=BE_Number,activity=request.POST).save()
    #     BEform = forms.Entertainment(
    #         request.POST, request.FILES, instance=BE)
    #     if BEform.is_valid():
    #         BEform.save()
    #     else:
    #         print(BEform.errors)
    # else:
    #     BEform = forms.Entertainment(instance=BE)
    context = {
        'Judul' : "Detail Biaya Entertainment dan Sejenisnya",
        'ListItem': ListItem,
        'BE': BE,
    }
    return render (request, 'entertainment/detail.html', context)

@login_required
@user_passes_test(is_membercreatebe)
def revise(request, ID):
    BE_Number = ID
    if 'rev' not in BE_Number:
        New_BE_Number = BE_Number + "rev1"
    else:
        New_BE_Number = BE_Number.split('rev', 1)[0] + "rev" + str(int(BE_Number.split('rev', 1)[1])+1)

    if request.method == "GET" :
        if not models.Entertainment.objects.filter(BE_Number = New_BE_Number).exists():
            newBE = models.Entertainment.objects.get(BE_Number = BE_Number)
            newBE.BE_Number = New_BE_Number
            newBE.pk = None
            newBE.Dept_Head_Approval_Date = None
            newBE.Dept_Head_Approval_Status = None
            newBE.PresDirektur_Approval_Date = None
            newBE.PresDirektur_Approval_Status = None
            newBE.Finance_Status = None
            newBE.Status = None
            newBE.Message = None
            newBE.save()
    newBE = models.Entertainment.objects.get(BE_Number = New_BE_Number)
    print(newBE)
    if request.method == "POST":
        print(request.POST)
        models.activity_log(user=request.user)
        if 'upload' in request.POST:
            print("attachment")
            BEsave = forms.Entertainment(request.POST, request.FILES, instance=newBE)
            if BEsave.is_valid():
                BEsave.save()
            else:
                print(BEsave.errors)
        elif 'Finish' in request.POST:
            print("Finish")
            BEsave = forms.Entertainment(request.POST, request.FILES, instance=newBE)
            if BEsave.is_valid():
                BEsave.SPV_Submit = datetime.datetime.now()
                newBE.SPV_Submit = datetime.datetime.now()
                BEsave.save()
            else:
                print(BEsave.errors)
            # models.Entertainment.objects.filter(BE_Number=New_BE_Number).update(Date=request.POST['Date'], Place=request.POST['Place'],
            #     Address=request.POST['Address'], Type=request.POST['Type'], Jumlah=request.POST['Jumlah'], Name_Internal=request.POST['Name_Internal'],
            #     Posisi_Internal=request.POST['Posisi_Internal'], Company_Name_Internal=request.POST['Company_Name_Internal'], Name_External=request.POST['Name_External'], 
            #     Posisi_External=request.POST['Posisi_External'], Company_Name_External=request.POST['Company_Name_External'], Company_Type=request.POST['Company_Type'], 
            #     SAP_Number=request.POST['SAP_Number'], SPV_Submit=datetime.datetime.now())
            BE = models.Entertainment.objects.get(BE_Number=request.POST['BE_Number'])
            approval = models.Approval.objects.get(User = request.user.username)
            ListItem = list(models.Entertainment.objects.filter(BE_Number=request.POST['BE_Number']))
            counter = 0
            contain = ''
            for item in ListItem:
                counter += 1
                contain += ''' <tr style="height: 30px; font-size:12px; border-collapse: collapse;">
                    <td rowspan="2" style="border: 1px solid black; border-collapse: collapse;padding: 5px; vertical-align: top;">1</td>
                    <td rowspan="2" style="border: 1px solid black; border-collapse: collapse; padding: 5px; vertical-align: top;">'''+str(item.Date)+'''</td>
                    <td rowspan="2" style="border: 1px solid black; border-collapse: collapse; padding: 5px; vertical-align: top; text-align: left; white-space: pre-wrap;"><div>'''+item.Place.replace("\r\n", "</div><div>")+'''</div></td>
                    <td rowspan="2" style="border: 1px solid black; border-collapse: collapse; padding: 5px; vertical-align: top; text-align: left; white-space: pre-wrap;"><div>'''+item.Address.replace("\r\n", "</div><div>")+'''</div></td>
                    <td rowspan="2" style="border: 1px solid black; border-collapse: collapse; padding: 5px; vertical-align: top;">'''+str(item.Type)+'''</td>
                    <td rowspan="2" style="border: 1px solid black; border-collapse: collapse; padding: 5px; vertical-align: top;">Rp. '''+str(item.Jumlah)+'''</td>
                    <td style="padding: 5px; text-align: left; border-top: 1px solid black; border-right: 1px solid black; border-collapse: collapse; vertical-align: top; white-space: pre-wrap"><diV><b>External</b></diV><div>'''+item.Name_External.replace("\r\n", "</div><div>")+'''</div></td>
                    <td style="padding: 5px; text-align: left; border-top: 1px solid black; border-right: 1px solid black; border-collapse: collapse; vertical-align: top; white-space: pre-wrap"><diV><b>External</b></diV><div>'''+item.Posisi_External.replace("\r\n", "</div><div>")+'''</div>
                    </td>
                    <td style="padding: 5px; text-align: left; border-top: 1px solid black; border-right: 1px solid black; border-collapse: collapse; vertical-align: top; white-space: pre-wrap"><diV><b>External</b></diV><div>'''+item.Company_Name_External.replace("\r\n", "</div><div>")+'''</div>
                    </td>
                    <td rowspan="2" style="border: 1px solid black; border-collapse: collapse; padding: 5px; vertical-align: top;">'''+str(item.Company_Type)+'''</td>
                    <td rowspan="2" style="border: 1px solid black; border-collapse: collapse; padding: 5px; vertical-align: top;">'''+str(item.SAP_Number)+'''</td>
                </tr>
                <tr style="height: 30px; font-size:12px; border-collapse: collapse;">
                    <td style="padding: 5px; text-align: left; border-bottom: 1px solid black; border-right: 1px solid black;  border-collapse: collapse; vertical-align: top; white-space: pre-wrap"><diV><b>Internal</b></diV><div>'''+item.Name_Internal.replace("\r\n", "</div><div>")+'''</div></td>
                    <td style="padding: 5px; text-align: left; border-bottom: 1px solid black; border-right: 1px solid black;  border-collapse: collapse; vertical-align: top; white-space: pre-wrap"><diV><b>Internal</b></diV><div>'''+item.Posisi_Internal.replace("\r\n", "</div><div>")+'''</div>
                    </td>
                    <td style="padding: 5px; text-align: left; border-bottom: 1px solid black; border-right: 1px solid black;  border-collapse: collapse; vertical-align: top; white-space: pre-wrap"><diV><b>Internal</b></diV><div>'''+item.Company_Name_Internal.replace("\r\n", "</div><div>")+'''</div>
                    </td>
                </tr>'''
            apptable = """
            <table style="font-size: 12px;text-align: center;border: 1px solid black;border-collapse: collapse;" >
                <tbody >
                    <tr style="height:10px;border: 1px solid black;border-collapse: collapse;">
                        <th style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Prepared By</th>
                        <th colspan="2" style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Approved By</th>
                    </tr>
                    <tr style="height:40px;border: 1px solid black;border-collapse: collapse;">
                        <td style="border: 1px solid black;border-collapse: collapse;padding:20px;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="SPV">Created """ + str(BE.SPV_Submit.strftime("%Y-%m-%d %H:%M:%S")) + """</td>
                        <td style="border: 1px solid black;border-collapse: collapse;padding:20px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="DEPT"></td>
                        <td style="border: 1px solid black;border-collapse: collapse;padding:20px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="PRDIR"></td>
                    </tr>
                    <tr style="height:20px;border: 1px solid black;border-collapse: collapse;">
                        <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">""" + approval.SPV.title() + """</td>
                        <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">""" + approval.Dept_Head.title() + """</td>
                        <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">""" + approval.PresDirektur.title() + """</td>
                    </tr>
                    <tr style="height:10px;border: 1px solid black;border-collapse: collapse;">
                        <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Supervisor</td>
                        <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Department Head</td>
                        <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">President Director</td>
                    </tr>
                </tbody>
            </table>
            """
            Superior = approval.Dept_Head.title()
            email_body = """
            <html>
                <head style="margin-bottom: 0px;">Dear Mr/Ms """ + Superior + """,</head>
                <body>
                <p style="margin-bottom: 0px;margin-top: 0px;">This Nominative List of Entertainment Cost Request needs your approval </>
                <hr>
                <table style="font-size: x-small; width: 100%">
                    <tr >
                        <td rowspan="3" style="width: 15%;  text-align: center; border-bottom: 1px solid black;"><h1>ASKI</h1></td>
                        <td rowspan="3" style="text-align: center;  border-bottom: 1px solid black;">
                            <div><h3>DAFTAR NOMINATIF BIAYA ENTERTAINMENT DAN SEJENISNYA</h3><div>
                            <div><h3>Tahun Pajak :  """ + str(BE.Tahun_Pajak) + """</h3></div>
                        </td>
                    </tr>
                </table>
                <br>
                <table style="width: 100%; font-size: x-small;">
                    <tr>
                    <td style="width: 10%;">Doc Number</td>
                    <td>:</td>
                    <td>""" + str(BE.BE_Number) + """</td>
                    </tr>
                </table>
                <br>
                <table style="width: 100%; border-collapse: collapse; font-size: 12px;text-align: center">
                    <thead>
                        <tr style=" height: 50px; word-break: normal; border: 1px solid">
                            <th rowspan="2" style="vertical-align: middle; border: 1px solid; padding: 5px; ">No</th>
                            <th colspan="4" style="vertical-align: middle; border: 1px solid; padding: 5px; ">Pemberian Entertainment dan Sejenisnya</th>
                            <th colspan="5" style="vertical-align: middle; border: 1px solid; padding: 5px; ">Relasi Usaha yang diberikan Entertainment dan Sejenisnya</th>
                            <th rowspan="2" style="vertical-align: middle; border: 1px solid; padding: 5px; ">No. Document SAP <br>(diisi oleh Fin. Dept)</th>
                        </tr>
                        <tr style="border: 1px solid">
                            <th style="padding: 5px; border: 1px solid;padding: 5px;">Tanggal</th>
                            <th style="padding: 5px; border: 1px solid;padding: 5px;">Tempat</th>
                            <th style="padding: 5px; border: 1px solid;padding: 5px;">Alamat</th>
                            <th style="padding: 5px; border: 1px solid;padding: 5px;">Jenis</th>
                            <th style="padding: 5px; border: 1px solid;padding: 5px;">Jumlah (Rp)</th>
                            <th style="padding: 5px; border: 1px solid;padding: 5px;">Nama</th>
                            <th style="padding: 5px; border: 1px solid;padding: 5px;">Posisi</th>
                            <th style="padding: 5px; border: 1px solid;padding: 5px;">Nama Perusahaan</th>
                            <th style="padding: 5px; border: 1px solid;padding: 5px;">Jenis Usaha</th>
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
                <hr>
                <p> Please give your response by click approval button bellow and then click send button. A response at your earliest convenience would be much appreciated. </p>
                <table width="100%" cellspacing="0" cellpadding="0">
                    <tr>
                        <td>
                            <table cellspacing="0" cellpadding="0">
                                <tr>
                                    <td style="border-radius: 2px;width : 150px;text-align: center;" bgcolor="#4bf542">
                                        <a href="mailto:online.approval@aski.component.astra.co.id?subject=Approve: """ + str(BE.BE_Number) + """&body=Approve Entertainment Request with ID """ + str(BE.BE_Number) + """ %0DApproval Message:" target="_blank" style="padding: 8px 12px; border: 1px solid #4bf542;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #ffffff;text-decoration: none;font-weight:bold;display: inline-block;">
                                            APPROVE
                                        </a>
                                    </td>
                                    <td>&nbsp;&nbsp;</td>
                                    <td style="border-radius: 2px;width: 150px;text-align: center;" bgcolor="#ED2939">
                                        <a href="mailto:online.approval@aski.component.astra.co.id?subject=Reject: """ + str(BE.BE_Number) + """&body=Reject Entertainment Request with ID """ + str(BE.BE_Number) + """ %0DReject Message:" target="_blank" style="padding: 8px 12px; border: 1px solid #ED2939;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #ffffff;text-decoration: none;font-weight:bold;display: inline-block;">
                                            REJECT
                                        </a>
                                    </td>
                                    <td>&nbsp;&nbsp;</td>
                                    <td style="border-radius: 2px;width: 150px;text-align: center;" bgcolor="#ebde34">
                                        <a href="mailto:online.approval@aski.component.astra.co.id?subject=Revise: """ + str(BE.BE_Number) + """&body=Need Revise Entertainment Request with ID """ + str(BE.BE_Number) + """ %0DRevision Message:" target="_blank" style="padding: 8px 12px; border: 1px solid #ebde34;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #000000;text-decoration: none;font-weight:bold;display: inline-block;">
                                            REVISE
                                        </a>
                                    </td>
                                    <td>&nbsp;&nbsp;</td>
                                    <td style="border-radius: 2px;width: 150px;text-align: center;" bgcolor="#cccccc">
                                        <a href="mailto:""" + str(BE.SPV_Email) + """?subject=Ask User: """ + str(BE.BE_Number) + """&body=Ask User about Entertainment Request with ID """ + str(BE.BE_Number) + """ %0DAsk User Message: " target="_blank" style="padding: 8px 12px; border: 1px solid #cccccc;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #000000;text-decoration: none;font-weight:bold;display: inline-block;">
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
                'Entertainment Online Approval: ' +
                request.POST['BE_Number'],
                body=email_body, from_email=settings.EMAIL_HOST_USER,
                to=[BE.Dept_Head_Email],
            )
            mailattach.content_subtype = "html"
            if len (str(newBE.Attachment1)) > 5:
                mailattach.attach_file(
                    'Media/'+str(newBE.Attachment1))
            if len (str(newBE.Attachment2)) > 5:
                mailattach.attach_file(
                    'Media/'+str(newBE.Attachment2))
            if len (str(newBE.Attachment3)) > 5:
                mailattach.attach_file(
                    'Media/'+str(newBE.Attachment3))
            if len (str(newBE.Attachment4)) > 5:
                mailattach.attach_file(
                    'Media/'+str(newBE.Attachment4))
            if len (str(newBE.Attachment5)) > 5:
                mailattach.attach_file(
                    'Media/'+str(newBE.Attachment5))
            if len (str(newBE.Attachment6)) > 5:
                mailattach.attach_file(
                    'Media/'+str(newBE.Attachment6))
            mailattach.send()

            email = models.Send(
                htmlmessage=email_body,
                mailfrom='online.approval@aski.component.astra.co.id',
                mailto=BE.Dept_Head_Email,
                BE_Number=request.POST['BE_Number'],
                mailheader='Biaya Entertainment Online Approval: ' + request.POST['BE_Number'])
            email.save()
            models.Entertainment.objects.filter(BE_Number=request.POST['BE_Number']).update(Status="Created")

            models.Entertainment.objects.filter(BE_Number=BE_Number).update(Status="Revised")
            return redirect("/BE/ListBE/")
    context = {
        'Judul' : 'Revise Entertainment Request ' +BE_Number+'',
        'New_BE_Number' : New_BE_Number,
        'BE': newBE,
        'BEForm': forms.Entertainment(instance=newBE),
    }
    return render(request, 'entertainment/revise.html', context)

@login_required
@user_passes_test(is_memberaddasset)
def listCheck(request):
    List = models.Entertainment.objects.filter(Status='FinanceCheck').order_by('-id')
    ListDone = models.Entertainment.objects.filter(Finance_Status='Done Checking').order_by('-id')
    context = {
        'Judul': 'List Checking Entertainment Request',
        'list': List,
        'listDone': ListDone,
    }
    return render(request, 'entertainment/listCheck.html', context)

@login_required
@user_passes_test(is_memberaddasset)
def viewCheck(request, ID):
    BE_Number = ID
    BE = models.Entertainment.objects.get(BE_Number= ID)
    ListItem = list(models.Entertainment.objects.filter(BE_Number=BE_Number))

    if request.method == "POST":
        models.activity_log(user = request.user.username, BE_Number=BE_Number, activity=request.POST).save()
        if 'revision' in request.POST:
            models.Entertainment.objects.filter(BE_Number = BE_Number).update(Status = 'NeedRevise', Message = request.POST['revisemessage'])
            return listCheck(request)
        if 'finish' in request.POST:
            print(request.POST)
            BE = models.Entertainment.objects.get(BE_Number=ID)
            ListItem = list(models.Entertainment.objects.filter(BE_Number=BE_Number))
            counter = 0
            contain = ''
            for item in ListItem:
                counter += 1
                contain += ''' <tr style="height: 30px; font-size:12px; border-collapse: collapse;">
                    <td rowspan="2" style="border: 1px solid black; border-collapse: collapse;padding: 5px; vertical-align: top;">1</td>
                    <td rowspan="2" style="border: 1px solid black; border-collapse: collapse; padding: 5px; vertical-align: top;">'''+str(item.Date)+'''</td>
                    <td rowspan="2" style="border: 1px solid black; border-collapse: collapse; padding: 5px; vertical-align: top; text-align: left; white-space: pre-wrap;"><div>'''+item.Place.replace("\r\n", "</div><div>")+'''</div></td>
                    <td rowspan="2" style="border: 1px solid black; border-collapse: collapse; padding: 5px; vertical-align: top; text-align: left; white-space: pre-wrap;"><div>'''+item.Address.replace("\r\n", "</div><div>")+'''</div></td>
                    <td rowspan="2" style="border: 1px solid black; border-collapse: collapse; padding: 5px; vertical-align: top;">'''+str(item.Type)+'''</td>
                    <td rowspan="2" style="border: 1px solid black; border-collapse: collapse; padding: 5px; vertical-align: top;">Rp. '''+str(item.Jumlah)+'''</td>
                    <td style="padding: 5px; text-align: left; border-top: 1px solid black; border-right: 1px solid black; border-collapse: collapse; vertical-align: top; white-space: pre-line"><diV><b>External</b></diV><div>'''+item.Name_External.replace("\r\n", "</div><div>")+'''</div></td>
                    <td style="padding: 5px; text-align: left; border-top: 1px solid black; border-right: 1px solid black; border-collapse: collapse; vertical-align: top; white-space: pre-line"><diV><b>External</b></diV>'''+item.Posisi_External.replace("\r\n", "</div><div>")+'''</div>
                    </td>
                    <td style="padding: 5px; text-align: left; border-top: 1px solid black; border-right: 1px solid black; border-collapse: collapse; vertical-align: top; white-space: pre-line"><diV><b>External</b></diV>'''+item.Company_Name_External.replace("\r\n", "</div><div>")+'''</div>
                    </td>
                    <td rowspan="2" style="border: 1px solid black; border-collapse: collapse; padding: 5px; vertical-align: top;">'''+str(item.Company_Type)+'''</td>
                    <td rowspan="2" style="border: 1px solid black; border-collapse: collapse; padding: 5px; vertical-align: top;">'''+str(item.SAP_Number)+'''</td>
                </tr>
                <tr style="height: 30px; font-size:12px; border-collapse: collapse;">
                    <td style="padding: 5px; text-align: left; border-bottom: 1px solid black; border-right: 1px solid black;  border-collapse: collapse; vertical-align: top; white-space: pre-line"><diV><b>Internal</b></diV>'''+item.Name_Internal.replace("\r\n", "</div><div>")+'''</div></td>
                    <td style="padding: 5px; text-align: left; border-bottom: 1px solid black; border-right: 1px solid black;  border-collapse: collapse; vertical-align: top; white-space: pre-line"><diV><b>Internal</b></diV>'''+item.Posisi_Internal.replace("\r\n", "</div><div>")+'''</div>
                    </td>
                    <td style="padding: 5px; text-align: left; border-bottom: 1px solid black; border-right: 1px solid black;  border-collapse: collapse; vertical-align: top; white-space: pre-line"><diV><b>Internal</b></diV>'''+item.Company_Name_Internal.replace("\r\n", "</div><div>")+'''</div>
                    </td>
                </tr>'''
            apptable = """
            <table style="font-size: 12px;text-align: center;border: 1px solid black;border-collapse: collapse;" >
                <tbody >
                    <tr style="height:10px;border: 1px solid black;border-collapse: collapse;">
                        <th style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Prepared By</th>
                        <th colspan="2" style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Approved By</th>
                    </tr>
                    <tr style="height:40px;border: 1px solid black;border-collapse: collapse;">
                        <td style="border: 1px solid black;border-collapse: collapse;padding:20px;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="SPV">Created """ + str(BE.Submit_Date.strftime("%Y-%m-%d %H:%M:%S")) + """</td>
                        <td style="border: 1px solid black;border-collapse: collapse;padding:20px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="DEPT">"""+str(BE.Dept_Head_Approval_Status)+" "+str(BE.Dept_Head_Approval_Date.strftime("%Y-%m-%d %H:%M:%S"))+"""</td>
                        <td style="border: 1px solid black;border-collapse: collapse;padding:20px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="PRDIR"></td>
                    </tr>
                    <tr style="height:20px;border: 1px solid black;border-collapse: collapse;">
                        <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">""" + BE.SPV.title() + """</td>
                        <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">""" + BE.Dept_Head.title() + """</td>
                        <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">""" + BE.PresDirektur.title() + """</td>
                    </tr>
                    <tr style="height:10px;border: 1px solid black;border-collapse: collapse;">
                        <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Supervisor</td>
                        <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Department Head</td>
                        <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">President Director</td>
                    </tr>
                </tbody>
            </table>
            """
            Superior = BE.PresDirektur.title()
            email_body = """
            <html>
                <head style="margin-bottom: 0px;">Dear Mr/Ms """ + Superior + """,</head>
                <body>
                <p style="margin-bottom: 0px;margin-top: 0px;">This Nominative List of Entertainment Cost Request needs your approval </>
                <hr>
                <table style="font-size: x-small; width: 100%">
                    <tr >
                        <td rowspan="3" style="width: 15%;  text-align: center; border-bottom: 1px solid black;"><h1>ASKI</h1></td>
                        <td rowspan="3" style="text-align: center;  border-bottom: 1px solid black;">
                            <div><h3>DAFTAR NOMINATIF BIAYA ENTERTAINMENT DAN SEJENISNYA</h3><div>
                            <div><h3>Tahun Pajak :  """ + str(BE.Tahun_Pajak) + """</h3></div>
                        </td>
                    </tr>
                </table>
                <br>
                <table style="width: 100%; font-size: x-small;">
                    <tr>
                    <td style="width: 10%;">Doc Number</td>
                    <td>:</td>
                    <td>""" + str(BE.BE_Number) + """</td>
                    </tr>
                </table>
                <br>
                <table style="width: 100%; border-collapse: collapse; font-size: 12px;text-align: center">
                    <thead>
                        <tr style=" height: 50px; word-break: normal; border: 1px solid">
                            <th rowspan="2" style="vertical-align: middle; border: 1px solid; padding: 5px; ">No</th>
                            <th colspan="4" style="vertical-align: middle; border: 1px solid; padding: 5px; ">Pemberian Entertainment dan Sejenisnya</th>
                            <th colspan="5" style="vertical-align: middle; border: 1px solid; padding: 5px; ">Relasi Usaha yang diberikan Entertainment dan Sejenisnya</th>
                            <th rowspan="2" style="vertical-align: middle; border: 1px solid; padding: 5px; ">No. Document SAP <br>(diisi oleh Fin. Dept)</th>
                        </tr>
                        <tr style="border: 1px solid">
                            <th style="padding: 5px; border: 1px solid;padding: 5px;">Tanggal</th>
                            <th style="padding: 5px; border: 1px solid;padding: 5px;">Tempat</th>
                            <th style="padding: 5px; border: 1px solid;padding: 5px;">Alamat</th>
                            <th style="padding: 5px; border: 1px solid;padding: 5px;">Jenis</th>
                            <th style="padding: 5px; border: 1px solid;padding: 5px;">Jumlah (Rp)</th>
                            <th style="padding: 5px; border: 1px solid;padding: 5px;">Nama</th>
                            <th style="padding: 5px; border: 1px solid;padding: 5px;">Posisi</th>
                            <th style="padding: 5px; border: 1px solid;padding: 5px;">Nama Perusahaan</th>
                            <th style="padding: 5px; border: 1px solid;padding: 5px;">Jenis Usaha</th>
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
                <hr>
                <p> Please give your response by click approval button bellow and then click send button. A response at your earliest convenience would be much appreciated. </p>
                <table width="100%" cellspacing="0" cellpadding="0">
                    <tr>
                        <td>
                            <table cellspacing="0" cellpadding="0">
                                <tr>
                                    <td style="border-radius: 2px;width : 150px;text-align: center;" bgcolor="#4bf542">
                                        <a href="mailto:online.approval@aski.component.astra.co.id?subject=Approve: """ + str(BE.BE_Number) + """&body=Approve Entertainment Request with ID """ + str(BE.BE_Number) + """ %0DApproval Message:" target="_blank" style="padding: 8px 12px; border: 1px solid #4bf542;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #ffffff;text-decoration: none;font-weight:bold;display: inline-block;">
                                            APPROVE
                                        </a>
                                    </td>
                                    <td>&nbsp;&nbsp;</td>
                                    <td style="border-radius: 2px;width: 150px;text-align: center;" bgcolor="#ED2939">
                                        <a href="mailto:online.approval@aski.component.astra.co.id?subject=Reject: """ + str(BE.BE_Number) + """&body=Reject Entertainment Request with ID """ + str(BE.BE_Number) + """ %0DReject Message:" target="_blank" style="padding: 8px 12px; border: 1px solid #ED2939;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #ffffff;text-decoration: none;font-weight:bold;display: inline-block;">
                                            REJECT
                                        </a>
                                    </td>
                                    <td>&nbsp;&nbsp;</td>
                                    <td style="border-radius: 2px;width: 150px;text-align: center;" bgcolor="#ebde34">
                                        <a href="mailto:online.approval@aski.component.astra.co.id?subject=Revise: """ + str(BE.BE_Number) + """&body=Need Revise Entertainment Request with ID """ + str(BE.BE_Number) + """ %0DRevision Message:" target="_blank" style="padding: 8px 12px; border: 1px solid #ebde34;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #000000;text-decoration: none;font-weight:bold;display: inline-block;">
                                            REVISE
                                        </a>
                                    </td>
                                    <td>&nbsp;&nbsp;</td>
                                    <td style="border-radius: 2px;width: 150px;text-align: center;" bgcolor="#cccccc">
                                        <a href="mailto:""" + str(BE.SPV_Email) + """?subject=Ask User: """ + str(BE.BE_Number) + """&body=Ask User about Entertainment Request with ID """ + str(BE.BE_Number) + """ %0DAsk User Message: " target="_blank" style="padding: 8px 12px; border: 1px solid #cccccc;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #000000;text-decoration: none;font-weight:bold;display: inline-block;">
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
                'Entertainment Online Approval: ' + BE_Number,
                body=email_body, from_email=settings.EMAIL_HOST_USER,
                to=[BE.PresDirektur_Email],
            )
            mailattach.content_subtype = "html"
            if len(str(BE.Attachment1))>1:
                mailattach.attach_file(
                    'Media/'+str(BE.Attachment1))
            if len(str(BE.Attachment2))>1:
                mailattach.attach_file(
                    'Media/'+str(BE.Attachment2))
            if len(str(BE.Attachment3))>1:
                mailattach.attach_file(
                    'Media/'+str(BE.Attachment3))
            if len(str(BE.Attachment4))>1:
                mailattach.attach_file(
                    'Media/'+str(BE.Attachment4))
            if len(str(BE.Attachment5))>1:
                mailattach.attach_file(
                    'Media/'+str(BE.Attachment5))
            if len(str(BE.Attachment6))>1:
                mailattach.attach_file(
                    'Media/'+str(BE.Attachment6))
            mailattach.send()

            email = models.Send(
                htmlmessage=email_body,
                mailfrom='online.approval@aski.component.astra.co.id',
                mailto=BE.PresDirektur_Email,
                BE_Number=BE_Number,
                mailheader='Biaya Entertainment Online Approval: ' + BE_Number)
            email.save()
        models.Entertainment.objects.filter(BE_Number=BE_Number).update(Status="Waiting Approval", Finance_Status="Done Checking")
        return redirect("/BE/ListCheck/")
    
    context = {
        'Judul' : "Checking Biaya Entertainment dan Sejenisnya",
        'ListItem': ListItem,
        'BE': BE,
    }
    return render (request, 'entertainment/viewsCheck.html', context)

def Generate(ID):
    BE_Number = ID

    BE = models.Entertainment.objects.get(BE_Number=BE_Number)
    ListItem = list(models.Entertainment.objects.filter(BE_Number=BE_Number))
    watermark = ""
    for x in range(100):
        watermark += BE_Number+" "
    apptable = """
    <table style="font-size: 12px;text-align: center;border: 1px solid black;border-collapse: collapse;" >
        <tbody >
            <tr style="height:10px;border: 1px solid black;border-collapse: collapse;">
                <th style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Prepared By</th>
                <th colspan="2" style="white-space: nowrap;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Approved By</th>
            </tr>
            <tr style="height:40px;border: 1px solid black;border-collapse: collapse;">
                <td style="border: 1px solid black;border-collapse: collapse;padding:20px;width: 230px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="SPV">Created """ + str(BE.Submit_Date.strftime("%Y-%m-%d %H:%M:%S")) + """</td>
                <td style="border: 1px solid black;border-collapse: collapse;padding:20px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="DEPT">"""+str(BE.Dept_Head_Approval_Status)+" "+str(BE.Dept_Head_Approval_Date.strftime("%Y-%m-%d %H:%M:%S"))+"""</td>
                <td style="border: 1px solid black;border-collapse: collapse;padding:20px;text-align: center;vertical-align: bottom;font-style: italic;color: green;" id="PRDIR">"""+str(BE.PresDirektur_Approval_Status)+' '+str(BE.PresDirektur_Approval_Date.strftime("%Y-%m-%d %H:%M:%S"))+"""</td>
            </tr>
            <tr style="height:20px;border: 1px solid black;border-collapse: collapse;">
                <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">""" + BE.SPV.title() + """</td>
                <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">""" + BE.Dept_Head.title() + """</td>
                <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;text-align: center;vertical-align: bottom;">""" + BE.PresDirektur.title() + """</td>
            </tr>
            <tr style="height:10px;border: 1px solid black;border-collapse: collapse;">
                <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Supervisor</td>
                <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">Department Head</td>
                <td style="white-space: nowrap;padding: 5px;border: 1px solid black;border-collapse: collapse;width: 230px;text-align: center;vertical-align: bottom;">President Director</td>
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
        <body>
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
                    <td rowspan="3" style="width: 15%;  text-align: center; border-bottom: 1px solid black;">
                    <img src="http://127.0.0.1:8000/static/image/ASKI.png"
                        style="width: 80%;margin-left: auto;margin-right: auto;display: block;" alt="GAMBARR">
                    </td>
                    <td rowspan="3" style="text-align: center;  border-bottom: 1px solid black; vertical-align: middle;">
                        <h3>DAFTAR NOMINATIF BIAYA ENTERTAINMENT DAN SEJENISNYA</h3>
                        <h3>TAHUN PAJAK : """ + str(BE.Tahun_Pajak) + """<h3>
                    </td>
                </tr>
            </table>
            <br>
            <table class="table-approve" style="width: 100%;">
                <thead style="vertical-align: middle; text-align: center">
                    <tr style=" height: 50px; word-break: normal; border: 1px solid">
                        <th rowspan="2" style="vertical-align: middle; padding: 5px; border: 1px solid ">No</th>
                        <th colspan="4" style="vertical-align: middle; border: 1px solid ">Pemberian Entertainment dan Sejenisnya</th>
                        <th colspan="5" style="vertical-align: middle; border: 1px solid ">Relasi Usaha yang diberikan Entertainment dan Sejenisnya</th>
                        <th rowspan="2" style="vertical-align: middle; border: 1px solid ">No. Document SAP <br>(diisi oleh Fin. Dept)</th>
                    </tr>
                    <tr style="border: 1px solid">
                        <th style="padding: 5px; border: 1px solid">Tanggal</th>
                        <th style="padding: 5px; border: 1px solid">Tempat</th>
                        <th style="padding: 5px; border: 1px solid">Alamat</th>
                        <th style="padding: 5px; border: 1px solid">Jenis</th>
                        <th style="padding: 5px; border: 1px solid">Jumlah (Rp)</th>
                        <th style="padding: 5px; border: 1px solid">Nama</th>
                        <th style="padding: 5px; border: 1px solid">Posisi</th>
                        <th style="padding: 5px; border: 1px solid">Nama Perusahaan</th>
                        <th style="padding: 5px; border: 1px solid">Jenis Usaha</th>
                    </tr>
                </thead>
                <tbody>
                <tr style="height: 30px; font-size:12px; border-collapse: collapse;">
                    <td rowspan="2" style="border: 1px solid black; border-collapse: collapse; padding: 5px; vertical-align: top;">1</td>
                    <td rowspan="2" style="border: 1px solid black; border-collapse: collapse; padding: 5px; vertical-align: top;">"""+str(BE.Date)+"""</td>
                    <td rowspan="2" style="border: 1px solid black; border-collapse: collapse; padding: 5px; vertical-align: top; text-align: left; white-space: pre-line; width: 150px;">"""+BE.Place+"""</td>
                    <td rowspan="2" style="border: 1px solid black; border-collapse: collapse; padding: 5px; vertical-align: top; text-align: left; white-space: pre-line; width: 150px;">"""+BE.Address+"""</td>
                    <td rowspan="2" style="border: 1px solid black; border-collapse: collapse; padding: 5px; vertical-align: top; width: 150px;">"""+str(BE.Type)+"""</td>
                    <td rowspan="2" style="border: 1px solid black; border-collapse: collapse; padding: 5px; vertical-align: top; text-align: center;">Rp. """+str(BE.Jumlah)+"""</td>
                    <td style="padding: 5px; text-align: left; border-top: 1px solid black; border-right: 1px solid black; border-collapse: collapse; vertical-align: top; white-space: pre-line"><diV><b>External</b></diV>"""+BE.Name_External+"""</td>
                    <td style="padding: 5px; text-align: left; border-top: 1px solid black; border-right: 1px solid black; border-collapse: collapse; vertical-align: top; white-space: pre-line"><diV><b>External</b></diV>"""+BE.Posisi_External+"""
                    </td>
                    <td style="padding: 5px; text-align: left; border-top: 1px solid black; border-right: 1px solid black; border-collapse: collapse; vertical-align: top; white-space: pre-line"><diV><b>External</b></diV>"""+BE.Company_Name_External+"""
                    </td>
                    <td rowspan="2" style="border: 1px solid black; border-collapse: collapse; padding: 5px; vertical-align: top;">"""+str(BE.Company_Type)+"""</td>
                    <td rowspan="2" style="border: 1px solid black; border-collapse: collapse; padding: 5px; vertical-align: top;">"""+str(BE.SAP_Number)+"""</td>
                </tr>
                <tr style="height: 30px; font-size:12px; border-collapse: collapse;">
                    <td style="padding: 5px; text-align: left; border-bottom: 1px solid black; border-right: 1px solid black;  border-collapse: collapse; vertical-align: top; white-space: pre-line"><diV><b>Internal</b></diV>"""+BE.Name_Internal+"""</td>
                    <td style="padding: 5px; text-align: left; border-bottom: 1px solid black; border-right: 1px solid black;  border-collapse: collapse; vertical-align: top; white-space: pre-line"><diV><b>Internal</b></diV>"""+BE.Posisi_Internal+"""
                    </td>
                    <td style="padding: 5px; text-align: left; border-bottom: 1px solid black; border-right: 1px solid black;  border-collapse: collapse; vertical-align: top; white-space: pre-line"><diV><b>Internal</b></diV>"""+BE.Company_Name_Internal+"""
                    </td>
                </tr>
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
    pdfkit.from_string(email_body, "Media\Entertaint\\"+BE_Number +".pdf", configuration=config)
    
def pdf(request, ID):
    Generate(ID)
    return HttpResponse("it works!")
