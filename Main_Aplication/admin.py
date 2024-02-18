from django.contrib import admin
from .models import Patients, Providers, TimePoints, Authorizations, PatientEntries, SensorEntries, PlusMScores, AmpproScores, AmpnoproScores, TimedupandgoScores, SixminwalktestScores

# Register your models here.
admin.site.register(Patients)
admin.site.register(Providers)
admin.site.register(TimePoints)
admin.site.register(Authorizations)
admin.site.register(PatientEntries)
admin.site.register(SensorEntries)
admin.site.register(PlusMScores)
admin.site.register(AmpproScores)
admin.site.register(AmpnoproScores)
admin.site.register(TimedupandgoScores)
admin.site.register(SixminwalktestScores)