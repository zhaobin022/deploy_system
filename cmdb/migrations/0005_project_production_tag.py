# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-15 00:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cmdb', '0004_auto_20170814_1318'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='production_tag',
            field=models.BooleanField(default=False),
        ),
    ]
