#_*_coding:utf-8_*_
from __future__ import absolute_import
from celery import task
from celery import shared_task
from certmgr import models
from datetime import datetime
from django.core.mail import send_mail as django_sendmail
from django.contrib.auth.models import Group
import redis
import subprocess
import json
import time
from pub_cmdb import settings
r = redis.Redis(connection_pool=settings.pool)

@task()
def update_load():
    key = "load"
    cmd = """uptime  | awk -F ':' '{print $5}'"""
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    msg = p.stdout.read()
    load_list = msg.strip().split(",")
    load1 = float(load_list[0])
    load2 = float(load_list[1])
    load3 = float(load_list[2])
    r.rpush(key,json.dumps([load1,load2,load3,time.time()]))

    # print r.lrange(key,1,-1)

    if r.llen(key) > 600:
        r.lpop(key)


@task()
def update_memory():
    key = "memory"
    cmd = """free -m | grep Mem"""
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    msg = p.stdout.read()
    ret_list = msg.strip().split()
    total = float(ret_list[1])
    used = float(ret_list[2])
    free = float(ret_list[3])
    print total,used,free


    r.rpush(key, json.dumps([total, used, free, time.time()]))
    #
    # print r.lrange(key, 1, -1)
    #
    if r.llen(key) > 600:
        r.lpop(key)


@task()
def a():
    pass