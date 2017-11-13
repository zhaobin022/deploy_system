from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def judge_current_page(page_num,iter_page,q,svn_id):
    if int(page_num) == iter_page:
        status = "disabled"
    else:
        status = ""
    html = '<li class ="%s"> <a href="?page=%s&q=%s&svn_id=%s">%s</a></li>' % (status,page_num,q,svn_id,page_num)
    return mark_safe(html)


@register.simple_tag
def judge_selected(svn_id1 ,svn_id2 ):
    if svn_id1:
        if long(svn_id1) == svn_id2:
            return True
        else:
            return False
    else:
        return False