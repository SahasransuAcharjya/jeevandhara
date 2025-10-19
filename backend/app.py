from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from pymongo import MongoClient
from bson.objectid import ObjectId

# Import route blueprints
from routes.auth import auth_bp
from routes.donor import donor_bp
from routes.hospital import hospital_bp
from routes.admin import admin_bp

import os

app = Flask(__name__)
CORS(app)

# Load configuration
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'super-secret-key')
app.config['MONGO_URI'] = os.getenv('MONGO_URI', 'mongodb://localhost:27017/jeevandhara')

jwt = JWTManager(app)

# MongoDB client setup
mongo_client = MongoClient(app.config['MONGO_URI'])
db = mongo_client.get_default_database()  # Default db from URI
app.db = db  # Attach db to app for shared access

# ObjectId converter for JSON responses
@app.before_request
def convert_objectid_to_str():
    # Custom function to help serialize Mongo IDs - use in routes when needed
    pass

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(donor_bp)
app.register_blueprint(hospital_bp)
app.register_blueprint(admin_bp)

# Make db accessible from imported modules
import sys
sys.modules['app'] = app

# Error handling
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

# Root endpoint to check if server is running
@app.route('/')
def index():
    return jsonify({"msg": "JeevanDhara API server running!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
