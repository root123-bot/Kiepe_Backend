# Generated by Django 3.2 on 2023-06-04 06:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0002_customerprofile_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='customerprofile',
            name='usergroup',
            field=models.CharField(default='Customer', max_length=50),
        ),
    ]
