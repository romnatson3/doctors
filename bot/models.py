from django.db import models
from django.utils import timezone


class BaseModel(models.Model):
    class Meta:
        abstract = True

    created = models.DateTimeField('Created', blank=False, default=timezone.now, editable=False)
    updated = models.DateTimeField('Updated', blank=False, auto_now=True)


class Doctor(BaseModel):
    class Meta:
        verbose_name_plural = 'Doctors'
        verbose_name = 'Doctor'

    first_name = models.CharField(max_length=50, verbose_name='First name')
    last_name = models.CharField(max_length=50, verbose_name='Last name')
    paternal_name = models.CharField(max_length=50, verbose_name='Paternal name')
    phone = models.CharField(max_length=15, verbose_name='Phone number')
    image = models.ImageField(upload_to='images/', default='images/None.png', verbose_name='Photo', blank=True)
    speciality = models.ForeignKey('Speciality', on_delete=models.CASCADE, verbose_name='Speciality')
    position = models.ForeignKey('Position', on_delete=models.CASCADE, verbose_name='Position')
    polyclinic = models.ManyToManyField('Polyclinic', verbose_name='Polyclinic')
    district = models.ManyToManyField('District', verbose_name='District')
    experience = models.IntegerField(verbose_name='Experience')
    cost = models.FloatField(verbose_name='Cost')
    schedule = models.ManyToManyField('Schedule', verbose_name='Schedule')

    def __str__(self):
        return f'{self.last_name} {self.first_name} {self.paternal_name}'


class Speciality(BaseModel):
    class Meta:
        verbose_name_plural = 'Specialities'
        verbose_name = 'Speciality'

    name = models.CharField(max_length=50, verbose_name='Speciality')

    def __str__(self):
        return self.name


class Polyclinic(BaseModel):
    class Meta:
        verbose_name_plural = 'Polyclinics'
        verbose_name = 'Polyclinic'

    name = models.CharField(max_length=50, verbose_name='Name')
    address = models.CharField(max_length=100, verbose_name='Address')

    def __str__(self):
        return self.name


class District(BaseModel):
    class Meta:
        verbose_name_plural = 'Districts'
        verbose_name = 'District'

    name = models.CharField(max_length=50, verbose_name='Name')

    def __str__(self):
        return self.name


class Position(BaseModel):
    class Meta:
        verbose_name_plural = 'Positions'
        verbose_name = 'Position'

    name = models.CharField(max_length=50, verbose_name='Name')

    def __str__(self):
        return self.name


class Schedule(BaseModel):
    class Meta:
        verbose_name_plural = 'Schedules'
        verbose_name = 'Schedule'

    DAY_OF_WEEK = (
        ('1', 'Monday'),
        ('2', 'Tuesday'),
        ('3', 'Wednesday'),
        ('4', 'Thursday'),
        ('5', 'Friday'),
        ('6', 'Saturday'),
        ('7', 'Sunday')
    )

    day_of_week = models.CharField(max_length=1, choices=DAY_OF_WEEK, verbose_name='Day of week')
    start_time = models.TimeField(verbose_name='Start time')
    end_time = models.TimeField(verbose_name='End time')
    polyclinic = models.ForeignKey('Polyclinic', on_delete=models.CASCADE, verbose_name='Polyclinic')

    @property
    def day_of_week_name(self):
        return list(filter(lambda x: x[0] == self.day_of_week, self.DAY_OF_WEEK))[0][1]

    def __str__(self):
        return f'{self.day_of_week_name} {self.start_time} - {self.end_time}, {self.polyclinic.name}'
