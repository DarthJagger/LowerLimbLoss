from django import forms
from .models import Patients, TimePoints


class NewPatientForm(forms.ModelForm):
    class Meta:
        model = Patients
        fields = ['pname', 'phone_number', 'email', 'ppassword']

class TimePointsForm(forms.ModelForm):
    class Meta:
        model = TimePoints
        fields = ['provider', 'tplocation', 'startdate','enddate','timepointtype']