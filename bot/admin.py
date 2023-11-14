from django.contrib import admin
from bot.models import Doctor, Speciality, Polyclinic, District, Position, Schedule, Phone, Address
from django.utils.html import mark_safe
from bot.forms import PolyclinicForm, DoctorForm
from django.utils.translation import gettext_lazy as _
import re


admin.site.site_header = _('DOCTOR BOT')
admin.site.site_title = _('DOCTOR BOT')
admin.site.index_title = _('DOCTOR BOT')


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    form = DoctorForm
    list_per_page = 150
    autocomplete_fields = ('polyclinic', 'district', 'schedule')
    list_display = ('id', 'last_name', 'first_name', 'paternal_name', 'phone',
                    'speciality', 'position', 'experience', 'cost', 'rating', 'image_tag')
    list_filter = ('speciality', 'position', 'polyclinic', 'district', 'schedule')
    search_fields = ('last_name', 'first_name', 'paternal_name')
    fields = ('last_name', 'first_name', 'paternal_name', 'phone', 'rating', 'image_tag',
              'image', 'speciality', 'position', 'polyclinic', 'district',
              'schedule', 'experience', 'cost')
    readonly_fields = ('image_tag',)
    list_display_links = ('last_name', 'first_name', 'paternal_name')

    def image_tag(self, obj):
        return mark_safe(f'<img src="{obj.image.url}" width="50" height="50" />')
    image_tag.short_description = 'Photo'

    def save_model(self, request, obj, form, change):
        if obj.rating:
            doctors = Doctor.objects.filter(rating=obj.rating).all()
            for i in doctors:
                i.rating = None
                i.save()
        super().save_model(request, obj, form, change)


@admin.register(Speciality)
class SpecialityAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Polyclinic)
class PolyclinicAdmin(admin.ModelAdmin):
    form = PolyclinicForm
    list_per_page = 150
    autocomplete_fields = ('speciality', 'phone', 'address')
    list_display = ('id', 'name', 'addresses', 'district', 'site', 'phones', 'work_time', 'rating', 'image_tag')
    search_fields = ('name',)
    fields = ('name', 'address', 'site_url', 'phone', 'rating', 'image_tag', 'image', 'district',
              'speciality', 'work_time_start', 'work_time_end')
    readonly_fields = ('image_tag',)
    list_display_links = ('name',)

    def image_tag(self, obj):
        return mark_safe(f'<img src="{obj.image.url}" width="50" height="50" />')
    image_tag.short_description = _('Photo')

    def phones(self, obj):
        if obj.phone.exists():
            text = ', '.join([i.number for i in obj.phone.all()])
            return text
        else:
            return '-'
    phones.short_description = _('Phone numbers')

    def save_model(self, request, obj, form, change):
        if obj.rating:
            polyclinics = Polyclinic.objects.filter(rating=obj.rating).all()
            for i in polyclinics:
                i.rating = None
                i.save()
        super().save_model(request, obj, form, change)

    def site(self, obj):
        if obj.site_url:
            return mark_safe(f'<a href="{obj.site_url}" target="_blank">{obj.site_url}</a>')
        else:
            return '-'
    site.short_description = _('Site URL')

    def addresses(self, obj):
        if obj.address.exists():
            text = ', '.join([i.name for i in obj.address.all()])
            return text
        else:
            return '-'
    addresses.short_description = _('Addresses')


@admin.register(Phone)
class PhoneAdmin(admin.ModelAdmin):
    list_per_page = 150
    list_display = ('number', 'location')
    search_fields = ('number',)

    # def get_search_results(self, request, queryset, search_term):
    #     queryset, may_have_duplicates = super().get_search_results(request, queryset, search_term)
    #     if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
    #         result = re.search(r'(?<=polyclinic/)\d+(?=/change)', request.headers['Referer'])
    #         if result:
    #             polyclinic_id = int(result.group(0))
    #             queryset = queryset.filter(polyclinic=polyclinic_id).order_by('-id')
    #     return queryset, may_have_duplicates

    def location(self, obj):
        polyclinics = Polyclinic.objects.filter(phone__number=obj.number).all()
        if polyclinics:
            text = ',<br>'.join([i.full_name for i in polyclinics])
            return mark_safe(f'<span>{text}</span>')
        else:
            return '-'
    location.short_description = _('Polyclinic')


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('name', 'location')
    search_fields = ('name',)

    def location(self, obj):
        polyclinics = Polyclinic.objects.filter(address__name=obj.name).all()
        if polyclinics:
            text = ',<br>'.join([i.name for i in polyclinics])
            return mark_safe(f'<span>{text}</span>')
        else:
            return '-'
    location.short_description = _('Polyclinic')


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('day_of_week', 'start_time', 'end_time', 'polyclinic')
    search_fields = ('day_of_week', 'start_time', 'end_time', 'polyclinic')
