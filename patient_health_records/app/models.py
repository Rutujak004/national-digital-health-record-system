from django.db import models
from django.contrib.auth.hashers import make_password, check_password

# ---------------------- PATIENT MODEL ----------------------
class Patient(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other')
    ]
    
    full_name = models.CharField(max_length=100)
    age = models.IntegerField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    disease = models.TextField(blank=True, null=True)
    doctor_assigned = models.CharField(max_length=100, blank=True, null=True)

    # 🧩 Blockchain + QR Fields
    blockchain_hash = models.CharField(max_length=255, blank=True, null=True)
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True, null=True)
    tx_hash = models.CharField(max_length=255, blank=True, null=True)

    # 🧩 NEW FIELD — Password (added for patient login)
    password = models.CharField(max_length=128, blank=True, null=True)
    is_password_set = models.BooleanField(default=False)  # ✅ to track password creation

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name

    # 🧠 Password handling
    def set_password(self, raw_password):
        """Hashes and stores the password."""
        self.password = make_password(raw_password)
        self.is_password_set = True

    def check_password(self, raw_password):
        """Validates plain password against the stored hash."""
        return check_password(raw_password, self.password)


# ---------------------- DOCTOR MODEL ----------------------
class Doctor(models.Model):
    full_name = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    experience = models.IntegerField(help_text="Experience in years")
    photo = models.ImageField(upload_to='doctors/', blank=True, null=True)
    
    # 🧩 NEW FIELD — Password for doctor login
    password = models.CharField(max_length=128, blank=True, null=True)
    is_password_set = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name

    # 🧠 Password handling
    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self.is_password_set = True

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)


# ---------------------- APPOINTMENT MODEL ----------------------
class Appointment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(
        max_length=20,
        choices=[
            ('Scheduled', 'Scheduled'),
            ('Completed', 'Completed'),
            ('Cancelled', 'Cancelled')
        ],
        default='Scheduled'
    )
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient.full_name} with {self.doctor.full_name} on {self.date}"

    @property
    def patient_name(self):
        return self.patient.full_name
    
    @property
    def doctor_name(self):
        return self.doctor.full_name


# ---------------------- PATIENT HISTORY MODEL ----------------------
class PatientHistory(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='history_records')
    full_name = models.CharField(max_length=100)
    age = models.IntegerField()
    gender = models.CharField(max_length=10)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    address = models.TextField()
    disease = models.TextField(blank=True, null=True)
    doctor_assigned = models.CharField(max_length=100, blank=True, null=True)
    blockchain_hash = models.CharField(max_length=255, blank=True, null=True)
    qr_code = models.ImageField(upload_to='qrcodes/history/', blank=True, null=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"History of {self.patient.full_name} at {self.updated_at.strftime('%Y-%m-%d %H:%M')}"


class DoctorRequest(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20,
        choices=[('Pending', 'Pending'), ('Accepted', 'Accepted')],
        default='Pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient.full_name} -> {self.doctor.full_name} ({self.status})"

class PatientVisit(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='visits')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)

    visit_date = models.DateField()
    follow_up_date = models.DateField(blank=True, null=True)

    symptoms = models.TextField(blank=True, null=True)
    diagnosis = models.TextField(blank=True, null=True)
    tests = models.TextField(blank=True, null=True)
    prescription = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    prescription_image = models.ImageField(upload_to='prescriptions/', blank=True, null=True)

    # ADD THIS 👇👇👇
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True, null=True)

    blockchain_hash = models.CharField(max_length=255, blank=True, null=True)
        # ➕ REQUIRED NEW FIELD
    sent_to_patient = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Visit of {self.patient.full_name} on {self.visit_date}"

class PatientNotification(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    body = models.TextField(blank=True, null=True)
    visit = models.ForeignKey(PatientVisit, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.patient.full_name}"
