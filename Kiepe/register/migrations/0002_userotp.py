# Generated by Django 3.2 on 2023-06-02 12:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('register', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserOTP',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deviceID', models.CharField(max_length=255)),
                ('otp', models.CharField(max_length=6)),
            ],
        ),
    ]
