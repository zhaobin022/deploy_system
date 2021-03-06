# -*-coding:utf-8 -*-


from django.contrib import admin
from django.utils.safestring import mark_safe
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.admin.widgets import FilteredSelectMultiple
from cmdb.models import *
from django.db.models import Q
import operator
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.utils.safestring import mark_safe
from django.conf.urls import url
from django.http import Http404
from django.db import IntegrityError
import traceback
import re
from django.db.models import Max
import traceback
from pub_cmdb import settings
import redis

r = redis.Redis(connection_pool=settings.pool)
# Register your models here.
class EnvironmentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EnvironmentForm, self).__init__(*args, **kwargs)

        # self.fields['app_variables'] = forms.MultipleChoiceField(
        #     # choices=[(o.id, str(o)) for o in AppVariables.objects.filter(key__startswith=self.instance.environment_name)],
        #     # widget=FilteredSelectMultiple("app variables",is_stacked=False),
        #     # initial=[o.pk for o in self.instance.app_variables.all()]
        # )
        if self.instance:
            self.fields['app_variables'].queryset=AppVariables.objects.filter(key__startswith="%s_" % self.instance.environment_name)
            self.fields['db_variables'].queryset=DbVariables.objects.filter(key__startswith="%s_" % self.instance.environment_name)

        # self.fields['app_variables'].initial=self.instance.app_variables.all()
        # print list(self.instance.app_variables.all().values_list("id",flat=True))
        # self.fields['app_variables'].initial=self.instance.app_variables.all()
        # initial = {'app_variables': self.instance.app_variables.all()}
        # print [(o.id, str(o)) for o in AppVariables.objects.filter(key__startswith=self.instance.environment_name)]
        # print [o.id for o in self.instance.app_variables.select_related()]


    def clean(self):
        if self.instance.environment_name != self.cleaned_data["environment_name"]:
            new_environment_name = self.cleaned_data["environment_name"]
            if self.instance.id:
                for app_var_obj in self.instance.app_variables.select_related():

                    real_key = app_var_obj.key.split('_',1)[1]
                    new_key = "%s_%s" % (new_environment_name,real_key)
                    app_var_obj.key = new_key
                    app_var_obj.save()

                for db_var_obj in self.instance.db_variables.select_related():
                    real_key = db_var_obj.key.split('_', 1)[1]
                    new_key = "%s_%s" % (new_environment_name, real_key)
                    db_var_obj.key = new_key
                    db_var_obj.save()

        return self.cleaned_data
    class Meta:
        model = Environment
        fields = '__all__'

    # def clean(self):
    #     """
    #     Checks that all the words belong to the sentence's language.
    #     """
    #     environment_variables = self.cleaned_data.get('app_variables')
    #     environment_name = self.cleaned_data.get('environment_name')
    #     if environment_variables:
    #         obj_list = environment_variables.filter(key__startswith=environment_name)
    #         if obj_list:
    #             raise ValidationError(
    #                 _("can't %(value)s "),
    #                 params={'value': "zhangsan"},
    #             )
    #     return self.cleaned_data


class EnvironmentAdmin(admin.ModelAdmin):
    form = EnvironmentForm
    list_display = ("environment_name",)
    filter_horizontal = ("app_variables","db_variables",)
    # inline_reverse = ['group','project']
    # inline_type = 'tabular'  # or could be 'stacked'


class HostEnvironmentRelationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(HostEnvironmentRelationForm, self).__init__(*args, **kwargs)

        # self.fields['app_variables'] = forms.MultipleChoiceField(
        #     # choices=[(o.id, str(o)) for o in AppVariables.objects.filter(key__startswith=self.instance.environment_name)],
        #     # widget=FilteredSelectMultiple("app variables",is_stacked=False),
        #     # initial=[o.pk for o in self.instance.app_variables.all()]
        # )
        if self.instance:
            try:
                self.fields['app_variables'].queryset = AppVariables.objects.filter(
                    key__startswith="%s_" % self.instance.environment.environment_name)
                self.fields['db_variables'].queryset = DbVariables.objects.filter(
                    key__startswith="%s_" % self.instance.environment.environment_name)

            except  Exception as e:
                pass

    class Meta:
        model = HostEnvironmentRelation
        fields = '__all__'


    def clean(self):
        """
        Checks that all the words belong to the sentence's language.
        """
        group_type = self.cleaned_data.get('group_type')
        app_foot = self.cleaned_data.get('app_foot')
        tomcat = self.cleaned_data.get('tomcat')



        if group_type == 0:
            if app_foot == None:
                raise ValidationError(
                            _("javaapp app_foot can't empty !")
                        )

        elif group_type ==1:
            if tomcat == None:
                raise ValidationError(
                    _("webapp tomcat can't empty !")
                )

        # print group_type
        # print app_foot
        # print tomcat
        # if environment_variables:
        #     obj_list = environment_variables.filter(key__startswith=environment_name)
        #     if obj_list:
        #         raise ValidationError(
        #             _("can't %(value)s "),
        #             params={'value': "zhangsan"},
        #         )
        return self.cleaned_data


class HostEnvironmentRelationAdmin(admin.ModelAdmin):
    form = HostEnvironmentRelationForm

    '''
        environment = models.OneToOneField(Environment)
    group = models.OneToOneField(Group)
    hosts = models.ManyToManyField(Hosts)
    project = models.OneToOneField(Project)
    app_foot = models.OneToOneField(JavaAppFoot,blank=True,null=True)
    variables = models.ManyToManyField(Variables,blank=True,null=True)
    group_type_choice = (
        (0, 'javaapp'),
        (1, 'webapp'),
    )
    group_type = models.IntegerField(choices=group_type_choice)
    '''
    search_fields = ("environment__environment_name","group__name","tomcat__name","hosts__ipaddr",)
    list_display = ("environment","group","app_foot","group_type","tomcat","get_servers","project",)
    list_editable = ("group","app_foot","group_type","tomcat","project",)
    filter_horizontal = ("app_variables","db_variables","hosts","templates",)
    raw_id_fields = ("group","app_foot","tomcat",)
    list_filter = ("environment__environment_name","project__name","project__version__name")
    list_per_page = 5
    def get_servers(self,obj):
        return "\n".join([h.ipaddr for h in obj.hosts.all()])

    def get_search_results(self, request, queryset, search_term):
        lst = []
        for c in HostEnvironmentRelationAdmin.search_fields:
            q_obj = Q(**{"%s__icontains" % c: search_term})
            lst.append(q_obj)
        # print lst
        if search_term.find("_") != -1:
            project_name , version = search_term.split("_")
            q1 = Q()
            q1.connector = 'AND'
            q1.children.append(('project__name__iendswith', project_name))
            q1.children.append(('project__version__name__istartswith', version))
            lst.append(q1)
        # print reduce(operator.or_, lst)
        queryset = queryset.filter(reduce(operator.or_, lst))

            # queryset = queryset.filter(project__name__icontains=project_name , project__version__name__icontains=version)
        #
        # queryset, use_distinct = super(HostEnvironmentRelationAdmin, self).get_search_results(request, queryset, search_term)
        # print queryset,333
        # print use_distinct,444
        # print search_term,555,type(search_term)
        # queryset.filter(project__name__icontains=search_term OR first_name__icontains=request.POST['query'])

        use_distinct=True
        return queryset, use_distinct




    def duplicate_host_environment_relation(modeladmin, request, queryset):
        try:
            for object in queryset:
                e_obj,status = Environment.objects.get_or_create(environment_name="%stemp" % object.environment.environment_name)

                if status:
                    app_var_qs = object.environment.app_variables.select_related()
                    # app_var_list = []
                    for app_var_obj in app_var_qs:
                        real_app_key = app_var_obj.key.split("_", 1)[1]
                        new_app_key = "%s_%s" % (e_obj.environment_name,real_app_key)
                        new_app_var_obj = AppVariables.objects.create(key=new_app_key,value=app_var_obj.value)
                        e_obj.app_variables.add(new_app_var_obj)

                        # app_var_list.append(new_app_var_obj)
                    # AppVariables.objects.bulk_create(app_var_list)



                    db_var_qs = object.environment.db_variables.select_related()
                    # db_var_list = []
                    for db_var_obj in db_var_qs:
                        real_db_key = db_var_obj.key.split("_", 1)[1]
                        new_db_key = "%s_%s" % (e_obj.environment_name,real_db_key)
                        new_db_var_obj = DbVariables.objects.create(key=new_db_key,value=db_var_obj.value)
                        e_obj.db_variables.add(new_db_var_obj)



                        # db_var_list.append(new_db_var_obj)
                    # DbVariables.objects.bulk_create(db_var_list)



                object.id = None
                object.environment = e_obj
                object.save()
                # e_obj.save()
        except Exception as e:
            traceback.print_exc()

    duplicate_host_environment_relation.short_description = u"复制主机关系记录"
    actions = (duplicate_host_environment_relation,)



class AppVariablesAddForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AppVariablesAddForm, self).__init__(*args, **kwargs)

    class Meta:
        model = AppVariables
        fields = '__all__'
        widgets = {
            'key': forms.TextInput(attrs={'size': 80}),
            'value': forms.TextInput(attrs={'size': 80})
        }
    # def clean_key(self):
    #     key = self.cleaned_data.get('key')
    #     if key:
    #         app_var_obj = AppVariables.objects.filter(key=key)
    #         if app_var_obj:
    #             raise ValidationError(
    #                         _("variables already in the table !")
    #                     )

    def clean(self):
        """
        Checks that all the words belong to the sentence's language.
        """
        key = self.cleaned_data.get('key')
        value = self.cleaned_data.get('value')
        if key:
            app_var_obj = AppVariables.objects.filter(key=key)

            if app_var_obj:
                raise ValidationError(
                            _("variables already in the table !")
                        )

        if key and value:
            db_var_obj = DbVariables.objects.filter(key=key)
            if db_var_obj:

                raise ValidationError(
                            _("variables already in db variables table !")
                        )

        return self.cleaned_data

class AppVariablesChangeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AppVariablesChangeForm, self).__init__(*args, **kwargs)

    #
    def __new__(cls, *args, **kwargs):
        # super(AppVariablesChangeForm,cls).__new__(cls,*args, **kwargs)
        #
        # for field_name,field_obj in  cls.base_fields.items():
        #     print field_name,field_obj,field_obj.bound_data(),1111111111111111
        return forms.ModelForm.__new__(cls)
    class Meta:
        model = AppVariables
        fields = '__all__'
        widgets = {
            'key': forms.TextInput(attrs={'size': 80}),
            'value': forms.TextInput(attrs={'size': 80})
        }

    # def clean_key(self):
    #     key = self.cleaned_data.get('key')
    #     if key:
    #         app_var_obj = AppVariables.objects.filter(key=key)
    #         if app_var_obj:
    #             raise ValidationError(
    #                         _("variables already in the table !")
    #                     )

    def clean(self):
        """
        Checks that all the words belong to the sentence's language.
        """
        key = self.cleaned_data.get('key')
        value = self.cleaned_data.get('value')

        if key and value:
            db_var_obj = DbVariables.objects.filter(key=key)
            if db_var_obj:

                raise ValidationError(
                            _("variables already in db variables table !")
                        )

        return self.cleaned_data


class AppVariablesFilter(admin.SimpleListFilter):
    title = _('Envirment')
    parameter_name = 'key'

    def lookups(self, request, model_admin):
        l = []
        p = re.compile(r'^([^_])+_')

        qa = AppVariables.objects.values_list('key',flat=True)
        for k in qa:
            match = p.match(k)
            if match:
                k = match.group().strip('_')
                if k not in l:
                    l.append(k)

        return [(i+'_',i) for i in l]

    def queryset(self, request, queryset):
        # print queryset


        if self.value():
            return queryset.filter(key__startswith=self.value())
        else:
            return queryset


class AppVariablesAdmin(admin.ModelAdmin):
    # form = AppVariablesForm
    list_display = ("id","key","value",)
    search_fields = ("key","value",)
    list_editable = ("key","value",)
    list_filter = (AppVariablesFilter,)
    ordering = ("key","value",)

    def get_form(self, request, obj=None, **kwargs):
        if obj:  # obj is not None, so this is a change page
            return AppVariablesChangeForm
        else:  # obj is None, so this is an add page
            return AppVariablesAddForm

    def duplicate_app_var(modeladmin, request, queryset):
        object_list = []
        for object in queryset:
            object.id=None
            envirment_name , real_key=object.key.split("_",1)
            object.key = "%stemp_%s" % (envirment_name,real_key)
            object_list.append(object)
        try:
            AppVariables.objects.bulk_create(object_list)
        except Exception as e:
            pass

    duplicate_app_var.short_description = u"复制应用变量"
    actions = (duplicate_app_var,)
        # return super(AppVariablesAdmin, self).get_form(request, obj, **kwargs)
    # def save_model(self, request, obj, form, change):
    #     print form,type(form)
    #     print change
    #     form.add_error("key",ValidationError("dupclicate"))
    #     try:
    #         obj.save()
    #     except (IntegrityError,ValidationError)  as e:
    #         raise ValidationError(e)

# class DbVariablesForm(forms.ModelForm):
#     def __init__(self, *args, **kwargs):
#         super(DbVariablesForm, self).__init__(*args, **kwargs)
#
#     class Meta:
#         model = DbVariables
#         fields = '__all__'
#
#
#     def clean(self):
#         """
#         Checks that all the words belong to the sentence's language.
#         """
#         key = self.cleaned_data.get('key')
#         value = self.cleaned_data.get('value')
#         if key and value:
#             db_var_obj = AppVariables.objects.filter(key=key)
#             if db_var_obj:
#
#                 raise ValidationError(
#                             _("variables already in app variables table !")
#                         )
#
#         return self.cleaned_data

class DbVariablesAddForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DbVariablesAddForm, self).__init__(*args, **kwargs)

    class Meta:
        model = DbVariables
        fields = '__all__'

        widgets = {
            'key': forms.TextInput(attrs={'size': 80}),
            'value': forms.TextInput(attrs={'size': 80})
        }

    # def clean_key(self):
    #     key = self.cleaned_data.get('key')
    #     if key:
    #         app_var_obj = AppVariables.objects.filter(key=key)
    #         if app_var_obj:
    #             raise ValidationError(
    #                         _("variables already in the table !")
    #                     )

    def clean(self):
        """
        Checks that all the words belong to the sentence's language.
        """
        key = self.cleaned_data.get('key')
        value = self.cleaned_data.get('value')
        if key:
            app_var_obj = DbVariables.objects.filter(key=key)

            if app_var_obj:
                raise ValidationError(
                            _("variables already in the table !")
                        )

        if key and value:
            db_var_obj = AppVariables.objects.filter(key=key)
            if db_var_obj:

                raise ValidationError(
                            _("variables already in app variables table !")
                        )

        return self.cleaned_data

class DbVariablesChangeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DbVariablesChangeForm, self).__init__(*args, **kwargs)

    class Meta:
        model = DbVariables
        fields = '__all__'

        widgets = {
            'key': forms.TextInput(attrs={'size': 80}),
            'value': forms.TextInput(attrs={'size': 80})
        }

    # def clean_key(self):
    #     key = self.cleaned_data.get('key')
    #     if key:
    #         app_var_obj = AppVariables.objects.filter(key=key)
    #         if app_var_obj:
    #             raise ValidationError(
    #                         _("variables already in the table !")
    #                     )

    def clean(self):
        """
        Checks that all the words belong to the sentence's language.
        """
        key = self.cleaned_data.get('key')
        value = self.cleaned_data.get('value')

        if key and value:
            db_var_obj = AppVariables.objects.filter(key=key)
            if db_var_obj:

                raise ValidationError(
                            _("variables already in app variables table !")
                        )

        return self.cleaned_data
class DbVariablesFilter(admin.SimpleListFilter):
    title = _('Envirment')
    parameter_name = 'key'

    def lookups(self, request, model_admin):
        l = []
        p = re.compile(r'^([^_])+_')

        qa = DbVariables.objects.values_list('key',flat=True)
        for k in qa:
            match = p.match(k)
            if match:
                k = match.group().strip('_')
                if k not in l:
                    l.append(k)

        return [(i, i) for i in l]
    def queryset(self, request, queryset):
        # print queryset


        if self.value():
            return queryset.filter(key__startswith=self.value())
        else:
            return queryset


class DbVariablesAdmin(admin.ModelAdmin):
    # form = DbVariablesForm
    list_display = ("id","key","value",)
    search_fields = ("key","value",)
    list_editable = ("key","value",)
    list_filter = (DbVariablesFilter,)
    def get_form(self, request, obj=None, **kwargs):
        if obj:  # obj is not None, so this is a change page
            return DbVariablesChangeForm
        else:  # obj is None, so this is an add page
            return DbVariablesAddForm
    def duplicate_db_var(modeladmin, request, queryset):
        object_list = []
        for object in queryset:
            object.id=None
            envirment_name , real_key=object.key.split("_",1)
            object.key = "%stemp_%s" % (envirment_name,real_key)
            object_list.append(object)
        try:
            DbVariables.objects.bulk_create(object_list)
        except Exception as e:
            pass

    duplicate_db_var.short_description = u"复制数据库变量"
    actions = (duplicate_db_var,)

class EmailListAdmin(admin.ModelAdmin):
    list_display = ("email",)
    search_fields = ("email",)



class ProjectFrom(forms.ModelForm):

    def clean(self):
        try:
            if self.cleaned_data["version"] and self.instance:
                project_name = self.instance.name
                last_version = self.instance.version.name
                current_version = self.cleaned_data["version"]
                last_change = "%s_%s_change" % (project_name,last_version)

                current_change = "%s_%s_change" % (project_name,current_version)
                current_changeall = "%s_%s_changeall" % (project_name,current_version)

                last_change_list = list(r.smembers(last_change))

                for i in last_change_list:
                    r.sadd(current_change,i)
                    r.sadd(current_changeall,i)
        except Exception as e:
            pass



    class Meta:
        model = Project
        fields = '__all__'


class ProjectAdmin(admin.ModelAdmin):
    list_display = ("id","name","version")
    search_fields = ("name","version__name")
    # list_editable = ("name","version")
    filter_horizontal = ("admin_email","test_email","develop_email")

    form = ProjectFrom


class HostAdmin(admin.ModelAdmin):
    def deploy_app_count(self,obj):
        count = 0
        try:
            count = obj.hostenvironmentrelation_set.select_related().count()
        except Exception as e:
            count = 0
        return mark_safe(str(count))
    list_display = ("ipaddr","host_type","deploy_app_count")


class TomcatAdmin(admin.ModelAdmin):
    def get_url(self,obj):
        content = ""

        for e_r in obj.hostenvironmentrelation_set.select_related():

            for host in  e_r.hosts.select_related():
                a_tag = '<a href="%s" target="_blank">%s</a>'
                if obj.http_type == 0:
                    link = "http://"
                else:
                    link = "https://"
                link += host.ipaddr+":"

                if obj.http_type == 0:
                    link += str(obj.http_port)
                else:
                    link += str(obj.https_port)

                link += "/"+e_r.group.name
                a_tag=a_tag % (link,link)
                content+=a_tag+"</br>"


        return mark_safe(content)

    list_display = ("name","http_type","shutdown_port","http_port","https_port","jvm_size","get_url")
    list_editable =  ("http_type","shutdown_port","http_port","https_port","jvm_size",)
    ordering = ("shutdown_port","http_port","https_port","jvm_size",)
    search_fields = ("name",)

    def duplicate_tomcat(modeladmin, request, queryset):
        try:
            max_shutdown_port = Tomcat.objects.all().aggregate(Max('shutdown_port'))
            max_http_port = Tomcat.objects.all().aggregate(Max('http_port'))
            max_https_port = Tomcat.objects.all().aggregate(Max('https_port'))
            print max_http_port

            tomcat_obj = queryset.first()

            Tomcat.objects.create(
                name=tomcat_obj.name,
                http_type=tomcat_obj.http_type,
                shutdown_port=max_shutdown_port["shutdown_port__max"]+1,
                http_port=max_http_port["http_port__max"]+1,
                https_port=max_https_port["https_port__max"]+1
            )
        except Exception as e:
            traceback.print_exc()

    duplicate_tomcat.short_description = u"生成tomcat"
    actions = (duplicate_tomcat,)
# AuthorizedEmail.objects.all().aggregate(Max('added'))


class GroupAdmin(admin.ModelAdmin):
    search_fields = ("name",)

class DbBaseInfoAdmin(admin.ModelAdmin):
    list_display = ('name','host','port','sid','db_user','db_password','db_charset')
    raw_id_fields = ('host','port','sid','db_user','db_password',)


    # def get_host_ipaddr(self, obj):
    #     return obj.host.ipaddr


class SvnPathAdmin(admin.ModelAdmin):
    list_display = ("id","path","svn_charset")

class ExecuteSqlLogAdmin(admin.ModelAdmin):
    list_display = ("id","get_db","get_svn","sql_file_name","get_user","get_status_display","create_time",)
    readonly_fields = ("db","user","svn","user","status","create_time","contents","sql_file_name",)

    def get_db(self,obj):
        return obj.db.name

    def get_svn(self,obj):
        return obj.svn.path

    def get_user(self,obj):
        return obj.user.username


admin.site.register(AppVariables,AppVariablesAdmin)
admin.site.register(DbVariables,DbVariablesAdmin)
admin.site.register(Templates)
admin.site.register(JavaAppFoot)
admin.site.register(Hosts,HostAdmin)
admin.site.register(Group,GroupAdmin)
admin.site.register(Tomcat,TomcatAdmin)
admin.site.register(EmailList,EmailListAdmin)
admin.site.register(Version)
admin.site.register(Project,ProjectAdmin)
admin.site.register(Environment,EnvironmentAdmin)
admin.site.register(HostEnvironmentRelation,HostEnvironmentRelationAdmin)
admin.site.register(DbBaseInfo,DbBaseInfoAdmin)
admin.site.register(SvnPath,SvnPathAdmin)
admin.site.register(ExecuteSqlLog,ExecuteSqlLogAdmin)
