# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-13 22:30
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('todo_list', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='todoitem',
            name='created_date',
        ),
    ]
