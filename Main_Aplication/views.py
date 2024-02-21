from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.shortcuts import render, redirect
from django.utils import timezone
from .forms import NewPatientForm, TimePointsForm, PatientEntryForm
from .models import Patients, Providers, TimePoints, PatientEntries
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required # Use @login_required to make a view require login
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
import datetime
import json

def nav(request):
    return render(request, "Base_Template.html")


def SignIn(request):
    if request.method == "POST":
        inputEmail = request.POST["email"]
        inputPassword = request.POST['ppassword']
        try:
            user = Patients.objects.get(email=inputEmail) # Find the patient corresponding to the email
            systemPassword = user.ppassword # Obtain the patient password in the database
            if (inputPassword == systemPassword): # Check that the password put into the login is the same as the database
                id = user.patient_id # Obtain the patient ID
                user = authenticate(request, username=id, password=inputPassword) # Authenticate the patient as a user
                if user is not None:
                    login(request, user) # Log the user into the website if the user is correct
                    return redirect('/home')
                else: # error for patients who don't have user account
                    messages.success(request, "Login Unsuccessful")
            else: # error for when the password is incorrect
                messages.success(request, "Login Unsuccessful")
        except Patients.DoesNotExist: #error if the patient doesn't exist in the database
            messages.success(request, "Login Unsuccessful")
    return render(request, "sign-in.html")


def SignUp(request):
    if request.method == "POST":
        form = NewPatientForm(request.POST or None)
        if form.is_valid():
            email = form.cleaned_data['email'] # Obtain patient email
            password = form.cleaned_data['ppassword'] # Obtain patient password
            # TODO: Requires further error checking for emails (maybe) and passwords
            form.save() # Creates a provider in the database
            userTemp = Patients.objects.get(email=email)
            id = userTemp.patient_id # TODO: Modifier to separate between Patient and Provider users
            user = User.objects.create_user(id, email, password) # Create a new user in Django
            user.save() # Creates a user in the django users database corresponding to the Patient
            return redirect('/SignIn')
    return render(request, "Create-Account.html")


def Logout(request):
    logout(request)
    return redirect('/home')


@login_required
def Patient(request):
    return render(request, "Patient_Home.html")


@login_required
def Enter_scores(request):
    if request.method == "POST":
        form = PatientEntryForm(request.POST or None)  # Obtain data from the form for a patient entry
        if form.is_valid():
            patient_entry = form.save(commit=False)
            if request.user.is_authenticated:  # Check if the user exists
                patient_id = request.user.username  # Obtain patient_ID for the current User TODO: Fix username handling
                currentDate = datetime.datetime.today()
                patient_entry.patient_id = patient_id
                patient_entry.entrydate = currentDate
                patient_entry.save()
                messages.success(request, "Scores added successfully")
                return render(request, "Patient_enter_scores.html")
            else:
                messages.success(request, "Error: Unable to add scores. Please try again.")
        else:
            messages.success(request, "Error: Unable to add scores. Please try again.")
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


@login_required
def Patient_Create_Timepoint(request):
    if request.method == "POST":
        form = TimePointsForm(request.POST or None)
        if form.is_valid():
            timePoint = form.save(commit=False)  # Save new TimePoint into timePoint
            id = form.cleaned_data['provider'].provider_id  # Obtain provider ID
            providerTemp = Providers.objects.get(provider_id=id)  # obtain provider corresponding to ID
            specialty = providerTemp.specialty  # Obtain provider specialty
            if request.user.is_authenticated:  # Check if the user exists
                patient_id = request.user.username  # Obtain patient_ID for the current User TODO: Fix username handling
                # Obtain the list of previous timepoints
                priorTimePoints = TimePoints.objects.filter(patient_id=patient_id).order_by('-timepointnum').values('timepointnum')
                timePoint.timepointnum = len(priorTimePoints)+1  # Set the current timepointnum to the next timepoint num in the list
                timePoint.specialty = specialty  # Set specialty in timePoint to the specialty of the provider
                timePoint.patient_id = patient_id   # Set patient_id in timePoint to the ID of the user.
                timePoint.save()  # Commit the timePoint into the database
                return redirect('/Patient_Time_Points')
            else: # Error if the user isn't authenticated
                messages.success(request, "Error. Unable to create time point. Please try again.")
        else: # Error if the inputted form isn't valid
            messages.success(request, "Error. Unable to create time point. Please try again.")
    return render(request, "Patient_Create_Timepoint.html")


@login_required
def Patient_Time_Points(request):
    if request.user.is_authenticated:  # Check if the user exists
        patient_id = request.user.username  # Obtain patient_ID for the current User TODO: Fix username handling
        time_points = TimePoints.objects.filter(patient_id=patient_id).order_by('timepointnum')  # Obtain all of the patient's timepoints
        return render(request, "Patient_Time_Points.html",{'time_points': time_points})
    else:  # If the user isn't authenticated, redirect to home
        return redirect('/home')


@login_required
def Patient_Time_Point_Info(request, timepointnum):
    if request.user.is_authenticated:  # Check if the user exists
        try:
            patient_id = request.user.username  # Obtain patient_ID for the current User TODO: Fix username handling
            time_point = TimePoints.objects.get(patient_id=patient_id, timepointnum=timepointnum) # Get the time_point corresponded to the timepointnum of the page
            provider_id = time_point.provider_id  # get the provider_ID for the associated time_point
            provider = Providers.objects.get(provider_id=provider_id) # get the provider information associated with the provider_ID form time_point
            return render(request, "Patient_Time_Point_Info.html",{'time_point': time_point, 'provider': provider})
        except ObjectDoesNotExist:
            return redirect('/home')
    else:
        return redirect('/home')


@login_required
def Patient_Postsurgical_Stabilization(request):
    if request.user.is_authenticated:
        try:
            patient_id = request.user.username  # Obtain patient_ID for the current User TODO: Fix username handling
            patient_entries = PatientEntries.objects.filter(patient_id=patient_id).order_by('entrydate')
            xValues = json.dumps([str(item.entrydate) for item in patient_entries])
            plsAvgValues = json.dumps([int(item.phantom_limb_ps_avg) for item in patient_entries])
            plsMaxValues = json.dumps([int(item.phantom_limb_ps_max) for item in patient_entries])
            rlsAvgValues = json.dumps([int(item.residual_limb_ps_avg) for item in patient_entries])
            rlsMaxValues = json.dumps([int(item.residual_limb_ps_max) for item in patient_entries])
            scsAvgValues = json.dumps([int(item.socket_comfort_score_avg) for item in patient_entries])
            scsMaxValues = json.dumps([int(item.socket_comfort_score_max) for item in patient_entries])
            #time_point = TimePoints.objects.get(patient_id=patient_id)
            return render(request, "Patient_Postsurgical_Stabilization.html",{'xValues': xValues, 'plsAvgValues': plsAvgValues, 'plsMaxValues': plsMaxValues, 'rlsAvgValues': rlsAvgValues, 'rlsMaxValues': rlsMaxValues, 'scsAvgValues':scsAvgValues, 'scsMaxValues':scsMaxValues})  # , 'time_point': time_point
        except: # Error in retrieving the patient entries
            return redirect('/home')
    return render(request, "Patient_Postsurgical_Stabilization.html")


@login_required
def Patient_Preprosthetic_Rehabilitation(request):
    return render(request, "Patient_Preprosthetic_Rehabilitation.html")


@login_required
def Patient_Limb_Healing(request):
    return render(request, "Patient_Limb_Healing.html")


@login_required
def Patient_Prosthetic_Fitting(request):
    return render(request, "Patient_Prosthetic_Fitting.html")


@login_required
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
