# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-06-26 11:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('petzoapp', '0004_auto_20170626_0956'),
    ]

    operations = [
        migrations.AddField(
            model_name='referralcode',
            name='discount_giver',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='referralcode',
            name='discount_taker',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
    ]
