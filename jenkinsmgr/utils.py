# -*- coding: utf-8 -*-

from jenkinsmgr import models as jenkins_models




def get_mail_str(job_obj):

    email_str = ""
    all_email_list = []

    admin_email_qs = job_obj.project.admin_email.select_related()
    develop_email_qs = job_obj.project.develop_email.select_related()
    test_email_qs = job_obj.project.test_email.select_related()

    """
        job_type_choice = (
            (0, '功能测试部署(FUN)'),
            (1, '用户验收测试部署(UAT)'),
            (2, '构建'),
            (3, '通过测试'),
            (4, '生产准备'),
        )

    """
    if job_obj.job_type == 2:
        all_email_list.extend(develop_email_qs)
    elif job_obj.job_type == 0 or job_obj.job_type == 1:
        all_email_list.extend(test_email_qs)

    all_email_list.extend(admin_email_qs)

    for email_obj in all_email_list:
        email_str += email_obj.email + ","

    email_str = email_str.rstrip(',')

    return email_str


def get_user_jenkins_server_list(user_obj):


    group_qs = user_obj.groups.select_related()

    jenkins_server_list = []
    for g in group_qs:
        job_qs = g.jenkins_job.select_related()

        for j in job_qs:
            jenkins_server_obj = j.jenkins_server
            jenkins_server_list.append(jenkins_server_obj)

    user_job_qs = user_obj.jenkins_job.select_related()

    for user_job in user_job_qs:
        jenkins_server_list.append(user_job.jenkins_server)
    jenkins_server_list = set(jenkins_server_list)


    return jenkins_server_list


def get_user_project_list(user_obj,jenkins_server_id):
    group_qs = user_obj.groups.select_related()
    jenkins_server_obj = jenkins_models.JenkinsServer.objects.get(id=jenkins_server_id)
    pro_list = []

    for g in group_qs:
        job_qs = g.jenkins_job.select_related()

        for j in job_qs:
            pro_list.append(j.project)

    user_job_qs = user_obj.jenkins_job.select_related()

    for user_job in user_job_qs:
        if user_job.jenkins_server == jenkins_server_obj:
            pro_list.append(user_job.project)

    pro_list = list(set(pro_list))

    return pro_list
