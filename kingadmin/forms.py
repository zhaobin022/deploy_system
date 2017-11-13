#_*_coding:utf-8_*_
from django import forms
from cmdb import models
from django.forms import widgets
from django.forms.models import ModelChoiceField
from django.forms.models import ModelMultipleChoiceField
from django.forms.fields import DateField
from django.forms.fields import DateTimeField






def create_model_form(request,admin_obj):
    class BaseForm(forms.ModelForm):
        class Meta:
            model = admin_obj.model
            fields = "__all__"


        def __new__(cls,*args,**kwargs):

            for field_name,field_obj in cls.base_fields.items():
                # if isinstance(field_obj,ModelChoiceField) and not isinstance(field_obj,ModelMultipleChoiceField):
                # print field_obj,9999
                if isinstance(field_obj,ModelChoiceField):
                    field_obj.widget.attrs["class"] = "select2"
                elif isinstance(field_obj,DateField):
                    field_obj.widget.attrs["class"] = "m-wrap m-ctrl-medium date-picker"
                    field_obj.widget.attrs["readonly"] = True
                elif isinstance(field_obj,DateTimeField):
                    field_obj.widget.attrs["class"] = "m-wrap"
                    field_obj.widget.attrs["readonly"] = True
                    field_obj.widget.attrs["size"] = 16


            return forms.ModelForm.__new__(cls,*args,**kwargs)


    if hasattr(admin_obj,"clean"):
        fun =  getattr(admin_obj,"clean")
        setattr(BaseForm,"clean",fun())
    return BaseForm