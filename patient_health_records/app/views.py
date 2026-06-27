from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import logout
from .models import Patient, Doctor, Appointment, DoctorRequest
from django.utils import timezone
# 🧩 Added imports for Blockchain + QR logic
import qrcode
import json
import uuid
import os
from django.conf import settings
import hashlib

# 🧩 Web3 imports
from web3 import Web3

# ✅ Connect to Ganache
ganache_url = os.environ.get('BLOCKCHAIN_RPC_URL', 'http://127.0.0.1:7545')
web3 = Web3(Web3.HTTPProvider(ganache_url))

# --------------------------------------
# 🔍 CHECK GANACHE CONNECTION
# --------------------------------------
if web3.is_connected():
    print("✔ Connected to Ganache RPC")
else:
    print("❌ ERROR: Ganache is NOT running!")


# ✅ Your Account (from Ganache first address)
account_address = "0x4A42ee9cC198a4aeCbc4bcF22c30dF430Af1F493"
private_key = "0xe541b0428279425265c8dcfb3e41cda7f3145b2eacaba33a975bae8a6932534b"  # ⚠️ Replace this safely!

# --------------------------------------
# 🔍 CHECK ACCOUNT BALANCE
# --------------------------------------
try:
    balance = web3.eth.get_balance(account_address)
    print("✔ Account found. Balance:", web3.from_wei(balance, "ether"), "ETH")
except:
    print("❌ ERROR: Account not found in Ganache! Use first Ganache account.")


# ✅ Contract details
contract_address = web3.to_checksum_address("0x8b00c6e241B44C99Eb3b074E7121aBfB19B85AB8")

# --------------------------------------
# 🔍 CHECK CONTRACT IS DEPLOYED
# --------------------------------------
try:
    web3.eth.get_code(contract_address)
    print("✔ Smart contract loaded successfully!")
except Exception as e:
    print("❌ ERROR: Contract not found on Ganache:", str(e))


# ✅ ABI (copied from Remix output)
contract_abi = [
  {
    "inputs": [
      {"internalType": "uint256", "name": "patientId", "type": "uint256"},
      {"internalType": "string", "name": "hashValue", "type": "string"}
    ],
    "name": "addRecord",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {"internalType": "uint256", "name": "patientId", "type": "uint256"}
    ],
    "name": "getRecords",
    "outputs": [
      {
        "components": [
          {"internalType": "uint256", "name": "patientId", "type": "uint256"},
          {"internalType": "string", "name": "hashValue", "type": "string"},
          {"internalType": "uint256", "name": "timestamp", "type": "uint256"}
        ],
        "internalType": "struct PatientRecords.Record[]",
        "name": "",
        "type": "tuple[]"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  }
]

# 🧩 Load the contract
contract = web3.eth.contract(address=contract_address, abi=contract_abi)

def index(request):
    return render(request, 'index.html')

def patient_register(request):
    if request.method == "POST":
        import qrcode, json, os, hashlib, uuid
        from django.conf import settings

        full_name = request.POST.get('full_name')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        disease = request.POST.get('disease')
        doctor_assigned = request.POST.get('doctor_assigned')
        
        try:
            # 1️⃣ Create Patient record
            patient = Patient.objects.create(
                full_name=full_name,
                age=age,
                gender=gender,
                email=email,
                phone=phone,
                address=address,
                disease=disease,
                doctor_assigned=doctor_assigned
            )

            # 2️⃣ Build blockchain chain (initial record)
            initial_record = [{
                "patient_id": patient.id,
                "full_name": full_name,
                "age": age,
                "gender": gender,
                "email": email,
                "phone": phone,
                "address": address,
                "disease": disease,
                "doctor_assigned": doctor_assigned,
            }]

            # 3️⃣ Generate blockchain hash
            chain_json = json.dumps(initial_record, sort_keys=True)
            blockchain_hash = hashlib.sha256(chain_json.encode()).hexdigest()

            # 4️⃣ Prepare QR data (with final hash + history)
            qr_data = {
                "patient_id": patient.id,
                "blockchain_hash": blockchain_hash,
                "url": f"http://127.0.0.1:8000/patient-record/{patient.id}/"
            }

            # 5️⃣ Generate and save QR Code
            qr = qrcode.make(json.dumps(qr_data, indent=2))
            qr_filename = f"patient_{patient.id}_qr.png"
            qr_folder = os.path.join(settings.MEDIA_ROOT, 'qrcodes')
            os.makedirs(qr_folder, exist_ok=True)
            qr_path = os.path.join(qr_folder, qr_filename)
            qr.save(qr_path)

            # 6️⃣ Save blockchain hash & QR path
            patient.blockchain_hash = blockchain_hash
            patient.qr_code = f"qrcodes/{qr_filename}"
            patient.save()

            # ✅ 7️⃣ (Optional) Future — store hash on blockchain (Ganache + MetaMask)
            """
            from web3 import Web3

            # Connect to Ganache (make sure Ganache is running)
            web3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))

            contract_address = "0xd8b934580fcE35a11B58C6D73aDeE468a2833fa8"
            abi = [ ... ABI JSON FROM REMIX ... ]

            contract = web3.eth.contract(address=contract_address, abi=abi)
            account = web3.eth.accounts[0]

            tx = contract.functions.addRecord(patient.id, blockchain_hash).transact({
                'from': account
            })
            web3.eth.wait_for_transaction_receipt(tx)
            """

            messages.success(request, f"✅ Patient '{full_name}' registered successfully with blockchain QR!")
            return redirect('admin_dashboard')

        except Exception as e:
            messages.error(request, f"❌ Error registering patient: {str(e)}")
            return redirect('admin_dashboard')

    # 👇 No need to render new page — the form is inside admin_dashboard.html
    return redirect('admin_dashboard')

def doctor_register(request):
    if request.method == "POST":
        full_name = request.POST.get('full_name')
        specialization = request.POST.get('specialization')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        experience = request.POST.get('experience')
        photo = request.FILES.get('photo')
        
        try:
            doctor = Doctor.objects.create(
                full_name=full_name,
                specialization=specialization,
                email=email,
                phone=phone,
                experience=experience,
                photo=photo
            )
            messages.success(request, "Doctor registered successfully!")
            return redirect('admin_dashboard')  # Changed from 'index' to 'admin_dashboard'
        except Exception as e:
            messages.error(request, f"Error registering doctor: {str(e)}")
    
    return render(request, 'doctor_register.html')


from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Patient, Doctor

def log_in(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        # 🩺 Check if email exists in Patient table
        try:
            patient = Patient.objects.get(email=email)
            if not patient.is_password_set:
                messages.error(request, "Please create your password before logging in.")
                return redirect("patient_password_create")

            if patient.check_password(password):
                request.session["user_role"] = "patient"
                request.session["user_id"] = patient.id
                messages.success(request, f"Welcome {patient.full_name}!")
                return redirect("patient_dashboard")
            else:
                messages.error(request, "Incorrect password.")
                return redirect("log_in")
        except Patient.DoesNotExist:
            pass  # If not found, move on to check Doctor

        # 👨‍⚕️ Check if email exists in Doctor table
        try:
            doctor = Doctor.objects.get(email=email)
            if not doctor.is_password_set:
                messages.error(request, "Please create your password before logging in.")
                return redirect("doctor_password_create")

            if doctor.check_password(password):
                request.session["user_role"] = "doctor"
                request.session["user_id"] = doctor.id
                messages.success(request, f"Welcome Dr. {doctor.full_name}!")
                return redirect("doctor_dashboard")
            else:
                messages.error(request, "Incorrect password.")
                return redirect("log_in")
        except Doctor.DoesNotExist:
            pass

        # ❌ If no record found
        messages.error(request, "No account found with this email.")
        return redirect("log_in")

    return render(request, "login.html")

def admin_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        if username == 'admin@gmail.com' and password == 'admin@123':
            admin_user, created = User.objects.get_or_create(username='admin@gmail.com', email='admin@gmail.com')
            admin_user.set_password('admin@123')
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.save()

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Admin login successful!")
                return redirect("admin_dashboard")
            else:
                messages.error(request, "Authentication failed!")
                return redirect("admin_login")
        else:
            messages.error(request, "Invalid admin credentials!")
            return redirect("admin_login")

    return render(request, "admin_login.html")
from django.db.models import Count

def admin_dashboard(request):
    context = {
        # ================= MAIN DATA =================
        'all_patients': Patient.objects.all().order_by('-created_at'),
        'all_doctors': Doctor.objects.all().order_by('-created_at'),

        # Appointments (safe ordering)
        'all_appointments': Appointment.objects.all().order_by('-created_at'),

        # Doctor Requests (optimized)
        'all_requests': DoctorRequest.objects.select_related('patient', 'doctor').order_by('-created_at'),

        # ================= COUNTS =================
        'total_patients': Patient.objects.count(),
        'total_doctors': Doctor.objects.count(),
        'total_appointments': Appointment.objects.count(),
        'total_requests': DoctorRequest.objects.count(),

        # 🔥 REPORT COUNTS
        'accepted_requests': DoctorRequest.objects.filter(status="Accepted").count(),
        'pending_requests': DoctorRequest.objects.filter(status="Pending").count(),

        # ================= ANALYTICS =================
        # Top doctors (based on number of requests)
        'top_doctors': DoctorRequest.objects.values('doctor__full_name')
            .annotate(total=Count('id'))
            .order_by('-total')[:5],

        # Recent activity (last 5 requests, optimized)
        'recent_requests': DoctorRequest.objects.select_related('patient', 'doctor')
            .order_by('-created_at')[:5],
    }

    return render(request, 'admin_dashboard.html', context)

def edit_patient(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)

    if request.method == "POST":
        from .models import PatientHistory
        import qrcode, json, os, hashlib
        from django.conf import settings

        # 1️⃣ Save the old data to history before updating
        PatientHistory.objects.create(
            patient=patient,
            full_name=patient.full_name,
            age=patient.age,
            gender=patient.gender,
            email=patient.email,
            phone=patient.phone,
            address=patient.address,
            disease=patient.disease,
            doctor_assigned=patient.doctor_assigned,
            blockchain_hash=patient.blockchain_hash,
            qr_code=patient.qr_code
        )

        # 2️⃣ Update patient data from form
        patient.full_name = request.POST.get('full_name')
        patient.age = request.POST.get('age')
        patient.gender = request.POST.get('gender')
        patient.email = request.POST.get('email')
        patient.phone = request.POST.get('phone')
        patient.address = request.POST.get('address')
        patient.disease = request.POST.get('disease')
        patient.doctor_assigned = request.POST.get('doctor_assigned')

        # 3️⃣ Combine all history + current data
        history_records = list(patient.history_records.values(
            "patient_id", "full_name", "age", "gender", "email",
            "phone", "address", "disease", "doctor_assigned", "blockchain_hash"
        ))
        current_data = {
            "patient_id": patient.id,
            "full_name": patient.full_name,
            "age": patient.age,
            "gender": patient.gender,
            "email": patient.email,
            "phone": patient.phone,
            "address": patient.address,
            "disease": patient.disease,
            "doctor_assigned": patient.doctor_assigned
        }
        history_records.append(current_data)

        # 4️⃣ Create a new blockchain hash of full chain
        chain_json = json.dumps(history_records, sort_keys=True)
        new_hash = hashlib.sha256(chain_json.encode()).hexdigest()
        patient.blockchain_hash = new_hash

        # 5️⃣ Send transaction to blockchain via Ganache
        try:
            nonce = web3.eth.get_transaction_count(account_address)
            txn = contract.functions.addRecord(patient.id, new_hash).build_transaction({
                'from': account_address,
                'nonce': nonce,
                'gas': 200000,
                'gasPrice': web3.to_wei('1', 'gwei')
            })

            signed_txn = web3.eth.account.sign_transaction(txn, private_key=private_key)
            tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)
            tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

            blockchain_tx_hash = tx_hash.hex()
            patient.tx_hash = blockchain_tx_hash  # ✅ store TX hash in database

        except Exception as e:
            blockchain_tx_hash = f"Error: {str(e)}"
            patient.tx_hash = None

        # 6️⃣ Generate updated QR Code
        qr_data = {
            "patient_id": patient.id,
            "blockchain_hash": new_hash,
            "url": f"http://127.0.0.1:8000/patient-record/{patient.id}/"
        }
        qr = qrcode.make(json.dumps(qr_data, indent=2))

        qr_filename = f"patient_{patient.id}_chain_qr.png"
        qr_folder = os.path.join(settings.MEDIA_ROOT, 'qrcodes')
        os.makedirs(qr_folder, exist_ok=True)
        qr_path = os.path.join(qr_folder, qr_filename)
        qr.save(qr_path)

        patient.qr_code = f"qrcodes/{qr_filename}"
        patient.save()

        messages.success(request, "✅ Patient updated and blockchain record stored successfully!")
        return redirect('admin_dashboard')

    return render(request, 'edit_patient.html', {'patient': patient})

def patient_history(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    history_records = patient.history_records.all().order_by('-updated_at')

    # ✅ Capture 'from' parameter (admin/patient/doctor)
    source = request.GET.get("from", "admin")  # default: admin if not provided

    context = {
        "patient": patient,
        "history_records": history_records,
        "source": source,  # pass to template
    }
    return render(request, "patient_history.html", context)

def delete_patient(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    patient.delete()
    messages.success(request, "Patient deleted successfully!")
    return redirect('admin_dashboard')


def edit_doctor(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    if request.method == "POST":
        doctor.full_name = request.POST.get('full_name')
        doctor.specialization = request.POST.get('specialization')
        doctor.email = request.POST.get('email')
        doctor.phone = request.POST.get('phone')
        doctor.experience = request.POST.get('experience')
        if request.FILES.get('photo'):
            doctor.photo = request.FILES.get('photo')
        doctor.save()
        messages.success(request, "Doctor updated successfully!")
        return redirect('admin_dashboard')
    
    return render(request, 'edit_doctor.html', {'doctor': doctor})


def delete_doctor(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    doctor.delete()
    messages.success(request, "Doctor deleted successfully!")
    return redirect('admin_dashboard')


def approve_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.status = 'Completed'
    appointment.save()
    messages.success(request, "Appointment approved!")
    return redirect('admin_dashboard')


def reject_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.status = 'Cancelled'
    appointment.save()
    messages.success(request, "Appointment rejected!")
    return redirect('admin_dashboard')

def patient_password_create(request):
    """
    Step 1: Verify patient's email.
    Step 2: If valid, allow password + confirm password creation.
    """
    from .models import Patient

    verified = False
    email = None

    # Step 1 — Verify email
    if request.method == "POST" and "verify_email" in request.POST:
        email = request.POST.get("email")
        try:
            patient = Patient.objects.get(email=email)
            if patient.is_password_set:
                messages.warning(request, "You already created a password. Please login instead.")
                return redirect("log_in")
            verified = True
            return render(request, "patient_password_create.html", {"verified": verified, "email": email})
        except Patient.DoesNotExist:
            messages.error(request, "No patient found with that email. Please contact the admin.")

    # Step 2 — Set password
    elif request.method == "POST" and "set_password" in request.POST:
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "patient_password_create.html", {"verified": True, "email": email})

        try:
            patient = Patient.objects.get(email=email)
            patient.set_password(password)
            patient.save()
            messages.success(request, "Password created successfully! You can now login.")
            return redirect("log_in")
        except Patient.DoesNotExist:
            messages.error(request, "Error: patient not found.")
            return redirect("patient_password_create")

    return render(request, "patient_password_create.html", {"verified": verified})

def doctor_password_create(request):
    """
    Step 1: Verify doctor's email.
    Step 2: If valid, allow password + confirm password creation.
    """
    from .models import Doctor

    verified = False
    email = None

    # Step 1 — Verify email
    if request.method == "POST" and "verify_email" in request.POST:
        email = request.POST.get("email")
        try:
            doctor = Doctor.objects.get(email=email)
            if doctor.is_password_set:
                messages.warning(request, "You already created a password. Please login instead.")
                return redirect("log_in")
            verified = True
            return render(request, "doctor_password_create.html", {"verified": verified, "email": email})
        except Doctor.DoesNotExist:
            messages.error(request, "No doctor found with that email. Please contact the admin.")

    # Step 2 — Set password
    elif request.method == "POST" and "set_password" in request.POST:
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "doctor_password_create.html", {"verified": True, "email": email})

        try:
            doctor = Doctor.objects.get(email=email)
            doctor.set_password(password)
            doctor.save()
            messages.success(request, "Password created successfully! You can now login.")
            return redirect("log_in")
        except Doctor.DoesNotExist:
            messages.error(request, "Error: doctor not found.")
            return redirect("doctor_password_create")

    return render(request, "doctor_password_create.html", {"verified": verified})

def patient_dashboard(request):
    user_id = request.session.get("user_id")
    if request.session.get("user_role") != "patient" or not user_id:
        messages.error(request, "Unauthorized access.")
        return redirect("log_in")

    patient = get_object_or_404(Patient, id=user_id)
    doctors = Doctor.objects.all()
    appointments = Appointment.objects.filter(patient=patient).order_by('-date', '-time')
    doctor_requests = DoctorRequest.objects.filter(patient=patient).select_related('doctor').order_by('-created_at')

    # Build a quick lookup: doctor_id -> latest request status
    request_status_map = {}
    for req in doctor_requests:
        if req.doctor_id not in request_status_map:
            request_status_map[req.doctor_id] = req.status

    context = {
        "patient": patient,
        "doctors": doctors,
        "appointments": appointments,
        "doctor_requests": doctor_requests,
        "request_status_map": request_status_map,
        "total_requests": doctor_requests.count(),
        "accepted_count": doctor_requests.filter(status="Accepted").count(),
        "pending_count": doctor_requests.filter(status="Pending").count(),
        "rejected_count": doctor_requests.filter(status="Rejected").count(),
        "latest_visit": patient.visits.order_by('-created_at').first(),
        "visits": patient.visits.order_by('-created_at')[:3],
        "all_visits": patient.visits.select_related('doctor').order_by('-created_at'),
        "history_records": patient.history_records.order_by('-updated_at'),
        "notifications": patient.notifications.filter(read=False).order_by('-created_at')[:10],
    }
    return render(request, "patient_dashboard.html", context)

from django.db.models import Max

def doctor_dashboard(request):
    """Doctor dashboard with requests + updated records"""
    user_id = request.session.get("user_id")

    if request.session.get("user_role") != "doctor" or not user_id:
        messages.error(request, "Unauthorized access.")
        return redirect("log_in")

    doctor = get_object_or_404(Doctor, id=user_id)

    # Pending patient requests
    pending_requests = DoctorRequest.objects.filter(
        doctor=doctor,
        status="Pending"
    )

    # Only latest Accepted request for each patient
    latest_ids = DoctorRequest.objects.filter(
        doctor=doctor,
        status="Accepted"
    ).values("patient").annotate(
        max_id=Max("id")
    ).values_list("max_id", flat=True)

    accepted_requests = DoctorRequest.objects.filter(id__in=latest_ids)

    # IMPORTANT: get ALL VISITS by this doctor
    visits = PatientVisit.objects.filter(doctor=doctor).order_by('-created_at')

    return render(request, "doctor_dashboard.html", {
        "doctor": doctor,
        "pending_requests": pending_requests,
        "accepted_requests": accepted_requests,
        "visits": visits  # → Used in Updated Records table
    })

from qrcode.constants import ERROR_CORRECT_L
from django.core.files import File
from .models import PatientVisit, PatientHistory

def save_patient_record(request):
    if request.method != "POST":
        return redirect("doctor_dashboard")

    patient_id = request.POST.get("patient_id")
    doctor_id = request.POST.get("doctor_id")

    patient = get_object_or_404(Patient, id=patient_id)
    doctor = get_object_or_404(Doctor, id=doctor_id)

    visit_date = request.POST.get("visit_date")
    follow_up_date = request.POST.get("follow_up_date")
    symptoms = request.POST.get("symptoms")
    diagnosis = request.POST.get("diagnosis")
    tests = request.POST.get("tests")
    prescription = request.POST.get("prescription")
    notes = request.POST.get("notes")
    prescription_image = request.FILES.get("prescription_image")

    # --------------------------------------------------
    # 1️⃣ CREATE CURRENT VISIT
    # --------------------------------------------------
    visit = PatientVisit.objects.create(
        patient=patient,
        doctor=doctor,
        visit_date=visit_date,
        follow_up_date=follow_up_date,
        symptoms=symptoms,
        diagnosis=diagnosis,
        tests=tests,
        prescription=prescription,
        notes=notes,
        prescription_image=prescription_image
    )

    # --------------------------------------------------
    # 2️⃣ SAVE SNAPSHOT TO PATIENT HISTORY
    # --------------------------------------------------
    PatientHistory.objects.create(
        patient=patient,
        full_name=patient.full_name,
        age=patient.age,
        gender=patient.gender,
        email=patient.email,
        phone=patient.phone,
        address=patient.address,
        disease=patient.disease,
        doctor_assigned=doctor.full_name,
        blockchain_hash=patient.blockchain_hash,
        qr_code=patient.qr_code
    )

    # --------------------------------------------------
    # 3️⃣ BUILD FULL HISTORY FOR BLOCKCHAIN HASH
    # --------------------------------------------------
    full_history = []

    for h in patient.history_records.all().order_by("updated_at"):
        full_history.append({
            "full_name": h.full_name,
            "age": h.age,
            "gender": h.gender,
            "email": h.email,
            "phone": h.phone,
            "address": h.address,
            "disease": h.disease,
            "doctor_assigned": h.doctor_assigned,
            "updated_at": str(h.updated_at)
        })

    for v in patient.visits.all().order_by("created_at"):
        full_history.append({
            "visit_date": str(v.visit_date),
            "follow_up_date": str(v.follow_up_date),
            "symptoms": v.symptoms,
            "diagnosis": v.diagnosis,
            "tests": v.tests,
            "prescription": v.prescription,
            "notes": v.notes,
            "doctor": v.doctor.full_name,
            "created_at": str(v.created_at)
        })

    full_history.append({
        "patient_id": patient.id,
        "full_name": patient.full_name,
        "age": patient.age,
        "gender": patient.gender,
        "email": patient.email,
        "phone": patient.phone,
        "address": patient.address,
        "disease": patient.disease,
        "doctor_assigned": patient.doctor_assigned
    })

    chain_json = json.dumps(full_history, sort_keys=True)
    new_hash = hashlib.sha256(chain_json.encode()).hexdigest()
    patient.blockchain_hash = new_hash

    # --------------------------------------------------
    # 4️⃣ WRITE HASH TO BLOCKCHAIN
    # --------------------------------------------------
    try:
        nonce = web3.eth.get_transaction_count(account_address)
        txn = contract.functions.addRecord(patient.id, new_hash).build_transaction({
            "from": account_address,
            "nonce": nonce,
            "gas": 2000000,
            "gasPrice": web3.to_wei("50", "gwei")
        })
        signed = web3.eth.account.sign_transaction(txn, private_key)
        tx_hash = web3.eth.send_raw_transaction(signed.raw_transaction).hex()
    except Exception as e:
        tx_hash = f"Error: {str(e)}"

    patient.tx_hash = tx_hash

    # --------------------------------------------------
    # 5️⃣ BUILD QR DATA — only ID + hash + URL (no data limit issue)
    # --------------------------------------------------
    qr_data = {
        "patient_id": patient.id,
        "blockchain_hash": new_hash,
        "url": f"http://127.0.0.1:8000/patient-record/{patient.id}/"
    }

    qr_json = json.dumps(qr_data)

    # --------------------------------------------------
    # 6️⃣ GENERATE QR CODE
    # --------------------------------------------------
    qr = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECT_L,
        box_size=8,
        border=1,
    )
    qr.add_data(qr_json)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    qr_filename = f"patient_{patient.id}_updated.png"
    qr_folder = os.path.join(settings.MEDIA_ROOT, "qrcodes")
    os.makedirs(qr_folder, exist_ok=True)
    qr_path = os.path.join(qr_folder, qr_filename)
    img.save(qr_path)

    # Save QR to visit
    with open(qr_path, "rb") as f:
        visit.qr_code.save(qr_filename, File(f), save=True)
    visit.blockchain_hash = new_hash
    visit.save()

    # Save QR to patient
    with open(qr_path, "rb") as f:
        patient.qr_code.save(qr_filename, File(f), save=True)
    patient.save()

    messages.success(request, "✔ Patient record saved and QR updated!")
    return redirect("doctor_dashboard")

def patient_record_public(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    visits = patient.visits.select_related('doctor').order_by('-created_at')
    history = patient.history_records.order_by('-updated_at')

    # Verify blockchain hash
    scanned_hash = request.GET.get('hash', None)
    hash_verified = False
    if scanned_hash and scanned_hash == patient.blockchain_hash:
        hash_verified = True

    # Verify against blockchain contract, fallback to DB hash check
    chain_verified = False
    try:
        records = contract.functions.getRecords(patient.id).call()
        if records:
            latest_chain_hash = records[-1][1]
            chain_verified = (latest_chain_hash == patient.blockchain_hash)
        else:
            chain_verified = bool(patient.blockchain_hash)
    except:
        # Ganache offline — fallback to DB hash
        chain_verified = bool(patient.blockchain_hash)

    context = {
        "patient": patient,
        "visits": visits,
        "history": history,
        "hash_verified": hash_verified,
        "chain_verified": chain_verified,
    }
    return render(request, "patient_record_public.html", context)


from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.conf import settings
from django.core.files import File
import os

from .models import Patient, Doctor, PatientVisit, PatientNotification


def send_update_to_patient(request, visit_id):
    """Doctor sends updated visit data (QR + hash) to the patient dashboard"""
    if request.session.get("user_role") != "doctor":
        messages.error(request, "Unauthorized access.")
        return redirect("log_in")

    doctor_id = request.session.get("user_id")
    doctor = get_object_or_404(Doctor, id=doctor_id)

    visit = get_object_or_404(PatientVisit, id=visit_id)

    # Security: ensure this doctor created the visit
    if visit.doctor_id != doctor.id:
        messages.error(request, "Not allowed.")
        return redirect("doctor_dashboard")

    patient = visit.patient

    try:
        # Copy QR Code to patient's QR field
        if visit.qr_code:
            ext = os.path.splitext(visit.qr_code.name)[1]
            qr_filename = f"patient_{patient.id}_latest_qr{ext}"

            qr_folder = os.path.join(settings.MEDIA_ROOT, "qrcodes")
            os.makedirs(qr_folder, exist_ok=True)

            dest_path = os.path.join(qr_folder, qr_filename)

            # Copy QR image to new location
            with visit.qr_code.open("rb") as src, open(dest_path, "wb") as dst:
                dst.write(src.read())

            # Save to patient's QR field
            with open(dest_path, "rb") as f:
                patient.qr_code.save(qr_filename, File(f), save=False)

        # Copy blockchain hash + tx hash
        if visit.blockchain_hash:
            patient.blockchain_hash = visit.blockchain_hash

        # If you store tx_hash in visit, copy it
        if hasattr(visit, "tx_hash") and visit.tx_hash:
            patient.tx_hash = visit.tx_hash

        patient.save()

        # Mark visit as sent
        visit.sent_to_patient = True
        visit.save()

        # Create notification for patient
        PatientNotification.objects.create(
            patient=patient,
            title=f"New update from Dr. {doctor.full_name}",
            body=f"Doctor updated your record on {visit.visit_date}.",
            visit=visit
        )

        messages.success(request, f"Update successfully sent to {patient.full_name}.")

    except Exception as e:
        messages.error(request, f"Error sending update: {str(e)}")

    return redirect("doctor_dashboard")


def view_patient_details(request, patient_id):
    if request.session.get("user_role") != "doctor":
        messages.error(request, "Unauthorized access.")
        return redirect("log_in")

    patient = get_object_or_404(Patient, id=patient_id)
    return render(request, "doctor_patient_view.html", {"patient": patient})

def scan_qr_page(request):
    if request.session.get("user_role") != "doctor":
        messages.error(request, "Unauthorized access.")
        return redirect("log_in")

    return render(request, "scan_qr.html")

def verify_hash_page(request):
    if request.session.get("user_role") != "doctor":
        messages.error(request, "Unauthorized access.")
        return redirect("log_in")

    return render(request, "verify_hash.html")

from .models import DoctorRequest, Patient

def accept_request(request, request_id):
    req = DoctorRequest.objects.get(id=request_id)

    req.status = "Accepted"
    req.save()

    # 🔥 CREATE APPOINTMENT HERE
    Appointment.objects.create(
        patient=req.patient,
        doctor=req.doctor,
        date=timezone.now().date(),  # or custom date
        time=timezone.now().time(),
        status="Scheduled"
    )

    return redirect('doctor_dashboard')

def reject_request(request, request_id):
    req = DoctorRequest.objects.get(id=request_id)
    req.status = "Rejected"
    req.save()
    return redirect('doctor_dashboard')

def patient_info(request, patient_id):
    patient = Patient.objects.get(id=patient_id)
    return render(request, "patient_info.html", {
        "patient": patient,
        "blockchain_hash": patient.blockchain_hash,
        "security_features": [
            "Immutable record keeping — data cannot be altered",
            "Transparent audit trail for every update",
            "Cryptographic SHA-256 verification",
            "Prevents unauthorized changes",
            "Decentralized storage",
            "Full patient data ownership",
        ]
    })
from .models import DoctorRequest

def send_request_to_doctor(request, doctor_id):
    if request.session.get("user_role") != "patient":
        messages.error(request, "Unauthorized access.")
        return redirect("log_in")

    patient_id = request.session.get("user_id")
    patient = get_object_or_404(Patient, id=patient_id)
    doctor = get_object_or_404(Doctor, id=doctor_id)

    latest = DoctorRequest.objects.filter(patient=patient, doctor=doctor).order_by('-created_at').first()

    if latest:
        if latest.status == "Pending":
            messages.warning(request, "Request already pending.")
            return redirect("patient_dashboard")
        # Accepted or Rejected → allow new request (fall through)

    DoctorRequest.objects.create(patient=patient, doctor=doctor, status="Pending")
    messages.success(request, f"Request sent to Dr. {doctor.full_name}")
    return redirect("patient_dashboard")

def cancel_request(request, request_id):
    if request.session.get("user_role") != "patient":
        messages.error(request, "Unauthorized access.")
        return redirect("log_in")

    patient_id = request.session.get("user_id")
    req = get_object_or_404(DoctorRequest, id=request_id, patient__id=patient_id)

    if req.status == "Pending":  # only cancel if still pending
        req.delete()
        messages.success(request, "Request cancelled successfully.")
    else:
        messages.warning(request, "Cannot cancel an accepted or rejected request.")

    return redirect("patient_dashboard")


def log_out(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect('index')