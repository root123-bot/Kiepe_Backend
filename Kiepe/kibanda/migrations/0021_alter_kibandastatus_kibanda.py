# Generated by Django 3.2 on 2023-06-16 09:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('kibanda', '0020_alter_defaultmenu_kibanda'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kibandastatus',
            name='kibanda',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='kibandastatus', to='kibanda.kibandaprofile'),
        ),
    ]