from django.shortcuts import render,HttpResponse,redirect,reverse
from kingadmin import app_config
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from cmdb.myadmin import site
from django.db.models import Q
from kingadmin import forms
import json
from django.contrib.auth.decorators import login_required
from usercenter.permissions import check_permission


# Create your views here.
# print site.enabled_admins, 11111
@login_required()
def get_list_filter_queryset(request,admin_obj,queryset):
    filter_dict = {}

    for k in admin_obj.list_filters:
        temp = request.GET.get(k)
        if temp:
            filter_dict[k] = temp
    admin_obj.filter_dict = filter_dict
    queryset = queryset.filter(**filter_dict)

    return queryset

@login_required()
def get_orderby(request,queryset):
    orderby_key = request.GET.get("_o")
    if orderby_key:
        qs = queryset.order_by(orderby_key)
    else:
        qs = queryset.order_by("-id")
    return qs

@login_required()
def get_search(request,admin_obj,queryset):

    search_value = request.GET.get("_q")
    if search_value:
        search_value = search_value.strip()
        q_obj = Q()
        q_obj.connector = "OR"
        for search_key in admin_obj.search_fields:
            q_obj.children.append(("%s__icontains" % search_key,search_value))
        queryset = queryset.filter(q_obj)
    return queryset

@login_required()
@check_permission
def index(request,app,model_name):
    enabled_admins = site.enabled_admins
    admin_obj = enabled_admins[app][model_name]
    queryset = admin_obj.model.objects.all()
    queryset = get_list_filter_queryset(request,admin_obj,queryset)

    queryset = get_orderby(request,queryset)
    queryset = get_search(request,admin_obj,queryset)
    paginator = Paginator(queryset, admin_obj.list_per_page)  # Show 25 contacts per page
    if request.method == "POST":
        action_type = request.POST.get("action_type")

        ids = request.POST.get("ids")

        if action_type == "delete_selected":
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
    return render(request,"deploy/index.html",locals())

@login_required()
@check_permission
def table_change(request,app,model_name,obj_id):
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


    return render(request,"deploy/table_change.html",locals())

@login_required()
@check_permission
def table_add(request,app,model_name):
    enabled_admins = site.enabled_admins
    admin_obj = enabled_admins[app][model_name]
    form_class = forms.create_model_form(request,admin_obj)
    if request.method == "GET":
        form_obj = form_class()
    elif request.method == "POST":
        form_obj = form_class(data=request.POST)
        if form_obj.is_valid():
            form_obj.save()
            return  redirect("/kingadmin/%s/%s" % (app,model_name))
    return render(request,"deploy/table_add.html",locals())















