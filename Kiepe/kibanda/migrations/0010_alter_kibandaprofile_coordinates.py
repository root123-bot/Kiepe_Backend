# Generated by Django 3.2 on 2023-06-08 12:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kibanda', '0009_alter_kibandastatus_opened'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kibandaprofile',
            name='coordinates',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]