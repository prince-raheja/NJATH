# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-10-11 11:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0011_auto_20161011_1115'),
    ]

    operations = [
        migrations.AddField(
            model_name='userlevelprogress',
            name='total_opened_questions',
            field=models.IntegerField(default=0),
        ),
    ]