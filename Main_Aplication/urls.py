from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("", views.nav, name="Navigation"),
    path("home/", views.nav, name="Navigation"),
    path("SignIn", views.SignIn, name="Navigation"),
    path("SignUp", views.SignUp, name="Navigation"),
    path("Patient", views.Patient, name="Navigation"),
    path("Enter_Scores", views.Enter_scores, name="Navigation"),



]

"""
Removed while updating to new HTML format

path("SensorScore/", views.sensor_score, name="Sensor Score"),
path("SensorGraph/<step>/", views.sensor_graph, name="Sensor Score"),
path("<step>/", views.self_score, name="Navigation"),

"""