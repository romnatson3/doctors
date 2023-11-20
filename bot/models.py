from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from bot import texts
from django.contrib import admin


RATING = (
    ('1', _('First place')),
    ('2', _('Second place')),
    ('3', _('Third place')),
    ('4', _('Fourth place')),
    ('5', _('Fifth place')),
)


class BaseModel(models.Model):
    class Meta:
        abstract = True

    created = models.DateTimeField('Created', blank=False, default=timezone.now, editable=False)
    updated = models.DateTimeField('Updated', blank=False, auto_now=True)


class User(BaseModel):
    class Meta:
        verbose_name_plural = _('Users')
        verbose_name = _('User')

    id = models.BigIntegerField(_('ID'), primary_key=True)
    username = models.CharField(_('Username'), max_length=50, blank=True, null=True)
    first_name = models.CharField(_('First name'), max_length=50, blank=True, null=True)
    last_name = models.CharField(_('Last name'), max_length=50, blank=True, null=True)
    phone = models.CharField(_('Phone number'), max_length=15, blank=True, null=True)
    is_bot = models.BooleanField(_('Is bot'), default=False)
    is_deleted = models.BooleanField(_('Is deleted'), default=False)

    def __str__(self):
        return f'{self.id} {self.username}'


class Speciality(BaseModel):
    class Meta:
        indexes = [models.Index(fields=['name'])]
        verbose_name_plural = _('Specialities')
        verbose_name = _('Speciality')

    name = models.CharField(_('Speciality'), max_length=50)

    def __str__(self):
        return self.name


class Phone(BaseModel):
    class Meta:
        verbose_name_plural = _('Phone numbers')
        verbose_name = _('Phone number')

    number = models.CharField(_('Number'), max_length=15, unique=True)

    def __str__(self):
        return self.number


class Address(BaseModel):
    class Meta:
        verbose_name_plural = _('Addresses')
        verbose_name = _('Address')

    name = models.CharField(_('Address'), max_length=100, unique=True)

    def __str__(self):
        return self.name


class District(BaseModel):
    class Meta:
        verbose_name_plural = _('Districts')
        verbose_name = _('District')

    name = models.CharField(_('Name'), max_length=50)

    def __str__(self):
        return self.name


class Position(BaseModel):
    class Meta:
        verbose_name_plural = _('Positions')
        verbose_name = _('Position')

    name = models.CharField(_('Name'), max_length=50)

    def __str__(self):
        return self.name


class Schedule(BaseModel):
    class Meta:
        verbose_name_plural = _('Schedules')
        verbose_name = _('Schedule')

    DAY_OF_WEEK = (
        ('1', _('Monday')),
        ('2', _('Tuesday')),
        ('3', _('Wednesday')),
        ('4', _('Thursday')),
        ('5', _('Friday')),
        ('6', _('Saturday')),
        ('7', _('Sunday'))
    )

    day_of_week = models.CharField(_('Day of week'), max_length=1, choices=DAY_OF_WEEK)
    start_time = models.TimeField(_('Start time'))
    end_time = models.TimeField(_('End time'))
    polyclinic = models.ForeignKey('Polyclinic', on_delete=models.SET_NULL, related_name='schedule', verbose_name=_('Polyclinic'), blank=True, null=True)

    @property
    def day_of_week_name(self):
        return list(filter(lambda x: x[0] == self.day_of_week, self.DAY_OF_WEEK))[0][1]

    def __str__(self):
        if self.polyclinic:
            return f'{self.day_of_week_name} {self.start_time:%H:%M} - {self.end_time:%H:%M}, {self.polyclinic}'
        else:
            return f'{self.day_of_week_name} {self.start_time:%H:%M} - {self.end_time:%H:%M}'


class Polyclinic(BaseModel):
    class Meta:
        indexes = [
            models.Index(fields=['district'])
        ]
        verbose_name_plural = _('Polyclinics')
        verbose_name = _('Polyclinic')

    name = models.CharField(_('Name'), max_length=50)
    address = models.ManyToManyField('Address', verbose_name=_('Address'))
    phone = models.ManyToManyField('Phone', verbose_name=_('Phone number'))
    speciality = models.ManyToManyField('Speciality', verbose_name=_('Speciality'))
    site_url = models.URLField(_('Site URL'), blank=True, null=True)
    image = models.ImageField(_('Photo'), upload_to='images/', default='images/NoneClinic.jpg', blank=True)
    work_time_start = models.TimeField(_('Work time start'), blank=True, null=True)
    work_time_end = models.TimeField(_('Work time end'), blank=True, null=True)
    district = models.ForeignKey('District', on_delete=models.SET_NULL, related_name='polyclinic', verbose_name=_('District'), blank=True, null=True)
    rating = models.CharField(_('Rating'), choices=RATING, blank=True, null=True)

    @admin.display(description=_('Work time'))
    def work_time(self):
        if not (self.work_time_start and self.work_time_end):
            return texts.around_the_clock
        else:
            return f'{self.work_time_start:%H:%M} - {self.work_time_end:%H:%M}'

    def __str__(self):
        if self.address.exists():
            return f'{self.name} - {self.address.all()[0]}'
        else:
            return self.name


class Doctor(BaseModel):
    class Meta:
        indexes = [
            models.Index(fields=['speciality'])
        ]
        verbose_name_plural = _('Doctors')
        verbose_name = _('Doctor')

    first_name = models.CharField(_('First name'), max_length=50)
    last_name = models.CharField(_('Last name'), max_length=50)
    paternal_name = models.CharField(_('Paternal name'), max_length=50)
    phone = models.CharField(_('Phone number'), max_length=15)
    image = models.ImageField(_('Photo'), upload_to='images/', default='images/None.png', blank=True)
    speciality = models.ForeignKey(Speciality, related_name='doctor', on_delete=models.SET_NULL, verbose_name=_('Speciality'), blank=False, null=True)
    position = models.ForeignKey(Position, on_delete=models.SET_NULL, verbose_name=_('Position'), blank=False, null=True)
    polyclinic = models.ManyToManyField(Polyclinic, verbose_name=_('Polyclinic'))
    district = models.ManyToManyField(District, verbose_name=_('District'))
    experience = models.IntegerField(_('Experience'), default=0, validators=[MinValueValidator(1), MaxValueValidator(100)])
    cost = models.FloatField(_('Cost'), default=0, validators=[MinValueValidator(0), MaxValueValidator(100000)])
    schedule = models.ManyToManyField(Schedule, verbose_name=_('Schedule'))
    rating = models.CharField(_('Rating'), choices=RATING, blank=True, null=True)

    @property
    def full_name(self):
        return f'{self.last_name} {self.first_name} {self.paternal_name}'

    def __str__(self):
        return self.full_name


class Share(BaseModel):
    class Meta:
        verbose_name_plural = _('Shares')
        verbose_name = _('Share')

    name = models.CharField(_('Name'), max_length=255, unique=True)
    start_date = models.DateField(_('Start date'))
    end_date = models.DateField(_('End date'))
    description = models.TextField(_('Description'))
    sum = models.FloatField(_('Sum'), default=0, validators=[MinValueValidator(0), MaxValueValidator(100000)], blank=True)
    rating = models.CharField(_('Rating'), choices=RATING, blank=True, null=True)
    image = models.ImageField(_('Photo'), upload_to='images/', default='images/None.png', blank=True)

    def __str__(self):
        return f'{self.name} {self.start_date:%d.%m.%Y}-{self.end_date:%d.%m.%Y}, {self.sum}'
