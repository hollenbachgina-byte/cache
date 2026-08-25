from datetime import datetime

from app import db


class Feedback(db.Model):
    """In-app feedback widget submissions. No in-app view — reviewed via
    Flask-Admin only."""

    __tablename__ = "feedback"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    message = db.Column(db.Text, nullable=False)
    # The route the user was on when they submitted — captured automatically
    # server-side, never a field the user sees or fills in.
    page_context = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship("User", backref="feedback_submissions")

    def __repr__(self):
        return f"<Feedback {self.id} from user {self.user_id}>"
