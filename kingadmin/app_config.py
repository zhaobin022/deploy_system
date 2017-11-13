#_*_coding:utf-8_*_

from django import conf
import importlib

for app in conf.settings.INSTALLED_APPS:
    try:
        admin_module = importlib.import_module("%s.myadmin" % app)
    except ImportError:
        pass