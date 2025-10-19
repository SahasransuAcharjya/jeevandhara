from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db

hospital_bp = Blueprint('hospital', __name__, url_prefix='/hospital')

@hospital_bp.route('/blood-stock', methods=['GET'])
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

@hospital_bp.route('/request-blood', methods=['POST'])
@jwt_required()
def request_blood():
    data = request.json
    request_doc = {
        "hospital_name": data.get('hospitalName'),
        "blood_type": data.get('bloodType'),
        "units": data.get('units'),
        "urgency": data.get('urgency', 'normal'),
        "status": "Pending",
        "requested_at": datetime.utcnow()
    }
    result = db.blood_requests.insert_one(request_doc)
    return jsonify({"msg": "Blood request submitted", "requestId": str(result.inserted_id)}), 201

@hospital_bp.route('/requests', methods=['GET'])
@jwt_required()
def get_requests():
    requests = list(db.blood_requests.find({}))
    for r in requests:
        r['_id'] = str(r['_id'])
    return jsonify(requests)
