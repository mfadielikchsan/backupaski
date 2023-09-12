from django.db import models

# Create your models here.
class Entertainment(models.Model):
    BE_Number = models.CharField(max_length=50, null=True)
    Tahun_Pajak = models.CharField(max_length=30, null=True, blank=True)
    Submit_Date = models.DateTimeField(auto_now=True, null=True)
    SPV = models.CharField(max_length=200, null=True)
    SPV_Submit = models.DateTimeField(null=True,blank=True) 
    SPV_Email = models.EmailField(null=True, blank=True)
    Dept_Head = models.CharField(max_length=200, null=True)
    Dept_Head_Email = models.EmailField(null=True, blank=True)
    Dept_Head_Approval_Status = models.CharField(max_length=20, null=True, blank=True)
    Dept_Head_Approval_Date = models.DateTimeField(null=True, blank=True)
    Finance_Status = models.CharField(max_length=20, null=True, blank=True)
    PresDirektur = models.CharField(max_length=200, null=True, blank=True)
    PresDirektur_Email = models.EmailField(null=True, blank=True)
    PresDirektur_Approval_Status = models.CharField(max_length=20, null=True, blank=True)
    PresDirektur_Approval_Date = models.DateTimeField(null=True, blank=True)

    Date =  models.CharField(max_length=30, null=True)
    Place =  models.TextField(null=True)
    Address =  models.TextField(null=True)
    Type = models.TextField(max_length=200, null=True)
    Jumlah = models.CharField(max_length=30, null=True)
    Name_Internal = models.TextField(null=True)
    Posisi_Internal = models.TextField(null=True)
    Company_Name_Internal = models.TextField(null=True)
    Name_External = models.TextField(null=True)
    Posisi_External = models.TextField(null=True)
    Company_Name_External = models.TextField(null=True)
    Company_Type = models.TextField(null=True)
    SAP_Number = models.TextField(null=True, blank=True)

    Status = models.CharField(max_length=30, null=True, blank=True)
    Message = models.CharField(max_length=200, null=True, blank=True)
    Attachment1 = models.FileField(upload_to='Uploads/',null=True,blank=True)
    Attachment2 = models.FileField(upload_to='Uploads/',null=True,blank=True)
    Attachment3 = models.FileField(upload_to='Uploads/',null=True,blank=True)
    Attachment4 = models.FileField(upload_to='Uploads/',null=True,blank=True)
    Attachment5 = models.FileField(upload_to='Uploads/',null=True,blank=True)
    Attachment6 = models.FileField(upload_to='Uploads/',null=True,blank=True)

    def str(self):
        return "%s" % (self.BE_Number)
    
class Approval(models.Model):
    User = models.CharField(max_length=200, null=True)
    SPV = models.CharField(max_length=200, null=True)
    SPV_Email = models.EmailField(null=True, blank=True)
    Dept_Head = models.CharField(max_length=200, null=True)
    Dept_Head_Email = models.EmailField(null=True, blank=True)
    PresDirektur = models.CharField(max_length=200, null=True)
    PresDirektur_Email = models.EmailField(null=True, blank=True)

    def _str_(self):
        return "%s %s" % (self.User,self.SPV)
    
class Received(models.Model):
    BE_Number = models.CharField(max_length=50, null=True)
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
    BE_Number = models.CharField(max_length=50, null=True)
    mailto = models.TextField()
    mailfrom = models.EmailField()
    mailheader = models.CharField(max_length=200)
    htmlmessage = models.TextField()
    htmlmessagefin = models.TextField(null=True)
    def __str__(self):
        return "%s %s" % (self.mailto, self.mailheader)

class activity_log(models.Model):
    user = models.CharField(max_length=30)
    actiontime = models.DateTimeField(auto_now_add=True)
    BE_Number = models.CharField(max_length=50, null=True, blank=True)
    activity = models.TextField()
    def __str__(self):
        return "%s %s" % (self.user, self.actiontime)