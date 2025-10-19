from datetime import datetime

class Appointment:
    def __init__(self, donor_id, date, location, status='Pending'):
        self.donor_id = donor_id
        self.date = date  # datetime object
        self.location = location
        self.status = status  # Pending, Confirmed, Completed, Cancelled
        self.created_at = datetime.utcnow()

    def to_dict(self):
        return {
            "donor_id": self.donor_id,
            "date": self.date,
            "location": self.location,
            "status": self.status,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            donor_id=data.get('donor_id'),
            date=data.get('date'),
            location=data.get('location'),
            status=data.get('status', 'Pending')
        )
