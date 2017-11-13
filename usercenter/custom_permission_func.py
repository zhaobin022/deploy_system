# -*- coding: utf-8 -*-

from django.core.urlresolvers import resolve


def check_job_obj_permission(request,*args,**kwargs):
    '''

    :param request:
    :param args: args 第一个参数为jenkins job 的 id
    :param kwargs:
    :return:

    检查job是否属于当前用户的组
    '''
    resolve_url_obj = resolve(request.path)

    job_id = resolve_url_obj.args[0]

    group_qs = request.user.groups.select_related()

    for g in group_qs:
        job_qs = g.jenkins_job.select_related()
        job_qs = job_qs.filter(id=job_id)
        if job_qs:
            return True

    job_qs = request.user.jenkins_job.select_related().filter(id=job_id)

    if job_qs:
        return True
    return False