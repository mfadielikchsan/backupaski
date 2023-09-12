from django.db import models

# Create your models here.
class capex(models.Model):
    CP_Number= models.CharField(max_length=50, null=True)
    Submit_Date= models.DateTimeField(auto_now=True, null=True)
    Business_Unit= models.CharField(max_length=100, null=True, blank=True)
    Division= models.CharField(max_length=100, null=True, blank=True)
    Department= models.CharField(max_length=100, null=True, blank=True)
    SPV = models.CharField(max_length=200, null=True, blank=True)
    SPV_Email = models.EmailField(null=True, blank=True)
    SPV_Submit = models.DateTimeField(null=True,blank=True)
    Dept_Head = models.CharField(max_length=200, null=True, blank=True)
    Dept_Head_Email = models.EmailField(null=True, blank=True)
    Dept_Head_Approval_Status = models.CharField(max_length=20, null=True, blank=True)
    Dept_Head_Approval_Date = models.DateTimeField(null=True, blank=True)
    Div_Head = models.CharField(max_length=200, null=True, blank=True)
    Div_Head_Email = models.EmailField(null=True, blank=True)
    Div_Head_Approval_Status = models.CharField(max_length=20, null=True, blank=True)
    Div_Head_Approval_Date = models.DateTimeField(null=True, blank=True)
    PresDirektur = models.CharField(max_length=200, null=True, blank=True)
    PresDirektur_Email = models.EmailField(null=True, blank=True)
    PresDirektur_Approval_Status = models.CharField(max_length=20, null=True, blank=True)
    PresDirektur_Approval_Date = models.DateTimeField(null=True, blank=True)
    Year = models.CharField(max_length=30, null=True, blank=True)
    Next_Year1 = models.CharField(max_length=30, null=True, blank=True)
    Next_Year2 = models.CharField(max_length=30, null=True, blank=True)

    Sum_Year = models.CharField(max_length=30, null=True, blank=True)
    Sum_NextYear1 = models.CharField(max_length=30, null=True, blank=True)
    Sum_NextYear2 = models.CharField(max_length=30, null=True, blank=True)

    Sum_Capex_Year = models.CharField(max_length=30, null=True, blank=True)
    Sum_Capex_NextYear1 = models.CharField(max_length=30, null=True, blank=True)
    Sum_Capex_NextYear2 = models.CharField(max_length=30, null=True, blank=True)

    Sum_Expense_Year = models.CharField(max_length=30, null=True, blank=True)
    Sum_Expense_NextYear1 = models.CharField(max_length=30, null=True, blank=True)
    Sum_Expense_NextYear2 = models.CharField(max_length=30, null=True, blank=True)
    
    Status = models.CharField(max_length=30, null=True, blank=True)
    Revision = models.CharField(max_length=30, null=True, blank=True)
    Message = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return "%s" % (self.CP_Number)    

class cpitem(models.Model):
    CP_Number = models.CharField(max_length=30, null=True)
    No = models.CharField(max_length=3, null=True, blank=True)
    CP_Name = models.CharField(max_length=200, null=True, blank=True)
    Grup = models.TextField(choices=(
        ('Capex', "Capex"),
        ("Expense", "Expense"),
    ), null=True, blank=True, default="Capex")
    Dept= models.CharField(max_length=100, null=True, blank=True)
    PIC = models.CharField(max_length=100, null=True, blank=True)
    Project = models.CharField(max_length=200, null=True, blank=True)
    Asset_Class = models.TextField(choices=(
        ("  Building ", "  Building "),
        ("  Building Eqp.", "  Building Eqp."),
        ("  Machinery Eqp", "  Machinery Eqp"),
        ("  Transportation", "  Transportation"),
        ("  Office Eqp.", "  Office Eqp."),
        ("  Furniture & Fixture", "  Furniture & Fixture"),
        ("  Tools & Eqp.", "  Tools & Eqp."),
        ("  Asset under cap.lease", "  Asset under cap.lease"),
        ("  Mold ISAK 8", "  Mold ISAK 8")
    ),
        default='  Building ', blank=True
    )
    Priority = models.TextField(choices=(
        ("  H I g h","  H I g h"),
        ("  M e d I u m", "  M e d I u m"),
        ("  L o w", "  L o w")
    ),
        default='  L o w', blank=True
    )
    Reason = models.TextField(choices=(
        ("  Penambahan", "  Penambahan"),
        ("  Penggantian ", "  Penggantian "),
        ("  Model Baru", "  Model Baru"),
        ("  Quality Control", "  Quality Control"),
        ("  Local Comp.", "  Local Comp."),
        ("  Keselamatan Kerja", "  Keselamatan Kerja"),
        ("  Peningkatan produk", "  Peningkatan produk"),
        ("  Others", "  Others")
    ),
        default= '  Penambahan', blank=True
    )
    Remarks = models.CharField(max_length=200, null=True, blank=True)
    Item_Year =models.CharField(max_length=30, null=True, blank=True)
    Jan_payment= models.CharField(max_length=30, null=True, blank=True)
    Feb_payment= models.CharField(max_length=30, null=True, blank=True)
    Mar_payment= models.CharField(max_length=30, null=True, blank=True)
    April_payment= models.CharField(max_length=30, null=True, blank=True)
    May_payment= models.CharField(max_length=30, null=True, blank=True)
    Jun_payment= models.CharField(max_length=30, null=True, blank=True)
    Jul_payment= models.CharField(max_length=30, null=True, blank=True)
    Augst_payment= models.CharField(max_length=30, null=True, blank=True)
    Sept_payment= models.CharField(max_length=30, null=True, blank=True)
    Oct_payment= models.CharField(max_length=30, null=True, blank=True)
    Nov_payment= models.CharField(max_length=30, null=True, blank=True)
    Dec_payment= models.CharField(max_length=30, null=True, blank=True)

    Summary_Current_Year = models.CharField(max_length=30, null=True, blank=True)
    Summary_Next_Year1 = models.CharField(max_length=30, null=True, blank=True)
    Summary_Next_Year2 = models.CharField(max_length=30, null=True, blank=True)

    After_Current_Year = models.CharField(max_length=30, null=True, blank=True)
    After_Next_Year1 = models.CharField(max_length=30, null=True, blank=True)
    After_Next_Year2 = models.CharField(max_length=30, null=True, blank=True)

    Payment_Check1 = models.CharField(max_length=30, null=True, blank=True)
    Payment_Check2 = models.CharField(max_length=30, null=True, blank=True)
    Payment_Check3 = models.CharField(max_length=30, null=True, blank=True)

    def __str__(self):
        return "%s %s" % (self.CP_Number, self.CP_Name)
    
class Approval(models.Model):
    user = models.CharField(max_length=200, null=True)
    Business_Unit= models.CharField(max_length=100, null=True, blank=True)
    Division= models.CharField(max_length=100, null=True, blank=True)
    Department= models.CharField(max_length=100, null=True, blank=True)
    SPV = models.CharField(max_length=200,null=True)
    SPV_Email = models.EmailField(null=True)
    Dept_Head = models.CharField(max_length=200, null=True)
    Dept_Head_Email = models.EmailField(null=True)
    Div_Head = models.CharField(max_length=200, null=True)
    Div_Head_Email = models.EmailField(null=True)
    PresDirektur = models.CharField(max_length=200, null=True)
    PresDirektur_Email = models.EmailField(null=True)

    def _str_(self):
        return "%s %s" % (self.User,self.SPV)
    
class Received(models.Model):
    CP_Number = models.CharField(max_length=50, null=True)
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
    CP_Number = models.CharField(max_length=50, null=True)
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
    CP_Number = models.CharField(max_length=50, null=True, blank=True)
    activity = models.TextField()
    def __str__(self):
        return "%s %s" % (self.user, self.actiontime)