from django.contrib.admin import SimpleListFilter
from bot.models import Speciality
from django.utils.translation import gettext_lazy as _


class SpecialityFilter(SimpleListFilter):
    title = _('Speciality')
    parameter_name = 'speciality'

    def lookups(self, request, model_admin):
        return [(speciality.id, speciality.name) for speciality in Speciality.objects.order_by('name').all()]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(speciality__id=self.value())
        else:
            return queryset
