from django.db import models
from datetime import date
import datetime, calendar

# Create your models here.
class PurchasingPrice (models.Model):
    PP_Number = models.CharField(max_length=60,null=True)
    Type = models.CharField(max_length=20,choices=(
        ("Otomotif", "Otomotif"),
        ("Non Otomotif", "Non Otomotif"),
    ))
    Submit = models.DateTimeField(null=True,blank=True) 
    Note = models.TextField(null=True)
    Admin = models.CharField(max_length=200, null=True, blank=True)
    Admin_Email = models.EmailField(null=True, blank=True)
    SPV = models.CharField(max_length=200, null=True, blank=True)
    SPV_Email = models.EmailField(null=True, blank=True)
    SPV_Approval_Status = models.CharField(max_length=20,null=True, blank=True)
    SPV_Approval_Date = models.DateTimeField(null=True, blank=True)
    Dept_Head = models.CharField(max_length=200,null=True, blank=True)
    Dept_Head_Email = models.EmailField(null=True, blank=True)
    Dept_Head_Approval_Status = models.CharField(max_length=20,null=True, blank=True)
    Dept_Head_Approval_Date = models.DateTimeField(null=True, blank=True)
    Mkt_Head = models.CharField(max_length=200,null=True, blank=True)
    Mkt_Head_Email = models.EmailField(null=True, blank=True)
    Mkt_Head_Approval_Status = models.CharField(max_length=20,null=True, blank=True)
    Mkt_Head_Approval_Date = models.DateTimeField(null=True, blank=True)
    Div_Head = models.CharField(max_length=200,null=True, blank=True)
    Div_Head_Email = models.EmailField(null=True, blank=True)
    Div_Head_Approval_Status = models.CharField(max_length=20,null=True, blank=True)
    Div_Head_Approval_Date = models.DateTimeField(null=True, blank=True)
    PresDirektur = models.CharField(max_length=200,null=True, blank=True)
    PresDirektur_Email = models.EmailField(null=True, blank=True)
    PresDirektur_Approval_Status = models.CharField(max_length=20,null=True, blank=True)
    PresDirektur_Approval_Date = models.DateTimeField(null=True, blank=True)
    Fin = models.CharField(max_length=200,null=True, blank=True)
    Fin_Email = models.EmailField(null=True, blank=True)
    Fin_Input_Status = models.CharField(max_length=20,null=True, blank=True)
    Fin_Input_Date = models.DateTimeField(null=True, blank=True)
    Dept_Fin = models.CharField(max_length=200,null=True, blank=True)
    Dept_Fin_Email = models.EmailField(null=True, blank=True)
    Dept_Fin_Confirm_Status = models.CharField(max_length=20,null=True, blank=True)
    Dept_Fin_Confirm_Date = models.DateTimeField(null=True, blank=True)
    Attachment1 = models.FileField(upload_to='Uploads/',null=True,blank=True)
    Attachment2 = models.FileField(upload_to='Uploads/',null=True,blank=True)
    Attachment3 = models.FileField(upload_to='Uploads/',null=True,blank=True)
    Attachment4 = models.FileField(upload_to='Uploads/',null=True,blank=True)
    Input1 = models.FileField(upload_to='Uploads/',null=True,blank=True)
    Input2 = models.FileField(upload_to='Uploads/',null=True,blank=True)
    Status = models.CharField(max_length=50,null=True, blank=True)
    Revise_Note = models.CharField(max_length=250,null=True, blank=True)
    Comment_Message = models.TextField(null=True, blank=True)
    Update_SAP = models.CharField(max_length=50,null=True, blank=True)
    Revise_Request = models.CharField(max_length=250,null=True, blank=True)

    Vendor = models.CharField(max_length=250,null=True, blank=True)
    Vendor_Email = models.EmailField(max_length=250,null=True)
    Attn1 = models.CharField(max_length=250,null=True, blank=True)
    Attn2 = models.CharField(max_length=250,null=True, blank=True)
    QuotDate = models.CharField(max_length=100,null=True, blank=True)
    ConfNote = models.TextField(null=True, blank=True)


    def __str__(self):
        return "%s" % (self.PP_Number)

class PP_Item (models.Model):
    PP_Number = models.CharField(max_length=60,null=True)
    Vend_Code = models.CharField(max_length=30,null=True,blank=True)
    Vend_Name = models.CharField(max_length=150,null=True,blank=True)
    Material = models.CharField(max_length=30,null=True,blank=True)
    Material_Desc = models.CharField(max_length=200,null=True,blank=True)    
    Qty = models.CharField(max_length=30,null=True,blank=True)
    UoM = models.CharField(max_length=30,null=True,blank=True)
    Currency = models.CharField(max_length=20,null=True,blank=True)  
    Old_Price = models.CharField(max_length=20,null=True,blank=True)
    Old_Delivery = models.CharField(max_length=20,null=True,blank=True)    
    New_Price = models.CharField(max_length=20,null=True,blank=True)
    New_Delivery = models.CharField(max_length=20,null=True,blank=True) 
    Ratio = models.CharField(max_length=20,null=True,blank=True)
    def __str__(self):
        return "%s %s" % (self.PP_Number)
    
class Approval(models.Model):
    User = models.CharField(max_length=200,null=True)
    Admin = models.CharField(max_length=200, null=True, blank=True)
    Admin_Email = models.EmailField(null=True, blank=True)
    SPV = models.CharField(max_length=200,null=True)
    SPV_Email = models.EmailField()
    Dept_Head = models.CharField(max_length=200,null=True)
    Dept_Head_Email = models.EmailField(null=True)
    Div_Head = models.CharField(max_length=200,null=True)
    Div_Head_Email = models.EmailField()
    PresDirektur = models.CharField(max_length=200,null=True)
    PresDirektur_Email = models.EmailField()
    Mkt_Auto = models.CharField(max_length=200,null=True)
    Mkt_Auto_Email = models.EmailField(null=True)
    Mkt_Non_Auto = models.CharField(max_length=200,null=True)
    Mkt_Non_Auto_Email = models.EmailField(null=True)
    Fin = models.CharField(max_length=200,null=True, blank=True)
    Fin_Email = models.EmailField(null=True, blank=True)
    Dept_Fin = models.CharField(max_length=200,null=True, blank=True)
    Dept_Fin_Email = models.EmailField(null=True, blank=True)
    def __str__(self):
        return "%s %s" % (self.User, self.SPV)
    
class Received(models.Model):
    PP_Number = models.CharField(max_length=50, null=True)
    mailto = models.TextField()
    mailfrom = models.EmailField()
    subject = models.CharField(max_length=200, null=True)
    receiveddetail = models.TextField(null=True)
    datetimereceived = models.CharField(max_length=100, null=True)
    messageid = models.CharField(max_length=200, null=True)
    message = models.TextField(null=True)
    def __str__(self):
        return "%s %s" % (self.mailfrom, self.mailheader)

class Send(models.Model):
    PP_Number = models.CharField(max_length=50, null=True)
    mailto = models.TextField()
    mailfrom = models.EmailField()
    mailheader = models.CharField(max_length=200)
    htmlmessage = models.TextField()
    htmlmessagefin = models.TextField(null=True)
    def __str__(self):
        return "%s %s" % (self.mailto, self.mailheader)

class activity_log(models.Model):
    user = models.CharField(max_length=20)
    actiontime = models.DateTimeField(auto_now_add=True)
    PP_Number = models.CharField(max_length=50,null=True,blank=True)
    activity = models.TextField()
    def __str__(self):
        return "%s %s" % (self.user, self.actiontime)
