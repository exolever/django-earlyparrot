# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2019-08-28 17:54
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Campaign',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('campaign_id', models.CharField(max_length=255)),
                ('status', models.CharField(choices=[('A', 'Active'), ('I', 'Inactive')], default='A', max_length=1)),
                ('name', models.CharField(max_length=255)),
                ('users', models.ManyToManyField(
                    blank=True, null=True,
                    related_name='referrals', to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
        ),
    ]
