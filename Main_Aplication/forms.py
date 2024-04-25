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
        fields = ['phantom_limb_ps_avg', 'phantom_limb_ps_max', 'residual_limb_ps_avg', 'residual_limb_ps_max',
                  'socket_comfort_score_avg', 'socket_comfort_score_max']


class ProviderAmpProForm(forms.ModelForm):
    class Meta:
        model = AmpproScores
        fields = ['amppro', 'time_balanced_sound', 'time_balanced_prosthesis']


class ProviderAmpNoProForm(forms.ModelForm):
    class Meta:
        model = AmpnoproScores
        fields = ['ampnopro']


class ProviderTimedGoForm(forms.ModelForm):
    class Meta:
        model = TimedupandgoScores
        fields = ['timedupandgo']


class Provider6MinForm(forms.ModelForm):
    class Meta:
        model = SixminwalktestScores
        fields = ['sixminwalktest']


class ProviderPlusMForm(forms.ModelForm):
    class Meta:
        model = PlusMScores
        fields = ['plus_m']
