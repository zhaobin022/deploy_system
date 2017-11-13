#_*_coding:utf-8_*_
from __future__ import absolute_import
from celery import task
from celery import shared_task
from certmgr import models
from datetime import datetime
from django.core.mail import send_mail as django_sendmail
from django.contrib.auth.models import Group
import traceback


# from celery.task import tasks
# from celery.task import Task
#
# @task()
# # @shared_task
# def add(x, y):
#     print "%d + %d = %d" % (x, y, x + y)
#     print models.Certificate.objects.all()
#     return x + y
#

# class AddClass(Task):
#    def run(x,y):
#        print "%d + %d = %d"%(x,y,x+y)
#        return x+y
# tasks.register(AddClass)

# @shared_task
# def mul(x, y):
#     print "%d * %d = %d" % (x, y, x * y)
#     return x * y
#
#
# @shared_task
# def sub(x, y):
#     print "%d - %d = %d" % (x, y, x - y)
#     return x - y

def send_mail(c_obj_list):
    subject = r'证书即将到期列表'

    #  user_email_list = Group.objects.get(name='admin').user_set.select_related().values("email")
    #  email_list = []
    #  for u in user_email_list:
    #      email_list.append(u["email"])
    email_list = ["ITappdatamanagement@tjpme.com", ]
    # email_list = ["zhaobin@tjpme.com",]

    msg = ""
    for c_obj in c_obj_list:
        msg += r"证书(%s)即将到期, 请及时处理!  </br></br>到期时间为: %s </br></br>" % (c_obj, c_obj.cexpired_date.strftime("%Y-%m-%d"))
    #
    django_sendmail(subject, msg, 'nonprod-monitor@tjpme.com',
                    email_list, fail_silently=False, html_message=msg)
    print 'sendmail .............', c_obj_list



@shared_task
def check_cert_expired_time():
    cert_list = models.Certificate.objects.filter(status=True)
    current_date = datetime.now().date()

    sendmail_obj_list = []
    for c in cert_list:

        notify_date = c.begin_notify_time

        diff_time = notify_date - current_date
        diff_time = diff_time.days
        if diff_time <= 0:
            sendmail_obj_list.append(c)
    try:
        send_mail(sendmail_obj_list)

    except Exception as e:
        traceback.print_exc()
