# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-10-10 16:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userscore',
            name='total_score',
            field=models.IntegerField(default=40),
        ),
    ]
