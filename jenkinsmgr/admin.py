# -*-coding:utf-8 -*-
from django.contrib import admin
from jenkinsmgr import models
# Register your models here.


class JenkinsJobAdmin(admin.ModelAdmin):
    list_display = ("id","job_name","project","action_type","jenkins_server","environment","job_type","auto_build")
    search_fields = ("job_name","project",)
    raw_id_fields = ("project",)
    list_editable = ("job_name","project","action_type","jenkins_server","environment","job_type","auto_build",)
    list_filter = ("auto_build",)
    filter_horizontal = ("emails",)
    list_per_page = 20
    def duplicate_jenkins_job(modeladmin, request, queryset):
        object_list = []
        for object in queryset:
            object.id=None
            object.job_name="%stemp" % object.job_name
            object_list.append(object)
        try:
            models.JenkinsJob.objects.bulk_create(object_list)
        except Exception as e:
            pass

    duplicate_jenkins_job.short_description = u"复制JENKINS JOB"
    actions = (duplicate_jenkins_job,)


class OperationAdmin(admin.ModelAdmin):
    list_display = ("operation_name","operation_value")

class JenkinsServerAdmin(admin.ModelAdmin):

    '''

        server_name = models.CharField(max_length=128)
    ip = models.GenericIPAddressField()
    username = models.CharField(max_length=64)
    password = models.CharField(max_length=256,blank=True,null=True)
    token = models.CharField(max_length=256)
    api_url = models.URLField()
    workspace = models.CharField(max_length=256,blank=True,null=True)

    '''
    list_display = ("server_name","ip","username","token","api_url","workspace")
    list_editable = ("ip","username","token","api_url","workspace")

admin.site.register(models.JenkinsServer,JenkinsServerAdmin)
admin.site.register(models.JenkinsJob,JenkinsJobAdmin)
admin.site.register(models.Operation,OperationAdmin)
