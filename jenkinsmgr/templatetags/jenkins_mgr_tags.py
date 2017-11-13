# -*- coding: utf-8 -*-

from jenkinsmgr import utils
from django import template
from django.utils.safestring import mark_safe
from jenkinsmgr import models as jenkinsmgr_models
from cmdb import models as cmdb_models
from jenkinsmgr.jenkins_api import JenkinsApi
import svn
import traceback
register = template.Library()

@register.simple_tag
def gen_jenkins_server_memu():
    html = ""
    for s in jenkinsmgr_models.JenkinsServer.objects.all():
        html += """
                        <li class="active">
                        <a href="/jenkinsmgr/{0}/{1}">
                            {2}
                        </a>
                        </li>
                    """.format(jenkinsmgr_models.JenkinsServer._meta.model_name,s.id,s.server_name)
    return mark_safe(html)


@register.simple_tag
def get_mail_list(job_obj):
    html = ""
    all_email_list = []

    admin_email_qs = job_obj.project.admin_email.select_related()
    develop_email_qs = job_obj.project.develop_email.select_related()
    test_email_qs = job_obj.project.test_email.select_related()

    all_email_list.extend(admin_email_qs)
    all_email_list.extend(develop_email_qs)
    all_email_list.extend(test_email_qs)


    for email_obj in all_email_list:
        html+=email_obj.email+","

    html = html.rstrip(",")

    return mark_safe(html)

@register.simple_tag
def get_project_name(job_obj):
    project_obj = job_obj.project

    project_str = "%s_%s" % (project_obj.name,project_obj.version.name)

    return mark_safe(project_str)



@register.simple_tag
def get_mail_ele(job_obj):
    html = ""
    mail_str = utils.get_mail_str(job_obj)

    mail_list = mail_str.split(',')
    for email in mail_list:
        html+=email + "</br>"
    return mark_safe(html)

@register.simple_tag
def get_url_list(job_obj):
    html = ""
    try:
        group_name = job_obj.job_name.split('-')[1]

        project_obj = job_obj.project
        e_r_list = cmdb_models.HostEnvironmentRelation.objects.filter(project=project_obj,group__name=group_name)
        for e_r in e_r_list:
            if e_r.group_type == 1:
                tomcat_obj = e_r.tomcat
                if tomcat_obj:
                    for host in e_r.hosts.select_related():
                        a_tag = '<a href="%s" target="_blank">%s</a>'
                        link = "http://"
                        links = "https://"
                        link += host.ipaddr + ":"
                        links += host.ipaddr + ":"

                        link += str(tomcat_obj.http_port)
                        links += str(tomcat_obj.https_port)

                        link += "/" + e_r.group.name
                        http_tag = a_tag % (link, link)
                        https_tag = a_tag % (links, links)
                        html += http_tag + "</br>" + https_tag + "</br>"

    except Exception as e:
        pass
    return mark_safe(html)


@register.simple_tag
def get_last_build_time(job_obj):
    jenkins_server_obj = job_obj.jenkins_server
    jenkins_handler = JenkinsApi(
        jenkins_server_obj.api_url,
        jenkins_server_obj.username,
        jenkins_server_obj.token,
        job_obj)
    job_info_dict = jenkins_handler.get_job_info()

    try:
        last_build_number = job_info_dict["lastBuild"]["number"]


        build_info_dict = jenkins_handler.get_build_info(last_build_number)
        timestamp = build_info_dict["timestamp"]/1000
        import time
        timeArray = time.localtime(timestamp)
        otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        return mark_safe(otherStyleTime)
    except Exception as e:
        return ""


@register.simple_tag
def get_last_buid_info_dict(job_obj):
    # info_list = []
    try:

        jenkins_server_obj = job_obj.jenkins_server
        jenkins_handler = JenkinsApi(
            jenkins_server_obj.api_url,
            jenkins_server_obj.username,
            jenkins_server_obj.token,
            job_obj)
        job_info_dict = jenkins_handler.get_job_info()

        last_build_number = job_info_dict["lastBuild"]["number"]


        build_info_dict = jenkins_handler.get_build_info(last_build_number)
        result = build_info_dict["result"]
        timestamp = build_info_dict["timestamp"]/1000
        import time
        timeArray = time.localtime(timestamp)
        otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        sn_in_jenkins = ""
        try:
            svn_info_list = build_info_dict["changeSet"]["revisions"]

            if len(svn_info_list) == 1:
                sn_in_jenkins = svn_info_list[0]["revision"]

        except Exception as e:
            pass
            # traceback.print_exc()


        # # get svn server last commit number
        # current_svn_number = ""
        # try:
        #     if len(svn_info_list) == 1:
        #         svn_url = svn_info_list[0]["module"]
        #
        #         l = svn.remote.RemoteClient(svn_url)
        #         current_svn_info_dict = l.info()
        #         current_svn_number = current_svn_info_dict["commit_revision"]
        # except Exception as e:
        #     traceback.print_exc()


        info_dict={
            'number':last_build_number,
            "datetime":otherStyleTime,
            "result":result,
            "sn_in_jenkins":sn_in_jenkins,
        }

        return info_dict
    except Exception as e:
        return ""
