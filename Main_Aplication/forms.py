from django import forms
from .models import Patients, TimePoints, PatientEntries


class NewPatientForm(forms.ModelForm):
    class Meta:
        model = Patients
        fields = ['pname', 'phone_number', 'email']

class TimePointsForm(forms.ModelForm):
    class Meta:
        model = TimePoints
        fields = ['provider', 'tplocation', 'startdate', 'enddate', 'timepointtype']

class PatientEntryForm(forms.ModelForm):
    class Meta:
        model = PatientEntries
        fields = ['phantom_limb_ps_avg', 'phantom_limb_ps_max', 'residual_limb_ps_avg', 'residual_limb_ps_max', 'socket_comfort_score_avg', 'socket_comfort_score_max']