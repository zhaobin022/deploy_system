from django import forms
from cmdb import models
from kingadmin.admin_base import BaseKingAdmin,site


class EnvironmentAdmin(BaseKingAdmin):
    list_display = ['id','environment_name',]
    list_filters = ('db_variables','app_variables',)


class AppVariablesAdmin(BaseKingAdmin):
    list_display = ['key','value',]


class DbVariablesAdmin(BaseKingAdmin):
    list_per_page = 3
    list_display = ["id",'key','value',]
    list_filters = ("key",)
    search_fields = ("key","value",)


class ProjectAdmin(BaseKingAdmin):
    list_per_page = 2
    list_display = ("name","version",)
    list_filters = ("version",)

class TomcatAdmin(BaseKingAdmin):
    list_per_page = 5
    list_display = ("name","http_type","http_port","https_port","shutdown_port")


class HostEnvironmentRelationAdmin(BaseKingAdmin):
    list_display = ("id","environment","group","project")


class HostsAdmin(BaseKingAdmin):
    list_per_page = 3
    list_display = ("id","ipaddr",)

site.register(models.Environment,EnvironmentAdmin)
site.register(models.AppVariables)
site.register(models.Project,ProjectAdmin)
site.register(models.DbVariables,DbVariablesAdmin)
site.register(models.JavaAppFoot)
site.register(models.Hosts,HostsAdmin)
site.register(models.Group)
site.register(models.Version)
site.register(models.Tomcat,TomcatAdmin)
site.register(models.Templates)
site.register(models.HostEnvironmentRelation,HostEnvironmentRelationAdmin)
site.register(models.EmailList)
# site.register(models.DbBaseInfo)
site.register(models.SvnPath)
# site.register(models.ExecuteSqlLog)









