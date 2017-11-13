# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.db import models
from usercenter.models import MyUser
from django.contrib.auth.models import Group
from cmdb import models as cmdb_models

# Create your models here.



class JenkinsServer(models.Model):
    server_name = models.CharField(max_length=128)
    ip = models.GenericIPAddressField()
    username = models.CharField(max_length=64)
    password = models.CharField(max_length=256,blank=True,null=True)
    token = models.CharField(max_length=256)
    api_url = models.URLField()
    workspace = models.CharField(max_length=256,blank=True,null=True)


    def __unicode__(self):
        return self.server_name


class Operation(models.Model):
    operation_name = models.CharField(max_length=128)
    operation_value = models.CharField(max_length=64)

    def __unicode__(self):
        return self.operation_name



    class Meta:
        unique_together = ("operation_name", "operation_value")



class JenkinsJob(models.Model):
    job_name = models.CharField(max_length=128,verbose_name="job名称")
    # notify_group = models.ManyToManyField(Group)
    project = models.ForeignKey(cmdb_models.Project,verbose_name="项目名",related_name='project_jobs')
    action_type=models.ForeignKey(Operation,blank=True,null=True)
    jenkins_server = models.ForeignKey(JenkinsServer)
    environment = models.ForeignKey(cmdb_models.Environment,blank=True,null=True)

    emails = models.ManyToManyField(cmdb_models.EmailList,blank=True)
    job_type_choice = (
        (0, u'功能测试部署(FUN)'),
        (1, u'用户验收测试部署(UAT)'),
        (2, u'构建'),
        (3, u'通过测试'),
        (4, u'生产准备'),
        (5, u'可选类型'),
        (6, u'生产部署'),
        (7, u'生产起停')
    )
    job_type = models.PositiveIntegerField(choices=job_type_choice,default=2)
    auto_build = models.BooleanField(default=False)
    # svn_url = models.URLField(null=True)

    # current_svn_version = models.PositiveIntegerField(blank=True,null=True)
    # fun_svn_version = models.PositiveIntegerField(blank=True,null=True)
    # uat_svn_version = models.PositiveIntegerField(blank=True,null=True)


    def __unicode__(self):
        if self.jenkins_server:
            return "%s(%s)" % (self.job_name,self.jenkins_server.server_name)
        else:
            return "%s()" % (self.job_name)


    class Meta:
        unique_together = (("job_name", "project"),)

Group.add_to_class('jenkins_job',models.ManyToManyField(JenkinsJob,blank=True))
MyUser.add_to_class('jenkins_job',models.ManyToManyField(JenkinsJob,blank=True))

# cmdb_models.Project.add_to_class('fun_job',models.ForeignKey(JenkinsJob,blank=True))