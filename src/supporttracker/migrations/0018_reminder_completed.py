# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-02 13:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supporttracker', '0017_note'),
    ]

    operations = [
        migrations.AddField(
            model_name='reminder',
            name='completed',
            field=models.BooleanField(default=False),
        ),
    ]