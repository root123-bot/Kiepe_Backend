# Generated by Django 3.2 on 2023-07-14 08:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0027_alter_kibandapayments_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='kibandapayments',
            name='type',
        ),
    ]
