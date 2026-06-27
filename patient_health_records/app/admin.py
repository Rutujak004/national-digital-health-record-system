from django.contrib import admin
from .models import Patient, Doctor, Appointment, PatientHistory, DoctorRequest, PatientVisit, PatientNotification

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', 'email', 'phone', 'gender', 'disease', 'doctor_assigned', 'created_at']
    search_fields = ['full_name', 'email', 'phone']
    list_filter = ['gender', 'created_at']

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', 'email', 'phone', 'specialization', 'experience', 'created_at']
    search_fields = ['full_name', 'email']
    list_filter = ['specialization']

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'patient', 'doctor', 'date', 'time', 'status', 'created_at']
    list_filter = ['status', 'date']
    search_fields = ['patient__full_name', 'doctor__full_name']

@admin.register(PatientHistory)
class PatientHistoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'patient', 'full_name', 'disease', 'doctor_assigned', 'updated_at']
    search_fields = ['full_name', 'patient__full_name']

@admin.register(DoctorRequest)
class DoctorRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'patient', 'doctor', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['patient__full_name', 'doctor__full_name']

@admin.register(PatientVisit)
class PatientVisitAdmin(admin.ModelAdmin):
    list_display = ['id', 'patient', 'doctor', 'visit_date', 'follow_up_date', 'diagnosis', 'sent_to_patient', 'created_at']
    list_filter = ['sent_to_patient', 'visit_date']
    search_fields = ['patient__full_name', 'doctor__full_name']

@admin.register(PatientNotification)
class PatientNotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'patient', 'title', 'read', 'created_at']
    list_filter = ['read']
    search_fields = ['patient__full_name', 'title']