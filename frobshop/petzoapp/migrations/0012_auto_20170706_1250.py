# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-07-06 12:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('petzoapp', '0011_auto_20170705_1257'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Totals',
        ),
        migrations.AlterField(
            model_name='referralcode',
            name='code',
            field=models.CharField(max_length=128, unique=True),
        ),
    ]
