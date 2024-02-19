from django.db.models import Q
from django.shortcuts import render, redirect
from django.utils import timezone
from .forms import NewPatientForm
from .models import Patients
from django.contrib import messages
from django.contrib.auth.decorators import login_required # Use @login_required to make a view require login
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

def nav(request):
    return render(request, "Base_Template.html")


def SignIn(request):
    if request.method == "POST":
        inputEmail = request.POST["email"]
        inputPassword = request.POST['ppassword']
        try:
            user = Patients.objects.get(email=inputEmail)
            systemPassword = user.ppassword
            if (inputPassword == systemPassword):
                id = user.patient_id
                user = authenticate(request, username=id, password=inputPassword)
                if user is not None:
                    login(request, user)
                    return redirect('/Patient')
                else:
                    messages.success(request, "Login Unsuccessful")
            else:
                messages.success(request, "Login Unsuccessful")
        except Patients.DoesNotExist:
            messages.success(request, "Login Unsuccessful")
    return render(request, "sign-in.html")


def SignUp(request):
    if request.method == "POST":
        form = NewPatientForm(request.POST or None)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['ppassword']
            # TODO: Requires further error checking for emails (maybe) and passwords
            form.save()
            userTemp = Patients.objects.get(email=email)
            id = userTemp.patient_id
            user = User.objects.create_user(id, email, password)
            user.save()
            return redirect('/SignIn')
    return render(request, "Create-Account.html")


def Logout(request):
    logout(request)
    return redirect('/home')

def Patient(request):
    return render(request, "Patient_Home.html")


def Enter_scores(request):
    return render(request, "Patient_enter_scores.html")



def Postsurgical_Stabilization(request):
    return render(request, "Postsurgical_Stabilization.html")


def Preprosthetic_Rehabilitation(request):
    return render(request, "Preprosthetic_Rehabilitation.html")


def Limb_Healing(request):
    return render(request, "Limb_Healing.html")


def Prosthetic_Fitting(request):
    return render(request, "Prosthetic_Fitting.html")


def Prosthetic_Rehabilitation(request):
    return render(request, "Prosthetic_Rehabilitation.html")



def Patient_Time_Points(request):
    return render(request, "Patient_Time_Points.html")


def Patient_Time_Point_Info(request):
    return render(request, "Patient_Time_Point_Info.html")


def Patient_Postsurgical_Stabilization(request):
    return render(request, "Patient_Postsurgical_Stabilization.html")


def Patient_Preprosthetic_Rehabilitation(request):
    return render(request, "Patient_Preprosthetic_Rehabilitation.html")


def Patient_Limb_Healing(request):
    return render(request, "Patient_Limb_Healing.html")


def Patient_Prosthetic_Fitting(request):
    return render(request, "Patient_Prosthetic_Fitting.html")


def Patient_Prosthetic_Rehabilitation(request):
    return render(request, "Patient_Prosthetic_Rehabilitation.html")



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
