from django import forms
from certmgr import models
from kingadmin.admin_base import BaseKingAdmin,site


def certificate_clean(self):
    print self.cleaned_data,444

class CertificateAdmin(BaseKingAdmin):
    list_display = ("cname","cperiod","cexpired_date","cprovider","public_name","cert_type","status",)
    list_filters = ("cert_type",)

    def clean(self):
        return certificate_clean
site.register(models.Certificate,CertificateAdmin)
site.register(models.CertificateType)









