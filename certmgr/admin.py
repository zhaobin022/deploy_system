# -*-coding:utf-8 -*-
from django.contrib import admin
from certmgr import models
# Register your models here.

class CertificateAdmin(admin.ModelAdmin):
    list_display = ("cname","cperiod","cexpired_date","cprovider","public_name",)




admin.site.register(models.Certificate,CertificateAdmin)
