from django import forms
from bot.models import Doctor, Polyclinic, Phone, Address, Schedule
from django.contrib.admin.widgets import AutocompleteSelectMultiple
from django.contrib import admin
from django.utils.translation import gettext_lazy as _


class PolyclinicForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['district'].required = True
        # instance = kwargs.get('instance')
        # queryset = Address.objects.filter(polyclinic=instance).all()
        # self.fields['address'].queryset = queryset
        # self.fields['speciality'].widget.can_add_related = False

    class Meta:
        model = Polyclinic
        fields = '__all__'


class DoctorForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rating'].empty_label = None
        self.fields['polyclinic'].required = False

    schedule = forms.ModelMultipleChoiceField(
        label=_('Schedule'),
        queryset=Schedule.objects.all(),
        required=True,
        widget=AutocompleteSelectMultiple(
            Doctor.schedule.field,
            admin.site,
            attrs={'style': 'width: 700px'}
        )
    )

    class Meta:
        model = Doctor
        fields = '__all__'
