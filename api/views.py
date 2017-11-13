from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.http import HttpResponseForbidden
import json
from cmdb import models
from django.views.decorators.csrf import csrf_exempt
import settings
from django.db import transaction
import re
import time
import subprocess
import redis
from django.contrib.auth.decorators import login_required
from jenkinsmgr import models as jenkins_models
# Create your views here.
pool = redis.ConnectionPool(host='localhost', port=6379)
r = redis.Redis(connection_pool=pool)

def construct_app_info(data,envirment_related_list,var_dict):

    group_variables_dict = {}
    for e_obj in envirment_related_list:
        if e_obj.get_group_type_display() == 'webapps':
            if not data["webapps"].get(e_obj.group.name):
                data["webapps"][e_obj.group.name] = {}
            data["webapps"][e_obj.group.name]["http_port"] = e_obj.tomcat.http_port
            data["webapps"][e_obj.group.name]["http_type"] = e_obj.tomcat.get_http_type_display()
            data["webapps"][e_obj.group.name]["https_port"] = e_obj.tomcat.https_port
            data["webapps"][e_obj.group.name]["shut_port"] = e_obj.tomcat.shutdown_port
            data["webapps"][e_obj.group.name]["tomcatname"] = e_obj.tomcat.name
            data["webapps"][e_obj.group.name]["jvm_size"] = e_obj.tomcat.jvm_size

            if not data["inventory"]["groups"].get(e_obj.group.name):
                data["inventory"]["groups"][e_obj.group.name] = []
            for h in e_obj.hosts.select_related():
                data["inventory"]["groups"][e_obj.group.name].append(h.ipaddr)


        elif e_obj.get_group_type_display() == 'javaapps':
            if not data["javaapps"].get(e_obj.group.name):
                data["javaapps"][e_obj.group.name] = {}
            if not data["javaapps"][e_obj.group.name].get("appfoot"):
                data["javaapps"][e_obj.group.name]["appfoot"] = []

            data["javaapps"][e_obj.group.name]["appfoot"].append(e_obj.app_foot.foot_name)

            if not data["inventory"]["groups"].get("%s_%s" % (e_obj.group.name, e_obj.app_foot.foot_name)):
                data["inventory"]["groups"]["%s_%s" % (e_obj.group.name, e_obj.app_foot.foot_name)] = []
            for h in e_obj.hosts.select_related():
                data["inventory"]["groups"]["%s_%s" % (e_obj.group.name, e_obj.app_foot.foot_name)].append(h.ipaddr)


        # print data
        #
        if e_obj.templates.select_related():
            data[e_obj.get_group_type_display()][e_obj.group.name]["templates"] = []
            for t in e_obj.templates.select_related():
                data[e_obj.get_group_type_display()][e_obj.group.name]["templates"].append(t.name)
        if e_obj.app_variables.select_related():
            for k, v in e_obj.app_variables.select_related().values_list("key", "value"):
                # k = k.split("%s_" % e_obj.environment.environment_name)[1]
                k = re.split("^%s_" % e_obj.environment.environment_name, k)[1]
                if e_obj.get_group_type_display() == 'webapps':
                    if not group_variables_dict.get(e_obj.group.name):
                        group_variables_dict[e_obj.group.name] = {}
                    group_variables_dict[e_obj.group.name][k] = v

                elif e_obj.get_group_type_display() == 'javaapps':
                    if not group_variables_dict.get("%s_%s" % (e_obj.group.name, e_obj.app_foot.foot_name)):
                        group_variables_dict["%s_%s" % (e_obj.group.name, e_obj.app_foot.foot_name)] = {}
                    group_variables_dict["%s_%s" % (e_obj.group.name, e_obj.app_foot.foot_name)][k] = v
                # var_dict[k] = v


        if e_obj.db_variables.select_related():
            for k, v in e_obj.db_variables.select_related().values_list("key", "value"):
                # k = k.split("%s_" % e_obj.environment.environment_name)[1]
                k = re.split("^%s_" % e_obj.environment.environment_name, k)[1]

                if e_obj.get_group_type_display() == 'webapps':
                    if not group_variables_dict.get(e_obj.group.name):
                        group_variables_dict[e_obj.group.name] = {}
                    group_variables_dict[e_obj.group.name][k] = v

                elif e_obj.get_group_type_display() == 'javaapps':
                    if not group_variables_dict.get("%s_%s" % (e_obj.group.name, e_obj.app_foot.foot_name)):
                        group_variables_dict["%s_%s" % (e_obj.group.name, e_obj.app_foot.foot_name)] = {}
                    group_variables_dict["%s_%s" % (e_obj.group.name, e_obj.app_foot.foot_name)][k] = v

                # var_dict[k] = v

    data["inventory"]["variables"] = var_dict
    data["inventory"]["group_variables"] = group_variables_dict


def deco(func):
    def _deco(request):
        api_key = request.META.get("HTTP_API_KEY")
        if api_key == settings.HTTP_API_KEY:
            ret = func(request)
        else:
            ret = {
                "status": False,
                "msg" : "authentication failed !"
            }
            return HttpResponse(json.dumps(ret))
        return ret




    return _deco

@deco
@csrf_exempt
def index(request):
    # print request.X-Bender
    ret = {
        "status" : True,
    }
    if request.method == "GET":
        if  request.GET.get('job_type') and request.GET.get('job_id'):
            job_id = request.GET.get('job_id')
            job_obj = jenkins_models.JenkinsJob.objects.get(id=job_id)
            envid = request.GET.get('envid')
            project = job_obj.project.name
            version = job_obj.project.version.name
            apps = request.GET.get('apps')
            job_type = request.GET.get('job_type')

            JENKINS_CONFIG = {
                'url': job_obj.jenkins_server.api_url,
                'username': job_obj.jenkins_server.username,
                'password': job_obj.jenkins_server.token
            }



            if job_type not in ["md5check","build","getmail","sync2pro"] and  envid == None:
                ret["status"] = False
                ret["msg"] = "envid can't empty !"
                return HttpResponse(json.dumps(ret))
            if job_obj.job_type == 0:
                deploy_type = 'fun'
            elif job_obj.job_type == 1:
                deploy_type = 'uat'
            else:
                deploy_type = None


            data = {
                    'builds_dir': settings.BUILDS_DIR,
                    'deploy_type': deploy_type,
                    'smtp_info': {
                        'server': settings.SMTP_SERVER,
                        'from_addr': settings.FROM_ADDR
                    },
                    'production_mount_point': settings.PRODUCTION_MOUNT_POINT,
                    'last_uat_successful_dir': settings.LAST_UAT_SUCCESSFUL_DIR,
                    'email_list': {
                        'admin': None,
                         'test': None,
                         'develop': None
                    },
                    'version':None,
                    'app_prefix': project,
                    'changelog_dir': settings.CHANGELOG_DIR,
                    'backup_dir': settings.BACKUP_DIR,
                    'web_app_file_path': settings.WEB_PATH,
                    'lastversion': None,
                    'java_app_template_path': settings.JAVA_TEMPLATE_PATH,
                    'last_fun_successful_dir': settings.LAST_FUN_SUCCESSFUL_DIR,
                    'webapps': {
                    },
                    'javaapps': {
                    },
                    'uat_job_name': None,
                    'fun_job_name': None,
                    'mn_prod_deploy_job':None,
                    'sp_prod_deploy_job':None,
                    'jenkins_config': JENKINS_CONFIG,
                    'web_app_template_path': settings.WEB_TEMPLATE_PATH,
                    'java_app_file_path': settings.JAVA_PATH,
                    'base_dir': job_obj.jenkins_server.workspace,
                    'inventory': {
                        "groups":{},
                        "variables":{}
                                  }
                }
            project_obj = models.Project.objects.filter(name=project,version__name=version).first()

            if not project_obj:
                ret = {
                    "status": False,
                    "msg": "not find %s_%s" % (project,version)
                }
                return HttpResponse(json.dumps(ret))
            if job_type == "build" and project_obj.pass_uat_test:
                data["version"] = project_obj.lastversion
            else:
                data["version"] = project_obj.version.name
            data["lastversion"] = project_obj.lastversion
            data["uat_job_name"] = project_obj.uat_job_name
            data["fun_job_name"] = project_obj.fun_job_name
            data["mn_prod_deploy_job"] = project_obj.mn_prod_deploy_job
            data["sp_prod_deploy_job"] = project_obj.sp_prod_deploy_job



            data["email_list"]["admin"] = ",".join([email.email for email in job_obj.project.admin_email.select_related()])
            data["email_list"]["test"] = ",".join([email.email for email in job_obj.project.test_email.select_related()])
            data["email_list"]["develop"] = ",".join([email.email for email in job_obj.project.develop_email.select_related()])


            if job_type in ['md5check','sync2pro']:
                h2e_list = models.HostEnvironmentRelation.objects.filter(project=project_obj).values('group__name',
                                                                                          'group_type').distinct()

                for obj in h2e_list:
                    if obj["group_type"] == 0:
                        data["javaapps"][obj["group__name"]] = {}
                    elif obj["group_type"] == 1:
                        data["webapps"][obj["group__name"]] = {}
                    else:
                        ret = {
                            "status": False,
                            "msg": "hostenvironmentrelation must selected the group type in db!!"
                        }
                        return HttpResponse(json.dumps(ret))

                ret["data"] = data

                return HttpResponse(json.dumps(ret))

            envirment_related_list = models.HostEnvironmentRelation.objects.filter(
                environment__environment_name=envid,
                project=project_obj
            )



            if job_type == "build":
                if apps == "all":
                    ret = {
                        "status": False,
                        "msg": "please input the right app name"
                    }
                    return HttpResponse(json.dumps(ret))


            if project_obj and not envirment_related_list:
                ret["data"] = data

                return HttpResponse(json.dumps(ret))

            if not envirment_related_list:

                ret = {
                    "status": False,
                    "msg": "search result empty . "
                }
                return HttpResponse(json.dumps(ret))

            # envirment_related_obj = envirment_related_list.first()
            envirment_obj = models.Environment.objects.filter(environment_name=envid).first()
            if not envirment_obj:
                ret = {
                    "status": False,
                    "msg": "not find env %s reocder " % envid
                }
                return HttpResponse(json.dumps(ret))


            app_variables_list = envirment_obj.app_variables.select_related().values_list("key","value")
            db_variables_list = envirment_obj.db_variables.select_related().values_list("key","value")
            var_dict = {}
            for k,v in app_variables_list:
                # k = k.split("%s_" % envirment_obj.environment_name)[1]
                k = re.split("^%s_" % envirment_obj.environment_name, k)[1]

                var_dict[k] = v


            for k,v in db_variables_list:
                # k = k.split("%s_" % envirment_obj.environment_name)[1]
                k = re.split("^%s_" % envirment_obj.environment_name, k)[1]

                var_dict[k] = v



            if job_type in ['sync2pro','tomcat']:
                apps = 'all'

            if apps != 'all':
                app_list = apps.split(",")
                for app in app_list:
                    obj = envirment_related_list.filter(group__name=app)
                    if not obj:
                        ret = {
                            "status": False,
                            "msg": "%s not find in db" % app
                        }
                        return HttpResponse(json.dumps(ret))

                envirment_related_list = envirment_related_list.filter(group__name__in=app_list)
                if not envirment_related_list:
                    ret = {
                        "status": False,
                        "msg": "apps not find in db"
                    }

                    return HttpResponse(json.dumps(ret))

            construct_app_info(data,envirment_related_list,var_dict)


            ret["data"] = data


        else:

            ret = {
                "status": False,
                "msg" : "The parameter can't empty !(job_type,job_id) "
            }
    elif request.method == "POST":
        project = request.POST.get('project')
        version = request.POST.get('version')
        job_type = request.POST.get('job_type')
        if not (project and version and job_type ):
            ret["status"] = False
            ret["msg"] = "input the right parameter"
        project_obj = models.Project.objects.filter(name=project,version__name=version).first()
        if not project_obj:
            ret = {
                "status": False,
                "msg" : "not find project %s_%s" % (project,version)
            }
            return HttpResponse(json.dumps(ret))
        with transaction.atomic():
            project_obj.pass_uat_test = True
            project_obj.lastversion = "%s_new" % project_obj.version.name
            project_obj.save()



    return HttpResponse(json.dumps(ret))



@login_required()
def get_load(request):
    t = time.time()*1000

    # ret = {"time":t,[]}
    ret = {
        "status":True
           }
    cmd = """uptime  | awk -F ':' '{print $4}'"""
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    return_code = p.wait()
    if return_code != 0:
        ret["status"] = False
        ret["msg"] = p.stdout.read()
    else:
        msg = p.stdout.read()
        load_list = msg.strip().split(",")
        load1 = float(load_list[0])
        load2 = float(load_list[1])
        load3 = float(load_list[2])
        ret["data"] = [load1,load2,load3,t]

    return HttpResponse(json.dumps(ret))


@login_required()
def get_all_load(request):
    key = "load"
    all_list = r.lrange(key,0,-1)
    ret = {
        "load1":[],
        "load2": [],
        "load3": [],
    }

    for l in all_list:
        l = json.loads(l)
        t= l[3]*1000
        ret["load1"].append([t,l[0]])
        ret["load2"].append([t,l[1]])
        ret["load3"].append([t,l[2]])

    return HttpResponse(json.dumps(ret))


@login_required()
def get_all_memory(request):
    key = "memory"
    all_list = r.lrange(key,0,-1)
    ret = {
        "total":[],
        "used": [],
        "free": [],
    }

    for l in all_list:
        l = json.loads(l)
        t = l[3]*1000
        ret["total"].append([t,l[0]])
        ret["used"].append([t,l[1]])
        ret["free"].append([t,l[2]])

    return HttpResponse(json.dumps(ret))
