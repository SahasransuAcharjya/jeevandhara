from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity
)
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient, ASCENDING
from datetime import datetime, timedelta
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

app = Flask(__name__)
CORS(app)

# Configuration
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'd1f2ba046ba2496397ca603fc1559485912a8d4323de4dc0b845c8b8d5067b93')
app.config['MONGO_URI'] = os.getenv('MONGO_URI', 'mongodb://localhost:27017/bloodbank')

# Initialize JWT and MongoDB
jwt = JWTManager(app)
client = MongoClient(app.config['MONGO_URI'])
db = client.get_default_database()

# ===========================
# Models as simple classes
# ===========================

class Donor:
    def __init__(self, name, email, password_hash, blood_type, phone=None, address=None, last_donation_date=None, total_donations=0, eligibility_status=True):
        self.name = name
        self.email = email
        self.password_hash = password_hash
        self.blood_type = blood_type
        self.phone = phone
        self.address = address
        self.last_donation_date = last_donation_date
        self.total_donations = total_donations
        self.eligibility_status = eligibility_status

    def to_dict(self):
        return {
            "name": self.name,
            "email": self.email,
            "password_hash": self.password_hash,
            "blood_type": self.blood_type,
            "phone": self.phone,
            "address": self.address,
            "last_donation_date": self.last_donation_date,
            "total_donations": self.total_donations,
            "eligibility_status": self.eligibility_status
        }

class Appointment:
    def __init__(self, donor_id, date, location, status='Pending'):
        self.donor_id = donor_id
        self.date = date
        self.location = location
        self.status = status
        self.created_at = datetime.utcnow()

    def to_dict(self):
        return {
            "donor_id": self.donor_id,
            "date": self.date,
            "location": self.location,
            "status": self.status,
            "created_at": self.created_at
        }

class BloodUnit:
    def __init__(self, bag_id, blood_type, collection_date, expiry_date, location, status='Available'):
        self.bag_id = bag_id
        self.blood_type = blood_type
        self.collection_date = collection_date
        self.expiry_date = expiry_date
        self.location = location
        self.status = status

    def to_dict(self):
        return {
            "bag_id": self.bag_id,
            "blood_type": self.blood_type,
            "collection_date": self.collection_date,
            "expiry_date": self.expiry_date,
            "location": self.location,
            "status": self.status
        }

# ===========================
# Utility functions
# ===========================

def chatbot_response(message):
    message = message.lower()
    faqs = {
        "how to donate": "Register and schedule your appointment through JeevanDhara.",
        "eligibility": "You must be healthy and not donated in last 3 months.",
        "emergency": "Use emergency alert system or contact nearby blood bank.",
        "thank you": "Thank you for supporting blood donation!"
    }
    for key in faqs:
        if key in message:
            return faqs[key]
    return "Sorry, I didn't understand. Please rephrase your question."

def geocode_address(address):
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": address, "format": "json", "limit": 1}
    headers = {'User-Agent': 'JeevanDharaApp'}
    try:
        resp = requests.get(url, params=params, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        if not data:
            return None
        return {
            "latitude": float(data[0]["lat"]),
            "longitude": float(data[0]["lon"]),
            "display_name": data[0]["display_name"]
        }
    except Exception as e:
        print("Geocoding error:", e)
        return None

def send_email(to_email, subject, body):
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    smtp_user = os.getenv('SMTP_USERNAME')
    smtp_pass = os.getenv('SMTP_PASSWORD')
    if not smtp_user or not smtp_pass:
        print("SMTP credentials missing")
        return False

    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print("Email send error:", e)
        return False

# ===========================
# Routes
# ===========================

# Authentication Routes
@app.route('/auth/signup', methods=['POST'])
def signup():
    data = request.json
    if db.donors.find_one({"email": data.get('email')}):
        return jsonify({"msg": "Email already exists"}), 409
    password_hash = generate_password_hash(data.get('password'))
    donor = Donor(
        name=data.get('name'),
        email=data.get('email'),
        password_hash=password_hash,
        blood_type=data.get('blood_type'),
        phone=data.get('phone'),
        address=data.get('address')
    )
    db.donors.insert_one(donor.to_dict())
    return jsonify({"msg": "User registered successfully"}), 201

@app.route('/auth/login', methods=['POST'])
def login():
    data = request.json
    user = db.donors.find_one({"email": data.get('email')})
    if not user or not check_password_hash(user['password_hash'], data.get('password')):
        return jsonify({"msg": "Invalid credentials"}), 401
    access_token = create_access_token(identity=str(user['_id']), expires_delta=timedelta(hours=8))
    return jsonify({
        "token": access_token,
        "user": {"name": user['name'], "blood_type": user['blood_type']}
    }), 200

# Donor Routes
@app.route('/donor/profile', methods=['GET'])
@jwt_required()
def donor_profile():
    user_id = get_jwt_identity()
    user = db.donors.find_one({"_id": user_id})
    if not user:
        return jsonify({"msg": "Donor not found"}), 404
    user.pop('password_hash', None)
    user['_id'] = str(user['_id'])
    return jsonify(user)

@app.route('/donor/book-appointment', methods=['POST'])
@jwt_required()
def book_appointment():
    user_id = get_jwt_identity()
    data = request.json
    try:
        appt_date = datetime.fromisoformat(data.get('date'))
        location = data.get('location')
        appointment = Appointment(user_id, appt_date, location)
        db.appointments.insert_one(appointment.to_dict())
        return jsonify({"msg": "Appointment booked"}), 201
    except Exception as e:
        return jsonify({"msg": "Failed to book appointment", "error": str(e)}), 400

@app.route('/donor/appointments', methods=['GET'])
@jwt_required()
def get_appointments():
    user_id = get_jwt_identity()
    appts = list(db.appointments.find({"donor_id": user_id}))
    for a in appts:
        a['_id'] = str(a['_id'])
        a['date'] = a['date'].isoformat() if isinstance(a['date'], datetime) else a['date']
    return jsonify(appts)

@app.route('/donor/check-eligibility', methods=['POST'])
@jwt_required()
def check_eligibility():
    data = request.json
    user_id = get_jwt_identity()
    user = db.donors.find_one({'_id': user_id})
    if not user:
        return jsonify({"eligible": False, "reason": "Donor not found"}), 404
    last_donation = user.get('last_donation_date')
    healthy = data.get('health') == 'yes'

    if not healthy:
        return jsonify({"eligible": False, "reason": "Not healthy today"})

    if last_donation:
        last_dt = last_donation if isinstance(last_donation, datetime) else datetime.fromisoformat(last_donation)
        if datetime.utcnow() - last_dt < timedelta(days=90):
            return jsonify({"eligible": False, "reason": "Donation too recent"})

    return jsonify({"eligible": True})

@app.route('/donor/history', methods=['GET'])
@jwt_required()
def donation_history():
    user_id = get_jwt_identity()
    history = list(db.donations.find({"donor_id": user_id}))
    for h in history:
        h['_id'] = str(h['_id'])
        h['date'] = h['date'].isoformat() if isinstance(h['date'], datetime) else h['date']
    return jsonify(history)

# Hospital Routes
@app.route('/hospital/blood-stock', methods=['GET'])
def blood_stock():
    blood_type = request.args.get('bloodType')
    location = request.args.get('location')
    query = {}
    if blood_type:
        query['blood_type'] = blood_type
    if location:
        query['location'] = location
    stock = list(db.blood_units.find(query))
    for s in stock:
        s['_id'] = str(s['_id'])
    return jsonify(stock)

@app.route('/hospital/request-blood', methods=['POST'])
@jwt_required()
def request_blood():
    data = request.json
    req = {
        "hospital_name": data.get('hospitalName'),
        "blood_type": data.get('bloodType'),
        "units": data.get('units'),
        "urgency": data.get('urgency', 'normal'),
        "status": "Pending",
        "requested_at": datetime.utcnow()
    }
    result = db.blood_requests.insert_one(req)
    return jsonify({"msg": "Request submitted", "requestId": str(result.inserted_id)}), 201

@app.route('/hospital/requests', methods=['GET'])
@jwt_required()
def hospital_requests():
    requests_list = list(db.blood_requests.find({}))
    for r in requests_list:
        r['_id'] = str(r['_id'])
    return jsonify(requests_list)

# Admin Routes
@app.route('/admin/blood-units', methods=['GET'])
@jwt_required()
def get_blood_units():
    units = list(db.blood_units.find())
    for u in units:
        u['_id'] = str(u['_id'])
    return jsonify(units)

@app.route('/admin/blood-units', methods=['POST', 'PUT'])
@jwt_required()
def manage_blood_unit():
    data = request.json
    if request.method == 'POST':
        result = db.blood_units.insert_one(data)
        return jsonify({"msg": "Blood unit added", "unitId": str(result.inserted_id)}), 201
    elif request.method == 'PUT':
        unit_id = data.get('_id')
        if not unit_id:
            return jsonify({"msg": "Missing unit ID"}), 400
        db.blood_units.update_one({"_id": unit_id}, {"$set": data})
        return jsonify({"msg": "Blood unit updated"}), 200

@app.route('/admin/blood-units/<unit_id>', methods=['DELETE'])
@jwt_required()
def delete_blood_unit(unit_id):
    db.blood_units.delete_one({"_id": unit_id})
    return jsonify({"msg": "Blood unit deleted"}), 200

@app.route('/admin/requests', methods=['GET'])
@jwt_required()
def get_requests():
    requests = list(db.blood_requests.find())
    for r in requests:
        r['_id'] = str(r['_id'])
    return jsonify(requests)

@app.route('/admin/requests/<request_id>', methods=['PUT'])
@jwt_required()
def update_request_status(request_id):
    data = request.json
    status = data.get('status')
    if not status:
        return jsonify({"msg": "Missing status"}), 400
    db.blood_requests.update_one({"_id": request_id}, {"$set": {"status": status}})
    return jsonify({"msg": "Request status updated"}), 200

@app.route('/admin/emergency-alert', methods=['POST'])
@jwt_required()
def send_emergency_alert():
    data = request.json
    blood_type = data.get('bloodType')
    region = data.get('region')
    # Here you should integrate SMS/email dispatch with real provider
    return jsonify({"msg": f"Emergency alert sent to {blood_type} donors in {region}"}), 200

# Root route
@app.route('/')
def home():
    return jsonify({"msg": "JeevanDhara backend running"})

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

# Create indexes on startup
if __name__ == '__main__':
    db.donors.create_index([('email', ASCENDING)], unique=True)
    db.blood_units.create_index([('bag_id', ASCENDING)], unique=True)
    db.appointments.create_index([('donor_id', ASCENDING)])
    db.blood_requests.create_index([('hospital_name', ASCENDING)])
    db.blood_requests.create_index([('status', ASCENDING)])

    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
