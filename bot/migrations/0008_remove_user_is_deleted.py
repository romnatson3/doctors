# Generated by Django 4.2.7 on 2023-11-04 12:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0007_user_alter_doctor_district_alter_doctor_first_name_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='is_deleted',
        ),
    ]
