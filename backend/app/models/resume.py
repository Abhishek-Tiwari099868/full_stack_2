from datetime import datetime
from app.extensions import db

class Resume(db.Model):
    __tablename__ = "resumes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)  # Path in the Supabase Storage bucket
    file_url = db.Column(db.Text, nullable=False)         # Public URL of the uploaded resume
    raw_text = db.Column(db.Text, nullable=True)          # Extracted raw text content
    extracted_name = db.Column(db.String(100), nullable=True)
    extracted_role = db.Column(db.String(100), nullable=True)
    extracted_skills = db.Column(db.JSON, nullable=True)  # List of technical skill chips
    analysis = db.Column(db.JSON, nullable=True)          # Structured analysis evaluation feedback from Gemini

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # One-to-one relationship with User
    user = db.relationship("User", backref=db.backref("resume", uselist=False, cascade="all, delete-orphan"))

    def __repr__(self):
        return f"<Resume {self.filename} for User {self.user_id}>"
