# Generated by Django 3.2 on 2023-06-25 19:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0005_remove_customerprofile_profile_is_completed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customerprofile',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='customer_images/'),
        ),
    ]