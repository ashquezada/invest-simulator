# Generated by Django 2.1.2 on 2018-10-19 23:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('perfiles', '0007_auto_20181014_1144'),
    ]

    operations = [
        migrations.CreateModel(
            name='Asset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('cant', models.PositiveIntegerField(blank=None)),
                ('old_unit_value', models.PositiveIntegerField(blank=None)),
                ('date', models.DateTimeField(verbose_name='date published')),
            ],
        ),
        migrations.RemoveField(
            model_name='perfil',
            name='usuario',
        ),
        migrations.AddField(
            model_name='customuser',
            name='virtual_money',
            field=models.PositiveIntegerField(blank=None, default=1000),
        ),
        migrations.DeleteModel(
            name='Perfil',
        ),
        migrations.AddField(
            model_name='asset',
            name='user',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
