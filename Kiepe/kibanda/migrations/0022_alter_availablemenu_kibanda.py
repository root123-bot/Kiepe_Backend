# Generated by Django 3.2 on 2023-06-19 08:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('kibanda', '0021_alter_kibandastatus_kibanda'),
    ]

    operations = [
        migrations.AlterField(
            model_name='availablemenu',
            name='kibanda',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='menuyaleo', to='kibanda.kibandaprofile'),
        ),
    ]
