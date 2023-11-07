from django import forms
from bot.models import Doctor, Speciality


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
