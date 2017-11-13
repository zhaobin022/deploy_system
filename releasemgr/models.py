# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

class AppName(models.Model):
    app_name = models.CharField(max_length=256,verbose_name=r"系统名称")

    def __unicode__(self):
        return self.app_name

    class Meta:
        verbose_name="系统名称配置项"
        verbose_name_plural="系统名称配置项"

class ReleaseType(models.Model):
    release_type = models.CharField(max_length=256,verbose_name=r"发布类型")

    def __unicode__(self):
        return self.release_type
    class Meta:
        verbose_name="发布类型配置项"
        verbose_name_plural="发布类型配置项"

class ReleasePlan(models.Model):
    app_name = models.ForeignKey(AppName,blank=True,null=True,verbose_name=r"系统名称")
    release_type = models.ForeignKey(ReleaseType,blank=True,null=True,verbose_name=r"发布类型")

    comments = models.TextField(blank=True,null=True,verbose_name=r"发布内容")
    release_date = models.DateField(verbose_name=r"发布时间")
    worker = models.CharField(max_length=256,verbose_name=r"实施负责人")
    need_validation = models.BooleanField(verbose_name=r"需要验证")
    create_time = models.DateTimeField(auto_now_add=True,verbose_name=r"创建时间")


    def __unicode__(self):
        return  self.app_name.app_name if self.app_name else ""

    class Meta:
        verbose_name="发布计划管理"
        verbose_name_plural="发布计划管理"