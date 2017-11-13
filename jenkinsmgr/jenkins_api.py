
import jenkins
import time
import datetime
import traceback
import svn.remote


class JenkinsApi(object):
    def __init__(self,url,user_name,token,job_obj):
        self.url = url
        self.user_name = user_name
        self.token = token
        self.job_obj = job_obj
        self.job_name = job_obj.job_name
        # print self.url, self.user_name, self.token
        self.server = jenkins.Jenkins(self.url, username=self.user_name, password=self.token)
        # print self.server.get_version()



    def build_job(self,**kwargs):
        try:
            ret = {
                "status":True
            }
            next_build_number = self.server.get_job_info(self.job_name)["nextBuildNumber"]
            self.server.build_job(self.job_name,parameters=kwargs)
            # data = self.server.build_job_url(self.job_name,parameters=kwargs)
            #
            # print data,111111


            if self.server.get_job_info(self.job_name)['lastBuild']:
                build_number = self.server.get_job_info(self.job_name)['lastBuild']['number']
            else:
                build_number = None


            while True:
                print next_build_number,build_number
                if next_build_number == build_number:
                    break
                # if next_build_number == 1:
                #     if self.server.get_job_info(self.job_name)['lastBuild']:
                #         build_number = self.server.get_job_info(self.job_name)['lastBuild']['number']
                #     else:
                #         build_number =

                if self.server.get_job_info(self.job_name)['lastBuild']:
                    build_number = self.server.get_job_info(self.job_name)['lastBuild']['number']
                time.sleep(1)

            # print self.server.get_job_info(self.job_name),11111
            build_info_dict = self.server.get_build_info(self.job_name, build_number)
            while True:
                if build_info_dict["result"] != None:
                    break

                time.sleep(1)
                build_info_dict = self.server.get_build_info(self.job_name, build_number)
            # build_info_dict = self.server.get_build_info(self.job_name, build_number)
            console_info = self.server.get_build_console_output(self.job_name, build_number)
            # running_list = self.server.get_running_builds()
            #
            # flag = False
            # while not flag:
            #     time.sleep(2)
            #
            #     for r in running_list:
            #         if self.job_name == r["name"] and next_build_number == r["number"]:
            #             break
            #     else:
            #         flag = True
            #
            # print self.job_name,next_build_number,111111
            # time.sleep(10)
            # # self.server = jenkins.Jenkins(self.url, username=self.user_name, password=self.token)
            # build_info_dict = self.server.get_build_info(self.job_name,next_build_number)
            # console_info = self.server.get_build_console_output(self.job_name,next_build_number)

            ret["msg"] = console_info
            ret["build_number"] = build_number

            if  build_info_dict["result"] != "SUCCESS":
                ret["status"] = False
                ret["error_type"] = "jenkins_api_error"

            '''
            [{'url': u'http://10.12.208.89:8080/job/a/14/', 'node': '(master)', 'executor': 1, 'name': u'a', 'number': 14}]
            '''
            # build_info = self.server.get_job_info(self.job_name)
            # print build_info
            #
            # print self.server.get_build_console_output(self.job_name,next_build_number),2222


            return ret
        except Exception as e:
            msg = traceback.format_exc()
            ret["status"] = False
            ret["error_type"] = "jenkins_api_error"
            ret["msg"] = msg
            return ret

    def get_job_builds_number_list(self):
        try:
            job_info_dict = self.server.get_job_info(self.job_name)

            job_buids_list = job_info_dict["builds"]

            for build_info_dict in job_buids_list:
                build_status_dict  = self.server.get_build_info(self.job_name,build_info_dict["number"])
                build_info_dict["result"] = build_status_dict["result"]

                d = datetime.datetime.fromtimestamp(build_status_dict["timestamp"]/1000)
                str1 = d.strftime("%Y-%m-%d %H:%M:%S")
                build_info_dict["timestamp"] = str1

            return job_buids_list
        except Exception as e:
            return []


    def get_console_output(self,build_number):

        console_info = self.server.get_build_console_output(self.job_name, int(build_number))

        return  console_info

    def get_job_info(self):
        job_info_dict = self.server.get_job_info(self.job_name)
        return job_info_dict


    def get_build_info(self,build_number):
        try:
            build_info_dict = self.server.get_build_info(self.job_name, build_number)
            return build_info_dict
        except Exception as e:
            return None
    def just_send_build_request(self,**kwargs):
        try:
            ret={
                "status" : True
            }
            self.server.build_job(self.job_name,parameters=kwargs)


            return ret
        except Exception as e:
            msg = traceback.format_exc()
            ret["status"] = False
            ret["error_type"] = "jenkins_api_error"
            ret["msg"] = msg
            return ret

    def get_svn_url(self):
        try:
            build_number = self.server.get_job_info(self.job_name)['lastBuild']['number']
            build_info_dict = self.server.get_build_info(self.job_name, build_number)
            if len(build_info_dict["changeSet"]["revisions"]) == 1:
                svn_info_dict = build_info_dict["changeSet"]["revisions"][0]

                # # get svn server last commit number
                current_svn_number = ""
                try:
                    svn_url = svn_info_dict["module"]
                    last_build_sn = svn_info_dict["revision"]
                    l = svn.remote.RemoteClient(svn_url)
                    current_svn_info_dict = l.info()
                    current_svn_number = current_svn_info_dict["commit_revision"]
                except Exception as e:
                    traceback.print_exc()
            else:
                svn_url = "","",""

            return svn_url,current_svn_number,last_build_sn
        except Exception as e:
            return "","",""


if __name__ == '__main__':
    # jenkins_handler = JenkinsApi("http://10.12.208.89:8080", "admin", "e0f51bfdafb9bcccec1ab1e59aac0e41","a")
    # jenkins_handler.build_job({})

    # server = jenkins.Jenkins("http://10.12.208.89:8080", username="admin", password="6879e44b3dce17ae2df63d898a6ec318")
    server = jenkins.Jenkins("http://10.12.10.61:8081/jenkins/", username="admin", password="c91e3c81b130bc41d4f1d9e1e882b57f")
    # print server.get_job_info("BUILD-exchange")
    build_info_dict = server.get_build_info("BUILD-moneyweb",28)
    print build_info_dict,1111
    # build_info_dict = server.get_build_info("BUILD-qtsystem",37)
    # print
    # svn_info_dict = build_info_dict["changeSet"]["revisions"][0]
    # svn_url = svn_info_dict["module"]
    # print svn_url
    # svn_number_in_jenkins = svn_info_dict["module"]
    #
    # import svn.remote
    # #
    # l = svn.remote.RemoteClient('https://10.12.10.65/svn/swap/trunk/core-parent/bargainingrmi')
    # print l.info()
    # print server.get_job_info("BUILD-core-parent")
    # print build_info_dict,11111111111111111
    # print server.get_job_info("ab")['lastBuild']['number']
    # print server.get_job_info("ab")


