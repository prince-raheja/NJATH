# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-10-16 18:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20161016_1846'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='activation',
            name='id',
        ),
        migrations.AlterField(
            model_name='activation',
            name='unique_key',
            field=models.CharField(max_length=35, primary_key=True, serialize=False),
        ),
    ]