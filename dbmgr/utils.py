import os
import settings
import subprocess
import shutil
from django.conf import settings as django_settings
import traceback
from cmdb import models
import re




def svn_checkout(svn_obj,user_obj):
    ret = {
        "status" : True
    }
    checkout_path = os.path.join(django_settings.BASE_DIR,settings.WORKSPACE,"%s_%s" % (user_obj.username , str(svn_obj.id)))
    cmd = "export LANG=%s;svn co %s %s" % (svn_obj.get_svn_charset_display() ,svn_obj.path,checkout_path)

    print cmd
    try:
        if os.path.exists(checkout_path):
            shutil.rmtree(checkout_path)
        os.makedirs(checkout_path)
        p = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE,shell=True)
        return_code = p.wait()
        if return_code != 0:
            ret["status"] = False
            if svn_obj.svn_charset == 2:
                ret["msg"] = "%s\n%s" % (p.stdout.read().decode("utf8"), p.stderr.read().decode("utf8"))

            elif svn_obj.svn_charset == 1:
                ret["msg"] = "%s\n%s" % (p.stdout.read().decode("gb2312"), p.stderr.read().decode("utf8"))
        else:
            sql_file_list = []
            for file_name in os.listdir(checkout_path):

                if file_name.endswith("sql"):
                    if svn_obj.svn_charset == 2:
                        sql_file_list.append(file_name.decode("utf8").encode("utf8"))
                    elif svn_obj.svn_charset == 1:
                        sql_file_list.append(file_name.decode("gb2312").encode("utf8"))

            sql_file_list.sort()
            sql_file_list.reverse()
            ret["data"] = sql_file_list

    except Exception as e:
        ret["status"] = False
        ret["msg"] = traceback.format_exc()

    finally:
        return ret



class ExecuteSqlplus(object):
    def __init__(self,svn_obj,db_obj,sql_file_list,user_obj):
        self.svn_obj = svn_obj
        self.db_obj = db_obj
        self.sql_file_list = sql_file_list
        self.user_obj = user_obj


    def validate_result(self,content):
        for i in settings.ERROR_STRING:
            p = re.compile(i, re.M)
            m = p.findall(content)
            if m:
                return False
        else:
            return True

    def execute_sql_on_use_sqlplus(self):

        checkout_path = os.path.join(django_settings.BASE_DIR,settings.WORKSPACE,"%s_%s" % (self.user_obj.username , str(self.svn_obj.id)))

        sql_file_list = sorted(self.sql_file_list)

        ret = {
            "status": True,
            "msg": ""
        }
        for sql_file in sql_file_list:



            sql_file_path = os.path.join(checkout_path,sql_file)
            # cmd = "sqlplus %s/%s@%s:%s/%s @%s" % (
            #     db_obj.db_user,
            #     db_obj.db_password,
            #     db_obj.host.ipaddr,
            #     db_obj.port,
            #     db_obj.sid,
            #     sql_file_path
            # )
            cmd = '''
export NLS_LANG="%s";sqlplus %s/%s@%s:%s/%s<<EOF
@%s
commit
exit
EOF
            ''' % (
                self.db_obj.get_db_charset_display(),
                self.db_obj.db_user.value,
                self.db_obj.db_password.value,
                self.db_obj.host.value,
                self.db_obj.port.value,
                self.db_obj.sid.value,
                sql_file_path
            )
            print cmd
            ret["msg"]+="%s\n" % cmd
            print type(self.user_obj)
            execute_log_obj = models.ExecuteSqlLog(db=self.db_obj,svn=self.svn_obj,sql_file_name=sql_file,user=self.user_obj)
            try:
                p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                return_code = p.wait()
                if return_code != 0:

                    if self.svn_obj.svn_charset == 2:
                        temp = '%s\n%s' % (p.stdout.read().decode("utf8"),p.stderr.read().decode("utf8"))

                    elif self.svn_obj.svn_charset == 1:

                        temp = '%s\n%s' % (p.stdout.read().decode("gb2312"),p.stderr.read().decode("utf8"))

                    execute_log_obj.status = 1
                    execute_log_obj.contents = cmd+"\n"+temp
                    ret["status"] = False
                    ret["msg"] += temp
                    break

                else:

                    if self.svn_obj.svn_charset == 2:
                        temp = p.stdout.read().decode("utf8")
                    elif self.svn_obj.svn_charset == 1:

                        temp = p.stdout.read().decode("gb2312")
                    ret["msg"] += temp
                    execute_log_obj.contents = cmd + "\n" + temp
                    if self.validate_result(temp):
                        execute_log_obj.status = 0
                    else:
                        execute_log_obj.status = 1
                        ret["status"] = False
                        break

            except Exception as e:
                ret["status"] = False
                temp = traceback.format_exc()
                ret["msg"] += temp
                execute_log_obj.status = 1
                execute_log_obj.contents = cmd+"\n"+temp
            finally:
                execute_log_obj.save()
        return ret