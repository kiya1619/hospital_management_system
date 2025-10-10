import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models

# -----------------------------
# User model with UUID
# -----------------------------
class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ROLE_CHOICES = [
        ('doctor', 'Doctor'),
        ('nurse', 'Nurse'),
        ('labtech', 'Lab Technician'),
        ('reception', 'Receptionist'),
        ('pharmacist', 'Pharmacist'),
        ('patient', 'Patient'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    # Fix related_name conflicts
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='hospital_users',  # changed from default 'user_set'
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='hospital_users_permissions',  # changed from default 'user_set'
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )
# -----------------------------
# Patient
# -----------------------------
class Patient(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'role':'patient'})
    dob = models.DateField()
    gender = models.CharField(max_length=10)
    current_bed = models.ForeignKey('Bed', on_delete=models.SET_NULL, null=True, blank=True, related_name='current_patient')
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
# -----------------------------
# Appointment
# -----------------------------
class Appointment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(User, limit_choices_to={'role':'doctor'}, on_delete=models.CASCADE, related_name='appointments')
    date_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=[('scheduled','Scheduled'), ('completed','Completed'), ('canceled','Canceled')], default='scheduled')

# -----------------------------
# Medicine
# -----------------------------
class Medicine(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    dosage = models.CharField(max_length=50, null=True, blank=True)
    instructions = models.TextField(null=True, blank=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    expiry_date = models.DateField(null=True, blank=True)  # Added field


# -----------------------------
# Prescription
# -----------------------------
class Prescription(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='prescriptions')
    doctor = models.ForeignKey(User, limit_choices_to={'role':'doctor'}, on_delete=models.CASCADE, related_name='prescriptions')
    pharmacist = models.ForeignKey(User, limit_choices_to={'role':'pharmacist'}, null=True, blank=True, on_delete=models.SET_NULL, related_name='fulfilled_prescriptions')
    medicines = models.ManyToManyField(Medicine, through='PrescriptionMedicine')
    notes = models.TextField(blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    fulfilled = models.BooleanField(default=False)

# -----------------------------
# PrescriptionMedicine
# -----------------------------
class PrescriptionMedicine(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE)
    medicine = models.ForeignKey(Medicine, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)

# -----------------------------
# LabRequest
# -----------------------------
class LabRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='lab_requests')
    doctor = models.ForeignKey(User, limit_choices_to={'role':'doctor'}, on_delete=models.CASCADE, related_name='lab_requests')
    lab_technician = models.ForeignKey(User, limit_choices_to={'role':'labtech'}, null=True, blank=True, on_delete=models.SET_NULL, related_name='assigned_lab_requests')
    tests = models.JSONField()
    results = models.JSONField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[('pending','Pending'),('in_progress','In Progress'),('completed','Completed')], default='pending')
    date_created = models.DateTimeField(auto_now_add=True)
    instructions = models.TextField(null=True, blank=True)

# -----------------------------
#  LabResultImage
# -----------------------------
class LabResultImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lab_request = models.ForeignKey(
        'LabRequest',
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='lab_results/')
    description = models.CharField(max_length=255, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.lab_request.id} - {self.description or 'No description'}"
# -----------------------------
# Bed & BedAssignment
# -----------------------------
class Bed(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bed_number = models.CharField(max_length=10, unique=True)
    ward = models.CharField(max_length=50)
    status = models.CharField(
        max_length=20,
        choices=[('available','Available'),('occupied','Occupied'),('maintenance','Maintenance')],
        default='available'
    )
    def __str__(self):
        return f'Bed {self.bed_number} - {self.ward} ({self.status})'
class BedRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='bed_requests')
    notes = models.TextField(null=True, blank=True)  # optional notes for nurse

    requested_by = models.ForeignKey(
        User,
        limit_choices_to={'role': 'doctor'},
        on_delete=models.CASCADE,
        related_name='bed_requests_requested'
    )
    fulfilled_by = models.ForeignKey(
        User,
        limit_choices_to={'role': 'nurse'},
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='bed_requests_fulfilled'
    )
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('fulfilled', 'Fulfilled')],
        default='pending'
    )
    date_requested = models.DateTimeField(auto_now_add=True)
    date_fulfilled = models.DateTimeField(null=True, blank=True)
class BedAssignment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bed = models.ForeignKey(Bed, on_delete=models.CASCADE, related_name='assignments')
    requested_bed = models.ForeignKey(BedRequest, on_delete=models.CASCADE, related_name='assignment', null=True, blank=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='bed_assignments')
    assigned_by = models.ForeignKey(User, limit_choices_to={'role':'nurse'}, on_delete=models.CASCADE)
    date_assigned = models.DateTimeField(auto_now_add=True)
    date_released = models.DateTimeField(null=True, blank=True)
