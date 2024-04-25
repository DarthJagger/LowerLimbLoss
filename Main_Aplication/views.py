from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .forms import NewPatientForm, TimePointsForm, PatientEntryForm
from .models import *
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
                id = userPatient.patient_id  # Obtain the patient ID
                username = "Patient_" + str(id)
                user = authenticate(request, username=username, password=inputPassword)  # Authenticate the patient as a user
                if user is not None:
                    login(request, user)  # Log the user into the website if the user is correct
                    return redirect('/home')
                else:  # error for patients who don't have user account
                    messages.success(request, "Login Unsuccessful")
            except Patient.DoesNotExist:
                messages.success(request, "Login Unsuccessful")
        elif(Providers.objects.filter(email=inputEmail).exists()):
            try:
                userProvider = Providers.objects.get(email=inputEmail)  # Find the provider corresponding to the email
                id = userProvider.provider_id  # Obtain the provider ID
                username = "Provider" + str(id)
                user = authenticate(request, username=username, password=inputPassword)  # Authenticate the provider as a user
                if user is not None:
                    login(request, user)  # Log the user into the website if the user is correct
                    return redirect('/Provider')
                else:  # error for providers who don't have user account
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
            patient = Patients.objects.create(pname=pname, email=email, phone_number=phone_number)
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
                    messages.success(request, 'Authorization Successful')
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
    if request.user.is_authenticated:
        try:
            patient_id = request.user.username[8:]
            authorizations = Authorizations.objects.filter(patient_id=patient_id, astatus='A')
            providers = []
            for authorization in authorizations:
                providers.append(authorization.provider)
            authorizationRequests = Authorizations.objects.filter(patient_id=patient_id, astatus='R')
            requests = []
            for authorization in authorizationRequests:
                requests.append(authorization.provider)
            return render(request, 'Patient_Authorizations.html', {'providers': providers, 'requests': requests})
        except ObjectDoesNotExist:
            print("Error")
            messages.success(request, 'Error with Viewing Authorizations')
            return redirect('/home')
    else:
        return redirect('/SignIn')

@login_required
@user_passes_test(is_patient)
def Patient_Provider_Info(request, provider_id):
    if request.user.is_authenticated:
        try:
            provider = Providers.objects.get(provider_id=provider_id)
            return render(request, 'Patient_Provider_Info.html',{'provider': provider})
        except ObjectDoesNotExist:
            messages.success(request, 'Error with Viewing Authorized Provider')
            return redirect('/Patient_Authorizations')
    else:
        return redirect('/SignIn')

@login_required
@user_passes_test(is_patient)
def Patient_Auth_Request_Info(request, provider_id):
    if request.user.is_authenticated:
        if request.method == 'POST':
            try:
                patient_id = request.user.username[8:]
                authorization = Authorizations.objects.get(patient_id=patient_id, provider=provider_id)
                authorization.astatus = 'A'
                authorization.save()
                messages.success(request, 'Patient Successfully Authorized')
                return redirect('/Patient_Authorizations')
            except ObjectDoesNotExist:
                messages.success(request, 'Error with Authorizing Provider')
                return redirect('/Patient_Authorizations')
        else:
            try:
                provider = Providers.objects.get(provider_id=provider_id)
                return render(request, 'Patient_Auth_Request_Info.html',{'provider': provider})
            except ObjectDoesNotExist:
                messages.success(request, 'Error with Viewing Requesting Provider')
                return redirect('/Patient_Authorizations')
    else:
        return redirect('/SignIn')

@login_required
@user_passes_test(is_patient)
def Patient_Create_Timepoint(request):
    if request.method == "POST":
        updateRequest = request.POST.copy() # Create a copy of the post request info
        startdate = request.POST['startdate']
        enddate = request.POST['enddate']
        # Modify the start and end date strings to not include the pseudo timezone consideration "T"
        startdate = startdate.replace("T", " ")
        enddate = enddate.replace("T", " ")
        # Update the copy of the post request info
        updateRequest.update({'startdate': startdate, 'enddate':enddate})
        # Create the TimePoints form based on the updated copy
        form = TimePointsForm(updateRequest or None)
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
            messages.success(request, "Error. Unable to create time point. Please try again. Form Invalid")
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

            # add entries for graph
            patient_entries = PatientEntries.objects.filter(patient_id=patient_id).order_by('entrydate')
            xValues = json.dumps([str(item.entrydate) for item in patient_entries])
            plsAvgValues = json.dumps([int(item.phantom_limb_ps_avg) for item in patient_entries])
            plsMaxValues = json.dumps([int(item.phantom_limb_ps_max) for item in patient_entries])
            rlsAvgValues = json.dumps([int(item.residual_limb_ps_avg) for item in patient_entries])
            rlsMaxValues = json.dumps([int(item.residual_limb_ps_max) for item in patient_entries])
            scsAvgValues = json.dumps([int(item.socket_comfort_score_avg) for item in patient_entries])
            scsMaxValues = json.dumps([int(item.socket_comfort_score_max) for item in patient_entries])

            #add active timepoint entries
            time_point_before = TimePoints.objects.all().filter(patient_id=patient_id, timepointtype='Surgery',
                                                                enddate__gt=datetime.date.today())
            time_point_after = TimePoints.objects.all().filter(patient_id=patient_id,
                                                               timepointtype='Pre-Prosthetic Admission',
                                                               enddate__gt=datetime.date.today())

            pmModel = PlusMScores.objects.filter(patient=patient_id).order_by('scoredate')
            pmY = json.dumps([int(item.plus_m) for item in pmModel])
            pmX = json.dumps([str(item.scoredate) for item in pmModel])

            ANPModel = AmpnoproScores.objects.filter(patient=patient_id).order_by('scoredate')
            ANPY = json.dumps([int(item.ampnopro) for item in ANPModel])
            ANPX = json.dumps([str(item.scoredate) for item in ANPModel])

            APModel = AmpproScores.objects.filter(patient=patient_id).order_by('scoredate')
            APY = json.dumps([int(item.amppro) for item in APModel])
            APX = json.dumps([str(item.scoredate) for item in APModel])

            UAGModel = TimedupandgoScores.objects.filter(patient=patient_id).order_by('scoredate')
            UAGY = json.dumps([int(item.timedupandgo) for item in UAGModel])
            UAGX = json.dumps([str(item.scoredate) for item in UAGModel])

            WTModel = SixminwalktestScores.objects.filter(patient=patient_id).order_by('scoredate')
            WTY = json.dumps([int(item.sixminwalktest) for item in WTModel])
            WTX = json.dumps([str(item.scoredate) for item in WTModel])


            return render(request, "Patient_Postsurgical_Stabilization.html",
                          {'xValues': xValues, 'plsAvgValues': plsAvgValues,
                           'plsMaxValues': plsMaxValues, 'rlsAvgValues': rlsAvgValues,
                           'rlsMaxValues': rlsMaxValues, 'scsAvgValues': scsAvgValues,
                           'scsMaxValues': scsMaxValues, 'time_point_before': time_point_before,
                           'time_point_after': time_point_after, 'pmY': pmY,
                           'pmX': pmX, 'ANPY': ANPY, 'ANPX': ANPX, 'APY': APY,
                           'APX': APX, 'UAGY':UAGY,'UAGX':UAGX,'WTY':WTY,'WTX':WTX })

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
            time_point_before = TimePoints.objects.all().filter(patient_id=patient_id, timepointtype='Pre-Prosthetic Admission',
                                                                enddate__gt=datetime.date.today())
            time_point_after = TimePoints.objects.all().filter(patient_id=patient_id,
                                                               timepointtype='Pre-Prosthetic Discharge',
                                                               enddate__gt=datetime.date.today())
            pmModel = PlusMScores.objects.filter(patient=patient_id).order_by('scoredate')
            pmY = json.dumps([int(item.plus_m) for item in pmModel])
            pmX = json.dumps([str(item.scoredate) for item in pmModel])

            ANPModel = AmpnoproScores.objects.filter(patient=patient_id).order_by('scoredate')
            ANPY = json.dumps([int(item.ampnopro) for item in ANPModel])
            ANPX = json.dumps([str(item.scoredate) for item in ANPModel])

            APModel = AmpproScores.objects.filter(patient=patient_id).order_by('scoredate')
            APY = json.dumps([int(item.amppro) for item in APModel])
            APX = json.dumps([str(item.scoredate) for item in APModel])

            UAGModel = TimedupandgoScores.objects.filter(patient=patient_id).order_by('scoredate')
            UAGY = json.dumps([int(item.timedupandgo) for item in UAGModel])
            UAGX = json.dumps([str(item.scoredate) for item in UAGModel])

            WTModel = SixminwalktestScores.objects.filter(patient=patient_id).order_by('scoredate')
            WTY = json.dumps([int(item.sixminwalktest) for item in WTModel])
            WTX = json.dumps([str(item.scoredate) for item in WTModel])
            return render(request, "Patient_Preprosthetic_Rehabilitation.html",
                          {'xValues': xValues, 'plsAvgValues': plsAvgValues,
                           'plsMaxValues': plsMaxValues, 'rlsAvgValues': rlsAvgValues,
                           'rlsMaxValues': rlsMaxValues, 'scsAvgValues': scsAvgValues,
                           'scsMaxValues': scsMaxValues, 'time_point_before': time_point_before,
                           'time_point_after': time_point_after, 'pmY': pmY,
                           'pmX': pmX, 'ANPY': ANPY, 'ANPX': ANPX, 'APY': APY,
                           'APX': APX, 'UAGY':UAGY,'UAGX':UAGX,'WTY':WTY,'WTX':WTX })

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
            time_point_before = TimePoints.objects.all().filter(patient_id=patient_id, timepointtype='Pre-Prosthetic Discharge',
                                                                enddate__gt=datetime.date.today())
            time_point_after = TimePoints.objects.all().filter(patient_id=patient_id,
                                                               timepointtype='Functioning Evaluation',
                                                               enddate__gt=datetime.date.today())
            pmModel = PlusMScores.objects.filter(patient=patient_id).order_by('scoredate')
            pmY = json.dumps([int(item.plus_m) for item in pmModel])
            pmX = json.dumps([str(item.scoredate) for item in pmModel])

            ANPModel = AmpnoproScores.objects.filter(patient=patient_id).order_by('scoredate')
            ANPY = json.dumps([int(item.ampnopro) for item in ANPModel])
            ANPX = json.dumps([str(item.scoredate) for item in ANPModel])

            APModel = AmpproScores.objects.filter(patient=patient_id).order_by('scoredate')
            APY = json.dumps([int(item.amppro) for item in APModel])
            APX = json.dumps([str(item.scoredate) for item in APModel])

            UAGModel = TimedupandgoScores.objects.filter(patient=patient_id).order_by('scoredate')
            UAGY = json.dumps([int(item.timedupandgo) for item in UAGModel])
            UAGX = json.dumps([str(item.scoredate) for item in UAGModel])

            WTModel = SixminwalktestScores.objects.filter(patient=patient_id).order_by('scoredate')
            WTY = json.dumps([int(item.sixminwalktest) for item in WTModel])
            WTX = json.dumps([str(item.scoredate) for item in WTModel])
            return render(request, "Patient_Limb_Healing.html",
                          {'xValues': xValues, 'plsAvgValues': plsAvgValues,
                           'plsMaxValues': plsMaxValues, 'rlsAvgValues': rlsAvgValues,
                           'rlsMaxValues': rlsMaxValues, 'scsAvgValues': scsAvgValues,
                           'scsMaxValues': scsMaxValues, 'time_point_before': time_point_before,
                           'time_point_after': time_point_after, 'pmY': pmY,
                           'pmX': pmX, 'ANPY': ANPY, 'ANPX': ANPX, 'APY': APY,
                           'APX': APX, 'UAGY':UAGY,'UAGX':UAGX,'WTY':WTY,'WTX':WTX })

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
            time_point_before = TimePoints.objects.all().filter(patient_id=patient_id, timepointtype='Functioning Evaluation',
                                                                enddate__gt=datetime.date.today())
            time_point_after = TimePoints.objects.all().filter(patient_id=patient_id,
                                                               timepointtype='Prosthetic Admission',
                                                               enddate__gt=datetime.date.today())
            pmModel = PlusMScores.objects.filter(patient=patient_id).order_by('scoredate')
            pmY = json.dumps([int(item.plus_m) for item in pmModel])
            pmX = json.dumps([str(item.scoredate) for item in pmModel])

            ANPModel = AmpnoproScores.objects.filter(patient=patient_id).order_by('scoredate')
            ANPY = json.dumps([int(item.ampnopro) for item in ANPModel])
            ANPX = json.dumps([str(item.scoredate) for item in ANPModel])

            APModel = AmpproScores.objects.filter(patient=patient_id).order_by('scoredate')
            APY = json.dumps([int(item.amppro) for item in APModel])
            APX = json.dumps([str(item.scoredate) for item in APModel])

            UAGModel = TimedupandgoScores.objects.filter(patient=patient_id).order_by('scoredate')
            UAGY = json.dumps([int(item.timedupandgo) for item in UAGModel])
            UAGX = json.dumps([str(item.scoredate) for item in UAGModel])

            WTModel = SixminwalktestScores.objects.filter(patient=patient_id).order_by('scoredate')
            WTY = json.dumps([int(item.sixminwalktest) for item in WTModel])
            WTX = json.dumps([str(item.scoredate) for item in WTModel])
            return render(request, "Patient_Prosthetic_Fitting.html",
                          {'xValues': xValues, 'plsAvgValues': plsAvgValues,
                           'plsMaxValues': plsMaxValues, 'rlsAvgValues': rlsAvgValues,
                           'rlsMaxValues': rlsMaxValues, 'scsAvgValues': scsAvgValues,
                           'scsMaxValues': scsMaxValues, 'time_point_before': time_point_before,
                           'time_point_after': time_point_after, 'pmY': pmY,
                           'pmX': pmX, 'ANPY': ANPY, 'ANPX': ANPX, 'APY': APY,
                           'APX': APX, 'UAGY':UAGY,'UAGX':UAGX,'WTY':WTY,'WTX':WTX })

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
            time_point_before = TimePoints.objects.all().filter(patient_id=patient_id, timepointtype='Prosthetic Admission',
                                                                enddate__gt=datetime.date.today())
            time_point_after = TimePoints.objects.all().filter(patient_id=patient_id,
                                                               timepointtype='Prosthetic Discharge',
                                                               enddate__gt=datetime.date.today())

            pmModel = PlusMScores.objects.filter(patient=patient_id).order_by('scoredate')
            pmY = json.dumps([int(item.plus_m) for item in pmModel])
            pmX = json.dumps([str(item.scoredate) for item in pmModel])

            ANPModel = AmpnoproScores.objects.filter(patient=patient_id).order_by('scoredate')
            ANPY = json.dumps([int(item.ampnopro) for item in ANPModel])
            ANPX = json.dumps([str(item.scoredate) for item in ANPModel])

            APModel = AmpproScores.objects.filter(patient=patient_id).order_by('scoredate')
            APY = json.dumps([int(item.amppro) for item in APModel])
            APX = json.dumps([str(item.scoredate) for item in APModel])

            UAGModel = TimedupandgoScores.objects.filter(patient=patient_id).order_by('scoredate')
            UAGY = json.dumps([int(item.timedupandgo) for item in UAGModel])
            UAGX = json.dumps([str(item.scoredate) for item in UAGModel])

            WTModel = SixminwalktestScores.objects.filter(patient=patient_id).order_by('scoredate')
            WTY = json.dumps([int(item.sixminwalktest) for item in WTModel])
            WTX = json.dumps([str(item.scoredate) for item in WTModel])

            return render(request, "Patient_Prosthetic_Rehabilitation.html",
                          {'xValues': xValues, 'plsAvgValues': plsAvgValues,
                           'plsMaxValues': plsMaxValues, 'rlsAvgValues': rlsAvgValues,
                           'rlsMaxValues': rlsMaxValues, 'scsAvgValues': scsAvgValues,
                           'scsMaxValues': scsMaxValues, 'time_point_before': time_point_before,
                           'time_point_after': time_point_after, 'pmY': pmY,
                           'pmX': pmX, 'ANPY': ANPY, 'ANPX': ANPX, 'APY': APY,
                           'APX': APX, 'UAGY':UAGY,'UAGX':UAGX,'WTY':WTY,'WTX':WTX })

        except ObjectDoesNotExist: # Error in retrieving the patient entries
            return redirect('/home')
    else:
        return redirect('/SignIn')
    #return render(request, "Patient_Prosthetic_Rehabilitation.html")


@login_required
@user_passes_test(is_provider)
def Provider(request):
    provider_id = request.user.username[8:]
    confirmedAuths = Authorizations.objects.filter(provider=provider_id, astatus='A')
    confirmedPatients = [auth.patient for auth in confirmedAuths]
    requestedAuths = Authorizations.objects.filter(provider=provider_id, astatus='P')
    requestedPatients = [auth.patient for auth in requestedAuths]
    return render(request, "Provider_Table.html", {'provider': provider_id, 'confirmedPatients': confirmedPatients, 'requestedPatients':requestedPatients})

@login_required
@user_passes_test(is_provider)
def Provider_Create_Authorization(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            try:
                provider_id = request.user.username[8:]
                patient_email = request.POST['patient']
                patientTemp = Patients.objects.get(email=patient_email)
                patient_id = patientTemp.patient_id
                aStatus = 'R'  # Authorization status of R means that Provider requested authorization but Patient hasn't accepted
                auth_entry, created = Authorizations.objects.get_or_create(patient_id=patient_id, provider_id=provider_id, astatus=aStatus)
                if(created):
                    auth_entry.save()
                    messages.success(request, 'Authorization Successful')
                else:
                    messages.success(request, 'Patient Already Authorized')
                return render(request, 'Provider_Create_Authorization.html')
            except ObjectDoesNotExist:
                messages.success(request, 'Authorization Unsuccessful')
                return render(request, 'Provider_Create_Authorization.html')
        else:
            return render(request, 'Provider_Create_Authorization.html')
    else:
        return redirect('/SignIn')

@login_required
@user_passes_test(is_provider)
def Provider_Auth_Request_Info(request, patient_id):
    if request.user.is_authenticated:
        if request.method == "POST":
            try:
                provider_id = request.user.username[8:]
                authorization = Authorizations.objects.get(patient_id=patient_id, provider=provider_id)
                authorization.astatus = 'A'
                authorization.save()
                messages.success(request, 'Patient Authorization Successful')
                return redirect('/Provider')
            except ObjectDoesNotExist:
                messages.success(request, 'Error with Accepting Patient Authorization')
                return redirect('/Provider')
        else:
            try:
                patient = Patients.objects.get(patient_id=patient_id)
                return render(request, 'Provider_Auth_Request_Info.html', {'patient': patient})
            except ObjectDoesNotExist:
                messages.success(request, 'Error with Viewing Requesting Provider')
                return redirect('/Provider')
    else:
        return redirect('/SignIn')

@login_required
@user_passes_test(is_provider)
def Provider_AmpPro_Survey(request, patient_email):
    patient = get_object_or_404(Patients, email=patient_email)
    if request.method == 'POST':
        total_score = int(request.POST.get('totalScore_'))
        score = int( total_score )
        sound_time_input = request.POST.get('soundTimeInput')
        pros_time_input = request.POST.get('prosTimeInput')
        sound_time = int(0 if sound_time_input is None else sound_time_input)
        pros_time = int(0 if pros_time_input is None else pros_time_input)
        if score >= 0 and sound_time >= 0 and pros_time >= 0:
            patient = Patients.objects.get(email=patient_email)
            AmpproScores.objects.create(patient=patient, scoredate=datetime.datetime.today(), amppro=score, time_balanced_sound=sound_time, time_balanced_prosthesis=pros_time)
            messages.success(request, "Scores added successfully")
            return render(request, 'Provider_Amppro_Survey.html', {'patient': patient})
    else:
        return render(request, 'Provider_Amppro_Survey.html', {'patient': patient})

@login_required
@user_passes_test(is_provider)
def Provider_AmpNoPro_Survey(request, patient_email):
    patient = get_object_or_404(Patients, email=patient_email)
    if request.method == 'POST':
        total_score = int(request.POST.get('totalScore_'))

        if total_score >= 0:
            patient = Patients.objects.get(email=patient_email)
            AmpnoproScores.objects.create(patient=patient, scoredate=datetime.datetime.today(), ampnopro=total_score)
            messages.success(request, "Scores added successfully")
            return render(request, 'Provider_AmpNopro_Survey.html', {'patient': patient})
    else:
        return render(request, 'Provider_AmpNopro_Survey.html', {'patient': patient})

@login_required
@user_passes_test(is_provider)
def Provider_TimedGo_Test(request, patient_email):
    patient = get_object_or_404(Patients, email=patient_email)
    if request.method == 'POST':
        timed_go_time = request.POST.get('timedGoTime')
        if timed_go_time.isdigit():
            timed_go = int(timed_go_time)
            if timed_go >= 0:
                patient = Patients.objects.get(email=patient_email)
                TimedupandgoScores.objects.create(patient=patient, scoredate=datetime.datetime.today(), timedupandgo=timed_go)
                messages.success(request, "Score added successfully")
                return render(request, 'Provider_TimedGo_Test.html', {'patient': patient})
    else:
        return render(request, 'Provider_TimedGo_Test.html', {'patient': patient})

@login_required
@user_passes_test(is_provider)
def Provider_6Min_Test(request, patient_email):
    patient = get_object_or_404(Patients, email=patient_email)
    if request.method == 'POST':
        six_min_time = int(request.POST.get('minuteTime'))

        if six_min_time >= 0:
            patient = Patients.objects.get(email=patient_email)
            SixminwalktestScores.objects.create(patient=patient, scoredate=datetime.datetime.today(), sixminwalktest=six_min_time)
            messages.success(request, "Score added successfully")
            return render(request, 'Provider_6Min_Test.html', {'patient': patient})
    else:
        return render(request, 'Provider_6Min_Test.html', {'patient': patient})

@login_required
@user_passes_test(is_provider)
def Provider_PlusM_Score(request, patient_email):
    patient = get_object_or_404(Patients, email=patient_email)
    if request.method == 'POST':
        plus_m_time = request.POST.get('plusMTime')
        if plus_m_time.isdigit():
            plus_m = int(plus_m_time)
            if plus_m >= 0:
                patient = Patients.objects.get(email=patient_email)
                PlusMScores.objects.create(patient=patient, scoredate=datetime.datetime.today(), plus_m=plus_m)
                messages.success(request, "Score added successfully")
                return render(request, 'Provider_PlusM_Score.html', {'patient': patient})
    else:
        return render(request, 'Provider_PlusM_Score.html', {'patient': patient})

@login_required
@user_passes_test(is_provider)
def Provider_Postsurgical_Stabilization(request, patient_email):
    if request.user.is_authenticated:
        try:
            # Retrieve patient information using the provided email
            patient_id = get_object_or_404(Patients, email=patient_email)
            # Retrieve patient entries for the specified patient
            patient_entries = PatientEntries.objects.filter(patient_id=patient_id.patient_id).order_by('entrydate')
            # Process patient entries and prepare data for rendering
            xValues = json.dumps([str(item.entrydate) for item in patient_entries])
            plsAvgValues = json.dumps([int(item.phantom_limb_ps_avg) for item in patient_entries])
            plsMaxValues = json.dumps([int(item.phantom_limb_ps_max) for item in patient_entries])
            rlsAvgValues = json.dumps([int(item.residual_limb_ps_avg) for item in patient_entries])
            rlsMaxValues = json.dumps([int(item.residual_limb_ps_max) for item in patient_entries])
            scsAvgValues = json.dumps([int(item.socket_comfort_score_avg) for item in patient_entries])
            scsMaxValues = json.dumps([int(item.socket_comfort_score_max) for item in patient_entries])

            time_point_before = TimePoints.objects.all().filter(patient_id=patient_id,
                                                                timepointtype='Prosthetic Admission',
                                                                enddate__gt=datetime.date.today())
            time_point_after = TimePoints.objects.all().filter(patient_id=patient_id,
                                                               timepointtype='Prosthetic Discharge',
                                                               enddate__gt=datetime.date.today())

            pmModel = PlusMScores.objects.filter(patient=patient_id).order_by('scoredate')
            pmY = json.dumps([int(item.plus_m) for item in pmModel])
            pmX = json.dumps([str(item.scoredate) for item in pmModel])

            ANPModel = AmpnoproScores.objects.filter(patient=patient_id).order_by('scoredate')
            ANPY = json.dumps([int(item.ampnopro) for item in ANPModel])
            ANPX = json.dumps([str(item.scoredate) for item in ANPModel])

            APModel = AmpproScores.objects.filter(patient=patient_id).order_by('scoredate')
            APY = json.dumps([int(item.amppro) for item in APModel])
            APX = json.dumps([str(item.scoredate) for item in APModel])

            UAGModel = TimedupandgoScores.objects.filter(patient=patient_id).order_by('scoredate')
            UAGY = json.dumps([int(item.timedupandgo) for item in UAGModel])
            UAGX = json.dumps([str(item.scoredate) for item in UAGModel])

            WTModel = SixminwalktestScores.objects.filter(patient=patient_id).order_by('scoredate')
            WTY = json.dumps([int(item.sixminwalktest) for item in WTModel])
            WTX = json.dumps([str(item.scoredate) for item in WTModel])
            return render(request, "Provider_Postsurgical_Stabilization.html",
                          {'patient': patient_id,'xValues': xValues, 'plsAvgValues': plsAvgValues,
                           'plsMaxValues': plsMaxValues, 'rlsAvgValues': rlsAvgValues,
                           'rlsMaxValues': rlsMaxValues, 'scsAvgValues': scsAvgValues,
                           'scsMaxValues': scsMaxValues, 'time_point_before': time_point_before,
                           'time_point_after': time_point_after, 'pmY': pmY,
                           'pmX': pmX, 'ANPY': ANPY, 'ANPX': ANPX, 'APY': APY,
                           'APX': APX, 'UAGY':UAGY,'UAGX':UAGX,'WTY':WTY,'WTX':WTX })
        except ObjectDoesNotExist: # Error in retrieving the patient entries
            return redirect('/home')  # Redirect to home page if patient entries not found
    else:
        return redirect('/SignIn')
    #if request.user.is_authenticated:
    #    try:
    #        patient_id = request.user.username[8:]  # Obtain patient_ID for the current User
    #        patient_entries = PatientEntries.objects.filter(patient_id=patient_id).order_by('entrydate')
    #        xValues = json.dumps([str(item.entrydate) for item in patient_entries])
    #        plsAvgValues = json.dumps([int(item.phantom_limb_ps_avg) for item in patient_entries])
    #        plsMaxValues = json.dumps([int(item.phantom_limb_ps_max) for item in patient_entries])
    #        rlsAvgValues = json.dumps([int(item.residual_limb_ps_avg) for item in patient_entries])
    #        rlsMaxValues = json.dumps([int(item.residual_limb_ps_max) for item in patient_entries])
    #        scsAvgValues = json.dumps([int(item.socket_comfort_score_avg) for item in patient_entries])
    #        scsMaxValues = json.dumps([int(item.socket_comfort_score_max) for item in patient_entries])
    #        #time_point = TimePoints.objects.get(patient_id=patient_id)
    #        return render(request, "Provider_Postsurgical_Stabilization.html",{'xValues': xValues, 'plsAvgValues': plsAvgValues, 'plsMaxValues': plsMaxValues, 'rlsAvgValues': rlsAvgValues, 'rlsMaxValues': rlsMaxValues, 'scsAvgValues':scsAvgValues, 'scsMaxValues':scsMaxValues})  # , 'time_point': time_point
    #    except ObjectDoesNotExist: # Error in retrieving the patient entries
    #        return redirect('/home')
    #else:
    #    return redirect('/SignIn')
    ##return render(request, "Patient_Postsurgical_Stabilization.html")


@login_required
@user_passes_test(is_provider)
def Provider_Preprosthetic_Rehabilitation(request, patient_email):
    if request.user.is_authenticated:
        try:
            # Retrieve patient information using the provided email
            patient_id = get_object_or_404(Patients, email=patient_email)
            # Retrieve patient entries for the specified patient
            patient_entries = PatientEntries.objects.filter(patient_id=patient_id.patient_id).order_by('entrydate')
            # Process patient entries and prepare data for rendering
            xValues = json.dumps([str(item.entrydate) for item in patient_entries])
            plsAvgValues = json.dumps([int(item.phantom_limb_ps_avg) for item in patient_entries])
            plsMaxValues = json.dumps([int(item.phantom_limb_ps_max) for item in patient_entries])
            rlsAvgValues = json.dumps([int(item.residual_limb_ps_avg) for item in patient_entries])
            rlsMaxValues = json.dumps([int(item.residual_limb_ps_max) for item in patient_entries])
            scsAvgValues = json.dumps([int(item.socket_comfort_score_avg) for item in patient_entries])
            scsMaxValues = json.dumps([int(item.socket_comfort_score_max) for item in patient_entries])

            time_point_before = TimePoints.objects.all().filter(patient_id=patient_id,
                                                                timepointtype='Prosthetic Admission',
                                                                enddate__gt=datetime.date.today())
            time_point_after = TimePoints.objects.all().filter(patient_id=patient_id,
                                                               timepointtype='Prosthetic Discharge',
                                                               enddate__gt=datetime.date.today())

            pmModel = PlusMScores.objects.filter(patient=patient_id).order_by('scoredate')
            pmY = json.dumps([int(item.plus_m) for item in pmModel])
            pmX = json.dumps([str(item.scoredate) for item in pmModel])

            ANPModel = AmpnoproScores.objects.filter(patient=patient_id).order_by('scoredate')
            ANPY = json.dumps([int(item.ampnopro) for item in ANPModel])
            ANPX = json.dumps([str(item.scoredate) for item in ANPModel])

            APModel = AmpproScores.objects.filter(patient=patient_id).order_by('scoredate')
            APY = json.dumps([int(item.amppro) for item in APModel])
            APX = json.dumps([str(item.scoredate) for item in APModel])

            UAGModel = TimedupandgoScores.objects.filter(patient=patient_id).order_by('scoredate')
            UAGY = json.dumps([int(item.timedupandgo) for item in UAGModel])
            UAGX = json.dumps([str(item.scoredate) for item in UAGModel])

            WTModel = SixminwalktestScores.objects.filter(patient=patient_id).order_by('scoredate')
            WTY = json.dumps([int(item.sixminwalktest) for item in WTModel])
            WTX = json.dumps([str(item.scoredate) for item in WTModel])
            return render(request, "Provider_Preprosthetic_Rehabilitation.html",
                          {'patient': patient_id, 'xValues': xValues, 'plsAvgValues': plsAvgValues,
                           'plsMaxValues': plsMaxValues, 'rlsAvgValues': rlsAvgValues,
                           'rlsMaxValues': rlsMaxValues, 'scsAvgValues': scsAvgValues,
                           'scsMaxValues': scsMaxValues, 'time_point_before': time_point_before,
                           'time_point_after': time_point_after, 'pmY': pmY,
                           'pmX': pmX, 'ANPY': ANPY, 'ANPX': ANPX, 'APY': APY,
                           'APX': APX, 'UAGY':UAGY,'UAGX':UAGX,'WTY':WTY,'WTX':WTX })
        except ObjectDoesNotExist: # Error in retrieving the patient entries
            return redirect('/home')  # Redirect to home page if patient entries not found
    else:
        return redirect('/SignIn')
    #if request.user.is_authenticated:
    #    try:
    #        patient_id = request.user.username[8:]  # Obtain patient_ID for the current User
    #        patient_entries = PatientEntries.objects.filter(patient_id=patient_id).order_by('entrydate')
    #        xValues = json.dumps([str(item.entrydate) for item in patient_entries])
    #        plsAvgValues = json.dumps([int(item.phantom_limb_ps_avg) for item in patient_entries])
    #        plsMaxValues = json.dumps([int(item.phantom_limb_ps_max) for item in patient_entries])
    #        rlsAvgValues = json.dumps([int(item.residual_limb_ps_avg) for item in patient_entries])
    #        rlsMaxValues = json.dumps([int(item.residual_limb_ps_max) for item in patient_entries])
    #        scsAvgValues = json.dumps([int(item.socket_comfort_score_avg) for item in patient_entries])
    #        scsMaxValues = json.dumps([int(item.socket_comfort_score_max) for item in patient_entries])
    #        #time_point = TimePoints.objects.get(patient_id=patient_id)
    #        return render(request, "Provider_Preprosthetic_Rehabilitation.html",{'xValues': xValues, 'plsAvgValues': plsAvgValues, 'plsMaxValues': plsMaxValues, 'rlsAvgValues': rlsAvgValues, 'rlsMaxValues': rlsMaxValues, 'scsAvgValues':scsAvgValues, 'scsMaxValues':scsMaxValues})  # , 'time_point': time_point
    #    except ObjectDoesNotExist: # Error in retrieving the patient entries
    #        return redirect('/home')
    #else:
    #    return redirect('/SignIn')
    ##return render(request, "Patient_Preprosthetic_Rehabilitation.html")


@login_required
@user_passes_test(is_provider)
def Provider_Limb_Healing(request, patient_email):
    if request.user.is_authenticated:
        try:
            # Retrieve patient information using the provided email
            patient_id = get_object_or_404(Patients, email=patient_email)
            # Retrieve patient entries for the specified patient
            patient_entries = PatientEntries.objects.filter(patient_id=patient_id.patient_id).order_by('entrydate')
            # Process patient entries and prepare data for rendering
            xValues = json.dumps([str(item.entrydate) for item in patient_entries])
            plsAvgValues = json.dumps([int(item.phantom_limb_ps_avg) for item in patient_entries])
            plsMaxValues = json.dumps([int(item.phantom_limb_ps_max) for item in patient_entries])
            rlsAvgValues = json.dumps([int(item.residual_limb_ps_avg) for item in patient_entries])
            rlsMaxValues = json.dumps([int(item.residual_limb_ps_max) for item in patient_entries])
            scsAvgValues = json.dumps([int(item.socket_comfort_score_avg) for item in patient_entries])
            scsMaxValues = json.dumps([int(item.socket_comfort_score_max) for item in patient_entries])

            time_point_before = TimePoints.objects.all().filter(patient_id=patient_id,
                                                                timepointtype='Prosthetic Admission',
                                                                enddate__gt=datetime.date.today())
            time_point_after = TimePoints.objects.all().filter(patient_id=patient_id,
                                                               timepointtype='Prosthetic Discharge',
                                                               enddate__gt=datetime.date.today())

            pmModel = PlusMScores.objects.filter(patient=patient_id).order_by('scoredate')
            pmY = json.dumps([int(item.plus_m) for item in pmModel])
            pmX = json.dumps([str(item.scoredate) for item in pmModel])

            ANPModel = AmpnoproScores.objects.filter(patient=patient_id).order_by('scoredate')
            ANPY = json.dumps([int(item.ampnopro) for item in ANPModel])
            ANPX = json.dumps([str(item.scoredate) for item in ANPModel])

            APModel = AmpproScores.objects.filter(patient=patient_id).order_by('scoredate')
            APY = json.dumps([int(item.amppro) for item in APModel])
            APX = json.dumps([str(item.scoredate) for item in APModel])

            UAGModel = TimedupandgoScores.objects.filter(patient=patient_id).order_by('scoredate')
            UAGY = json.dumps([int(item.timedupandgo) for item in UAGModel])
            UAGX = json.dumps([str(item.scoredate) for item in UAGModel])

            WTModel = SixminwalktestScores.objects.filter(patient=patient_id).order_by('scoredate')
            WTY = json.dumps([int(item.sixminwalktest) for item in WTModel])
            WTX = json.dumps([str(item.scoredate) for item in WTModel])
            return render(request, "Provider_Limb_Healing.html",
                          {'patient': patient_id,'xValues': xValues, 'plsAvgValues': plsAvgValues,
                           'plsMaxValues': plsMaxValues, 'rlsAvgValues': rlsAvgValues,
                           'rlsMaxValues': rlsMaxValues, 'scsAvgValues': scsAvgValues,
                           'scsMaxValues': scsMaxValues, 'time_point_before': time_point_before,
                           'time_point_after': time_point_after, 'pmY': pmY,
                           'pmX': pmX, 'ANPY': ANPY, 'ANPX': ANPX, 'APY': APY,
                           'APX': APX, 'UAGY':UAGY,'UAGX':UAGX,'WTY':WTY,'WTX':WTX })
        except ObjectDoesNotExist: # Error in retrieving the patient entries
            return redirect('/home')  # Redirect to home page if patient entries not found
    else:
        return redirect('/SignIn')
    #if request.user.is_authenticated:
    #    try:
    #        patient_id = request.user.username[8:]  # Obtain patient_ID for the current User
    #        patient_entries = PatientEntries.objects.filter(patient_id=patient_id).order_by('entrydate')
    #        xValues = json.dumps([str(item.entrydate) for item in patient_entries])
    #        plsAvgValues = json.dumps([int(item.phantom_limb_ps_avg) for item in patient_entries])
    #        plsMaxValues = json.dumps([int(item.phantom_limb_ps_max) for item in patient_entries])
    #        rlsAvgValues = json.dumps([int(item.residual_limb_ps_avg) for item in patient_entries])
    #        rlsMaxValues = json.dumps([int(item.residual_limb_ps_max) for item in patient_entries])
    #        scsAvgValues = json.dumps([int(item.socket_comfort_score_avg) for item in patient_entries])
    #        scsMaxValues = json.dumps([int(item.socket_comfort_score_max) for item in patient_entries])
    #        #time_point = TimePoints.objects.get(patient_id=patient_id)
    #        return render(request, "Provider_Limb_Healing.html",{'xValues': xValues, 'plsAvgValues': plsAvgValues, 'plsMaxValues': plsMaxValues, 'rlsAvgValues': rlsAvgValues, 'rlsMaxValues': rlsMaxValues, 'scsAvgValues':scsAvgValues, 'scsMaxValues':scsMaxValues})  # , 'time_point': time_point
    #    except ObjectDoesNotExist: # Error in retrieving the patient entries
    #        return redirect('/home')
    #else:
    #    return redirect('/SignIn')
    #return render(request, "Patient_Limb_Healing.html")


@login_required
@user_passes_test(is_provider)
def Provider_Prosthetic_Fitting(request, patient_email):
    if request.user.is_authenticated:
        try:
            # Retrieve patient information using the provided email
            patient_id = get_object_or_404(Patients, email=patient_email)
            # Retrieve patient entries for the specified patient
            patient_entries = PatientEntries.objects.filter(patient_id=patient_id.patient_id).order_by('entrydate')
            # Process patient entries and prepare data for rendering
            xValues = json.dumps([str(item.entrydate) for item in patient_entries])
            plsAvgValues = json.dumps([int(item.phantom_limb_ps_avg) for item in patient_entries])
            plsMaxValues = json.dumps([int(item.phantom_limb_ps_max) for item in patient_entries])
            rlsAvgValues = json.dumps([int(item.residual_limb_ps_avg) for item in patient_entries])
            rlsMaxValues = json.dumps([int(item.residual_limb_ps_max) for item in patient_entries])
            scsAvgValues = json.dumps([int(item.socket_comfort_score_avg) for item in patient_entries])
            scsMaxValues = json.dumps([int(item.socket_comfort_score_max) for item in patient_entries])

            time_point_before = TimePoints.objects.all().filter(patient_id=patient_id,
                                                                timepointtype='Prosthetic Admission',
                                                                enddate__gt=datetime.date.today())
            time_point_after = TimePoints.objects.all().filter(patient_id=patient_id,
                                                               timepointtype='Prosthetic Discharge',
                                                               enddate__gt=datetime.date.today())

            pmModel = PlusMScores.objects.filter(patient=patient_id).order_by('scoredate')
            pmY = json.dumps([int(item.plus_m) for item in pmModel])
            pmX = json.dumps([str(item.scoredate) for item in pmModel])

            ANPModel = AmpnoproScores.objects.filter(patient=patient_id).order_by('scoredate')
            ANPY = json.dumps([int(item.ampnopro) for item in ANPModel])
            ANPX = json.dumps([str(item.scoredate) for item in ANPModel])

            APModel = AmpproScores.objects.filter(patient=patient_id).order_by('scoredate')
            APY = json.dumps([int(item.amppro) for item in APModel])
            APX = json.dumps([str(item.scoredate) for item in APModel])

            UAGModel = TimedupandgoScores.objects.filter(patient=patient_id).order_by('scoredate')
            UAGY = json.dumps([int(item.timedupandgo) for item in UAGModel])
            UAGX = json.dumps([str(item.scoredate) for item in UAGModel])

            WTModel = SixminwalktestScores.objects.filter(patient=patient_id).order_by('scoredate')
            WTY = json.dumps([int(item.sixminwalktest) for item in WTModel])
            WTX = json.dumps([str(item.scoredate) for item in WTModel])
            return render(request, "Provider_Prosthetic_Fitting.html",
                          {'patient': patient_id,'xValues': xValues, 'plsAvgValues': plsAvgValues,
                           'plsMaxValues': plsMaxValues, 'rlsAvgValues': rlsAvgValues,
                           'rlsMaxValues': rlsMaxValues, 'scsAvgValues': scsAvgValues,
                           'scsMaxValues': scsMaxValues, 'time_point_before': time_point_before,
                           'time_point_after': time_point_after, 'pmY': pmY,
                           'pmX': pmX, 'ANPY': ANPY, 'ANPX': ANPX, 'APY': APY,
                           'APX': APX, 'UAGY':UAGY,'UAGX':UAGX,'WTY':WTY,'WTX':WTX })
        except ObjectDoesNotExist: # Error in retrieving the patient entries
            return redirect('/home')  # Redirect to home page if patient entries not found
    else:
        return redirect('/SignIn')
    #if request.user.is_authenticated:
    #    try:
    #        patient_id = request.user.username[8:]  # Obtain patient_ID for the current User
    #        patient_entries = PatientEntries.objects.filter(patient_id=patient_id).order_by('entrydate')
    #        xValues = json.dumps([str(item.entrydate) for item in patient_entries])
    #        plsAvgValues = json.dumps([int(item.phantom_limb_ps_avg) for item in patient_entries])
    #        plsMaxValues = json.dumps([int(item.phantom_limb_ps_max) for item in patient_entries])
    #        rlsAvgValues = json.dumps([int(item.residual_limb_ps_avg) for item in patient_entries])
    #        rlsMaxValues = json.dumps([int(item.residual_limb_ps_max) for item in patient_entries])
    #        scsAvgValues = json.dumps([int(item.socket_comfort_score_avg) for item in patient_entries])
    #        scsMaxValues = json.dumps([int(item.socket_comfort_score_max) for item in patient_entries])
    #        #time_point = TimePoints.objects.get(patient_id=patient_id)
    #        return render(request, "Provider_Prosthetic_Fitting.html",{'xValues': xValues, 'plsAvgValues': plsAvgValues, 'plsMaxValues': plsMaxValues, 'rlsAvgValues': rlsAvgValues, 'rlsMaxValues': rlsMaxValues, 'scsAvgValues':scsAvgValues, 'scsMaxValues':scsMaxValues})  # , 'time_point': time_point
    #    except ObjectDoesNotExist: # Error in retrieving the patient entries
    #        return redirect('/home')
    #else:
    #    return redirect('/SignIn')
    ##return render(request, "Patient_Prosthetic_Fitting.html")


@login_required
@user_passes_test(is_provider)
def Provider_Prosthetic_Rehabilitation(request, patient_email):
    if request.user.is_authenticated:
        try:
            # Retrieve patient information using the provided email
            patient_id = get_object_or_404(Patients, email=patient_email)
            # Retrieve patient entries for the specified patient
            patient_entries = PatientEntries.objects.filter(patient_id=patient_id.patient_id).order_by('entrydate')
            # Process patient entries and prepare data for rendering
            xValues = json.dumps([str(item.entrydate) for item in patient_entries])
            plsAvgValues = json.dumps([int(item.phantom_limb_ps_avg) for item in patient_entries])
            plsMaxValues = json.dumps([int(item.phantom_limb_ps_max) for item in patient_entries])
            rlsAvgValues = json.dumps([int(item.residual_limb_ps_avg) for item in patient_entries])
            rlsMaxValues = json.dumps([int(item.residual_limb_ps_max) for item in patient_entries])
            scsAvgValues = json.dumps([int(item.socket_comfort_score_avg) for item in patient_entries])
            scsMaxValues = json.dumps([int(item.socket_comfort_score_max) for item in patient_entries])

            time_point_before = TimePoints.objects.all().filter(patient_id=patient_id,
                                                                timepointtype='Prosthetic Admission',
                                                                enddate__gt=datetime.date.today())
            time_point_after = TimePoints.objects.all().filter(patient_id=patient_id,
                                                               timepointtype='Prosthetic Discharge',
                                                               enddate__gt=datetime.date.today())

            pmModel = PlusMScores.objects.filter(patient=patient_id).order_by('scoredate')
            pmY = json.dumps([int(item.plus_m) for item in pmModel])
            pmX = json.dumps([str(item.scoredate) for item in pmModel])

            ANPModel = AmpnoproScores.objects.filter(patient=patient_id).order_by('scoredate')
            ANPY = json.dumps([int(item.ampnopro) for item in ANPModel])
            ANPX = json.dumps([str(item.scoredate) for item in ANPModel])

            APModel = AmpproScores.objects.filter(patient=patient_id).order_by('scoredate')
            APY = json.dumps([int(item.amppro) for item in APModel])
            APX = json.dumps([str(item.scoredate) for item in APModel])

            UAGModel = TimedupandgoScores.objects.filter(patient=patient_id).order_by('scoredate')
            UAGY = json.dumps([int(item.timedupandgo) for item in UAGModel])
            UAGX = json.dumps([str(item.scoredate) for item in UAGModel])

            WTModel = SixminwalktestScores.objects.filter(patient=patient_id).order_by('scoredate')
            WTY = json.dumps([int(item.sixminwalktest) for item in WTModel])
            WTX = json.dumps([str(item.scoredate) for item in WTModel])
            return render(request, "Provider_Prosthetic_Rehabilitation.html",
                          {'patient': patient_id,'xValues': xValues, 'plsAvgValues': plsAvgValues,
                           'plsMaxValues': plsMaxValues, 'rlsAvgValues': rlsAvgValues,
                           'rlsMaxValues': rlsMaxValues, 'scsAvgValues': scsAvgValues,
                           'scsMaxValues': scsMaxValues, 'time_point_before': time_point_before,
                           'time_point_after': time_point_after, 'pmY': pmY,
                           'pmX': pmX, 'ANPY': ANPY, 'ANPX': ANPX, 'APY': APY,
                           'APX': APX, 'UAGY':UAGY,'UAGX':UAGX,'WTY':WTY,'WTX':WTX })
        except ObjectDoesNotExist: # Error in retrieving the patient entries
            return redirect('/home')  # Redirect to home page if patient entries not found
    else:
        return redirect('/SignIn')
    #if request.user.is_authenticated:
    #    try:
    #        patient_id = request.user.username[8:]  # Obtain patient_ID for the current User
    #        patient_entries = PatientEntries.objects.filter(patient_id=patient_id).order_by('entrydate')
    #        xValues = json.dumps([str(item.entrydate) for item in patient_entries])
    #        plsAvgValues = json.dumps([int(item.phantom_limb_ps_avg) for item in patient_entries])
    #        plsMaxValues = json.dumps([int(item.phantom_limb_ps_max) for item in patient_entries])
    #        rlsAvgValues = json.dumps([int(item.residual_limb_ps_avg) for item in patient_entries])
    #        rlsMaxValues = json.dumps([int(item.residual_limb_ps_max) for item in patient_entries])
    #        scsAvgValues = json.dumps([int(item.socket_comfort_score_avg) for item in patient_entries])
    #        scsMaxValues = json.dumps([int(item.socket_comfort_score_max) for item in patient_entries])
    #        #time_point = TimePoints.objects.get(patient_id=patient_id)
    #        return render(request, "Provider_Prosthetic_Rehabilitation.html",{'xValues': xValues, 'plsAvgValues': plsAvgValues, 'plsMaxValues': plsMaxValues, 'rlsAvgValues': rlsAvgValues, 'rlsMaxValues': rlsMaxValues, 'scsAvgValues':scsAvgValues, 'scsMaxValues':scsMaxValues})  # , 'time_point': time_point
    #    except ObjectDoesNotExist: # Error in retrieving the patient entries
    #        return redirect('/home')
    #else:
    #    return redirect('/SignIn')
    ##return render(request, "Patient_Prosthetic_Rehabilitation.html")


@login_required
@user_passes_test(is_provider)
def Provider_Home(request, patient_email):
    patient = get_object_or_404(Patients, email=patient_email)
    return render(request, 'Provider_base_template.html', {'patient': patient})#Provider_Home.html
    #patient = Patient.objects.get(pk=patient)
    #return render(request, 'Provider_Home.html', {'patient': patient})

@login_required
def Admin_Create_Provider(request):
    if request.user.is_staff:
        try:
            if request.method == "POST":
                email = request.POST["email"]
                password = request.POST["ppassword"]
                password_confirm = request.POST["password_confirm"]
                priorPatients = Patients.objects.filter(email=email)
                priorProviders = Providers.objects.filter(email=email)
                if (priorPatients.exists() or priorProviders.exists() or (not (password == password_confirm))):  # Check to see if the email is in use
                    messages.success(request, "Sign Up Unsuccessful")
                    return render(request, "Admin_Create_Provider.html")
                else:
                    pname = request.POST["pname"]
                    phone_number = request.POST["phone_number"]
                    specialty = request.POST["specialty"]
                    organization = request.POST["organization"]
                    provider = Providers.objects.create(pname=pname, phone_number=phone_number, email=email, specialty=specialty, organization=organization)
                    userTemp = Providers.objects.get(email=email)
                    group = Group.objects.get(name="Provider")
                    id = userTemp.provider_id  # TODO: Modifier to separate between Patient and Provider users (Later signup code)
                    username = "Provider" + str(
                        id)  # Construct a backend username that starts with Patient for patients
                    user = User.objects.create_user(username, email, password)  # Create a new user in Django
                    user.save()  # Creates a user in the django users database corresponding to the Patient
                    user.groups.add(group)
                    return redirect('/admin')
            else:
                return render(request, "Admin_Create_Provider.html")
        except ObjectDoesNotExist:
            return render(request, "Admin_Create_Provider.html")
    else:
        return redirect('/admin')
