#_*_coding:utf-8_*_
from django.shortcuts import  render,redirect


class BaseKingAdmin(object):
    list_display = []
    list_filters = []
    search_fields = []
    list_per_page = 20
    ordering = None
    filter_horizontal = []
    list_editable = []
    readonly_fields = []
    actions = ["delete_selected_objs",]
    readonly_table = False
    modelform_exclude_fields = []
    add_form = None



class AdminAlreadyRegistered(Exception):
    def __init__(self,msg):
        self.message = msg


class AdminSite(object):
    def __init__(self, name='admin'):
        self.enabled_admins = {}  # model_class class -> admin_class instance
        self.name = name
        #self.default_actions = {'delete_selected': actions.delete_selected}
        #self._global_actions = self._actions.copy()


    def register(self,model_class,admin_class=None):
        if model_class._meta.app_label not in self.enabled_admins:
            self.enabled_admins[model_class._meta.app_label] = {} #enabled_admins['crm'] = {}
        # else:
        #     print(self.enabled_admins)
        #     raise AdminAlreadyRegistered("model %s has registered already"% model_class._meta.model_name)
        #admin_obj = admin_class()
        if not admin_class:#no custom admin class , use BaseAdmin
            admin_class = BaseKingAdmin
        admin_class = admin_class()
        admin_class.model = model_class #缁戝畾model 瀵硅薄鍜宎dmin 绫
        # admin_obj = admin_class()

        self.enabled_admins[model_class._meta.app_label][model_class._meta.model_name] = admin_class
        #enabled_admins['app']['tablename'] = tableadmin
site = AdminSite()


