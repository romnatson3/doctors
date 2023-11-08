from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator


class BaseModel(models.Model):
    class Meta:
        abstract = True

    created = models.DateTimeField('Created', blank=False, default=timezone.now, editable=False)
    updated = models.DateTimeField('Updated', blank=False, auto_now=True)


class Speciality(BaseModel):
    class Meta:
        verbose_name_plural = _('Specialities')
        verbose_name = _('Speciality')

    name = models.CharField(_('Speciality'), max_length=50)
    rating_1 = models.ForeignKey('Doctor', related_name='doctor_1', on_delete=models.CASCADE, verbose_name=_('Rating 1'), blank=True, null=True)
    rating_2 = models.ForeignKey('Doctor', related_name='doctor_2', on_delete=models.CASCADE, verbose_name=_('Rating 2'), blank=True, null=True)
    rating_3 = models.ForeignKey('Doctor', related_name='doctor_3', on_delete=models.CASCADE, verbose_name=_('Rating 3'), blank=True, null=True)
    rating_4 = models.ForeignKey('Doctor', related_name='doctor_4', on_delete=models.CASCADE, verbose_name=_('Rating 4'), blank=True, null=True)
    rating_5 = models.ForeignKey('Doctor', related_name='doctor_5', on_delete=models.CASCADE, verbose_name=_('Rating 5'), blank=True, null=True)

    def __str__(self):
        return self.name


class Polyclinic(BaseModel):
    class Meta:
        verbose_name_plural = _('Polyclinics')
        verbose_name = _('Polyclinic')

    name = models.CharField(_('Name'), max_length=50)
    address = models.CharField(_('Address'), max_length=100)
    phone = models.ManyToManyField('Phone', related_name='phone', verbose_name=_('Phones'))
    position = models.ManyToManyField('Position', related_name='position_set', verbose_name=_('Position'), blank=True, null=True)
    speciality = models.ManyToManyField('Speciality', related_name='speciality_set', verbose_name=_('Speciality'))
    site_url = models.URLField(_('Site URL'), blank=True, null=True)
    image = models.ImageField(_('Photo'), upload_to='images/', default='images/NoneClinic.jpg', blank=True)
    work_time_start = models.TimeField(_('Work time start'), blank=True, null=True)
    work_time_end = models.TimeField(_('Work time end'), blank=True, null=True)
    district = models.ForeignKey('District', on_delete=models.CASCADE, related_name='district_set', verbose_name=_('District'), blank=True, null=True)

    def __str__(self):
        return f'{self.name} - {self.address}'


class Phone(BaseModel):
    class Meta:
        verbose_name_plural = _('Phones')
        verbose_name = _('Phone')

    number = models.CharField(_('Number'), max_length=15, unique=True)
    name = models.ForeignKey(Polyclinic, on_delete=models.CASCADE, related_name='polyclinic_set', verbose_name=_('Polyclinic'), blank=True, null=True)

    def __str__(self):
        return f'{self.number} - {self.name}'


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
    polyclinic = models.ForeignKey(Polyclinic, on_delete=models.CASCADE)

    @property
    def day_of_week_name(self):
        return list(filter(lambda x: x[0] == self.day_of_week, self.DAY_OF_WEEK))[0][1]

    def __str__(self):
        return f'{self.day_of_week_name} {self.start_time} - {self.end_time}, {self.polyclinic.name}'


class Doctor(BaseModel):
    class Meta:
        verbose_name_plural = _('Doctors')
        verbose_name = _('Doctor')

    first_name = models.CharField(_('First name'), max_length=50)
    last_name = models.CharField(_('Last name'), max_length=50)
    paternal_name = models.CharField(_('Paternal name'), max_length=50)
    phone = models.CharField(_('Phone number'), max_length=15)
    image = models.ImageField(_('Photo'), upload_to='images/', default='images/None.png', blank=True)
    speciality = models.ForeignKey(Speciality, related_name='speciality', on_delete=models.CASCADE, verbose_name=_('Speciality'))
    position = models.ForeignKey(Position, on_delete=models.CASCADE, verbose_name=_('Position'))
    polyclinic = models.ManyToManyField(Polyclinic, related_name='polyclinic', verbose_name=_('Polyclinic'))
    district = models.ManyToManyField(District, related_name='district', verbose_name=_('District'))
    experience = models.IntegerField(_('Experience'), default=0, validators=[MinValueValidator(1), MaxValueValidator(100)])
    cost = models.FloatField(_('Cost'), default=0, validators=[MinValueValidator(0), MaxValueValidator(100000)])
    schedule = models.ManyToManyField(Schedule, related_name='schedule', verbose_name=_('Schedule'))

    @property
    def full_name(self):
        return f'{self.last_name} {self.first_name} {self.paternal_name}'

    def __str__(self):
        return self.full_name


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
