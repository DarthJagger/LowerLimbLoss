from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("", views.nav, name="Navigation"),
    path("SensorScore/", views.sensor_score, name="Sensor Score"),
    path("SensorGraph/<step>/", views.sensor_graph, name="Sensor Score"),
    path("<step>/", views.self_score, name="Navigation"),





]