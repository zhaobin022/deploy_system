from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from usercenter.permissions import check_permission
from cmdb.myadmin import site
from kingadmin.views import get_list_filter_queryset
from kingadmin.views import get_orderby
from kingadmin.views import get_search
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json
from kingadmin import forms
from django.shortcuts import render,HttpResponse,redirect,reverse

# Create your views here.


@login_required()
@check_permission
def certmgr_index(request,app,model_name):
    enabled_admins = site.enabled_admins
    admin_obj = enabled_admins[app][model_name]
    queryset = admin_obj.model.objects.all()
    queryset = get_list_filter_queryset(request,admin_obj,queryset)

    queryset = get_orderby(request,queryset)
    queryset = get_search(request,admin_obj,queryset)
    paginator = Paginator(queryset, admin_obj.list_per_page)  # Show 25 contacts per page
    if request.method == "POST":
        action_type = request.POST.get("action_type")


        if action_type == "delete_selected":
            ids = request.POST.get("ids")

            ids = json.loads(ids)

            admin_obj.model.objects.filter(id__in=ids).delete()


    page = request.GET.get('page')
    try:
        objs = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        objs = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        objs = paginator.page(paginator.num_pages)

    admin_obj.queryset = objs
    return render(request,"certmgr/index.html",locals())



@login_required()
@check_permission
def certmgr_table_change(request,app,model_name,obj_id):
    enabled_admins = site.enabled_admins
    admin_obj = enabled_admins[app][model_name]

    model_obj = admin_obj.model.objects.get(id=obj_id)

    # form_format = "%sFrom" % admin_obj.model._meta.model_name.capitalize()
    form_class = forms.create_model_form(request,admin_obj)
    if request.method == "GET":
        form_obj = form_class(instance=model_obj)
    elif request.method == "POST":
        form_obj = form_class(instance=model_obj,data=request.POST)
        if form_obj.is_valid():
            form_obj.save()
            success_msg = True


    return render(request,"certmgr/table_change.html",locals())

@login_required()
@check_permission
def certmgr_table_add(request,app,model_name):
    enabled_admins = site.enabled_admins
    admin_obj = enabled_admins[app][model_name]
    form_class = forms.create_model_form(request,admin_obj)
    if request.method == "GET":
        form_obj = form_class()
    elif request.method == "POST":
        print request.POST,"cert add post....."
        form_obj = form_class(data=request.POST)
        if form_obj.is_valid():
            form_obj.save()
            return  redirect("/kingadmin/certmgr/%s" % (model_name))
    return render(request,"certmgr/table_add.html",locals())