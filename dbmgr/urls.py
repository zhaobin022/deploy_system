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
from django.contrib import admin
from cmdb import views
from dbmgr import views

urlpatterns = [
    url(r'^db_list', views.index,name="db_list"),
    url(r'^db_detail/([0-9]+)/$', views.detail,name='db_detail'),
    url(r'^svn_update/$', views.svn_update, name='svn_update'),
    url(r'^execute_sql/$', views.execute_sql, name='execute_sql'),
    url(r'^db_log_list/([0-9]+)/$', views.db_log_list, name='db_log_list'),
    url(r'^db_log_detail/$', views.db_log_detail, name='db_log_detail'),

]
