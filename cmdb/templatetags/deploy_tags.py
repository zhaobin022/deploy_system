# -*- coding: utf-8 -*-
from django import template
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
from django.core.urlresolvers import resolve
from cmdb import models as cmdb_model
from django.forms.boundfield import BoundField
from django.forms.fields import DateField
from django.forms.fields import DateTimeField
from django.db.models.fields import BooleanField
from usercenter import models as usercenter_model
from certmgr import models as cert_model
from usercenter.permission_list import perm_dic
from usercenter.permissions import check_permission_for_spical_url
# models.Environment._meta.fields


register = template.Library()

@register.simple_tag
def gen_deploy_menu(enabled_admins,request,custom_app):
    '''
        <li >
        <a href="{% url 'db_list' %}">
            数据库列表
        </a>
    </li>
    :param enabled_admins:
    :return:
    '''
    html = ''
    resolve_url_obj = resolve(request.path)
    # app_name,table_name = resolve_url_obj.args
    if resolve_url_obj.args :
        if resolve_url_obj.args[0] in enabled_admins.keys():
            app_name = resolve_url_obj.args[0]
            table_name = resolve_url_obj.args[1]
    for app,model_dict in enabled_admins.items():
        if app != custom_app:continue
        for model_name, model_admin in model_dict.items():
            verbose_name_plural = model_admin.model._meta.verbose_name_plural
            if resolve_url_obj.args and resolve_url_obj.args[0] == app:
                if app == app_name and table_name == model_name:
                    temp = """
                        <li class="active">
                        <a href="/kingadmin/%s/%s">
                            %s
                        </a>
                        </li>
                    """ % (app,model_name,verbose_name_plural)

                else:
                    temp = """
                        <li >
                        <a href="/kingadmin/%s/%s">
                            %s
                        </a>
                        </li>
                    """ % (app, model_name, verbose_name_plural)
            else:
                temp = """
                    <li >
                    <a href="/kingadmin/%s/%s">
                        %s
                    </a>
                    </li>
                """ % (app,model_name,verbose_name_plural)

            html += temp
    return mark_safe(html)

@register.simple_tag
def gen_table_header(request,field,page,admin_obj):
    html = ""
    current_orderby_key = request.GET.get("_o")
    search_value = request.GET.get("_q")

    field_obj = admin_obj.model._meta.get_field(field)

    if field_obj.verbose_name:
        column_text = field_obj.verbose_name
    else:
        column_text = field

    if not search_value:
        search_value = ""
    if current_orderby_key:
        if current_orderby_key.strip("-") == field:
            if current_orderby_key.startswith("-"):
                html += """<th class="sorting_desc"><a  href="?_o=%s&page=%s&_q=%s">%s</a></th>""" % (field.strip("-"),page,search_value,column_text)
            else:
                html += """<th  class="sorting_asc"><a  href="?_o=-%s&page=%s&_q=%s">%s</a></th>""" % (field,page,search_value,column_text)
        else:
            html += """<th  class="sorting"><a  href="?_o=-%s&page=%s&_q=%s">%s</a></th>""" % (field,page,search_value,column_text)
    else:
        html += """<th  class="sorting"><a href="?_o=%s&page=%s&_q=%s">%s</a></th>""" % (field,page,search_value,column_text)
    return mark_safe(html)


@register.simple_tag
def gen_td_ele(model_obj,field,request):
    html = ""
    field_data = getattr(model_obj,field)
    field_obj = model_obj._meta.get_field(field)

    if field_obj.choices:
        f = getattr(model_obj,"get_%s_display" % field)
        field_data = f()
    if not field_data:
        field_data = ""
    if field == "id":
        href = "/kingadmin/%s/%s/%d/change/" % (model_obj._meta.app_label,model_obj._meta.model_name,model_obj.id)

        flag = check_permission_for_spical_url(request.user,href,"GET")


        if flag:
            html += '''<td><input type="checkbox" class="id_checkboxes" name="id",value="%s"><a href="%s">%s</a></td>''' % (field_data,href,field_data)
        else:
            html += '''<td><input type="checkbox" class="id_checkboxes" name="id",value="%s">%s</td>''' % (field_data,field_data)

    else:
        if isinstance(field_obj,BooleanField):
            if field_data:
                html += """<td><span class="label label-success">%s</span></td>""" % field_data
            else:
                html += """<td><span class="label label-important">%s</span></td>""" % "False"
        else:
            html += "<td>%s</td>" % field_data

    return mark_safe(html)


@register.simple_tag
def get_model_verbose_name(admin_obj):
    html = ""
    verbose_name = admin_obj.model._meta.verbose_name
    if verbose_name:
        html += verbose_name
    else:
        html += admin_obj.model._meta.model_name

    return mark_safe(html)


@register.simple_tag
def get_field_name(admin_obj,field):
    html = ""
    try:
        field_obj = admin_obj.model._meta.get_field(field)

        verbose_name = field_obj.verbose_name
    except Exception as e:
        verbose_name = field
    if verbose_name:
        html = verbose_name
    else:
        html = field.name


    return mark_safe(html)

@register.simple_tag
def get_list_filter_options(admin_obj,field):
    html = ''
    try:
        field_obj = admin_obj.model._meta.get_field(field)
        selected_value = admin_obj.filter_dict.get(field)
        for opt_value,opt_text in field_obj.get_choices():
            if selected_value == str(opt_value):
                html += '''<option value="%s" selected>%s</option>''' %  (opt_value,opt_text)
            else:
                html += '''<option value="%s">%s</option>''' %  (opt_value,opt_text)

    except Exception as e:
        obj_list = admin_obj.model.objects.values_list(field)
        html += '''<option value="" selected>%s</option>''' % '--------'

        for field_value in  obj_list:
            field_value = field_value[0]
            if selected_value == str(field_value):
                html += '''<option value="%s" selected>%s</option>''' % (field_value, field_value)
            else:
                html += '''<option value="%s">%s</option>''' % (field_value, field_value)
        # for i in
        # html += '''<option value="%s">%s</option>''' % (opt_value, opt_text)
    return mark_safe(html)

@register.simple_tag
def kingadmin_judge_current_page(page_obj,request):


    html = ""

    current_orderby_key = request.GET.get("_o")
    search_value = request.GET.get("_q")
    if not search_value:
        search_value = ""

    page_range = page_obj.paginator.page_range
    current_page = page_obj.number


    first = False

    for page_num in page_range:

        diff_number = abs(current_page - page_num)

        print diff_number

        if diff_number > 3:
            if not first:
                html += '<li class =""><a>..</a></li>'
                first = True
        else:
            first = False
            if int(page_num) == current_page:
                status = "disabled"
            else:
                status = ""

            if current_orderby_key:
                html += '<li class ="%s"> <a href="?page=%s&_o=%s&_q=%s">%s</a></li>' % (status, page_num,current_orderby_key,search_value, page_num)
            else:
                html += '<li class ="%s"> <a href="?page=%s&_q=%s">%s</a></li>' % (status,page_num,search_value,page_num)
    return mark_safe(html)


@register.simple_tag
def get_ordery_by_par(request):
    current_orderby_key = request.GET.get("_o")
    html = ""
    if current_orderby_key:
        html+="&_o=%s" % current_orderby_key


    return mark_safe(html)



@register.simple_tag
def get_search_content(request):
    html = ""
    search_content = request.GET.get("_q")
    if search_content:
        html += search_content


    return html

@register.simple_tag
def get_search_par(request):
    html = ""
    search_content = request.GET.get("_q")
    if search_content:
        html += "&_q=%s" % search_content

    return html


@register.simple_tag
def get_model_list_url(admin_obj):
    html = "/kingadmin/%s/%s/" % (admin_obj.model._meta.app_label,admin_obj.model._meta.model_name)
    return html

@register.simple_tag
def judge_field_date_type(field_obj):
    # BoundField.field
    if isinstance(field_obj.field,DateField):
        return True
    else:
        return False


@register.simple_tag
def judge_field_datetime_type(field_obj):
    # BoundField.field
    if isinstance(field_obj.field,DateTimeField):
        return True
    else:
        return False


@register.simple_tag
def get_current_user_count():
    user_count = usercenter_model.MyUser.objects.count()
    return user_count


@register.simple_tag
def get_current_server_count():
    server_count = cmdb_model.Hosts.objects.count()
    return server_count


@register.simple_tag
def get_current_cert_count():
    cert_counts = cert_model.Certificate.objects.count()
    return cert_counts

@register.simple_tag
def get_db_count():
    db_count = cmdb_model.DbBaseInfo.objects.count()
    return db_count