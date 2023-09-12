from django.db import models
from datetime import date
import datetime, calendar


# Create your models here.


class PRheader(models.Model):
    Company = models.TextField(choices=(
        ("PT ASTRA KOMPONEN INDONESIA PLANT 1",
         "PT ASTRA KOMPONEN INDONESIA PLANT 1"),
        ("PT ASTRA KOMPONEN INDONESIA PLANT 2",
         "PT ASTRA KOMPONEN INDONESIA PLANT 2"),
    ),

    )
    Bussiness_Area = models.CharField(max_length=100)
    Date_Created = models.DateField(default=date.today)
    Submit = models.DateTimeField(auto_now=True)
    Jenis_PP = models.TextField(choices=(
        ("ZRMT-PR Material", "ZRMT-PR Material"),
        ("ZRSV-PR Service", "ZRSV-PR Service"),
        ("ZRAT-PR Asset", "ZRAT-PR Asset"),
    ),
    )
    PP_Number = models.CharField(max_length=50, null=True)
    User_Name = models.CharField(
        max_length=100, null=True, help_text="Nama User Purchase Request")
    PR_Number = models.CharField(max_length=20, null=True, blank=True)
    PR_Date = models.DateField(null=True, blank=True)
    User_Email = models.EmailField(
        null=True, help_text="Email User Purchase Request")
    SPV_Email = models.EmailField(null=True, blank=True)
    SPV_Approval_Status = models.CharField(
        max_length=20, null=True, blank=True)
    SPV_Approval_Date = models.DateTimeField(null=True, blank=True)
    Dept_Head_Email = models.EmailField(null=True, blank=True)
    Dept_Head_Approval_Status = models.CharField(
        max_length=20, null=True, blank=True)
    Dept_Head_Approval_Date = models.DateTimeField(null=True, blank=True)
    Div_Head_Email = models.EmailField(null=True, blank=True)
    Div_Head_Approval_Status = models.CharField(
        max_length=20, null=True, blank=True)
    Div_Head_Approval_Date = models.DateTimeField(null=True, blank=True)
    Finance_Email = models.EmailField(null=True, blank=True)
    Finance_Approval_Status = models.CharField(
        max_length=20, null=True, blank=True)
    Finance_Approval_Date = models.DateTimeField(null=True, blank=True)
    Direktur_Email = models.EmailField(null=True, blank=True)
    Direktur_Approval_Status = models.CharField(
        max_length=20, null=True, blank=True)
    Direktur_Approval_Date = models.DateTimeField(null=True, blank=True)
    Purchase_Email = models.EmailField(null=True, blank=True)
    Purchase_Approval_Status = models.CharField(
        max_length=20, null=True, blank=True)
    Purchase_Approval_Date = models.DateTimeField(null=True, blank=True)
    PR_Status = models.CharField(max_length=20, null=True, blank=True)

    Attachment1 = models.FileField(upload_to='Uploads/', null=True, blank=True)
    Attachment2 = models.FileField(upload_to='Uploads/', null=True, blank=True)
    Attachment3 = models.FileField(upload_to='Uploads/', null=True, blank=True)

    Budget_No = models.CharField(max_length=30, null=True, blank=True)
    Budget_Rp = models.CharField(max_length=30, null=True, blank=True)
    PP_diProses = models.CharField(max_length=30, null=True, blank=True)
    Sisa_Budget = models.CharField(max_length=30, null=True, blank=True)
    PP_diAjukan = models.CharField(max_length=30, null=True, blank=True)
    Sisa_Final = models.CharField(max_length=30, null=True, blank=True)

    Purchasing_Status = models.CharField(max_length = 200,null=True,blank=True)

    def __str__(self):
        return "%s" % (self.PP_Number)


class PRitem(models.Model):
    PP_Number = models.CharField(max_length=50, null=True)
    Expense = models.TextField(choices=(
        ("F", "Internal Order (F)"),
        ("K", "Cost Center (K)"),
        ("P", "Project (P)"),
        ("A", "Asset (A)"),
    ), null=True, blank=True
    )
    Jenis_Barang = models.TextField(choices=(
        ("K", "Konsiyasi (K)"),
        ("L", "Subcontracting (L)"),
        ("D", "Service (D)"),
    ), null=True, blank=True
    )
    Kode_Barang = models.CharField(max_length=20, null=True, blank=True)
    Nama_Barang = models.CharField(max_length=200, null=True)
    Detail_Spec = models.CharField(max_length=15, null=True, blank=True)
    Jumlah_Order = models.IntegerField()
    Unit_Order = models.TextField(choices=(
        ("AU", "Activity Unit"),
        ("BOX", "Box"),
        ("BTG", "Batang"),
        ("BTL", "Bottle"),
        ("CAN", "Can"),
        ("CAR", "Carrier"),
        ("DBR", "Drum Besar"),
        ("DR", "Drum"),
        ("DZ", "Dozen"),
        ("G", "Gram"),
        ("KG", "Kilogram"),
        ("L", "Liter"),
        ("LBR", "Lembar"),
        ("LOT", "Lot"),
        ("M", "Meter"),
        ("ML", "Mililiter"),
        ("PAA", "Pasang"),
        ("PAC", "Pack"),
        ("PAI", "Pail"),
        ("PAL", "Pallet"),
        ("PCS", "Pcs"),
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
    Currency = models.CharField(max_length=20, choices=(("IDR", "Indonesian Rupiah"), ("USD", "US Dollar"), (
        "SGD", "Singapore Dollar"), ("RMB", "Ren Min Bi"), ("EURO", "Euro")), default="IDR")
    Harga_Satuan = models.CharField(max_length=20, null=True)
    Harga_Total = models.CharField(max_length=20, blank=True, null=True)
    Tgl_Kedatangan = models.CharField(max_length=50, blank=True, null=True)
    Cost_Center = models.CharField(max_length=20, null=True)
    Asset_No_GL_Account = models.CharField(
        max_length=50, null=True, blank=True)
    Minimal_Stock = models.IntegerField(null=True, blank=True)
    Actual_Stock = models.IntegerField(null=True, blank=True)
    Average_Usage = models.IntegerField(null=True, blank=True)
    Budget = models.TextField(choices=(
        ("Budget", "Budget"), ("Un-Budget", "Un-Budget"),), null=True, blank=True)
    Note = models.CharField(max_length=250)

    def __str__(self):
        return "%s %s" % (self.PP_Number, self.Nama_Barang)


class ItemList(models.Model):
    Expense = models.TextField(choices=(
        ("F", "Internal Order (F)"),
        ("K", "Cost Center (K)"),
        ("P", "Project (P)"),
        ("A", "Asset (A)"),
    ),
    null=True, blank=True
    )
    Jenis_Barang = models.TextField(choices=(
        ("K", "Konsiyasi (K)"),
        ("L", "Subcontracting (L)"),
        ("D", "Service (D)"),
    ),
    null=True, blank=True
    )
    Kode_Barang = models.CharField(max_length=20, null=True, blank=True)
    Nama_Barang = models.CharField(max_length=200, null=True)
    Unit_Order = models.TextField(choices=(
        ("AU", "Activity Unit"),
        ("BOX", "Box"),
        ("BTG", "Batang"),
        ("BTL", "Bottle"),
        ("CAN", "Can"),
        ("CAR", "Carrier"),
        ("DBR", "Drum Besar"),
        ("DR", "Drum"),
        ("DZ", "Dozen"),
        ("G", "Gram"),
        ("KG", "Kilogram"),
        ("L", "Liter"),
        ("LBR", "Lembar"),
        ("LOT", "Lot"),
        ("M", "Meter"),
        ("ML", "Mililiter"),
        ("PAA", "Pasang"),
        ("PAC", "Pack"),
        ("PAI", "Pail"),
        ("PAL", "Pallet"),
        ("PCS", "Pcs"),
        ("RIM", "Rim"),
        ("ROL", "Rol"),
        ("SA", "Satuan Asset"),
        ("SET", "Set"),
        ("TAB", "Tabung"),
        ("UN", "Unit"),
        ("YR", "Year"),
    ),
        default="Pcs",
    )
    Harga_Satuan = models.CharField(max_length=20, null=True, blank=True)
    Currency = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return "%s %s" % (self.Kode_Barang, self.Nama_Barang)


class CostCenter(models.Model):
    Cost_Center = models.CharField(max_length=150)
    Plant = models.CharField(max_length=200, choices=(
        ("Plant 1", "Plant 1"), ("Plant 2", "Plant 2")))
    Area = models.CharField(max_length=100, choices=(("Plastic Injection", "Plastic Injection"), ("Rearview", "Rearview"), ("Painting", "Painting"), ("Assy Seat 2W",
                                                                                                                                                      "Assy Seat 2W"), ("Assy Seat 4W", "Assy Seat 4W"), ("Assy Mirror 2W", "Assy Mirror 2W"), ("Assy Mirror 4W", "Assy Mirror 4W"), ("General", "General")))
    Description = models.CharField(max_length=100)


class Approval(models.Model):
    User = models.CharField(max_length=100)
    Supervisor = models.CharField(max_length=100, null=True)
    Supervisor_email = models.EmailField(null=True)
    DeptHead = models.CharField(max_length=100, null=True)
    DeptHead_email = models.EmailField(null=True)
    DivHead = models.CharField(max_length=100, null=True)
    DivHead_email = models.EmailField(null=True)
    Finance = models.CharField(max_length=100, null=True)
    Finance_email = models.EmailField(null=True)
    Direktur = models.CharField(max_length=100, null=True)
    Direktur_email = models.EmailField(null=True)
    Purchase = models.CharField(max_length=100, null=True)
    Purchase_email = models.EmailField(null=True)
    Dir_Finance = models.CharField(max_length=100, null=True)
    Dir_Finance_email = models.EmailField(null=True)

    def __str__(self):
        return "%s %s" % (self.User, self.Supervisor)


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
    PP_Number = models.CharField(max_length=50)
    mailto = models.TextField()
    mailfrom = models.EmailField()
    mailheader = models.CharField(max_length=200)
    htmlmessage = models.TextField()
    htmlmessagefin = models.TextField(null=True)

    def __str__(self):
        return "%s %s" % (self.mailto, self.mailheader)


class Budget(models.Model):
    Budget_No = models.CharField(max_length=50)
    Plant = models.CharField(max_length=100,choices=(
        ("Plant 1", "Plant 1"),
        ("Plant 2", "Plant 2"),
        ("Common", "Common"),
    ),
       default="Plant 1", )
    Description = models.CharField(max_length=200)
    Project = models.CharField(max_length=200,null=True,blank=True)
    Year = models.IntegerField(choices=[(r, r) for r in range(
        datetime.date.today().year, datetime.date.today().year+5)], default=datetime.date.today().year+1)
    Budget_Value = models.CharField(max_length=50,null=True,blank=True)
    Budget_Unit = models.CharField(max_length=5, choices=(
        ("IDR", "Rupiah"),
    ),
    default="IDR",
    )
    
    Created_At = models.DateTimeField(auto_now_add = True)
    Modified_At = models.DateTimeField(auto_now=True)
    Budget_User = models.CharField(max_length=100)
    Current_Budget_Value = models.CharField(max_length=50,null=True,blank=True)
    Budget_Note = models.CharField(max_length=100,null=True,blank=True)

    def __str__(self):
        return "%s %s" % (self.Budget_No, self.Budget_User)


class EmailList(models.Model):
    Name = models.CharField(max_length=100)
    Email = models.EmailField()
    Jabatan = models.CharField(null=True, max_length=100)

    def __str__(self):
        return "%s %s" % (self.Name, self.Jabatan)


class HistoryApproval(models.Model):
    PP_Number = models.CharField(max_length=50)
    Approval_By = models.CharField(max_length=100)
    Email_By = models.EmailField()
    Approval_Status = models.CharField(max_length=50)
    Comment = models.TextField()
    HistoryDate = models.DateTimeField(auto_now_add=True)


class activity_log(models.Model):
    user = models.CharField(max_length=20)
    actiontime = models.DateTimeField(auto_now_add=True)
    PP_Number = models.CharField(max_length=50,null=True,blank=True)
    activity = models.TextField()
    def __str__(self):
        return "%s %s" % (self.user, self.actiontime)


MONTHS = tuple(zip((calendar.month_name[i] for i in range(1,13)), (calendar.month_name[i] for i in range(1,13))))

class MRPheader (models.Model):
    Company = models.TextField(choices=(
        ("PT ASTRA KOMPONEN INDONESIA PLANT 1",
         "PT ASTRA KOMPONEN INDONESIA PLANT 1"),
        ("PT ASTRA KOMPONEN INDONESIA PLANT 2",
         "PT ASTRA KOMPONEN INDONESIA PLANT 2"),
    ),

    )
    Bussiness_Area = models.CharField(max_length=100)
    Date_Created = models.DateField(default=date.today)
    Submit = models.DateTimeField(auto_now=True)
    PP_Number = models.CharField(max_length=50, null=True)
    PP_Type = models.TextField(choices=(
        ("Material","Material"),
        ("Component","Component"),
        ("Consumable","Consumable"),
        ("Sparepart","Sparepart"),
        ("Subcont/Part OutSource","Subcont/Part OutSource"),
        ("After Market & HSO","After Market & HSO"),
        ("Health Care Unit","Health Care Unit")
    ),
    )
    MRP_Month = models.TextField(choices=MONTHS)
    User_Name = models.CharField(
        max_length=100, null=True, help_text="Nama User Purchase Request")
    User_Email = models.EmailField(
        null=True, help_text="Email User Purchase Request")
    SPV_Name = models.CharField(max_length=100, null=True)
    SPV_Email = models.EmailField(null=True, blank=True)
    SPV_Approval_Status = models.CharField(
        max_length=20, null=True, blank=True)
    SPV_Approval_Date = models.DateTimeField(null=True, blank=True)
    Dept_Head_Name = models.CharField(max_length=100, null=True,blank=True)
    Dept_Head_Email = models.EmailField(null=True, blank=True)
    Dept_Head_Approval_Status = models.CharField(
        max_length=20, null=True, blank=True)
    Dept_Head_Approval_Date = models.DateTimeField(null=True, blank=True)
    Div_Head_Name = models.CharField(max_length=100, null=True,blank=True)
    Div_Head_Email = models.EmailField(null=True, blank=True)
    Div_Head_Approval_Status = models.CharField(
        max_length=20, null=True, blank=True)
    Div_Head_Approval_Date = models.DateTimeField(null=True, blank=True)
    Direktur_Name = models.CharField(max_length=100, null=True)
    Direktur_Email = models.EmailField(null=True, blank=True)
    Direktur_Approval_Status = models.CharField(
        max_length=20, null=True, blank=True)
    Direktur_Approval_Date = models.DateTimeField(null=True, blank=True)
    Purchase_Name = models.CharField(max_length=100, null=True)
    Purchase_Email = models.EmailField(null=True, blank=True)
    Purchase_Approval_Status = models.CharField(
        max_length=20, null=True, blank=True)
    Purchase_Approval_Date = models.DateTimeField(null=True, blank=True)
    PR_Status = models.CharField(max_length=20, null=True, blank=True)

    MRP_Item = models.FileField(upload_to='Uploads/', null=True, blank=True)

    Purchasing_Status = models.CharField(max_length = 200,null=True,blank=True)
    Approval_Message = models.CharField(max_length = 200,null=True,blank=True)

    Attachment1 = models.FileField(upload_to='Uploads/', null=True, blank=True)
    Attachment2 = models.FileField(upload_to='Uploads/', null=True, blank=True)

    def __str__(self):
        return "%s %s" % (self.PP_Number, self.User_Name)


