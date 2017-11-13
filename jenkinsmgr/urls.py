from django.conf.urls import url,include
from jenkinsmgr import views

urlpatterns = [
    url(r'^jenkinsserver_list/$', views.jenkinsserver_list, name="jenkinsserver_list"),
    url(r'^project_list/([0-9]+)/$', views.project_list, name="project_list"),
    url(r'^job_list/([0-9]+)/([0-9]+)/$', views.job_list, name='job_list'),
    url(r'^job_detail/([0-9]+)/$', views.job_detail, name='job_detail'),
    url(r'^job_builds_list/([0-9]+)/$', views.job_builds_list, name="job_builds_list"),
    url(r'^job_builds_detail/([0-9]+)/$', views.job_builds_detail, name="job_builds_detail"),
    url(r'^batch_build/$', views.batch_build, name="batch_build"),
]
