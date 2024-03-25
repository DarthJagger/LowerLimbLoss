from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.shortcuts import render, redirect
# from django.utils import timezone
from .forms import NewPatientForm, TimePointsForm, PatientEntryForm
from .models import Patients, Providers, TimePoints, PatientEntries, Authorizations
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required # Use @login_required to make a view require login
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login, logout
import datetime
import json

# Function used to check if the user is a patient
def is_patient(user):
    return user.groups.filter(name='Patient').exists()

# Function used to check if the user is a patient
def is_provider(user):
    return user.groups.filter(name='Provider').exists()

def nav(request):
    return render(request, "Base_Template.html")


def SignIn(request):
    if request.method == "POST":
        inputEmail = request.POST["email"]
        inputPassword = request.POST['ppassword']
        if(Patients.objects.filter(email=inputEmail).exists()):
            try:
                userPatient = Patients.objects.get(email=inputEmail)  # Find the patient corresponding to the email
                systemPassword = userPatient.ppassword  # Obtain the patient password in the database
                if (inputPassword == systemPassword):  # Check that the password put into the login is the same as the database
                    id = userPatient.patient_id  # Obtain the patient ID
                    username = "Patient_" + str(id)
                    user = authenticate(request, username=username, password=inputPassword)  # Authenticate the patient as a user
                    if user is not None:
                        login(request, user)  # Log the user into the website if the user is correct
                        return redirect('/home')
                    else:  # error for patients who don't have user account
                        messages.success(request, "Login Unsuccessful")
                else:  # error for when the password is incorrect
                    messages.success(request, "Login Unsuccessful")
            except Patient.DoesNotExist:
                messages.success(request, "Login Unsuccessful")
        elif(Providers.objects.filter(email=inputEmail).exists()):
            try:
                userProvider = Providers.objects.get(email=inputEmail)  # Find the provider corresponding to the email
                systemPassword = userProvider.ppassword  # Obtain the provider password in the database
                if (inputPassword == systemPassword):  # Check that the password put into the login is the same as the database
                    id = userProvider.provider_id  # Obtain the provider ID
                    username = "Provider" + str(id)
                    user = authenticate(request, username=username, password=inputPassword)  # Authenticate the provider as a user
                    if user is not None:
                        login(request, user)  # Log the user into the website if the user is correct
                        return redirect('/Provider')
                    else:  # error for providers who don't have user account
                        messages.success(request, "Login Unsuccessful")
                else:  # error for when the password is incorrect
                    messages.success(request, "Login Unsuccessful")
            except Provider.DoesNotExist:
                messages.success(request, "Login Unsuccessful")
        else:  # error for when user doesn't exist
            messages.success(request, "Login Unsuccessful")
    return render(request, "sign-in.html")


def SignUp(request):
    if request.method == "POST":
        #form = NewPatientForm(request.POST or None)
        email = request.POST["email"]
        password = request.POST["ppassword"]
        password_confirm = request.POST["password_confirm"]
        priorPatients = Patients.objects.filter(email=email)
        priorProviders = Providers.objects.filter(email=email)
        if (priorPatients.exists() or priorProviders.exists() or (not(password == password_confirm))):  # Check to see if the email is in use
            messages.success(request, "Sign Up Unsuccessful")
            return render(request, "Create-Account.html")
        else:
            # Generate a new form with only the needed data
            pname = request.POST["pname"]
            phone_number = request.POST["phone_number"]
            patient = Patients.objects.create(pname=pname, email=email, phone_number=phone_number, ppassword=password)
            '''if(patient.is_valid()):  # Check if the generated form is valid
                form.save()  # Creates a provider in the database
            else:  # Display an error if the form was unable to be created
                messages.success(request, "Sign Up Unsuccessful")
                return render(request, "Create-Account.html")'''
            userTemp = Patients.objects.get(email=email)
            group = Group.objects.get(name="Patient")
            id = userTemp.patient_id  # TODO: Modifier to separate between Patient and Provider users (Later signup code)
            username = "Patient_" + str(id)  # Construct a backend username that starts with Patient for patients
            user = User.objects.create_user(username, email, password)  # Create a new user in Django
            user.save()  # Creates a user in the django users database corresponding to the Patient
            user.groups.add(group)
            return redirect('/SignIn')
    return render(request, "Create-Account.html")


def Logout(request):
    logout(request)
    return redirect('/home')


@login_required
@user_passes_test(is_patient)
def Patient(request):
    return render(request, "Patient_Home.html")


@login_required
@user_passes_test(is_patient)
def Enter_scores(request):
    if request.method == "POST":
        form = PatientEntryForm(request.POST or None)  # Obtain data from the form for a patient entry
        if form.is_valid():
            patient_entry = form.save(commit=False)
            if request.user.is_authenticated:  # Check if the user exists
                patient_id = request.user.username[8:]  # Obtain patient_ID for the current User
                currentDate = datetime.datetime.today()
                defaults = {"phantom_limb_ps_avg":patient_entry.phantom_limb_ps_avg, "phantom_limb_ps_max":patient_entry.phantom_limb_ps_max, "residual_limb_ps_avg":patient_entry.residual_limb_ps_avg, "residual_limb_ps_max":patient_entry.residual_limb_ps_max, "socket_comfort_score_avg":patient_entry.socket_comfort_score_avg, "socket_comfort_score_max":patient_entry.socket_comfort_score_max}
                patient_entry, created = PatientEntries.objects.update_or_create(patient_id=patient_id, entrydate=currentDate, defaults=defaults)
                patient_entry.save()
                messages.success(request, "Scores added successfully")
                return render(request, "Patient_enter_scores.html")
            else:
                messages.success(request, "Error: Unable to add scores. Please try again.")
        else:
            messages.success(request, "Error: Unable to add scores. Please try again.")
    return render(request, "Patient_enter_scores.html")




@login_required
@user_passes_test(is_patient)
def Patient_Authorize(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            try:
                patient_id = request.user.username[8:]
                provider_email = request.POST['provider']
                providerTemp = Providers.objects.get(email=provider_email)
                provider_id = providerTemp.provider_id
                aStatus = 'P'  # Authorization status of P means that patient provided authorization but Provider hasn't accepted
                auth_entry, created = Authorizations.objects.get_or_create(patient_id=patient_id, provider_id=provider_id, astatus=aStatus)
                if(created):
                    auth_entry.save()
                    messages.success(request, 'Authorization Sucessful')
                else:
                    messages.success(request, 'Provider Already Authorized')
                return render(request, 'Patient_Create_Authorization.html')
            except ObjectDoesNotExist:
                messages.success(request, 'Authorization Unsuccessful')
                return render(request, 'Patient_Create_Authorization.html')
        else:
            return render(request, 'Patient_Create_Authorization.html')
    else:
        return redirect('/SignIn')

@login_required
@user_passes_test(is_patient)
def Patient_Authorizations(request):
    return render(request, 'Patient_Authorizations.html')

@login_required
@user_passes_test(is_patient)
def Patient_Create_Timepoint(request):
    if request.method == "POST":
        form = TimePointsForm(request.POST or None)
        if form.is_valid():
            timePoint = form.save(commit=False)  # Save new TimePoint into timePoint
            id = form.cleaned_data['provider'].provider_id  # Obtain provider ID
            providerTemp = Providers.objects.get(provider_id=id)  # obtain provider corresponding to ID
            specialty = providerTemp.specialty  # Obtain provider specialty
            if request.user.is_authenticated:  # Check if the user exists
                patient_id = request.user.username[8:]  # Obtain patient_ID for the current User
                # Obtain the list of previous timepoints
                priorTimePoints = TimePoints.objects.defer(id).filter(patient_id=patient_id).order_by('-timepointnum').values('timepointnum')
                timePoint.timepointnum = len(priorTimePoints)+1  # Set the current timepointnum to the next timepoint num in the list
                timePoint.specialty = specialty  # Set specialty in timePoint to the specialty of the provider
                timePoint.patient_id = patient_id   # Set patient_id in timePoint to the ID of the user.
                timePoint.save()  # Commit the timePoint into the database
                return redirect('/Patient_Time_Points')
            else:  # Error if the user isn't authenticated
                messages.success(request, "Error. Unable to create time point. Please try again.")
        else:  # Error if the inputted form isn't valid
            messages.success(request, "Error. Unable to create time point. Please try again.")
    return render(request, "Patient_Create_Timepoint.html")


@login_required
@user_passes_test(is_patient)
def Patient_Time_Points(request):
    if request.user.is_authenticated:  # Check if the user exists
        patient_id = request.user.username[8:]  # Obtain patient_ID for the current User
        time_points = TimePoints.objects.filter(patient_id=patient_id, enddate__gt=datetime.date.today()).order_by('timepointnum')  # Obtain all of the patient's timepoints
        return render(request, "Patient_Time_Points.html",{'time_points': time_points})
    else:  # If the user isn't authenticated, redirect to home
        return redirect('/home')


@login_required
@user_passes_test(is_patient)
def Patient_Step_Time_Points(request, timepointtype):
    if request.user.is_authenticated:  # Check if the user exists
        patient_id = request.user.username[8:]  # Obtain patient_ID for the current User
        time_points = TimePoints.objects.filter(patient_id=patient_id, enddate__gt=datetime.date.today(), timepointtype=timepointtype).order_by('timepointnum')  # Obtain all of the patient's timepoints
        return render(request, "Patient_Time_Points.html",{'time_points': time_points})
    else:  # If the user isn't authenticated, redirect to home
        return redirect('/home')

@login_required
@user_passes_test(is_patient)
def Patient_Time_Point_Info(request, timepointnum):
    if request.user.is_authenticated:  # Check if the user exists
        try:
            patient_id = request.user.username[8:]  # Obtain patient_ID for the current User
            time_point = TimePoints.objects.get(patient_id=patient_id, timepointnum=timepointnum)  # Get the time_point corresponded to the timepointnum of the page
            provider_id = time_point.provider_id  # get the provider_ID for the associated time_point
            provider = Providers.objects.get(provider_id=provider_id)  # get the provider information associated with the provider_ID form time_point
            return render(request, "Patient_Time_Point_Info.html", {'time_point': time_point, 'provider': provider})
        except ObjectDoesNotExist:
            return redirect('/home')
    else:
        return redirect('/home')


@login_required
@user_passes_test(is_patient)
def Patient_Postsurgical_Stabilization(request):
    if request.user.is_authenticated:
        try:
            patient_id = request.user.username[8:]  # Obtain patient_ID for the current User
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
        except ObjectDoesNotExist: # Error in retrieving the patient entries
            return redirect('/home')
    else:
        return redirect('/SignIn')
    #return render(request, "Patient_Postsurgical_Stabilization.html")


@login_required
@user_passes_test(is_patient)
def Patient_Preprosthetic_Rehabilitation(request):
    if request.user.is_authenticated:
        try:
            patient_id = request.user.username[8:]  # Obtain patient_ID for the current User
            patient_entries = PatientEntries.objects.filter(patient_id=patient_id).order_by('entrydate')
            xValues = json.dumps([str(item.entrydate) for item in patient_entries])
            plsAvgValues = json.dumps([int(item.phantom_limb_ps_avg) for item in patient_entries])
            plsMaxValues = json.dumps([int(item.phantom_limb_ps_max) for item in patient_entries])
            rlsAvgValues = json.dumps([int(item.residual_limb_ps_avg) for item in patient_entries])
            rlsMaxValues = json.dumps([int(item.residual_limb_ps_max) for item in patient_entries])
            scsAvgValues = json.dumps([int(item.socket_comfort_score_avg) for item in patient_entries])
            scsMaxValues = json.dumps([int(item.socket_comfort_score_max) for item in patient_entries])
            #time_point = TimePoints.objects.get(patient_id=patient_id)
            return render(request, "Patient_Preprosthetic_Rehabilitation.html",{'xValues': xValues, 'plsAvgValues': plsAvgValues, 'plsMaxValues': plsMaxValues, 'rlsAvgValues': rlsAvgValues, 'rlsMaxValues': rlsMaxValues, 'scsAvgValues':scsAvgValues, 'scsMaxValues':scsMaxValues})  # , 'time_point': time_point
        except ObjectDoesNotExist: # Error in retrieving the patient entries
            return redirect('/home')
    else:
        return redirect('/SignIn')
    #return render(request, "Patient_Preprosthetic_Rehabilitation.html")


@login_required
@user_passes_test(is_patient)
def Patient_Limb_Healing(request):
    if request.user.is_authenticated:
        try:
            patient_id = request.user.username[8:]  # Obtain patient_ID for the current User
            patient_entries = PatientEntries.objects.filter(patient_id=patient_id).order_by('entrydate')
            xValues = json.dumps([str(item.entrydate) for item in patient_entries])
            plsAvgValues = json.dumps([int(item.phantom_limb_ps_avg) for item in patient_entries])
            plsMaxValues = json.dumps([int(item.phantom_limb_ps_max) for item in patient_entries])
            rlsAvgValues = json.dumps([int(item.residual_limb_ps_avg) for item in patient_entries])
            rlsMaxValues = json.dumps([int(item.residual_limb_ps_max) for item in patient_entries])
            scsAvgValues = json.dumps([int(item.socket_comfort_score_avg) for item in patient_entries])
            scsMaxValues = json.dumps([int(item.socket_comfort_score_max) for item in patient_entries])
            #time_point = TimePoints.objects.get(patient_id=patient_id)
            return render(request, "Patient_Limb_Healing.html",{'xValues': xValues, 'plsAvgValues': plsAvgValues, 'plsMaxValues': plsMaxValues, 'rlsAvgValues': rlsAvgValues, 'rlsMaxValues': rlsMaxValues, 'scsAvgValues':scsAvgValues, 'scsMaxValues':scsMaxValues})  # , 'time_point': time_point
        except ObjectDoesNotExist: # Error in retrieving the patient entries
            return redirect('/home')
    else:
        return redirect('/SignIn')
    #return render(request, "Patient_Limb_Healing.html")


@login_required
@user_passes_test(is_patient)
def Patient_Prosthetic_Fitting(request):
    if request.user.is_authenticated:
        try:
            patient_id = request.user.username[8:]  # Obtain patient_ID for the current User
            patient_entries = PatientEntries.objects.filter(patient_id=patient_id).order_by('entrydate')
            xValues = json.dumps([str(item.entrydate) for item in patient_entries])
            plsAvgValues = json.dumps([int(item.phantom_limb_ps_avg) for item in patient_entries])
            plsMaxValues = json.dumps([int(item.phantom_limb_ps_max) for item in patient_entries])
            rlsAvgValues = json.dumps([int(item.residual_limb_ps_avg) for item in patient_entries])
            rlsMaxValues = json.dumps([int(item.residual_limb_ps_max) for item in patient_entries])
            scsAvgValues = json.dumps([int(item.socket_comfort_score_avg) for item in patient_entries])
            scsMaxValues = json.dumps([int(item.socket_comfort_score_max) for item in patient_entries])
            #time_point = TimePoints.objects.get(patient_id=patient_id)
            return render(request, "Patient_Prosthetic_Fitting.html",{'xValues': xValues, 'plsAvgValues': plsAvgValues, 'plsMaxValues': plsMaxValues, 'rlsAvgValues': rlsAvgValues, 'rlsMaxValues': rlsMaxValues, 'scsAvgValues':scsAvgValues, 'scsMaxValues':scsMaxValues})  # , 'time_point': time_point
        except ObjectDoesNotExist: # Error in retrieving the patient entries
            return redirect('/home')
    else:
        return redirect('/SignIn')
    #return render(request, "Patient_Prosthetic_Fitting.html")


@login_required
@user_passes_test(is_patient)
def Patient_Prosthetic_Rehabilitation(request):
    if request.user.is_authenticated:
        try:
            patient_id = request.user.username[8:]  # Obtain patient_ID for the current User
            patient_entries = PatientEntries.objects.filter(patient_id=patient_id).order_by('entrydate')
            xValues = json.dumps([str(item.entrydate) for item in patient_entries])
            plsAvgValues = json.dumps([int(item.phantom_limb_ps_avg) for item in patient_entries])
            plsMaxValues = json.dumps([int(item.phantom_limb_ps_max) for item in patient_entries])
            rlsAvgValues = json.dumps([int(item.residual_limb_ps_avg) for item in patient_entries])
            rlsMaxValues = json.dumps([int(item.residual_limb_ps_max) for item in patient_entries])
            scsAvgValues = json.dumps([int(item.socket_comfort_score_avg) for item in patient_entries])
            scsMaxValues = json.dumps([int(item.socket_comfort_score_max) for item in patient_entries])
            #time_point = TimePoints.objects.get(patient_id=patient_id)
            return render(request, "Patient_Prosthetic_Rehabilitation.html",{'xValues': xValues, 'plsAvgValues': plsAvgValues, 'plsMaxValues': plsMaxValues, 'rlsAvgValues': rlsAvgValues, 'rlsMaxValues': rlsMaxValues, 'scsAvgValues':scsAvgValues, 'scsMaxValues':scsMaxValues})  # , 'time_point': time_point
        except ObjectDoesNotExist: # Error in retrieving the patient entries
            return redirect('/home')
    else:
        return redirect('/SignIn')
    #return render(request, "Patient_Prosthetic_Rehabilitation.html")


@login_required
@user_passes_test(is_provider)
def Provider(request):
    return render(request, "Provider_Home.html")

@login_required
@user_passes_test(is_provider)
def Provider_AmpPro_Survey(request):
    return render(request, "Provider_AmpPro_Survey.html")

@login_required
@user_passes_test(is_provider)
def Provider_AmpNoPro_Survey(request):
    return render(request, "Provider_AmpNoPro_Survey.html")

@login_required
@user_passes_test(is_provider)
def Provider_TimedGo_Test(request):
    return render(request, "Provider_TimedGo_Test.html")

@login_required
@user_passes_test(is_provider)
def Provider_6Min_Test(request):
    return render(request, "Provider_6Min_Test.html")


