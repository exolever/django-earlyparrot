# Generated by Django 2.2.5 on 2019-09-18 08:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('referral', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='campaign',
            name='users',
        ),
    ]
