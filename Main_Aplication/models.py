# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Patients(models.Model):
    patient_id = models.AutoField(db_column='Patient_ID', primary_key=True)  # Field name made lowercase.
    pname = models.CharField(db_column='PName', max_length=255)  # Field name made lowercase.
    phone_number = models.CharField(db_column='Phone_Number', max_length=11, blank=True, null=True)  # Field name made lowercase.
    email = models.CharField(db_column='Email', unique=True, max_length=255, blank=True, null=True)  # Field name made lowercase.
    ppassword = models.CharField(db_column='PPassword', max_length=255)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'patients'


class Providers(models.Model):
    provider_id = models.AutoField(db_column='Provider_ID', primary_key=True)  # Field name made lowercase.
    pname = models.CharField(db_column='PName', max_length=255)  # Field name made lowercase.
    phone_number = models.CharField(db_column='Phone_Number', max_length=11, blank=True, null=True)  # Field name made lowercase.
    email = models.CharField(db_column='Email', unique=True, max_length=255, blank=True, null=True)  # Field name made lowercase.
    specialty = models.CharField(db_column='Specialty', max_length=255, blank=True, null=True)  # Field name made lowercase.
    organization = models.CharField(db_column='Organization', max_length=255, blank=True, null=True)  # Field name made lowercase.
    ppassword = models.CharField(db_column='PPassword', max_length=255)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'providers'


class AmpnoproScores(models.Model):
    patient = models.OneToOneField('Patients', models.DO_NOTHING, db_column='Patient_ID', primary_key=True)  # Field name made lowercase. The composite primary key (Patient_ID, ScoreDate) found, that is not supported. The first column is selected.
    scoredate = models.DateTimeField(db_column='ScoreDate')  # Field name made lowercase.
    ampnopro = models.DecimalField(db_column='AmpNoPro', max_digits=10, decimal_places=0)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ampnopro_scores'
        unique_together = (('patient', 'scoredate'),)


class AmpproScores(models.Model):
    patient = models.OneToOneField('Patients', models.DO_NOTHING, db_column='Patient_ID', primary_key=True)  # Field name made lowercase. The composite primary key (Patient_ID, ScoreDate) found, that is not supported. The first column is selected.
    scoredate = models.DateTimeField(db_column='ScoreDate')  # Field name made lowercase.
    amppro = models.DecimalField(db_column='AmpPro', max_digits=10, decimal_places=0)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'amppro_scores'
        unique_together = (('patient', 'scoredate'),)


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class Authorizations(models.Model):
    patient = models.OneToOneField('Patients', models.DO_NOTHING, db_column='Patient_ID', primary_key=True)  # Field name made lowercase. The composite primary key (Patient_ID, Provider_ID) found, that is not supported. The first column is selected.
    provider = models.ForeignKey('Providers', models.DO_NOTHING, db_column='Provider_ID')  # Field name made lowercase.
    astatus = models.CharField(db_column='AStatus', max_length=1)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'authorizations'
        unique_together = (('patient', 'provider'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class PatientEntries(models.Model):
    patient = models.OneToOneField('Patients', models.DO_NOTHING, db_column='Patient_ID', primary_key=True)  # Field name made lowercase. The composite primary key (Patient_ID, EntryDate) found, that is not supported. The first column is selected.
    entrydate = models.DateField(db_column='EntryDate')  # Field name made lowercase.
    phantom_limb_ps_avg = models.DecimalField(db_column='Phantom_Limb_PS_Avg', max_digits=2, decimal_places=0, blank=True, null=True)  # Field name made lowercase.
    phantom_limb_ps_max = models.DecimalField(db_column='Phantom_Limb_PS_Max', max_digits=2, decimal_places=0, blank=True, null=True)  # Field name made lowercase.
    residual_limb_ps_avg = models.DecimalField(db_column='Residual_Limb_PS_Avg', max_digits=2, decimal_places=0, blank=True, null=True)  # Field name made lowercase.
    residual_limb_ps_max = models.DecimalField(db_column='Residual_Limb_PS_Max', max_digits=2, decimal_places=0, blank=True, null=True)  # Field name made lowercase.
    socket_comfort_score_avg = models.DecimalField(db_column='Socket_Comfort_Score_AVG', max_digits=2, decimal_places=0, blank=True, null=True)  # Field name made lowercase.
    socket_comfort_score_max = models.DecimalField(db_column='Socket_Comfort_Score_Max', max_digits=2, decimal_places=0, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'patient_entries'
        unique_together = (('patient', 'entrydate'),)


class PlusMScores(models.Model):
    patient = models.OneToOneField(Patients, models.DO_NOTHING, db_column='Patient_ID', primary_key=True)  # Field name made lowercase. The composite primary key (Patient_ID, ScoreDate) found, that is not supported. The first column is selected.
    scoredate = models.DateTimeField(db_column='ScoreDate')  # Field name made lowercase.
    plus_m = models.DecimalField(db_column='Plus_M', max_digits=10, decimal_places=0)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'plus_m_scores'
        unique_together = (('patient', 'scoredate'),)


class SensorEntries(models.Model):
    patient = models.OneToOneField(Patients, models.DO_NOTHING, db_column='Patient_ID', primary_key=True)  # Field name made lowercase. The composite primary key (Patient_ID, EntryDate) found, that is not supported. The first column is selected.
    entrydate = models.DateField(db_column='EntryDate')  # Field name made lowercase.
    cadence = models.FloatField(db_column='Cadence', blank=True, null=True)  # Field name made lowercase.
    walking_time = models.FloatField(db_column='Walking_Time', blank=True, null=True)  # Field name made lowercase.
    distance_walked = models.FloatField(db_column='Distance_Walked', blank=True, null=True)  # Field name made lowercase.
    walking_speed = models.FloatField(db_column='Walking_Speed', blank=True, null=True)  # Field name made lowercase.
    step_height = models.FloatField(db_column='Step_Height', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'sensor_entries'
        unique_together = (('patient', 'entrydate'),)


class SixminwalktestScores(models.Model):
    patient = models.OneToOneField(Patients, models.DO_NOTHING, db_column='Patient_ID', primary_key=True)  # Field name made lowercase. The composite primary key (Patient_ID, ScoreDate) found, that is not supported. The first column is selected.
    scoredate = models.DateTimeField(db_column='ScoreDate')  # Field name made lowercase.
    sixminwalktest = models.DecimalField(db_column='SixMinWalkTest', max_digits=10, decimal_places=0)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'sixminwalktest_scores'
        unique_together = (('patient', 'scoredate'),)


class TimePoints(models.Model):
    timepointnum = models.PositiveIntegerField(db_column='TimePointNum', primary_key=True)  # Field name made lowercase. The composite primary key (TimePointNum, Patient_ID, Provider_ID) found, that is not supported. The first column is selected.
    patient = models.ForeignKey(Patients, models.DO_NOTHING, db_column='Patient_ID')  # Field name made lowercase.
    provider = models.ForeignKey(Providers, models.DO_NOTHING, db_column='Provider_ID')  # Field name made lowercase.
    specialty = models.CharField(db_column='Specialty', max_length=255, blank=True, null=True)  # Field name made lowercase.
    tplocation = models.CharField(db_column='TPLocation', max_length=255)  # Field name made lowercase.
    startdate = models.DateTimeField(db_column='StartDate')  # Field name made lowercase.
    enddate = models.DateTimeField(db_column='EndDate', blank=True, null=True)  # Field name made lowercase.
    timepointtype = models.CharField(db_column='TimePointType', max_length=255, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'time_points'
        unique_together = (('timepointnum', 'patient', 'provider'),)


class TimedupandgoScores(models.Model):
    patient = models.OneToOneField(Patients, models.DO_NOTHING, db_column='Patient_ID', primary_key=True)  # Field name made lowercase. The composite primary key (Patient_ID, ScoreDate) found, that is not supported. The first column is selected.
    scoredate = models.DateTimeField(db_column='ScoreDate')  # Field name made lowercase.
    timedupandgo = models.DecimalField(db_column='TimedUpAndGo', max_digits=10, decimal_places=0)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'timedupandgo_scores'
        unique_together = (('patient', 'scoredate'),)
