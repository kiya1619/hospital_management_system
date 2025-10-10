from django.shortcuts import render, redirect
from hospital.models import User, Patient, Appointment, Medicine, Bed,LabResultImage, Prescription,BedRequest, PrescriptionMedicine, LabRequest, BedAssignment, Bed
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from .decorators import role_required
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from datetime import date
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
@role_required('admin')
def create_user_view(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')

        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role=role,
            first_name=first_name,
            last_name=last_name
        )
        messages.success(request, f'User {username} created successfully as {role}.')

        return redirect('create_user')  # redirect after creation
    roles = ['admin', 'doctor', 'nurse', 'reception', 'labtech', 'pharmacist', 'patient']
    return render(request, 'hospital/create_user.html', {'roles': roles})

def home_view(request):
    return render(request, 'hospital/home.html')
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            # Redirect based on role
            if user.role == 'admin':
                return redirect('admin_dashboard')
            elif user.role == 'doctor':
                return redirect('doctor_dashboard')
            elif user.role == 'nurse':
                return redirect('nurse_dashboard')
            elif user.role == 'labtech':
                return redirect('lab_dashboard')
            elif user.role == 'reception':
                return redirect('reception_dashboard')
            elif user.role == 'pharmacist':
                return redirect('pharmacist_dashboard')
            else:
                return redirect('login')
        else:
            return render(request, 'hospital/login.html', {'error': 'Invalid username or password'})
    return render(request, 'hospital/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')
def admin_dashboard(request):
    # Patients
    total_patients = Patient.objects.count()

    # Appointments
    total_appointments = Appointment.objects.count()
    scheduled_appointments = Appointment.objects.filter(status='scheduled').count()
    completed_appointments = Appointment.objects.filter(status='completed').count()
    canceled_appointments = Appointment.objects.filter(status='canceled').count()

    # Lab Requests
    total_lab_requests = LabRequest.objects.count()
    pending_lab_requests = LabRequest.objects.filter(status='pending').count()
    in_progress_lab_requests = LabRequest.objects.filter(status='in_progress').count()
    completed_lab_requests = LabRequest.objects.filter(status='completed').count()

    # Prescriptions
    total_prescriptions = Prescription.objects.count()
    fulfilled_prescriptions = Prescription.objects.filter(fulfilled=True).count()
    unfulfilled_prescriptions = total_prescriptions - fulfilled_prescriptions

    # Beds
    total_beds = Bed.objects.count()
    available_beds = Bed.objects.filter(status='available').count()
    occupied_beds = Bed.objects.filter(status='occupied').count()
    maintenance_beds = Bed.objects.filter(status='maintenance').count()

    context = {
        'total_patients': total_patients,
        'total_appointments': total_appointments,
        'scheduled_appointments': scheduled_appointments,
        'completed_appointments': completed_appointments,
        'canceled_appointments': canceled_appointments,
        'total_lab_requests': total_lab_requests,
        'pending_lab_requests': pending_lab_requests,
        'in_progress_lab_requests': in_progress_lab_requests,
        'completed_lab_requests': completed_lab_requests,
        'total_prescriptions': total_prescriptions,
        'fulfilled_prescriptions': fulfilled_prescriptions,
        'unfulfilled_prescriptions': unfulfilled_prescriptions,
        'total_beds': total_beds,
        'available_beds': available_beds,
        'occupied_beds': occupied_beds,
        'maintenance_beds': maintenance_beds,
    }
    return render(request, 'dashboards/admin_dashboard.html', context)

def pharmacist_dashboard(request):
    today = timezone.now().date()

    total_medicines = Medicine.objects.count()
    low_stock = Medicine.objects.filter(stock_quantity__lte=10, stock_quantity__gt=0).count()
    out_of_stock = Medicine.objects.filter(stock_quantity=0).count()
    expired_medicines = Medicine.objects.filter(expiry_date__lt=today).count()

    in_stock = total_medicines - out_of_stock  # calculate in-stock directly

    # Get all medicines for chart and alerts
    medicines = Medicine.objects.all().order_by('stock_quantity')[:20]

    # For chart: medicine stock distribution
    chart_data = {
        'labels': [m.name for m in medicines],
        'quantities': [m.stock_quantity for m in medicines],
    }

    context = {
        'today': today,
        'total_medicines': total_medicines,
        'in_stock': in_stock,           # pass in-stock value
        'low_stock': low_stock,
        'out_of_stock': out_of_stock,
        'expired_medicines': expired_medicines,
        'chart_data': chart_data,
        'medicines': medicines,
    }
    return render(request, 'dashboards/pharmacist_dashboard.html', context)
def doctor_dashboard(request):
    doctor = request.user
    
    # Total Appointments
    total_appointments = Appointment.objects.filter(doctor=doctor).count()
    
    # Scheduled Appointments
    scheduled = Appointment.objects.filter(doctor=doctor, status='scheduled').count()
    
    # Completed Appointments
    completed = Appointment.objects.filter(doctor=doctor, status='completed').count()
    
    # Pending Lab Requests
    pending_lab_requests = LabRequest.objects.filter(doctor=doctor, status='pending').count()
    
    # Upcoming appointments (future scheduled)
    upcoming_appointments = Appointment.objects.filter(
        doctor=doctor,
        status='scheduled',
        date_time__gte=timezone.now()
    ).order_by('date_time')[:10]
    
    context = {
        'total_appointments': total_appointments,
        'scheduled': scheduled,
        'completed': completed,
        'pending_lab_requests': pending_lab_requests,
        'upcoming_appointments': upcoming_appointments,
    }
    
    return render(request, 'dashboards/doctor_dashboard.html',context)
def nurse_dashboard(request):
    # Counts
    total_beds = Bed.objects.count()
    available_beds = Bed.objects.filter(status='available').count()
    occupied_beds = Bed.objects.filter(status='occupied').count()
    maintenance_beds = Bed.objects.filter(status='maintenance').count()
    pending_requests = BedRequest.objects.filter(status='pending').count()

    # Chart data
    bed_status_data = {
        'Available': available_beds,
        'Occupied': occupied_beds,
        'Maintenance': maintenance_beds,
    }

    context = {
        'total_beds': total_beds,
        'available_beds': available_beds,
        'occupied_beds': occupied_beds,
        'maintenance_beds': maintenance_beds,
        'pending_requests': pending_requests,
        'bed_status_data': bed_status_data,
    }

    return render(request, 'dashboards/nurse_dashboard.html', context)
def lab_dashboard(request):
    total_requests = LabRequest.objects.count()

    # Pending Requests
    pending_requests = LabRequest.objects.filter(status='pending').count()

    # In Progress Requests
    in_progress_requests = LabRequest.objects.filter(status='in_progress').count()

    # Completed Requests
    completed_requests = LabRequest.objects.filter(status='completed').count()

    # Upcoming / recent requests
    upcoming_requests = LabRequest.objects.order_by('date_created')[:10]

    context = {
        'total_requests': total_requests,
        'pending_requests': pending_requests,
        'in_progress_requests': in_progress_requests,
        'completed_requests': completed_requests,
        'upcoming_requests': upcoming_requests,
    }
    return render(request, 'dashboards/lab_dashboard.html', context)
def reception_dashboard(request):
    total_patients = Patient.objects.count()
    total_appointments = Appointment.objects.count()
    scheduled = Appointment.objects.filter(status='scheduled').count()
    completed = Appointment.objects.filter(status='completed').count()
    canceled = Appointment.objects.filter(status='canceled').count()

    upcoming_appointments = Appointment.objects.filter(
        date_time__gte=timezone.now()
    ).order_by('date_time')[:5]

    context = {
        'total_patients': total_patients,
        'total_appointments': total_appointments,
        'scheduled': scheduled,
        'completed': completed,
        'canceled': canceled,
        'upcoming_appointments': upcoming_appointments,
    }
    return render(request, 'dashboards/reception_dashboard.html', context)
def user_list_view(request):
    users = User.objects.all()
    return render(request, 'hospital/user_list.html', {'users': users})

def delete_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        user.delete()
        messages.success(request, 'User deleted successfully.')
    except User.DoesNotExist:
        pass
    return redirect('user_list')


@role_required('reception')
def register_patients(request):
    if request.method == 'POST':
        # User fields
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Patient fields
        dob = request.POST.get('dob')
        gender = request.POST.get('gender')
        phone = request.POST.get('phone')
        address = request.POST.get('address')

        # Create the User
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role='patient',
            first_name=first_name,
            last_name=last_name
        )

        # Create the Patient
        patient = Patient.objects.create(
            user=user,
            dob=dob,
            gender=gender,
            phone=phone,
            address=address,
        )

        messages.success(request, f"Patient {first_name} {last_name} registered successfully!")
        return redirect('register_patients')

    return render(request, 'hospital/register_patients.html')


def schedule_appointment(request):
    patients = Patient.objects.all()
    doctors = User.objects.filter(role='doctor')

    if request.method == 'POST':
        patient_id = request.POST.get('patient')
        doctor_id = request.POST.get('doctor')
        date_time = request.POST.get('date_time')

        # Get patient and doctor objects
        try:
            patient = Patient.objects.get(id=patient_id)
            doctor = User.objects.get(id=doctor_id, role='doctor')
        except (Patient.DoesNotExist, User.DoesNotExist):
            messages.error(request, "Invalid patient or doctor selected!")
            return redirect('schedule_appointment')

        # Create Appointment
        Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            date_time=date_time,
            status='scheduled'
        )
        messages.success(request, f"Appointment scheduled for {patient.user.get_full_name()} with Dr. {doctor.get_full_name()} on {date_time}."
)
        return redirect('schedule_appointment')

    # Existing appointments
    appointments = Appointment.objects.all().order_by('-date_time')
    return render(request, 'hospital/schedule_appointment.html', {
        'patients': patients,
        'doctors': doctors,
        'appointments': appointments
    })
def my_appointments(request):
    appointments = Appointment.objects.filter(doctor=request.user).order_by('date_time')
    for a in appointments:
        a.has_prescription = a.prescriptions.exists()
        a.lab_completed = a.lab_requests.filter(status='completed').exists()
        a.bed_fulfilled = a.bed_requests.filter(status='fulfilled').exists()
    return render(request, 'hospital/my_appointments.html', {'appointments': appointments})
def create_prescription(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    medicines = Medicine.objects.all()  # List all medicines

    if request.method == "POST":
        selected_meds = request.POST.getlist('medicines')
        notes = request.POST.get('notes')

        # Create the prescription
        prescription = Prescription.objects.create(
            appointment=appointment,
            doctor=request.user,
            notes=notes
        )

        # Save each selected medicine with its quantity
        for med_id in selected_meds:
            med = Medicine.objects.get(id=med_id)
            qty = request.POST.get(f'quantity_{med_id}', 1)  # get from input field
            if not qty or int(qty) <= 0:
                qty = 1  # fallback to 1 if invalid or empty

            PrescriptionMedicine.objects.create(
                prescription=prescription,
                medicine=med,
                quantity=qty
            )

        messages.success(request, f"Prescription created for {appointment.patient.user.get_full_name()}!")
        return redirect('my_appointments')

    return render(request, 'hospital/create_prescription.html', {
        'appointment': appointment,
        'medicines': medicines
    })
@role_required('pharmacist')    
def add_medicine(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        dosage = request.POST.get('dosage')
        instructions = request.POST.get('instructions')
        stock_quantity = request.POST.get('stock_quantity')
        expiry_date = request.POST.get('expiry_date')
        Medicine.objects.create(
            name=name,
            dosage=dosage,
            instructions=instructions,
            stock_quantity=stock_quantity,
            expiry_date=expiry_date
        )
        messages.success(request, f'Medicine {name} added successfully.')
        return redirect('add_medicine')

    medicines = Medicine.objects.all()
    return render(request, 'hospital/add_medicine.html', {'medicines': medicines})

def view_prescription(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    prescription = Prescription.objects.filter(appointment=appointment).first()  # usually one per appointment

    prescribed_medicines = []
    if prescription:
        prescribed_medicines = PrescriptionMedicine.objects.filter(prescription=prescription).select_related('medicine')

    return render(request, 'hospital/view_prescription.html', {
        'appointment': appointment,
        'prescription': prescription,
        'prescribed_medicines': prescribed_medicines
    })

def request_lab_test(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    # Example list of available lab tests
    lab_tests = [
        {'id': 'blood', 'name': 'Blood Test'},
        {'id': 'urine', 'name': 'Urine Test'},
        {'id': 'xray', 'name': 'X-Ray'},
        {'id': 'mri', 'name': 'MRI Scan'},
        {'id': 'ct', 'name': 'CT Scan'},
    ]

    if request.method == "POST":
        selected_tests = request.POST.getlist('tests')
        instructions = request.POST.get('instructions')

        if not selected_tests:
            messages.error(request, "Please select at least one lab test.")
            return redirect('request_lab_test', appointment_id=appointment_id)

        lab_request = LabRequest.objects.create(
            appointment=appointment,
            doctor=request.user,
            instructions  =instructions,
            tests={test: instructions for test in selected_tests},  # store as JSON
            status='pending'
        )

        messages.success(request, f"Lab request created for {appointment.patient.user.get_full_name()}!")
        return redirect('my_appointments')

    return render(request, 'hospital/request_lab_test.html', {
        'appointment': appointment,
        'lab_tests': lab_tests
    })

def lab_requests(request):
    requests = LabRequest.objects.all().order_by('-date_created')
    return render(request, 'hospital/lab_requests.html', {'requests': requests})
def fill_lab_request(request, request_id):
    lab_request = get_object_or_404(LabRequest, id=request_id)

    # Only allow lab technicians to update results
    if request.user.role != 'labtech':
        messages.error(request, "You are not authorized to update this request.")
        return redirect('lab_requests')

    if request.method == "POST":
        # ✅ Collect text results for each test
        results = {}
        for test_name in lab_request.tests:
            result_value = request.POST.get(f"result_{test_name}", "")
            results[test_name] = result_value

        # ✅ Save results
        lab_request.results = results
        lab_request.status = 'completed'
        lab_request.lab_technician = request.user
        lab_request.save()

        # ✅ Handle uploaded images (optional)
        uploaded_images = request.FILES.getlist('images')
        for img in uploaded_images:
            LabResultImage.objects.create(lab_request=lab_request, image=img)

        messages.success(request, "Lab results and images saved successfully!")
        return redirect('lab_requests')

    return render(request, 'hospital/fill_lab_request.html', {'lab_request': lab_request})
@role_required('labtech')
def view_lab_request(request, request_id):
    lab_request = get_object_or_404(LabRequest, id=request_id)

    # Allow all lab technicians and admins
    if request.user.role not in ['labtech', 'admin']:
        messages.error(request, "You are not authorized to view this lab request.")
        return redirect('lab_requests')

    return render(request, 'hospital/view_lab_request.html', {'lab_request': lab_request})
@role_required('doctor')
def view_lab_test(request, lab_request_id):
    """
    Doctor can view lab results filled by the lab technician.
    """
    lab_request = get_object_or_404(LabRequest, id=lab_request_id)

    return render(request, 'hospital/view_lab_test.html', {
        'lab_request': lab_request
    })


def request_bed(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if request.method == "POST":
        notes = request.POST.get('notes', '')

        BedRequest.objects.create(
            appointment=appointment,
            requested_by=request.user,
            notes=notes
        )

        messages.success(request,f"Bed request submitted for {appointment.patient.user.get_full_name()}.")        
        return redirect('my_appointments')

    return render(request, 'hospital/request_bed.html', {
        'appointment': appointment
    })

def view_bed_request(request):
    bed_requests = BedRequest.objects.all().order_by('-date_requested')
    context = {
        'bed_requests': bed_requests
    }
    return render(request, 'hospital/view_bed_request.html', context)

def fulfill_bed_request(request, bed_request_id):
    # Ensure only nurses can fulfill
    if request.user.role != 'nurse':
        messages.error(request, "You are not authorized to fulfill bed requests.")
        return redirect('view_bed_request')

    bed_request = get_object_or_404(BedRequest, id=bed_request_id)

    if bed_request.status == 'fulfilled':
        messages.warning(request, "This bed request has already been fulfilled.")
        return redirect('view_bed_request')

    # Mark as fulfilled by the current nurse
    bed_request.status = 'fulfilled'
    bed_request.fulfilled_by = request.user
    bed_request.date_fulfilled = timezone.now()
    bed_request.save()

    messages.success(request, f"Bed request for {bed_request.appointment.patient.user.get_full_name} has been fulfilled.")
    return redirect('view_bed_request')

def assign_bed(request, bed_request_id):
    bed_request = get_object_or_404(BedRequest, id=bed_request_id)

    available_beds = Bed.objects.filter(status='available')

    if request.method == 'POST':
        bed_id = request.POST.get('bed_id')
        bed = get_object_or_404(Bed, id=bed_id)

        # Create BedAssignment
        BedAssignment.objects.create(
            bed=bed,
            requested_bed=bed_request,
            patient=bed_request.appointment.patient,
            assigned_by=request.user
        )

        # Update bed status
        bed.status = 'occupied'
        bed.save()

        # Mark request as fulfilled
        bed_request.status = 'fulfilled'
        bed_request.fulfilled_by = request.user
        bed_request.date_fulfilled = timezone.now()
        bed_request.save()

        messages.success(request, f"Bed {bed.bed_number} assigned successfully!")
        return redirect('view_bed_request')

    return render(request, 'hospital/assign_bed.html', {
        'bed_request': bed_request,
        'available_beds': available_beds
    })
def add_bed(request):
    wards = ['General', 'ICU', 'Maternity', 'Pediatrics', 'Surgery']  # predefined wards
    suggested_number = ''

    if request.method == 'POST':
        ward = request.POST.get('ward')
        bed_number = request.POST.get('bed_number').strip()

        if Bed.objects.filter(bed_number=bed_number).exists():
            messages.error(request, f"Bed number {bed_number} already exists!")
        else:
            Bed.objects.create(
                ward=ward,
                bed_number=bed_number,
                status='available'
            )
            messages.success(request, f"Bed {bed_number} added to {ward} ward successfully!")
            return redirect('add_bed')

    else:
        # Suggest next available bed number for each ward
        suggested_numbers = {}
        for ward in wards:
            existing_beds = Bed.objects.filter(ward=ward).order_by('bed_number')
            if existing_beds.exists():
                last_number = max([int(b.bed_number.split('-')[-1]) for b in existing_beds if '-' in b.bed_number] or [0])
                suggested_numbers[ward] = f"{ward[:3].upper()}-{last_number + 1:02d}"
            else:
                suggested_numbers[ward] = f"{ward[:3].upper()}-01"

    return render(request, 'hospital/add_bed.html', {
        'wards': wards,
        'suggested_numbers': suggested_numbers
    })

def view_medical_record(request):
    patients = Patient.objects.all()

    selected_patient_id = request.GET.get('patient_id')
    selected_patient = None
    appointments = []
    prescriptions = []
    lab_requests = []
    bed_assignments = []
    age = None

    if selected_patient_id:
        selected_patient = get_object_or_404(Patient, id=selected_patient_id)
        
        # Calculate age
        today = date.today()
        age = today.year - selected_patient.dob.year - (
            (today.month, today.day) < (selected_patient.dob.month, selected_patient.dob.day)
        )

        # Fetch related data
        appointments = Appointment.objects.filter(patient=selected_patient)
        prescriptions = Prescription.objects.filter(appointment__patient=selected_patient)
        lab_requests = LabRequest.objects.filter(appointment__patient=selected_patient)
        bed_assignments = BedAssignment.objects.filter(patient=selected_patient).select_related('bed')

    context = {
        'patients': patients,
        'selected_patient': selected_patient,
        'appointments': appointments,
        'prescriptions': prescriptions,
        'lab_requests': lab_requests,
        'bed_assignments': bed_assignments,
        'age': age,
    }
    return render(request, 'hospital/view_medical_record.html', context)


def patinet_list(request):
    patients = Patient.objects.all()
    return render(request, 'hospital/patinet_list.html', {'patients': patients})


def manage_appointments(request):
    appointments = Appointment.objects.all().order_by('-date_time')
    return render(request, 'hospital/manage_appointments.html', {'appointments': appointments})

def complete_appointment(request, id):
    appointment = get_object_or_404(Appointment, id=id)
    if request.method == 'POST':
        if appointment.status == 'scheduled':
            appointment.status = 'completed'
            appointment.save()
            messages.success(request, 'Appointment marked as completed.')
            return redirect('my_appointments')
        else:
            messages.warning(request, 'Appointment is already completed or canceled.')
            return redirect('my_appointments')
      
def cancel_appointment(request, id):
    appointment = get_object_or_404(Appointment, id=id)
    
    # Only allow cancellation if the appointment is scheduled
    if appointment.status == "scheduled":
        appointment.status = "canceled"
        appointment.save()
        messages.success(request, "Appointment canceled successfully.")
    else:
        messages.warning(request, "Only scheduled appointments can be canceled.")
    
    return redirect('manage_appointments') 


def medicine_list(request):
    medicines = Medicine.objects.all().order_by('name')
    return render(request, 'hospital/medicine_list.html', {'medicines': medicines})


def view_bedrooms(request):
    beds = Bed.objects.all().order_by('ward', 'bed_number')
    return render(request, 'hospital/view_bedrooms.html', {'beds': beds})

def view_appointments(request):
    appointments = Appointment.objects.all().order_by('-date_time')
    return render(request, 'hospital/view_appointments.html', {'appointments': appointments})
@role_required('nurse')
def patient_list_nurse_view(request):
    bed_requests = BedRequest.objects.select_related(
        'appointment__patient__user', 
        'requested_by',
        'fulfilled_by'
    ).prefetch_related('assignment__bed').order_by('-date_requested')

    context = {'bed_requests': bed_requests}
    return render(request, 'hospital/patient_list_nurse_view.html', context)

def release_bed(request, bed_id):
    assignment = get_object_or_404(BedAssignment, id=bed_id)
    if request.method == "POST":
        assignment.date_released = timezone.now()
        assignment.bed.status = 'available'
        assignment.bed.save()
        assignment.save()
        messages.success(request, f"Bed {assignment.bed.bed_number} has been released.")
    return redirect('patient_list_nurse_view')


def medical_report(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    # Only allow completed appointments
    if appointment.status != 'completed':
        messages.warning(request, "Medical report is only available for completed appointments.")
        return redirect('my_appointments')  # or your appointment list view

    return render(request, 'hospital/medical_report.html', {
        'appointment': appointment
    })


def expired_medicine_report(request):
    today = timezone.now().date()
    expired_medicines = Medicine.objects.filter(expiry_date__lt=today).order_by('expiry_date')
    return render(request, 'hospital/expired_medicine_report.html', {
        'expired_medicines': expired_medicines
    })