from operator import mod
from django.db import models

# Create your models here.
class POData (models.Model):
    PO_Number = models.CharField(max_length=30,null=True)
    PO_Date = models.CharField(max_length=30,null=True)
    PR_Reference = models.CharField(max_length=20,null=True, blank=True)
    Vendor_Number = models.CharField(max_length=30,null=True)
    Vendor_Name = models.CharField(max_length=200,null=True)
    Revision_Status = models.IntegerField(default=0)
    Approval_Level = models.CharField(max_length=20,null=True,blank=True)
    PO_Before_Approval = models.FileField(upload_to='InitialPO/' )
    PO_Admin = models.CharField(max_length=200)
    PO_Admin_Email = models.EmailField()
    PO_Submit = models.DateTimeField(auto_now_add = True)
    PO_SPV = models.CharField(max_length=200)
    PO_SPV_Email = models.EmailField(null=True, blank=True)
    PO_SPV_Approval_Status = models.CharField(max_length=20,null=True, blank=True)
    PO_SPV_Approval_Date = models.DateTimeField(null=True, blank=True)
    PO_Dept_Head = models.CharField(max_length=200)
    PO_Dept_Head_Email = models.EmailField(null=True, blank=True)
    PO_Dept_Head_Approval_Status = models.CharField(max_length=20,null=True, blank=True)
    PO_Dept_Head_Approval_Date = models.DateTimeField(null=True, blank=True)
    PO_Direktur = models.CharField(max_length=200,null=True, blank=True)
    PO_Direktur_Email = models.EmailField(null=True, blank=True)
    PO_Direktur_Approval_Status = models.CharField(max_length=20,null=True, blank=True)
    PO_Direktur_Approval_Date = models.DateTimeField(null=True, blank=True)
    PO_PresDirektur = models.CharField(max_length=200,null=True, blank=True)
    PO_PresDirektur_Email = models.EmailField(null=True, blank=True)
    PO_PresDirektur_Approval_Status = models.CharField(max_length=20,null=True, blank=True)
    PO_PresDirektur_Approval_Date = models.DateTimeField(null=True, blank=True)
    PO_After_Approval = models.FileField(upload_to='ApprovedPO/',null=True,blank=True)
    PO_Attachment1 = models.FileField(upload_to='Uploads/',null=True,blank=True)
    PO_Attachment2 = models.FileField(upload_to='Uploads/',null=True,blank=True)
    PO_Attachment3 = models.FileField(upload_to='Uploads/',null=True,blank=True)
    PO_Attachment4 = models.FileField(upload_to='Uploads/',null=True,blank=True)
    PO_Status = models.CharField(max_length=30,null=True, blank=True)
    Cancel_Message = models.CharField(max_length=250,blank=True,null=True)
    Revise_Message = models.CharField(max_length=250,blank=True,null=True)
    Note = models.CharField(max_length=250,blank=True,null=True)
    User_Note = models.CharField(max_length=250,blank=True,null=True)
    Vendor_Confirm = models.CharField(max_length=30,null=True, blank=True)

    def __str__(self):
        return "%s" % (self.PO_Number)

class VendorData (models.Model):
    Vendor_Number = models.CharField(max_length=20,null=True)
    Vendor_Name = models.CharField(max_length=250,null=True)
    def __str__(self):
        return "%s" % (self.Vendor_Number)

class POApproval(models.Model):
    Admin = models.CharField(max_length=200)
    Admin_Email = models.EmailField()
    SPV = models.CharField(max_length=200)
    SPV_Email = models.EmailField()
    Dept_Head = models.CharField(max_length=200)
    Dept_Head_Email = models.EmailField()
    Direktur = models.CharField(max_length=200)
    Direktur_Email = models.EmailField()
    PresDirektur = models.CharField(max_length=200)
    PresDirektur_Email = models.EmailField()
    def __str__(self):
        return "%s" % (self.Admin)

class Send(models.Model):
    PO_Number = models.CharField(max_length=50,null=True)
    mailto = models.TextField()
    mailfrom = models.EmailField()
    mailheader = models.CharField(max_length=200)
    htmlmessage = models.TextField()

    def __str__(self):
        return "%s %s" % (self.mailto, self.mailheader)

class ReceivedMail(models.Model):
    PO_Number = models.CharField(max_length=50, null=True)
    mailto = models.TextField()
    mailfrom = models.EmailField()
    subject = models.CharField(max_length=200, null=True)
    receiveddetail = models.TextField(null=True)
    datetimereceived = models.CharField(max_length=100, null=True)
    messageid = models.CharField(max_length=200, null=True)
    message = models.TextField(null=True)

    def __str__(self):
        return "%s %s" % (self.mailfrom, self.mailheader)