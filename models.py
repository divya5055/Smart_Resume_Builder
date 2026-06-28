from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

# ================= USER =================
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)
    #time_spent = db.Column(db.Integer)
    time_spent = db.Column(db.Integer, default=0)

# ================= RESUME =================
class Resume(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    template = db.Column(db.String(50))
    skills = db.Column(db.Text)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    linkedin = db.Column(db.String(200))
    summary = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='resumes')

    # ✅ ADD THESE RELATIONSHIPS
    educations = db.relationship('Education', backref='resume', lazy=True, cascade="all, delete-orphan")
    experiences = db.relationship('Experience', backref='resume', lazy=True, cascade="all, delete-orphan")
    projects = db.relationship('Project', backref='resume', lazy=True, cascade="all, delete-orphan")
    certificates = db.relationship('Certificate', backref='resume', lazy=True, cascade="all, delete-orphan")


class Education(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey('resume.id'), nullable=False)
    degree = db.Column(db.String(150))
    college = db.Column(db.String(200))
    year = db.Column(db.String(50))


class Experience(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey('resume.id'), nullable=False)
    company = db.Column(db.String(200))
    role = db.Column(db.String(150))
    duration = db.Column(db.String(100))
    description = db.Column(db.Text)


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey('resume.id'), nullable=False)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)


class Certificate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey('resume.id'), nullable=False)
    name = db.Column(db.String(200))
    
class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey('resume.id'), nullable=False)
    name = db.Column(db.String(100))