# Generated by Django 3.2 on 2023-06-08 12:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0004_customerprofile_profile_is_completed'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customerprofile',
            name='profile_is_completed',
        ),
    ]
