from django import template
from django.utils.safestring import mark_safe
from usercenter.permissions import check_permission
from django.core.urlresolvers import resolve
from usercenter.permission_list import perm_dic
from usercenter.permissions import check_permission_for_spical_url

register = template.Library()

'''

    'usercenter_cert_delete': ['certmgr_index', ['POST',], [], {}, ],
'''
@register.simple_tag
def check_add_permission(request,request_method):
    add_url = request.path + "add/"

    ret = check_permission_for_spical_url(request.user,add_url,request_method)


    return ret



