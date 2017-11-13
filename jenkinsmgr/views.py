# -*- coding: utf-8 -*-

from django.shortcuts import render,HttpResponse,redirect
from jenkinsmgr.jenkins_api import JenkinsApi
from cmdb import models as cmdb_models
from jenkinsmgr import models as jenkins_models
from jenkinsmgr.myadmin import site
from jenkinsmgr import forms
import json
from jenkinsmgr import jenkins_api
from pub_cmdb import settings
import redis
from jenkinsmgr import utils
from django.contrib.auth.decorators import login_required
from usercenter.permissions import check_permission

import traceback



r = redis.Redis(connection_pool=settings.pool)



@login_required()
@check_permission
def jenkinsserver_list(request):
    if request.method == "GET":
        enabled_admins = site.enabled_admins
        admin_obj = enabled_admins['jenkinsmgr']['jenkinsserver']
        jenkins_server_list = utils.get_user_jenkins_server_list(request.user)
        return render(request,"jenkins_mgr/index.html",locals())


@login_required()
def job_list(request,jenkins_server_id , project_id):
    enabled_admins = site.enabled_admins
    if request.method == "GET":
        # enabled_admins = site.enabled_admins
        # admin_obj = enabled_admins['jenkinsmgr']['jenkinsserver']
        project_obj = cmdb_models.Project.objects.get(id=project_id)
        group_qs = request.user.groups.select_related()
        jenkins_server_obj = jenkins_models.JenkinsServer.objects.get(id=jenkins_server_id)
        jenkins_pro_job_list = []
        for g in group_qs:
            job_qs = g.jenkins_job.select_related()
            jenkins_pro_job_list.extend(job_qs.filter(project__id=project_id,jenkins_server=jenkins_server_obj))


        temp_job_list = request.user.jenkins_job.select_related().filter(project__id=project_id,jenkins_server=jenkins_server_obj)
        jenkins_pro_job_list.extend(temp_job_list)

        jenkins_pro_job_list = list(set(jenkins_pro_job_list))
        # job_list = jenkins_server_obj.jenkinsjob_set.select_related()
        return render(request, "jenkins_mgr/job_list.html", locals())


@login_required()
@check_permission
def job_detail(request,job_id):
    enabled_admins = site.enabled_admins
    # admin_obj = enabled_admins['jenkinsmgr']['jenkinsserver']


    disploy_config = {
        "deployapps_list":{
            "display": False,
            'result_list': None,
            'result_list_selected':None
        },
        "operation_list" : {
            "display": True,
            'result_list': None
        },
        "env_list": {
            "display": False,
            'result_list': None
        }
    }



    job_obj = jenkins_models.JenkinsJob.objects.get(id=job_id)
    select_email_qs = job_obj.emails.select_related()
    select_email_ids = [ email.id for email in  select_email_qs]
    jenkins_server_obj = job_obj.jenkins_server


    if request.user.has_perm('usercenter.jenkins_admin'):
        disploy_config["operation_list"]["result_list"] = jenkins_models.Operation.objects.all()
    elif job_obj.job_type == 7:
        disploy_config["operation_list"]["result_list"] = jenkins_models.Operation.objects.filter(
            operation_value__in=['start', 'stop','restart']
        )
    else:
        disploy_config["operation_list"]["result_list"] = jenkins_models.Operation.objects.exclude(operation_value__in=['md5check', 'sync2pro'])

    disploy_config["env_list"]["result_list"] = cmdb_models.Environment.objects.all()

    if job_obj.job_name == job_obj.project.uat_job_name or job_obj.job_type in [4,6,7]:
        deployapps_set = r.smembers("%s_%s_changeall" % (job_obj.project.name, job_obj.project.version.name))
        disploy_config["deployapps_list"]["result_list_selected"] = list(deployapps_set)
    else:
        deployapps_set = r.smembers("%s_%s_change" % (job_obj.project.name ,job_obj.project.version.name))
        disploy_config["deployapps_list"]["result_list_selected"]= list(deployapps_set)

    if job_obj.environment:
        group_name_qs = cmdb_models.HostEnvironmentRelation.objects.filter(project=job_obj.project,environment=job_obj.environment).values_list("group__name")
    else:
        group_name_qs = cmdb_models.HostEnvironmentRelation.objects.filter(project=job_obj.project).values_list("group__name")
    group_name_qs = set(group_name_qs)
    # group_name_list = []
    disploy_config["deployapps_list"]["result_list"] = []
    group_name_choice = []
    for group_name_tuple in group_name_qs:
        disploy_config["deployapps_list"]["result_list"].append(group_name_tuple[0])
        group_name_choice.append((group_name_tuple[0],group_name_tuple[0]))

    email_str = ','.join([e.email for e in select_email_qs])
    email_list = cmdb_models.EmailList.objects.all()



    '''
        job_type_choice = (
        (0, u'功能测试部署(FUN)'),
        (1, u'用户验收测试部署(UAT)'),
        (2, u'构建'),
        (3, u'通过测试'),
        (4, u'生产准备'),
        (5, u'可选类型'),
        (6, u'生产管理')
    )
    '''


    if job_obj.job_type in [0,1,3,4,5,6,7]:
        disploy_config["deployapps_list"]["display"] = True

    if job_obj.job_type in [0, 1, 5,6,7]:
        disploy_config["env_list"]["display"] = True

    if request.method == "GET":
        job_form = forms.JobForm(group_name_choice,request.user,instance=job_obj)
        if job_obj.job_type == 2:
            jenkins_handler = JenkinsApi(
                jenkins_server_obj.api_url,
                jenkins_server_obj.username,
                jenkins_server_obj.token,
                job_obj)
            svn_url,svn_number_on_server,last_build_sn = jenkins_handler.get_svn_url()
            # svn_url = job_obj.svn_url
        return render(request, "jenkins_mgr/job_detail.html", locals())
    elif request.method == "POST":
        # svn_url = job_obj.svn_url
        job_form = forms.JobForm(group_name_choice, request.user, instance=job_obj, data=request.POST)

        change_email_tag = request.POST.get("change_email")

        if change_email_tag and change_email_tag == 'yes':
            email_ids = request.POST.getlist("job_emails")
            selected_ids = set([int(id) for id in email_ids])
            all_ids = set([e.id for e in select_email_qs])
            if selected_ids != all_ids:
                selected_email_obj =  cmdb_models.EmailList.objects.filter(id__in=list(selected_ids))
                job_obj.emails.set(selected_email_obj)
                return redirect(request.path)
                # email_str = ','.join([e.email for e in job_obj.emails.select_related()])

        else:

            if job_form.is_valid():
                jenkins_handler = JenkinsApi(
                    jenkins_server_obj.api_url,
                    jenkins_server_obj.username,
                    jenkins_server_obj.token,
                    job_obj)
                '''
                {'environment': None, 'job_name': u'a', 'action_type': <Operation: 停止服务>} 111

                deployversion

                '''



                variables_dict = {}
                if job_form.cleaned_data["environment"]:
                    variables_dict["env_id"] = job_form.cleaned_data["environment"].environment_name

                # variables_dict["project_prefix"] = job_obj.project.name

                if job_obj.job_name == job_obj.project.uat_job_name or job_obj.job_type == 4:
                    variables_dict["deployapps"] = ','.join(disploy_config["deployapps_list"]["result_list_selected"])
                    if job_obj.job_type == 4:
                        variables_dict["deployapps_count"] = len(disploy_config["deployapps_list"]["result_list_selected"])
                else:
                    if job_form.cleaned_data["deployapps"]:
                        variables_dict["deployapps"] = ','.join(job_form.cleaned_data["deployapps"])
                # variables_dict["version"] = job_obj.project.version.name
                variables_dict["job_id"] = job_obj.id

                variables_dict["email_list"] = email_str
                variables_dict["action_type"] = job_form.cleaned_data["action_type"].operation_value
                # if job_obj.job_type == 2:
                #     variables_dict["svn_url"] = job_obj.svn_url

                ret = jenkins_handler.build_job(**variables_dict)
                # jenkins_handler
                return HttpResponse(json.dumps(ret))
            else:
                ret= {
                    "status" : False,
                    "error_type" : "form_error",
                    "data" : job_form.errors.as_json()
                }

                return HttpResponse(json.dumps(ret))



    return render(request, "jenkins_mgr/job_detail.html", locals())

@login_required()
def job_builds_list(request,job_id):
    enabled_admins = site.enabled_admins
    # enabled_admins = site.enabled_admins
    # admin_obj = enabled_admins['jenkinsmgr']['jenkinsserver']
    job_obj = jenkins_models.JenkinsJob.objects.get(id=job_id)
    jenkins_server_obj = job_obj.jenkins_server

    jenkins_handler = JenkinsApi(
        jenkins_server_obj.api_url,
        jenkins_server_obj.username,
        jenkins_server_obj.token,
        job_obj
    )

    job_builds_number_list = jenkins_handler.get_job_builds_number_list()
    return render(request, "jenkins_mgr/builds_list.html", locals())



@login_required()
def job_builds_detail(request,job_id):
    enabled_admins = site.enabled_admins
    # admin_obj = enabled_admins['jenkinsmgr']['jenkinsserver']
    if request.method == "GET":
        ret = {
            "status" : True
        }
        # enabled_admins = site.enabled_admins
        # admin_obj = enabled_admins['jenkinsmgr']['jenkinsserver']

        build_number = request.GET.get("build_number")
        job_obj = jenkins_models.JenkinsJob.objects.get(id=job_id)
        jenkins_server_obj = job_obj.jenkins_server

        jenkins_handler = JenkinsApi(
            jenkins_server_obj.api_url,
            jenkins_server_obj.username,
            jenkins_server_obj.token,
            job_obj
        )

        ret["msg"] = jenkins_handler.get_console_output(build_number)



        return HttpResponse(json.dumps(ret))





@login_required()
def project_list(request,jenkins_server_id):
    enabled_admins = site.enabled_admins
    # admin_obj = enabled_admins['jenkinsmgr']['jenkinsserver']
    if request.method == "GET":
        user_obj = request.user
        group_qs = user_obj.groups.select_related()
        jenkins_server_obj = jenkins_models.JenkinsServer.objects.get(id=jenkins_server_id)
        pro_list = []

        for g in group_qs:
            job_qs = g.jenkins_job.select_related().filter(jenkins_server=jenkins_server_obj)
            for j in job_qs:
                pro_list.append(j.project)

        user_job_qs = user_obj.jenkins_job.select_related()

        for user_job in user_job_qs:
            if user_job.jenkins_server == jenkins_server_obj:
                pro_list.append(user_job.project)

        pro_list = list(set(pro_list))

        return render(request, "jenkins_mgr/project_list.html", locals())

@login_required()
def batch_build(request):

    if request.method == "POST":
        print request.POST
        ret = {
            "status":True,
             "msg" : None,
            "data" : None
        }
        project_id = request.POST.get("project_id")
        jenkins_server_id = request.POST.get("jenkins_server_id")
        job_name_list = request.POST.get("job_name_list")

        '''

            job_name = models.CharField(max_length=128,verbose_name="job名称")
    # notify_group = models.ManyToManyField(Group)
    project = models.ForeignKey(cmdb_models.Project,verbose_name="项目名",related_name='project_jobs')

        '''
        if all([project_id,jenkins_server_id,job_name_list]):
            job_name_list = json.loads(job_name_list)
            jenkins_server_obj = jenkins_models.JenkinsServer.objects.get(id=jenkins_server_id)
            try:
                for job_name in job_name_list:
                    variables_dict = {}
                    job_obj = jenkins_models.JenkinsJob.objects.get(job_name=job_name,project_id=project_id)
                    select_email_qs = job_obj.emails.select_related()
                    email_str = ','.join([e.email for e in select_email_qs])

                    # email_str = utils.get_mail_str(job_obj)

                    variables_dict["job_id"] = job_obj.id

                    variables_dict["email_list"] = email_str
                    variables_dict["action_type"] = job_obj.action_type.operation_value
                    jenkins_handler = JenkinsApi(
                        jenkins_server_obj.api_url,
                        jenkins_server_obj.username,
                        jenkins_server_obj.token,
                        job_obj
                    )
                    # if job_obj.job_type == 2:
                    #     variables_dict["svn_url"] = job_obj.svn_url

                    result = jenkins_handler.just_send_build_request(**variables_dict)
                    if result["status"] == False:
                        return HttpResponse(json.dumps(result))
                ret["msg"] = "调度已发送到jenkins服务器"

            except Exception as e:
                ret["status"] = False
                ret["msg"] = traceback.format_exc()

        else:
            ret["status"] = False
            ret["msg"] = "参数不全"




        return HttpResponse(json.dumps(ret))
