# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-06 16:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supporttracker', '0020_auto_20160506_1123'),
    ]

    operations = [
        migrations.AlterField(
            model_name='call',
            name='date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='call',
            name='time',
            field=models.TimeField(blank=True, null=True),
        ),
    ]
