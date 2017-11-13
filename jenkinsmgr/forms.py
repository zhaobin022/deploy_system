# -*- coding: utf-8 -*-
from django.forms import ModelForm
from django.forms import widgets
from jenkinsmgr import models as jenkins_models
from django.forms import ValidationError

from django import forms

class JobForm(ModelForm):
    def __init__(self, deployapps_choices,user_obj,*args, **kwargs):
        super(JobForm, self).__init__(*args, **kwargs)
        self.fields['deployapps'].choices = deployapps_choices
        self.user_obj = user_obj
        # from django.forms.fields import TextInput


    deployapps = forms.MultipleChoiceField(required=False,widget=widgets.SelectMultiple())

    def clean_action_type(self):
        data = self.cleaned_data['action_type']
        if not data:
            raise ValidationError("你必须选择操作类型!")

        return data

    def clean(self):
        cleaned_data = super(JobForm, self).clean()
        operation_obj = cleaned_data.get("action_type")
        environment_obj = cleaned_data.get("environment")
        job_type = cleaned_data.get("job_type")
        deployapps = cleaned_data.get("deployapps")

        #
        # job_type_choice = (
        #     (0, u'功能测试部署(FUN)'),
        #     (1, u'用户验收测试部署(UAT)'),
        #     (2, u'构建'),
        #     (3, u'通过测试'),
        #     (4, u'生产准备'),
        #     (5, u'可选类型'),
        # )

        if job_type and (job_type not in [2,3,4] ) and (not environment_obj or not deployapps):

            if not environment_obj:
                self.add_error('environment', "必须选择环境!")


            if not deployapps and job_type != 1:
                self.add_error('deployapps', "必须选择应用!")

        if  job_type != None and job_type in [0] and not deployapps:
            self.add_error('deployapps', "必须选择应用!")


        if  operation_obj and \
                operation_obj.operation_value in \
                ['md5check','sync2pro'] and not\
                self.user_obj.has_perm('usercenter.jenkins_admin'):
            self.add_error('action_type', "没有此权限!")


        # if operation_obj and (operation_obj.operation_value != 'build' and  operation_obj.operation_value != 'md5check' ) and not environment_obj:
        #     self.add_error('environment',"必须选择环境!")
        # if cc_myself and subject and "help" not in subject:
        #     msg = "Must put 'help' in subject when cc'ing yourself."
        #     self.add_error('cc_myself', msg)
        #     self.add_error('subject', msg)
        #




    class Meta:
        model = jenkins_models.JenkinsJob
        fields = '__all__'
        exclude = ('jenkins_server','project',)
        widgets = {
            'job_name': widgets.TextInput(attrs={"readonly":True, "class":"span6 m-wrap"}),
        }