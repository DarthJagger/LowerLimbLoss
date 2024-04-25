from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("", views.nav, name="Navigation"),
    path("home/", views.nav, name="Navigation"),
    path("SignIn", views.SignIn, name="Navigation"),
    path("SignUp", views.SignUp, name="Navigation"),
    path("Logout", views.Logout, name="Navigation"),
    path("Patient", views.Patient, name="Navigation"),
    path("Provider", views.Provider, name="Navigation"),
    path("Enter_Scores", views.Enter_scores, name="Navigation"),

    path("Patient_Postsurgical_Stabilization", views.Patient_Postsurgical_Stabilization, name="Navigation"),
    path("Patient_Preprosthetic_Rehabilitation", views.Patient_Preprosthetic_Rehabilitation, name="Navigation"),
    path("Patient_Limb_Healing", views.Patient_Limb_Healing, name="Navigation"),
    path("Patient_Prosthetic_Fitting", views.Patient_Prosthetic_Fitting, name="Navigation"),
    path("Patient_Prosthetic_Rehabilitation", views.Patient_Prosthetic_Rehabilitation, name="Navigation"),
    path("Patient_Time_Points", views.Patient_Time_Points, name="Navigation"),
    path("Patient_Step_Time_Points/<str:timepointtype>", views.Patient_Step_Time_Points, name="Navigation"),
    path("Patient_Time_Point_Info/<int:timepointnum>", views.Patient_Time_Point_Info, name="Navigation"),
    path("Patient_Create_Timepoint", views.Patient_Create_Timepoint, name="Navigation"),
    path("Patient_Create_Authorization", views.Patient_Authorize, name="Navigation"),
    path("Patient_Authorizations", views.Patient_Authorizations, name="Navigation"),
    path("Patient_Provider_Info/<int:provider_id>", views.Patient_Provider_Info, name="Navigation"),
    path("Patient_Auth_Request_Info/<int:provider_id>", views.Patient_Auth_Request_Info, name="Navigation"),

    path("Provider_AmpPro_Survey/<str:patient_email>/", views.Provider_AmpPro_Survey, name="Navigation"),
    path("Provider_AmpNoPro_Survey/<str:patient_email>/", views.Provider_AmpNoPro_Survey, name="Navigation"),
    path("Provider_TimedGo_Test/<str:patient_email>/", views.Provider_TimedGo_Test, name="Navigation"),
    path("Provider_6Min_Test/<str:patient_email>/", views.Provider_6Min_Test, name="Navigation"),
    path("Provider_PlusM_Score/<str:patient_email>/", views.Provider_PlusM_Score, name="Navigation"),

    path('Provider_Home/<str:patient_email>/', views.Provider_Home, name='provider_home'),
    path("Provider_Postsurgical_Stabilization/<str:patient_email>/", views.Provider_Postsurgical_Stabilization,
         name="provider_postsurgical_stabilization"),
    path("Provider_Preprosthetic_Rehabilitation/<str:patient_email>/", views.Provider_Preprosthetic_Rehabilitation,
         name="provider_preprosthetic_rehabilitation"),
    path("Provider_Limb_Healing/<str:patient_email>/", views.Provider_Limb_Healing, name="provider_limb_healing"),
    path("Provider_Prosthetic_Fitting/<str:patient_email>/", views.Provider_Prosthetic_Fitting,
         name="provider_prosthetic_fitting"),
    path("Provider_Prosthetic_Rehabilitation/<str:patient_email>/", views.Provider_Prosthetic_Rehabilitation,
         name="provider_prosthetic_rehabilitation"),
    path("Provider_Create_Authorization", views.Provider_Create_Authorization, name="Navigation"),
    path("Provider_Auth_Request_Info/<int:patient_id>/", views.Provider_Auth_Request_Info, name="Navigation"),

    path("Admin_Create_Provider",views.Admin_Create_Provider , name="Navigation")

]

"""
Removed while updating to new HTML format

path("SensorScore/", views.sensor_score, name="Sensor Score"),
path("SensorGraph/<step>/", views.sensor_graph, name="Sensor Score"),
path("<step>/", views.self_score, name="Navigation"),

"""
