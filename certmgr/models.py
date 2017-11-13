# -*-coding:utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.


class CertificateType(models.Model):
    cert_type_name = models.CharField(max_length=256,verbose_name=r"证书类型名")

    def __unicode__(self):
        return self.cert_type_name


    class Meta:
        verbose_name="证书类型"
        verbose_name_plural="证书类型"


class Certificate(models.Model):
    cname = models.CharField(max_length=256,verbose_name=r"证书名称")
    cperiod = models.CharField(max_length=32,verbose_name=r"证书有效周期")
    cexpired_date = models.DateField(verbose_name=r"证书有效期")
    cprovider = models.CharField(max_length=256,verbose_name=r"证书提供方")
    public_name = models.CharField(max_length=256,blank=True,null=True,verbose_name=r"颁发的公用名")
    comments = models.TextField(blank=True,null=True,verbose_name=r"备注")
    begin_notify_time = models.DateField(blank=True,null=True,verbose_name=r"开始提醒时间")
    status = models.BooleanField(verbose_name=r"证书状态")

    # cert_type_choice = (
    #     (0, r'未分类'),
    #     (1, r'银行证书'),
    #     (2, r'其它证书'),
    # )
    cert_type = models.ForeignKey(CertificateType,blank=True,null=True,verbose_name=r"证书类型")

    def __unicode__(self):
        return self.cname


    class Meta:
        verbose_name="证书"
        verbose_name_plural="证书"

