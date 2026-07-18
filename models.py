from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Attendee(db.Model):
    """A registered event attendee and their QR ticket state."""

    __tablename__ = "attendees"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    ticket_type = db.Column(db.String(20), default="General", nullable=False)
    ticket_code = db.Column(db.String(36), unique=True, nullable=False, index=True)

    is_checked_in = db.Column(db.Boolean, default=False, nullable=False)
    checkin_time = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "ticket_type": self.ticket_type,
            "ticket_code": self.ticket_code,
            "is_checked_in": self.is_checked_in,
            "checkin_time": self.checkin_time.strftime("%H:%M:%S") if self.checkin_time else None,
        }

    def __repr__(self):
        return f"<Attendee {self.name} ({self.ticket_code[:8]})>"
