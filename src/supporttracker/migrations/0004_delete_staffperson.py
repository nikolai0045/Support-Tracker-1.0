# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-19 17:34
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('supporttracker', '0003_auto_20160419_0933'),
    ]

    operations = [
        migrations.DeleteModel(
            name='StaffPerson',
        ),
    ]
