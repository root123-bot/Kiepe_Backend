# Generated by Django 3.2 on 2023-06-08 12:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kibanda', '0010_alter_kibandaprofile_coordinates'),
    ]

    operations = [
        migrations.AddField(
            model_name='kibandaprofile',
            name='profile_is_completed',
            field=models.BooleanField(default=False),
        ),
    ]