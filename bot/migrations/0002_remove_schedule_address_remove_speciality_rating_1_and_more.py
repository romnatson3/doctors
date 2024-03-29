# Generated by Django 4.2.7 on 2023-11-13 19:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='schedule',
            name='address',
        ),
        migrations.RemoveField(
            model_name='speciality',
            name='rating_1',
        ),
        migrations.RemoveField(
            model_name='speciality',
            name='rating_2',
        ),
        migrations.RemoveField(
            model_name='speciality',
            name='rating_3',
        ),
        migrations.RemoveField(
            model_name='speciality',
            name='rating_4',
        ),
        migrations.RemoveField(
            model_name='speciality',
            name='rating_5',
        ),
        migrations.AddField(
            model_name='doctor',
            name='rating',
            field=models.CharField(blank=True, choices=[('1', 'First place'), ('2', 'Second place'), ('3', 'Third place'), ('4', 'Fourth place'), ('5', 'Fifth place')], null=True, verbose_name='Rating'),
        ),
        migrations.AddField(
            model_name='polyclinic',
            name='rating',
            field=models.CharField(blank=True, choices=[('1', 'First place'), ('2', 'Second place'), ('3', 'Third place'), ('4', 'Fourth place'), ('5', 'Fifth place')], null=True, verbose_name='Rating'),
        ),
        migrations.AlterField(
            model_name='doctor',
            name='district',
            field=models.ManyToManyField(to='bot.district', verbose_name='District'),
        ),
        migrations.AlterField(
            model_name='doctor',
            name='polyclinic',
            field=models.ManyToManyField(to='bot.polyclinic', verbose_name='Polyclinic'),
        ),
        migrations.AlterField(
            model_name='doctor',
            name='schedule',
            field=models.ManyToManyField(to='bot.schedule', verbose_name='Schedule'),
        ),
        migrations.AlterField(
            model_name='polyclinic',
            name='address',
            field=models.ManyToManyField(to='bot.address', verbose_name='Address'),
        ),
        migrations.AlterField(
            model_name='polyclinic',
            name='phone',
            field=models.ManyToManyField(to='bot.phone', verbose_name='Phone number'),
        ),
        migrations.AlterField(
            model_name='polyclinic',
            name='speciality',
            field=models.ManyToManyField(to='bot.speciality', verbose_name='Speciality'),
        ),
    ]
