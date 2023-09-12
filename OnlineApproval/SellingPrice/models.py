from django.db import models
from datetime import date
import datetime, calendar

# Create your models here.
class SellingPrice (models.Model):
    SP_Number = models.CharField(max_length=50,null=True)
    Cust_Code = models.CharField(max_length=30,null=True,blank=True)
    Cust_Name = models.CharField(max_length=150,null=True,blank=True)
    Dist_Channel = models.CharField(max_length=50,null=True,blank=True)
    Product_Status = models.TextField (choices=(
        ("Die Go", "Die Go"),
        ("PP1", "PP1"),
        ("PP2", "PP2"),
        ("Mass Pro", "Mass Pro"),
        ("Reguler", "Reguler")
    ), default="Reguler",
    )
    UserName = models.CharField(max_length=200, null=True, blank=True)
    User_Email = models.EmailField(null=True, blank=True)
    Submit_Date = models.DateField(auto_now=True)
    SPV = models.CharField(max_length=200, null=True, blank=True)
    SPV_Email = models.EmailField(null=True, blank=True)
    User_Submit = models.DateTimeField(null=True,blank=True) 
    SPV_Approval_Status = models.CharField(max_length=20,null=True, blank=True)
    SPV_Approval_Date = models.DateTimeField(null=True, blank=True)
    Dept_Head = models.CharField(max_length=200,null=True, blank=True)
    Dept_Head_Email = models.EmailField(null=True, blank=True)
    Dept_Head_Approval_Status = models.CharField(max_length=20,null=True, blank=True)
    Dept_Head_Approval_Date = models.DateTimeField(null=True, blank=True)
    Div_Head = models.CharField(max_length=200,null=True, blank=True)
    Div_Head_Email = models.EmailField(null=True, blank=True)
    Div_Head_Approval_Status = models.CharField(max_length=20,null=True, blank=True)
    Div_Head_Approval_Date = models.DateTimeField(null=True, blank=True)
    PresDirektur = models.CharField(max_length=200,null=True, blank=True)
    PresDirektur_Email = models.EmailField(null=True, blank=True)
    PresDirektur_Approval_Status = models.CharField(max_length=20,null=True, blank=True)
    PresDirektur_Approval_Date = models.DateTimeField(null=True, blank=True)
    Acc = models.CharField(max_length=200,null=True, blank=True)
    Acc_Email = models.EmailField(null=True, blank=True)
    Acc_Input_Status = models.CharField(max_length=20,null=True, blank=True)
    Acc_Input_Date = models.DateTimeField(null=True, blank=True)
    Dept_Acc = models.CharField(max_length=200,null=True, blank=True)
    Dept_Acc_Email = models.EmailField(null=True, blank=True)
    Dept_Acc_Confirm_Status = models.CharField(max_length=20,null=True, blank=True)
    Dept_Acc_Confirm_Date = models.DateTimeField(null=True, blank=True)

    Attachment1 = models.FileField(upload_to='Uploads/',null=True,blank=True)
    Attachment2 = models.FileField(upload_to='Uploads/',null=True,blank=True)
    Attachment3 = models.FileField(upload_to='Uploads/',null=True,blank=True)
    Attachment4 = models.FileField(upload_to='Uploads/',null=True,blank=True)

    Input1 = models.FileField(upload_to='Uploads/',null=True,blank=True)
    Input2 = models.FileField(upload_to='Uploads/',null=True,blank=True)

    Note = models.CharField(max_length=200,null=True, blank=True)
    Status = models.CharField(max_length=100,null=True, blank=True)
    Message = models.CharField(max_length=200 ,null=True, blank=True)
    
    def __str__(self):
        return "%s" % (self.SP_Number)

class PriceItem (models.Model):
    SP_Number = models.CharField(max_length=50,null=True)
    No = models.CharField(max_length=3,null=True)
    Type = models.CharField(max_length=100,null=True)
    Material_No = models.CharField(max_length=20,null=True)
    Material_Description = models.CharField(max_length=200,null=True)
    Customer_Material = models.CharField(max_length=100,null=True)
    Old_Price = models.CharField(max_length=15,null=True)
    Old_Depreciation = models.CharField(max_length=15,null=True)
    Old_Total = models.CharField(max_length=15,null=True)
    Old_UoM = models.TextField (choices=(
        ("AU", "Activity Unit"),
        ("BOX", "Box"),
        ("BTG", "Batang"),
        ("BTL", "Bottle"),
        ("CAN", "Can"),
        ("CAR", "Carrier"),
        ("DBR", "Drum Besar"),
        ("DR", "Drum"),
        ("DZ", "Dozen"),
        ("KG", "Kilogram"),
        ("L", "Liter"),
        ("LBR", "Lembar"),
        ("LOT", "Lot"),
        ("M", "Meter"),
        ("PAA", "Pasang"),
        ("PAC", "Pack"),
        ("PAI", "Pail"),
        ("PAL", "Pallet"),
        ("PCS", "PCS"),
        ("RIM", "Rim"),
        ("ROL", "Rol"),
        ("SA", "Satuan Asset"),
        ("SET", "Set"),
        ("TAB", "Tabung"),
        ("UN", "Unit"),
        ("YR", "Year"),
    ),
        default="PCS",
    )
    Old_Valid_From = models.CharField(max_length=50, blank=True, null=True)
    New_Price = models.CharField(max_length=15,null=True)
    New_Depreciation = models.CharField(max_length=15,null=True)
    New_Total = models.CharField(max_length=15,null=True)
    New_UoM = models.TextField (choices=(
        ("AU", "Activity Unit"),
        ("BOX", "Box"),
        ("BTG", "Batang"),
        ("BTL", "Bottle"),
        ("CAN", "Can"),
        ("CAR", "Carrier"),
        ("DBR", "Drum Besar"),
        ("DR", "Drum"),
        ("DZ", "Dozen"),
        ("KG", "Kilogram"),
        ("L", "Liter"),
        ("LBR", "Lembar"),
        ("LOT", "Lot"),
        ("M", "Meter"),
        ("PAA", "Pasang"),
        ("PAC", "Pack"),
        ("PAI", "Pail"),
        ("PAL", "Pallet"),
        ("PCS", "PCS"),
        ("RIM", "Rim"),
        ("ROL", "Rol"),
        ("SA", "Satuan Asset"),
        ("SET", "Set"),
        ("TAB", "Tabung"),
        ("UN", "Unit"),
        ("YR", "Year"),
    ),
        default="PCS",
    )
    New_Valid_From = models.CharField(max_length=50, blank=True, null=True)
    Ratio_Variance = models.CharField(max_length=15,null=True)
    Note = models.CharField(max_length=200,null=True)
    
    def __str__(self):
        return "%s %s" % (self.SP_Number, self.Material_Description)

class Approval(models.Model):
    User = models.CharField(max_length=200,null=True)
    User_Name = models.CharField(max_length=200, null=True, blank=True)
    User_Email = models.EmailField(null=True)
    SPV = models.CharField(max_length=200,null=True)
    SPV_Email = models.EmailField()
    Dept_Head = models.CharField(max_length=200,null=True)
    Dept_Head_Email = models.EmailField(null=True)
    Div_Head = models.CharField(max_length=200,null=True)
    Div_Head_Email = models.EmailField()
    PresDirektur = models.CharField(max_length=200,null=True)
    PresDirektur_Email = models.EmailField()
    Acc = models.CharField(max_length=200,null=True)
    Acc_Email = models.EmailField(null=True)
    Dept_Acc = models.CharField(max_length=200,null=True)
    Dept_Acc_Email = models.EmailField(null=True)
    def __str__(self):
        return "%s %s" % (self.User, self.SPV)
    
class Received(models.Model):
    SP_Number = models.CharField(max_length=50, null=True)
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
    SP_Number = models.CharField(max_length=50, null=True)
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
    SP_Number = models.CharField(max_length=50,null=True,blank=True)
    activity = models.TextField()
    def __str__(self):
        return "%s %s" % (self.user, self.actiontime)