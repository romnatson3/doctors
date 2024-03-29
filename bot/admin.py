from django.contrib import admin
from bot.models import Doctor, Speciality, Polyclinic, District, Position, Schedule, Phone, Address, Share
from django.utils.html import mark_safe
from bot.forms import PolyclinicForm, DoctorForm, ShareForm
from django.utils.translation import gettext_lazy as _
import re
from bot.filters import SpecialityFilter


admin.site.site_header = _('DOCTOR BOT')
admin.site.site_title = _('DOCTOR BOT')
admin.site.index_title = _('DOCTOR BOT')


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    form = DoctorForm
    list_per_page = 50
    autocomplete_fields = ('polyclinic', 'district', 'schedule')
    list_display = ('id', 'last_name', 'first_name', 'paternal_name', 'phone',
                    'speciality', 'position', 'experience', 'cost',
                    'rating', 'image_tag')
    list_filter = (SpecialityFilter, 'district')
    search_fields = ('last_name', 'first_name', 'paternal_name')
    fields = ('last_name', 'first_name', 'paternal_name', 'phone', 'rating',
              'image_tag', 'image', 'speciality', 'position', 'polyclinic', 'district',
              'schedule', 'experience', 'cost')
    readonly_fields = ('image_tag',)
    list_display_links = ('last_name', 'first_name', 'paternal_name')
    actions = ('copy_action',)

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

    def copy_action(self, request, queryset):
        for obj in queryset:
            previous_polyclinic = obj.polyclinic.all()
            previous_district = obj.district.all()
            previous_schedule = obj.schedule.all()
            obj.id = None
            obj.save()
            obj.polyclinic.set(previous_polyclinic)
            obj.district.set(previous_district)
            obj.schedule.set(previous_schedule)
        self.message_user(request, _('Selected records were copied successfully'))
    copy_action.short_description = _('Copy chosen records')


@admin.register(Polyclinic)
class PolyclinicAdmin(admin.ModelAdmin):
    form = PolyclinicForm
    list_per_page = 50
    list_filter = (SpecialityFilter, 'district')
    autocomplete_fields = ('speciality', 'phone', 'address')
    list_display = ('id', 'name', 'addresses', 'district', 'site', 'phones',
                    'work_time', 'rating', 'image_tag')
    search_fields = ('name',)
    fields = ('name', 'address', 'site_url', 'phone', 'rating', 'image_tag',
              'image', 'district', 'speciality', 'work_time_start', 'work_time_end')
    readonly_fields = ('image_tag',)
    list_display_links = ('name',)
    actions = ('copy_action',)

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

    def copy_action(self, request, queryset):
        for obj in queryset:
            previous_address = obj.address.all()
            previous_phone = obj.phone.all()
            previous_speciality = obj.speciality.all()
            obj.id = None
            obj.save()
            obj.address.set(previous_address)
            obj.phone.set(previous_phone)
            obj.speciality.set(previous_speciality)
        self.message_user(request, _('Selected records were copied successfully'))
    copy_action.short_description = _('Copy chosen records')


@admin.register(Share)
class ShareAdmin(admin.ModelAdmin):
    form = ShareForm
    list_display_links = ('name',)
    list_display = ('id', 'name', 'start_date', 'end_date', 'sum', 'rating', 'image_tag')
    search_fields = ('name',)
    fields = ('name', 'description', 'start_date', 'end_date', 'sum', 'rating', 'image_tag', 'image')
    readonly_fields = ('image_tag',)

    def save_model(self, request, obj, form, change):
        if obj.rating:
            shares = Share.objects.filter(rating=obj.rating).all()
            for i in shares:
                i.rating = None
                i.save()
        super().save_model(request, obj, form, change)

    def image_tag(self, obj):
        return mark_safe(f'<img src="{obj.image.url}" width="50" height="50" />')
    image_tag.short_description = _('Photo')


@admin.register(Phone)
class PhoneAdmin(admin.ModelAdmin):
    list_display = ('number', '_polyclinic')
    search_fields = ('number',)
    fields = ('number', '_polyclinic')
    readonly_fields = ('_polyclinic',)

    # def get_search_results(self, request, queryset, search_term):
    #     queryset, may_have_duplicates = super().get_search_results(request, queryset, search_term)
    #     if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
    #         result = re.search(r'(?<=polyclinic/)\d+(?=/change)', request.headers['Referer'])
    #         if result:
    #             polyclinic_id = int(result.group(0))
    #             queryset = queryset.filter(polyclinic=polyclinic_id).order_by('-id')
    #     return queryset, may_have_duplicates

    def _polyclinic(self, obj):
        if obj.id:
            polyclinics = Polyclinic.objects.filter(phone__id=obj.id).values('name', 'address__name')
            if polyclinics:
                polyclinic_address = [f'{i["name"]} - {i["address__name"]}' for i in polyclinics]
                text = ',<br>'.join(polyclinic_address)
                return mark_safe(f'<span>{text}</span>')
        return '-'
    _polyclinic.short_description = _('Polyclinic')


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('name', '_polyclinic')
    search_fields = ('name',)
    fields = ('name', '_polyclinic')
    readonly_fields = ('_polyclinic',)

    def _polyclinic(self, obj):
        if obj.id:
            polyclinics = Polyclinic.objects.filter(address__id=obj.id).values_list('name', flat=True)
            if polyclinics:
                text = ',<br>'.join(polyclinics)
                return mark_safe(f'<span>{text}</span>')
        return '-'
    _polyclinic.short_description = _('Polyclinic')


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


@admin.register(Speciality)
class SpecialityAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
