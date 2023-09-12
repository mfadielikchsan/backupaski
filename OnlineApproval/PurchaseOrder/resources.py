from django.db.models import fields
from import_export import resources
from .models import POData

class ListPO(resources.ModelResource):
    class Meta:
        model = POData
        fields = ('id',"PO_Number","PO_Date","PR_Reference","Vendor_Number","Vendor_Name","Revision_Status","PO_Admin","PO_Submit","PO_SPV","PO_SPV_Approval_Status","PO_SPV_Approval_Date","PO_Dept_Head","PO_Dept_Head_Approval_Status","PO_Dept_Head_Approval_Date","PO_Direktur","PO_Direktur_Approval_Status","PO_Direktur_Approval_Date","PO_PresDirektur","PO_PresDirektur_Approval_Status","PO_PresDirektur_Approval_Date","PO_Attachment1","PO_Attachment2","PO_Attachment3","PO_Attachment4","PO_Status","Cancel_Message","Revise_Message","Note","User_Note")



