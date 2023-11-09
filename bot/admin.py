from django.contrib import admin
from bot.models import Doctor, Speciality, Polyclinic, District, Position, Schedule, Phone
from django.utils.html import mark_safe
from bot.forms import SpecialityForm, PolyclinicForm
from django.utils.translation import gettext_lazy as _
import re


admin.site.site_header = 'DOCTOR BOT'
admin.site.site_title = 'DOCTOR BOT'
admin.site.index_title = 'DOCTOR BOT'


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    autocomplete_fields = ('polyclinic', 'district', 'schedule')
    list_display = ('last_name', 'first_name', 'paternal_name', 'phone',
                    'speciality', 'position', 'experience', 'cost', 'image_tag')
    list_filter = ('speciality', 'position', 'polyclinic', 'district', 'schedule')
    search_fields = ('last_name', 'first_name', 'paternal_name')
    fields = ('last_name', 'first_name', 'paternal_name', 'phone', 'image_tag',
              'image', 'speciality', 'position', 'polyclinic', 'district',
              'schedule', 'experience', 'cost')
    readonly_fields = ('image_tag',)
    list_display_links = ('last_name', 'first_name', 'paternal_name')

    def image_tag(self, obj):
        return mark_safe(f'<img src="{obj.image.url}" width="50" height="50" />')
    image_tag.short_description = 'Photo'


@admin.register(Speciality)
class SpecialityAdmin(admin.ModelAdmin):
    form = SpecialityForm
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Polyclinic)
class PolyclinicAdmin(admin.ModelAdmin):
    form = PolyclinicForm
    autocomplete_fields = ('position', 'speciality', 'phone')
    list_display = ('name', 'address', 'district', 'site', 'phones', 'work_time', 'image_tag')
    search_fields = ('name', 'address')
    fields = ('name', 'address', 'site_url', 'phone', 'image_tag', 'image', 'district',
              'speciality', 'work_time_start', 'work_time_end')
    readonly_fields = ('image_tag',)
    list_display_links = ('name', 'address')

    def image_tag(self, obj):
        return mark_safe(f'<img src="{obj.image.url}" width="50" height="50" />')
    image_tag.short_description = _('Photo')

    def phones(self, obj):
        if obj.phone.exists():
            text = ', '.join([i.number for i in obj.phone.all()])
            return text
        else:
            return '-'
    phones.short_description = _('Phones')

    def site(self, obj):
        if obj.site_url:
            return mark_safe(f'<a href="{obj.site_url}" target="_blank">{obj.site_url}</a>')
        else:
            return '-'
    site.short_description = _('Site URL')


@admin.register(Phone)
class PhomeAdmin(admin.ModelAdmin):
    list_display = ('number', 'name')
    search_fields = ('number', 'name')

    def get_search_results(self, request, queryset, search_term):
        queryset, may_have_duplicates = super().get_search_results(request, queryset, search_term)
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            result = re.search(r'(?<=polyclinic/)\d+(?=/change)', request.headers['Referer'])
            if result:
                polyclinic_id = int(result.group(0))
                queryset = queryset.filter(name=polyclinic_id).order_by('-id')
        return queryset, may_have_duplicates


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
