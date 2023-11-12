# Generated by Django 4.2.7 on 2023-11-12 16:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0018_schedule_address'),
    ]

    operations = [
        migrations.AlterField(
            model_name='phone',
            name='number',
            field=models.CharField(max_length=15, verbose_name='Number'),
        ),
        migrations.AlterField(
            model_name='schedule',
            name='polyclinic',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bot.polyclinic', verbose_name='Polyclinic'),
        ),
    ]
