from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password_hash = db.Column(db.String(200), nullable=False)
    intro = db.Column(db.Text, default="Hi. I'm new to CoWrite. Let's collaborate and write stories together!")
    profile_image = db.Column(db.String(255), nullable=True)

    # Relationship to drafts and contributions
    drafts = db.relationship("CoDraft", backref="creator", lazy=True)
    contributions = db.relationship("Contribution", backref="author", lazy=True)

class CoDraft(db.Model):
    __tablename__ = "codrafts"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50), nullable=False)

    # Maximum contribution limit
    max_units = db.Column(db.Integer, nullable=False)
    max_unit_type = db.Column(db.String(20), nullable=False) # Words, sentences, paragraphs

    # Whether the draft is finished
    is_completed = db.Column(db.Boolean, default=False)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Foreign key: who created it
    creator_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    # Relationship to contributions
    contributions = db.relationship("Contribution", backref="codraft", lazy=True)

class Contribution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codraft_id = db.Column(db.Integer, db.ForeignKey("codrafts.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    # Snapshot of the text at that moment
    text_snapshot = db.Column(db.Text, nullable=False)

    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
