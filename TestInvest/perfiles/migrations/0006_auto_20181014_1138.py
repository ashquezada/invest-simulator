# Generated by Django 2.1.2 on 2018-10-14 14:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('perfiles', '0005_auto_20181014_1137'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='avatar',
            field=models.ImageField(blank=True, upload_to='perfiles/'),
        ),
    ]
