# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-06-14 07:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('petzoblog', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, upload_to=b''),
        ),
    ]
