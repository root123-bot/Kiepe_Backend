# Generated by Django 3.2 on 2023-06-21 06:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kibanda', '0024_kibandaprofile_anadaiwa'),
    ]

    operations = [
        migrations.AddField(
            model_name='kibandaprofile',
            name='physical_address',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
