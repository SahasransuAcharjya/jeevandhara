from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from app import db
from models.donor import Donor
from models.appointment import Appointment

donor_bp = Blueprint('donor', __name__, url_prefix='/donor')

@donor_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    donor_id = get_jwt_identity()
    donor_data = db.donors.find_one({'_id': donor_id})
    if not donor_data:
        return jsonify({"msg": "Donor not found"}), 404
    donor = Donor.from_dict(donor_data)
    profile = donor.to_dict()
    profile.pop('password_hash', None)  # Remove sensitive data
    return jsonify(profile)

@donor_bp.route('/book-appointment', methods=['POST'])
@jwt_required()
def book_appointment():
    donor_id = get_jwt_identity()
    data = request.json
    try:
        appointment_date = datetime.fromisoformat(data.get('date'))
        location = data.get('location')
        appointment = Appointment(donor_id, appointment_date, location)
        db.appointments.insert_one(appointment.to_dict())
        return jsonify({"msg": "Appointment booked successfully"}), 201
    except Exception as e:
        return jsonify({"msg": "Failed to book appointment", "error": str(e)}), 400

@donor_bp.route('/appointments', methods=['GET'])
@jwt_required()
def list_appointments():
    donor_id = get_jwt_identity()
    appointments = list(db.appointments.find({'donor_id': donor_id}))
    for a in appointments:
        a['_id'] = str(a['_id'])
        a['date'] = a['date'].isoformat() if isinstance(a['date'], datetime) else a['date']
    return jsonify(appointments)

@donor_bp.route('/check-eligibility', methods=['POST'])
@jwt_required()
def check_eligibility():
    data = request.json
    # Simplified eligibility: not donated in last 3 months, healthy status
    donor_id = get_jwt_identity()
    donor_data = db.donors.find_one({'_id': donor_id})
    if not donor_data:
        return jsonify({"eligible": False, "reason": "Donor not found"}), 404

    last_donation = donor_data.get('last_donation_date')
    healthy = data.get('health') == 'yes'

    if not healthy:
        return jsonify({"eligible": False, "reason": "Not healthy today"})

    if last_donation:
        last_date = last_donation if isinstance(last_donation, datetime) else datetime.fromisoformat(last_donation)
        if datetime.utcnow() - last_date < timedelta(days=90):
            return jsonify({"eligible": False, "reason": "Donation too recent"})

    return jsonify({"eligible": True})

@donor_bp.route('/history', methods=['GET'])
@jwt_required()
def donation_history():
    donor_id = get_jwt_identity()
    donations = list(db.donations.find({'donor_id': donor_id}))
    for d in donations:
        d['_id'] = str(d['_id'])
        d['date'] = d['date'].isoformat() if isinstance(d['date'], datetime) else d['date']
    return jsonify(donations)
