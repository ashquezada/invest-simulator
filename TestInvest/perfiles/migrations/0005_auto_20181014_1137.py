# Generated by Django 2.1.2 on 2018-10-14 14:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('perfiles', '0004_auto_20181014_1131'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='avatar',
            field=models.ImageField(blank=True, default='perfiles/default.jpg', upload_to='perfiles/'),
        ),
    ]
