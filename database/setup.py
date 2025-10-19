from pymongo import MongoClient, ASCENDING
import os

def initialize_db():
    mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/jeevandhara')
    client = MongoClient(mongo_uri)
    db = client.get_default_database()

    # Create indexes for fast querying and uniqueness constraints
    db.donors.create_index([('email', ASCENDING)], unique=True)
    db.blood_units.create_index([('bag_id', ASCENDING)], unique=True)
    db.appointments.create_index([('donor_id', ASCENDING)])
    db.blood_requests.create_index([('hospital_name', ASCENDING)])
    db.blood_requests.create_index([('status', ASCENDING)])

    print("Indexes created successfully.")

    # Seed initial blood bank locations or camps if needed (optional)
    locations = [
        {"name": "AIIMS Delhi", "address": "Ansari Nagar, New Delhi", "type": "Permanent"},
        {"name": "Fortis Gurgaon", "address": "Gurgaon, Haryana", "type": "Permanent"},
        {"name": "Mobile Camp - Connaught Place", "address": "Connaught Place, New Delhi", "type": "Camp", "date": "2025-10-25"}
    ]
    if db.locations.count_documents({}) == 0:
        db.locations.insert_many(locations)
        print("Seeded initial blood bank locations.")

if __name__ == '__main__':
    initialize_db()
