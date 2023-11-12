from django import forms
from bot.models import Doctor, Speciality, Polyclinic, Phone, Address, Schedule
from django.contrib.admin.widgets import AutocompleteSelectMultiple
from django.contrib import admin


class SpecialityForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        queryset = Doctor.objects.filter(speciality=instance).all()
        self.fields['rating_1'].queryset = queryset
        self.fields['rating_2'].queryset = queryset
        self.fields['rating_3'].queryset = queryset
        self.fields['rating_4'].queryset = queryset
        self.fields['rating_5'].queryset = queryset

    class Meta:
        model = Speciality
        fields = '__all__'


class PolyclinicForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        queryset = Phone.objects.filter(polyclinic=instance).all()
        self.fields['phone'].queryset = queryset
        queryset = Address.objects.filter(polyclinic=instance).all()
        self.fields['address'].queryset = queryset
        self.fields['speciality'].widget.can_add_related = False

    class Meta:
        model = Polyclinic
        fields = '__all__'


class ScheduleForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        queryset = Address.objects.filter(polyclinic=instance.polyclinic).all()
        self.fields['address'].queryset = queryset

    class Meta:
        model = Schedule
        fields = '__all__'


class DoctorForm(forms.ModelForm):
    schedule = forms.ModelMultipleChoiceField(
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
