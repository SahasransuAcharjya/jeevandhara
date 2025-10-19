from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from bson.objectid import ObjectId
from app import db

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/blood-units', methods=['GET'])
@jwt_required()
def get_blood_units():
    units = list(db.blood_units.find())
    for u in units:
        u['_id'] = str(u['_id'])
    return jsonify(units)

@admin_bp.route('/blood-units', methods=['POST', 'PUT'])
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
        db.blood_units.update_one({"_id": ObjectId(unit_id)}, {"$set": data})
        return jsonify({"msg": "Blood unit updated"}), 200

@admin_bp.route('/blood-units/<unit_id>', methods=['DELETE'])
@jwt_required()
def delete_blood_unit(unit_id):
    db.blood_units.delete_one({"_id": ObjectId(unit_id)})
    return jsonify({"msg": "Blood unit deleted"}), 200

@admin_bp.route('/requests', methods=['GET'])
@jwt_required()
def get_requests():
    requests = list(db.blood_requests.find())
    for r in requests:
        r['_id'] = str(r['_id'])
    return jsonify(requests)

@admin_bp.route('/requests/<request_id>', methods=['PUT'])
@jwt_required()
def update_request_status(request_id):
    data = request.json
    status = data.get('status')
    if status is None:
        return jsonify({"msg": "Missing status"}), 400
    db.blood_requests.update_one({"_id": ObjectId(request_id)}, {"$set": {"status": status}})
    return jsonify({"msg": "Request status updated"}), 200

@admin_bp.route('/emergency-alert', methods=['POST'])
@jwt_required()
def send_emergency_alert():
    data = request.json
    # Integration with SMS/email API should be implemented here.
    blood_type = data.get('bloodType')
    region = data.get('region')
    # For demo, just return success message
    return jsonify({"msg": f"Emergency alert sent to {blood_type} donors in {region}"}), 200
