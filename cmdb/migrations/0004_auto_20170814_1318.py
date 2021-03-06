# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-14 05:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cmdb', '0003_auto_20170806_0917'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='mn_prod_deploy_job',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='sp_prod_deploy_job',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='tomcat',
            name='jvm_size',
            field=models.PositiveIntegerField(default=2048),
        ),
    ]
