# models.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Annotation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    paragraph_id = db.Column(db.String, index=True)
    source_filename = db.Column(db.String)
    page = db.Column(db.Integer)
    offset_start = db.Column(db.Integer)
    offset_end = db.Column(db.Integer)
    created_at = db.Column(db.DateTime)
    model = db.Column(db.String)
    prompt_version = db.Column(db.String)
    annotation_data = db.Column(db.JSON)
