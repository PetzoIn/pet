# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-06-29 06:33
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('petzoapp', '0007_auto_20170627_1137'),
    ]

    operations = [
        migrations.AlterField(
            model_name='referralcode',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
