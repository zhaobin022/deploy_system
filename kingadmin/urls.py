"""pub_cmdb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,include
from kingadmin import views as kingadmin_views
from certmgr import views as certmgr_views
from releasemgr import views as releasemgr_views

urlpatterns = [
    url(r'^(cmdb)/(\w+)/$', kingadmin_views.index,name="kingadmin_index"),
    url(r'^(cmdb)/(\w+)/(\d+)/change/$', kingadmin_views.table_change, name="table_change"),
    url(r'^(cmdb)/(\w+)/add/$', kingadmin_views.table_add, name="table_add"),

    url(r'^(certmgr)/(\w+)/$', certmgr_views.certmgr_index, name="certmgr_index"),
    url(r'^(certmgr)/(\w+)/(\d+)/change/$', certmgr_views.certmgr_table_change, name="certmgr_table_change"),
    url(r'^(certmgr)/(\w+)/add/$', certmgr_views.certmgr_table_add, name="certmgr_table_add"),

   url(r'^(releasemgr)/(\w+)/$', releasemgr_views.index, name="releasemgr_index"),
   url(r'^(releasemgr)/(\w+)/(\d+)/change/$', releasemgr_views.table_change, name="releasemgr_table_change"),
   url(r'^(releasemgr)/(\w+)/add/$', releasemgr_views.table_add, name="releasemgr_table_add"),
]
