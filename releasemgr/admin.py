# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from releasemgr import models

# Register your models here.


admin.site.register(models.AppName)
admin.site.register(models.ReleasePlan)
admin.site.register(models.ReleaseType)