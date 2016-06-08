# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-20 16:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supporttracker', '0007_supportrelationship_date_entered'),
    ]

    operations = [
        migrations.AlterField(
            model_name='call',
            name='time',
            field=models.DateTimeField(blank=True),
        ),
        migrations.AlterField(
            model_name='letter',
            name='note',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='meeting',
            name='location',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='meeting',
            name='note',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='city',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='person',
            name='email_address',
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.AlterField(
            model_name='person',
            name='phone_number',
            field=models.BigIntegerField(blank=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='spouse_name',
            field=models.CharField(blank=True, max_length=120),
        ),
        migrations.AlterField(
            model_name='person',
            name='state',
            field=models.CharField(blank=True, choices=[('AL', 'Alabama'), ('AK', 'Alaska'), ('AZ', 'Arizona'), ('AR', 'Arkansas'), ('CA', 'California'), ('CO', 'Colorado'), ('CT', 'Connecticut'), ('DE', 'Delaware'), ('FL', 'Florida'), ('GA', 'Georgia'), ('HI', 'Hawaii'), ('ID', 'Idaho'), ('IL', 'Illinois'), ('IN', 'Indiana'), ('IA', 'Iowa'), ('KS', 'Kansas'), ('KY', 'Kentucky'), ('LA', 'Louisiana'), ('ME', 'Maine'), ('MD', 'Maryland'), ('MA', 'Massachussets'), ('MI', 'Michigan'), ('MN', 'Minnesota'), ('MS', 'Mississippi'), ('MO', 'Missouri'), ('MT', 'Montana'), ('NE', 'Nebraska'), ('NV', 'Nevada'), ('NH', 'New Hampshire'), ('NJ', 'New Jersey'), ('NM', 'New Mexico'), ('NY', 'New York'), ('NC', 'North Carolina'), ('ND', 'North Dakota'), ('OH', 'Ohio'), ('OK', 'Oklahoma'), ('OR', 'Oregon'), ('PA', 'Pennsylvania'), ('RI', 'Rhode Island'), ('SC', 'South Carolina'), ('SD', 'South Dakota'), ('TN', 'Tennessee'), ('TX', 'Texas'), ('UT', 'Utah'), ('VT', 'Vermont'), ('WA', 'Washington'), ('WV', 'West Virginia'), ('WI', 'Wisconsin'), ('WY', 'Wyoming')], max_length=2),
        ),
        migrations.AlterField(
            model_name='person',
            name='street_address',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='person',
            name='title',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AlterField(
            model_name='person',
            name='zip',
            field=models.IntegerField(blank=True),
        ),
        migrations.AlterField(
            model_name='thankyou',
            name='note',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='spouse_name',
            field=models.CharField(blank=True, max_length=120),
        ),
        migrations.AlterField(
            model_name='voicemail',
            name='note',
            field=models.TextField(blank=True),
        ),
    ]