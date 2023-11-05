# Generated by Django 4.2.7 on 2023-11-04 17:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0009_alter_user_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='first_name',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='First name'),
        ),
        migrations.AlterField(
            model_name='user',
            name='last_name',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Last name'),
        ),
        migrations.AlterField(
            model_name='user',
            name='phone',
            field=models.CharField(blank=True, max_length=15, null=True, verbose_name='Phone number'),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Username'),
        ),
    ]
