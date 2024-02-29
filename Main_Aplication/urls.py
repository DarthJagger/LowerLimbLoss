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
    path("Provider", views.Provider, name="Navigation"),
    path("Enter_Scores", views.Enter_scores, name="Navigation"),

    path("Postsurgical_Stabilization", views.Postsurgical_Stabilization, name="Navigation"),
    path("Preprosthetic_Rehabilitation", views.Preprosthetic_Rehabilitation, name="Navigation"),
    path("Limb_Healing", views.Limb_Healing, name="Navigation"),
    path("Prosthetic_Fitting", views.Prosthetic_Fitting, name="Navigation"),
    path("Prosthetic_Rehabilitation", views.Prosthetic_Rehabilitation, name="Navigation"),
    path("Patient_Postsurgical_Stabilization", views.Patient_Postsurgical_Stabilization, name="Navigation"),
    path("Patient_Preprosthetic_Rehabilitation", views.Patient_Preprosthetic_Rehabilitation, name="Navigation"),
    path("Patient_Limb_Healing", views.Patient_Limb_Healing, name="Navigation"),
    path("Patient_Prosthetic_Fitting", views.Patient_Prosthetic_Fitting, name="Navigation"),
    path("Patient_Prosthetic_Rehabilitation", views.Patient_Prosthetic_Rehabilitation, name="Navigation"),
    path("Patient_Time_Points", views.Patient_Time_Points, name="Navigation"),
    path("Patient_Time_Point_Info", views.Patient_Time_Point_Info, name="Navigation"),

    path("Provider_AmpPro_Survey", views.Provider_AmpPro_Survey , name="Navigation"),
    path("Provider_AmpNoPro_Survey", views.Provider_AmpNoPro_Survey , name="Navigation"),
    path("Provider_TimedGo_Test", views.Provider_TimedGo_Test , name="Navigation"),
    path("Provider_6Min_Test", views.Provider_6Min_Test , name="Navigation"),

]

"""
Removed while updating to new HTML format

path("SensorScore/", views.sensor_score, name="Sensor Score"),
path("SensorGraph/<step>/", views.sensor_graph, name="Sensor Score"),
path("<step>/", views.self_score, name="Navigation"),

"""
