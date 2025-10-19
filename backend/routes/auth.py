from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from datetime import timedelta
from app import db  # MongoDB client instance
from models.donor import Donor

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.json
    email = data.get('email')
    if db.donors.find_one({'email': email}):
        return jsonify({"msg": "Email already registered"}), 409

    password_hash = generate_password_hash(data.get('password'))
    donor = Donor(
        name=data.get('name'),
        email=email,
        password_hash=password_hash,
        blood_type=data.get('blood_type'),
        phone=data.get('phone'),
        address=data.get('address')
    )
    db.donors.insert_one(donor.to_dict())
    return jsonify({"msg": "User registered successfully"}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    user_data = db.donors.find_one({'email': email})
    if not user_data or not check_password_hash(user_data.get('password_hash'), password):
        return jsonify({"msg": "Invalid email or password"}), 401
    
    access_token = create_access_token(identity=str(user_data['_id']), expires_delta=timedelta(hours=8))
    return jsonify({"token": access_token, "user": {"name": user_data['name'], "blood_type": user_data['blood_type']}}), 200
