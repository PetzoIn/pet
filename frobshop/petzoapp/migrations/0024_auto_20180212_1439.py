# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-02-12 14:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('petzoapp', '0023_foodinvoice_supplementsinvoice'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='vet',
            field=models.CharField(max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='vet_update',
            field=models.DateTimeField(null=True),
        ),
    ]
