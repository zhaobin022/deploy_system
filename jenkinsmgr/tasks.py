#_*_coding:utf-8_*_
from __future__ import absolute_import
from celery import task
import svn.remote
from jenkinsmgr import models as jenkinsmgr_model
from jenkinsmgr.jenkins_api import JenkinsApi
from jenkinsmgr import utils
import svn.remote
import traceback


@task()
def auto_build():
    jenkins_job_checklist = jenkinsmgr_model.JenkinsJob.objects.filter(auto_build=True,job_type=2)
    for job_obj in jenkins_job_checklist:
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

            if len(build_info_dict["changeSet"]["revisions"]) == 1:
                svn_info_dict = build_info_dict["changeSet"]["revisions"][0]
                svn_url = svn_info_dict["module"]
                svn_number_in_jenkins = svn_info_dict["revision"]

                l = svn.remote.RemoteClient(svn_url)
                current_svn_info_dict = l.info()
                current_svn_number = current_svn_info_dict["commit_revision"]
                print job_obj.job_name, current_svn_number,svn_number_in_jenkins
                if current_svn_number != svn_number_in_jenkins:
                    variables_dict={}
                    variables_dict["job_id"] = job_obj.id
                    email_str = utils.get_mail_str(job_obj)

                    variables_dict["email_list"] = email_str
                    variables_dict["action_type"] = job_obj.action_type.operation_value

                    print 'trigger to building job %s ' % job_obj.job_name
                    ret = jenkins_handler.just_send_build_request(**variables_dict)
                    print ret
        except Exception as e:
            traceback.print_exc()