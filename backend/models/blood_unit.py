from datetime import datetime

class BloodUnit:
    def __init__(self, bag_id, blood_type, collection_date, expiry_date, location, status='Available'):
        self.bag_id = bag_id  # Unique identifier for blood bag
        self.blood_type = blood_type  # e.g., A+, B-, O+
        self.collection_date = collection_date  # datetime object
        self.expiry_date = expiry_date  # datetime object
        self.location = location  # Blood bank location string
        self.status = status  # Available, Reserved, Used, Expired

    def to_dict(self):
        return {
            "bag_id": self.bag_id,
            "blood_type": self.blood_type,
            "collection_date": self.collection_date,
            "expiry_date": self.expiry_date,
            "location": self.location,
            "status": self.status
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            bag_id=data.get('bag_id'),
            blood_type=data.get('blood_type'),
            collection_date=data.get('collection_date'),
            expiry_date=data.get('expiry_date'),
            location=data.get('location'),
            status=data.get('status', 'Available')
        )
