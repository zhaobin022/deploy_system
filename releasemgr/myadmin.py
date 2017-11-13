from django import forms
from releasemgr import models
from kingadmin.admin_base import BaseKingAdmin,site


def certificate_clean(self):
    print self.cleaned_data,444

class ReleasePlanAdmin(BaseKingAdmin):
    list_display = ("app_name","release_type","comments","release_date","worker","need_validation")
    list_filters = ("release_type",)

    def clean(self):
        return certificate_clean
site.register(models.AppName)
site.register(models.ReleaseType)
site.register(models.ReleasePlan,ReleasePlanAdmin)









