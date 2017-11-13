# -*- coding: utf-8 -*-

from django.shortcuts import render,HttpResponse
from cmdb import models
import json
import utils
import traceback
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import settings
from django.contrib.auth.decorators import login_required
from usercenter.permissions import check_permission
from django.core.exceptions import ObjectDoesNotExist
from cmdb.myadmin import site



# models.Environment._meta.verbose_name

@login_required()
@check_permission
def index(request):
    # try:
    #     print send_mail('Subject here', 'Here is the message.', 'cuihaoran@tjpme.com',
    #               ['zhaobin@tjpme.com'], fail_silently=False)
    #     print 'send_mail..........................'
    # except Exception as e:
    #     print 'send mail failed ...............'
    db_info_list = models.DbBaseInfo.objects.all()
    enabled_admins = site.enabled_admins

    return render(request,"db_mgr/index.html",locals())


@login_required()
def detail(request,obj_id):
    try:
        db_obj = models.DbBaseInfo.objects.get(pk=obj_id)
    except ObjectDoesNotExist:
        db_obj = None

    svn_list = models.SvnPath.objects.all()
    enabled_admins = site.enabled_admins
    return render(request,"db_mgr/db_detail.html",locals())


@login_required()
def svn_update(request):
    if request.method == "POST":
        svn_id = request.POST.get("svn_id")

        svn_obj = models.SvnPath.objects.get(pk=svn_id)
        ret = utils.svn_checkout(svn_obj,request.user)
        return HttpResponse(json.dumps(ret,ensure_ascii=False))

@login_required()
@check_permission
def execute_sql(request):
    if request.method == "POST":
        ret = {
            "status" : True
        }
        db_id = request.POST.get("db_id")
        svn_obj_id = request.POST.get("svn_name")
        sql_file_list = request.POST.getlist("sql_file_list")



        if not db_id or not sql_file_list or not svn_obj_id:
            ret["status"] = False
            ret["msg"] = "传参错误"
            return HttpResponse(json.dumps(ret))

        try:
            db_obj = models.DbBaseInfo.objects.get(id=db_id)
        except Exception as e:

            ret["status"] = False
            ret["msg"] = "未找到数据库信息"
            return HttpResponse(json.dumps(ret))


        try:
            svn_obj = models.SvnPath.objects.get(id=svn_obj_id)
        except Exception as e:

            ret["status"] = False
            ret["msg"] = "未找到svn信息"
            return HttpResponse(json.dumps(ret))

        execute_sqlplus_handler = utils.ExecuteSqlplus(svn_obj,db_obj,sql_file_list,request.user)
        ret = execute_sqlplus_handler.execute_sql_on_use_sqlplus()
        return HttpResponse(json.dumps(ret))

@login_required()
def db_log_list(request,obj_id ):
    enabled_admins = site.enabled_admins
    db_obj = models.DbBaseInfo.objects.get(pk=obj_id)

    log_list = models.ExecuteSqlLog.objects.filter(db=db_obj).order_by("-id")

    svn_list = models.ExecuteSqlLog.objects.values("svn__id","svn__path").distinct()

    q = request.GET.get("q")
    if q:
        log_list = log_list.filter(sql_file_name__icontains=q)
    else:
        q = ""
    svn_id = request.GET.get("svn_id")
    if svn_id:
        log_list = log_list.filter(svn=svn_id)
    else:
        svn_id=""

    paginator = Paginator(log_list, settings.PER_PAGE)  # Show 25 contacts per page


    page = request.GET.get('page')
    try:
        log_list = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        log_list = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        log_list = paginator.page(paginator.num_pages)
    return render(request,"db_mgr/db_log.html",locals())

@login_required()
def db_log_detail(request):
    if request.method == "POST":
        ret = {
            "status" : True
        }
        log_id = request.POST.get("log_id")
        try:
            log_obj = models.ExecuteSqlLog.objects.get(id=log_id)
            ret["data"] = log_obj.contents
        except Exception as e:
            ret["status"] = False
            ret["msg"] = traceback.format_exc()


        return HttpResponse(json.dumps(ret))