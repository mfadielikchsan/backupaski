from django.db import models

# Create your models here.
class VendorSelection (models.Model):
    VS_Number = models.CharField(max_length=50)
    VS_Type = models.CharField(max_length=15,choices=(('Reguler','Reguler'),('Non Reguler','Non Reguler')),default='Reguler')
    VS_Status = models.CharField(max_length=20,blank=True,null=True)
    Currency = models.CharField(max_length=5, choices=(
        ("IDR", "Rupiah"),
    ),
    default="IDR",
    )
    Note = models.TextField(blank=True,null=True)
    Review = models.TextField(blank=True,null=True)
    Term_of_Payment =  models.CharField(max_length=250,blank=True,null=True)
    Term_of_Delivery =  models.CharField(max_length=250,blank=True,null=True)

    Review_Price_1 = models.IntegerField(default=0,blank=True)
    Review_Quality_1 = models.IntegerField(default=0,blank=True)
    Review_Delivery_1 = models.IntegerField(default=0,blank=True)
    Review_Safety_1 = models.IntegerField(default=0,blank=True)
    Review_Moral_1 = models.IntegerField(default=0,blank=True)
    Review_Value_Chain_1 =  models.IntegerField(default=0,blank=True)
    Review_Total_1 = models.IntegerField(default=0,blank=True)
    Review_Final_Result_1 = models.IntegerField(default=0,blank=True)
    Review_Price_2 = models.IntegerField(default=0,blank=True)
    Review_Quality_2 = models.IntegerField(default=0,blank=True)
    Review_Delivery_2 = models.IntegerField(default=0,blank=True)
    Review_Safety_2 = models.IntegerField(default=0,blank=True)
    Review_Moral_2 = models.IntegerField(default=0,blank=True)
    Review_Value_Chain_2 =  models.IntegerField(default=0,blank=True)
    Review_Total_2 = models.IntegerField(default=0,blank=True)
    Review_Final_Result_2 = models.IntegerField(default=0,blank=True)
    Review_Price_3 = models.IntegerField(default=0,blank=True)
    Review_Quality_3 = models.IntegerField(default=0,blank=True)
    Review_Delivery_3 = models.IntegerField(default=0,blank=True)
    Review_Safety_3 = models.IntegerField(default=0,blank=True)
    Review_Moral_3 = models.IntegerField(default=0,blank=True)
    Review_Value_Chain_3 =  models.IntegerField(default=0,blank=True)
    Review_Total_3 = models.IntegerField(default=0,blank=True)
    Review_Final_Result_3 = models.IntegerField(default=0,blank=True)
    Review_Price_4 = models.IntegerField(default=0,blank=True)
    Review_Quality_4 = models.IntegerField(default=0,blank=True)
    Review_Delivery_4 = models.IntegerField(default=0,blank=True)
    Review_Safety_4 = models.IntegerField(default=0,blank=True)
    Review_Moral_4 = models.IntegerField(default=0,blank=True)
    Review_Value_Chain_4 =  models.IntegerField(default=0,blank=True)
    Review_Total_4 = models.IntegerField(default=0,blank=True)
    Review_Final_Result_4 = models.IntegerField(default=0,blank=True)
    Review_Price_5 = models.IntegerField(default=0,blank=True)
    Review_Quality_5 = models.IntegerField(default=0,blank=True)
    Review_Delivery_5 = models.IntegerField(default=0,blank=True)
    Review_Safety_5 = models.IntegerField(default=0,blank=True)
    Review_Moral_5 = models.IntegerField(default=0,blank=True)
    Review_Value_Chain_5 =  models.IntegerField(default=0,blank=True)
    Review_Total_5 = models.IntegerField(default=0,blank=True)
    Review_Final_Result_5 = models.IntegerField(default=0,blank=True)

    User_Name = models.CharField(max_length=100, null=True, help_text="Nama User")
    User_Email = models.EmailField(null=True, help_text="Email User")
    DeptHead = models.CharField(max_length=100, null=True, blank= True)
    DeptHead_Approval = models.CharField(max_length=10, null=True, blank= True)
    DeptHead_Approval_Date = models.DateTimeField(null=True,blank=True)
    DeptHead_Email =  models.EmailField(null=True, blank= True)  
    Direktur = models.CharField(max_length=100, null=True, blank= True)
    Direktur_Approval = models.CharField(max_length=10, null=True, blank= True)
    Direktur_Approval_Date = models.DateTimeField(null=True,blank=True)
    Direktur_Email =  models.EmailField(null=True, blank= True)
    Pres_Direktur = models.CharField(max_length=100, null=True, blank= True)
    Pres_Direktur_Approval = models.CharField(max_length=10, null=True, blank= True)
    Pres_Direktur_Approval_Date = models.DateTimeField(null=True,blank=True)
    Pres_Direktur_Email =  models.EmailField(null=True, blank= True)
    Attachment1 = models.FileField(upload_to='Uploads/', null=True, blank=True)
    Attachment2 = models.FileField(upload_to='Uploads/', null=True, blank=True)
    Attachment3 = models.FileField(upload_to='Uploads/', null=True, blank=True)
    

class VS_Item(models.Model):
    VS_Number = models.CharField(max_length=50)
    Part_Number = models.CharField(max_length=50)
    Item_Description = models.CharField(max_length=150)
    Quantity =  models.IntegerField()
    UoM = models.TextField(choices=(
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
    COGM = models.IntegerField()
    Quantity_Per_Month = models.IntegerField()
    Selected_Vendor =  models.IntegerField()
    Vendor_Name_1 = models.CharField(max_length=150,blank=True,null=True) 
    Vendor_Price_1 = models.IntegerField(default=0,blank=True)
    Vendor_Name_2 = models.CharField(max_length=150,blank=True,null=True) 
    Vendor_Price_2 = models.IntegerField(default=0,blank=True)
    Vendor_Name_3 = models.CharField(max_length=150,blank=True,null=True) 
    Vendor_Price_3 = models.IntegerField(default=0,blank=True)
    Vendor_Name_4 = models.CharField(max_length=150,blank=True,null=True) 
    Vendor_Price_4 = models.IntegerField(default=0,blank=True)
    Vendor_Name_5 = models.CharField(max_length=150,blank=True,null=True) 
    Vendor_Price_5 = models.IntegerField(default=0,blank=True)
    COGM_Amount = models.IntegerField()
    Outsource = models.IntegerField()
    Deviation = models.IntegerField()

class PriceChange(models.Model):
    PC_Number = models.CharField(max_length=50)
    Code_Vendor = models.CharField(max_length=50)
    Vendor_Name = models.CharField(max_length=150)
    PIC_Vendor = models.CharField(max_length=150)
    PIC_Level = models.CharField(max_length=150)
    Total_Change_Before = models.IntegerField()
    Total_Change_After = models.IntegerField()
    Total_Change_Dev = models.IntegerField()
    Total_Change_Percent = models.FloatField()
    Create_Date = models.DateTimeField()
    User_Name = models.CharField(max_length=100, null=True, help_text="Nama User")
    User_Email = models.EmailField(null=True, help_text="Email User")
    DeptHead = models.CharField(max_length=100, null=True, blank= True)
    DeptHead_Approval = models.CharField(max_length=10, null=True, blank= True)
    DeptHead_Approval_Date = models.DateTimeField(null=True,blank=True)
    DeptHead_Email =  models.EmailField(null=True, blank= True)  
    Marketing = models.CharField(max_length=100, null=True, blank= True)
    Marketing_Approval = models.CharField(max_length=10, null=True, blank= True)
    Marketing_Approval_Date = models.DateTimeField(null=True,blank=True)
    Marketing_Email =  models.EmailField(null=True, blank= True)  
    Direktur = models.CharField(max_length=100, null=True, blank= True)
    Direktur_Approval = models.CharField(max_length=10, null=True, blank= True)
    Direktur_Approval_Date = models.DateTimeField(null=True,blank=True)
    Direktur_Email =  models.EmailField(null=True, blank= True)
    Pres_Direktur = models.CharField(max_length=100, null=True, blank= True)
    Pres_Direktur_Approval = models.CharField(max_length=10, null=True, blank= True)
    Pres_Direktur_Approval_Date = models.DateTimeField(null=True,blank=True)
    Pres_Direktur_Email =  models.EmailField(null=True, blank= True)
    Attachment1 = models.FileField(upload_to='Uploads/', null=True, blank=True)
    Attachment2 = models.FileField(upload_to='Uploads/', null=True, blank=True)
    Attachment3 = models.FileField(upload_to='Uploads/', null=True, blank=True)

class PC_Item(models.Model):
    PC_Number = models.CharField(max_length=20)
    Material_No = models.CharField(max_length=50)
    Material_Description = models.CharField(max_length=150)
    Old_Price =  models.IntegerField()
    Old_Curr = models.CharField(max_length=5, choices=(
        ("IDR", "Rupiah"),
    ),
    default="IDR",
    )
    Old_Per = models.IntegerField(default=1)
    Old_Unit = models.TextField(choices=(
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
    Old_Valid_From = models.CharField(max_length=150)
    New_Price =  models.IntegerField()
    New_Curr = models.CharField(max_length=5, choices=(
        ("IDR", "Rupiah"),
    ),
    default="IDR",
    )
    New_Per = models.IntegerField(default=1)
    New_Unit = models.TextField(choices=(
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
    New_Valid_From = models.CharField(max_length=150)
    Ratio = models.FloatField()