# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-10-19 07:19
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('releasemgr', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='releaseplan',
            name='create_time',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='\u521b\u5efa\u65f6\u95f4'),
            preserve_default=False,
        ),
    ]