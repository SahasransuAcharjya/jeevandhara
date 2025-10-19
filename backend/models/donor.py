from datetime import datetime

class Donor:
    def __init__(self, name, email, password_hash, blood_type, phone=None, address=None, last_donation_date=None, total_donations=0, eligibility_status=True):
        self.name = name
        self.email = email
        self.password_hash = password_hash
        self.blood_type = blood_type  # e.g., A+, O-
        self.phone = phone
        self.address = address
        self.last_donation_date = last_donation_date  # datetime object
        self.total_donations = total_donations
        self.eligibility_status = eligibility_status  # True if eligible to donate

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

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data.get('name'),
            email=data.get('email'),
            password_hash=data.get('password_hash'),
            blood_type=data.get('blood_type'),
            phone=data.get('phone'),
            address=data.get('address'),
            last_donation_date=data.get('last_donation_date'),
            total_donations=data.get('total_donations', 0),
            eligibility_status=data.get('eligibility_status', True)
        )
