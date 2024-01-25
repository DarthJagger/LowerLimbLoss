from django.db.models import Q
from django.shortcuts import render, redirect


# Create your views here.
def nav(request):
    return render(request, "Base_Template.html")

def SignIn(request):
    return render(request, "sign-in.html")
def SignUp(request):
    return render(request, "Create-Account.html")

"""

Removed while updating to new HTML format 
 
def self_score(request, step):
    if (step == "PS"):
        return render(request, "Self_Score_Base.html", {"step": "Postsurgical Stabilization"})
    if (step == "PPR"):
        return render(request, "Self_Score_Base.html", {"step": "Preprosthetic Rehabilitation"})
    if (step == "LHM"):
        return render(request, "Self_Score_Base.html", {"step": "Limb Healing &  Maturation"})
    if (step == "PF"):
        return render(request, "Self_Score_Base.html", {"step": "Prosthetic Fitting"})
    if (step == "PR"):
        return render(request, "Self_Score_Base.html", {"step": "Prosthetic Rehabilitation"})


def sensor_score(request):
    return render(request, "Sensor_Score_Base.html")

def sensor_graph(request,step):
    if (step == "Cadence"):
        return render(request, "Sensor_Graph_Base.html", {"type": "Cadence"})
    if (step == "WalkTime"):
        return render(request, "Sensor_Graph_Base.html", {"type": "Walking Time"})
    if (step == "DistanceWalked"):
        return render(request, "Sensor_Graph_Base.html", {"type": "Distance Walked"})
    if (step == "WalkSpeed"):
        return render(request, "Sensor_Graph_Base.html", {"type": "Walking Speed"})
    if (step == "StepHeight"):
        return render(request, "Sensor_Graph_Base.html", {"type": "Step Height"})

"""
