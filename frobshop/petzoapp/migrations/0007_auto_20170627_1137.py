# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-06-27 11:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('petzoapp', '0006_auto_20170627_1130'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='user_credit',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=8),
        ),
    ]
