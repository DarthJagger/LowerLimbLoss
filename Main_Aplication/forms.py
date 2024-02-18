from django import forms
from .models import Patients


class NewPatientForm(forms.ModelForm):
    class Meta:
        model = Patients
        fields = ['pname', 'phone_number', 'email', 'ppassword']
