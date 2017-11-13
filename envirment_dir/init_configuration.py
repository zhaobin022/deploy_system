import yaml
import os
import sys
basedir = (os.path.sep).join(os.path.abspath(__file__).split(os.path.sep)[:-2])
print basedir
sys.path.append(basedir)
os.environ['DJANGO_SETTINGS_MODULE'] = 'pub_cmdb.settings'
import django

django.setup()
from cmdb.models import *

l = []
with open("147/group_vars_147/all") as f:
    variables_dict = yaml.load(f)
for k , v in variables_dict.items():
    v = DbVariables(key="%s_%s" %("147",k),value=v)
    l.append(v)

print len(l)

DbVariables.objects.bulk_create(l)