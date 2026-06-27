from django.contrib import admin
from django.urls import path
from app import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Home
    path('', views.index, name='index'),

    # ✅ Authentication
    path('log_in/', views.log_in, name='log_in'),
    path('log_out/', views.log_out, name='log_out'),
    path('admin_login/', views.admin_login, name='admin_login'),

    # ✅ Dashboards
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('patient_dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('doctor_dashboard/', views.doctor_dashboard, name='doctor_dashboard'),

    # ✅ Registration
    path('patient_register/', views.patient_register, name='patient_register'),
    path('doctor_register/', views.doctor_register, name='doctor_register'),

    # ✅ Password Setup
    path('create-patient-password/', views.patient_password_create, name='patient_password_create'),
    path('create-doctor-password/', views.doctor_password_create, name='doctor_password_create'),

    # ✅ Patient CRUD
    path('edit_patient/<int:patient_id>/', views.edit_patient, name='edit_patient'),
    path('delete_patient/<int:patient_id>/', views.delete_patient, name='delete_patient'),
    path('patient_history/<int:patient_id>/', views.patient_history, name='patient_history'),
    path('patient-record/<int:patient_id>/', views.patient_record_public, name='patient_record_public'),

    # ✅ Doctor CRUD
    path('edit_doctor/<int:doctor_id>/', views.edit_doctor, name='edit_doctor'),
    path('delete_doctor/<int:doctor_id>/', views.delete_doctor, name='delete_doctor'),

    # ✅ Appointments
    path('approve_appointment/<int:appointment_id>/', views.approve_appointment, name='approve_appointment'),
    path('reject_appointment/<int:appointment_id>/', views.reject_appointment, name='reject_appointment'),
    path('cancel-request/<int:request_id>/', views.cancel_request, name='cancel_request'),

    # ✅ Doctor Request System
    path('send-request/<int:doctor_id>/', views.send_request_to_doctor, name='send_request_to_doctor'),
    path('accept-request/<int:request_id>/', views.accept_request, name='accept_request'),
    path('reject-request/<int:request_id>/', views.reject_request, name='reject_request'),

    # ✅ Patient view + QR + Hash
    path('view-patient/<int:patient_id>/', views.view_patient_details, name='view_patient_details'),
    path('patient-info/<int:patient_id>/', views.patient_info, name='patient_info'),
    # Doctor sends updated record to patient
    path('send-update/<int:visit_id>/', views.send_update_to_patient, name='send_update_to_patient'),


    # ✅ Blockchain QR / Hash verify
    path('scan-qr/', views.scan_qr_page, name='scan_qr_page'),
    path('verify-hash/', views.verify_hash_page, name='verify_hash_page'),

    path("save-patient-record/", views.save_patient_record, name="save_patient_record"),
    

]

# Serve Media (QR, Images) in DEBUG mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
