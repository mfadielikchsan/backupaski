from django.contrib import admin

# Register your models here.

from .models import PRitem, PRheader, Approval, EmailList, Received, Send,activity_log

admin.site.register(PRitem)
admin.site.register(PRheader)
admin.site.register(Approval)
admin.site.register(EmailList)
admin.site.register(Received)
admin.site.register(Send)
admin.site.register(activity_log)



