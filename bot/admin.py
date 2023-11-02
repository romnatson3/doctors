from django.contrib import admin
from bot.models import Doctor, Speciality, Polyclinic, District, Position, Schedule
from django.utils.html import mark_safe


admin.site.site_header = 'DOCTOR BOT'
admin.site.site_title = 'DOCTOR BOT'
admin.site.index_title = 'DOCTOR BOT'


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    autocomplete_fields = ('polyclinic', 'district', 'schedule')
    list_display = ('last_name', 'first_name', 'paternal_name', 'phone', 'speciality', 'position', 'experience', 'cost', 'image_tag')
    list_filter = ('speciality', 'position', 'polyclinic', 'district', 'schedule')
    search_fields = ('last_name', 'first_name', 'paternal_name', 'phone', 'speciality', 'position', 'polyclinic', 'district', 'schedule')
    fields = ('last_name', 'first_name', 'paternal_name', 'phone', 'image_tag', 'image', 'speciality', 'position', 'polyclinic', 'district', 'schedule', 'experience', 'cost')
    readonly_fields = ('image_tag',)

    def image_tag(self, obj):
        return mark_safe(f'<img src="{obj.image.url}" width="50" height="50" />')
    image_tag.short_description = 'Photo'


@admin.register(Speciality)
class SpecialityAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Polyclinic)
class PolyclinicAdmin(admin.ModelAdmin):
    list_display = ('name', 'address')
    search_fields = ('name', 'address')


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
