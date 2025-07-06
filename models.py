from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json

db = SQLAlchemy()

class Team(db.Model):
    __tablename__ = 'teams'
    
    id = db.Column(db.Integer, primary_key=True)
    team_name = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    institution = db.Column(db.String(200), nullable=False)
    members = db.Column(db.Text, nullable=False)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    round1_completed = db.Column(db.Boolean, default=False)
    round2_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    submissions = db.relationship('Submission', backref='team', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'team_name': self.team_name,
            'institution': self.institution,
            'members': self.members,
            'registered_at': self.registered_at.isoformat() if self.registered_at else None,
            'round1_completed': self.round1_completed,
            'round2_completed': self.round2_completed
        }

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)  # The quantity amount (e.g., 100, 50, 1, 4)
    unit_type = db.Column(db.String(10), nullable=False)  # 'grams' or 'pieces'
    image_filename = db.Column(db.String(255), nullable=True)  # Stored image filename
    image_data = db.Column(db.LargeBinary, nullable=True)  # Store image as binary data
    image_mimetype = db.Column(db.String(50), nullable=True)  # Store MIME type (image/jpeg, image/png, etc.)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def unit_display(self):
        """Display the full unit description like 'per 100 grams' or '4 pieces'"""
        if self.unit_type == 'grams':
            return f"per {self.quantity} grams"
        else:  # pieces
            return f"{self.quantity} piece{'s' if self.quantity != 1 else ''}"
    
    @property 
    def unit_price(self):
        """Price per single unit (gram or piece)"""
        return float(self.price) / self.quantity
    
    @property
    def image_url(self):
        """Get the URL for the product image"""
        if self.image_data:
            return f"/product_image/{self.id}"
        elif self.image_filename:
            return f"/static/uploads/{self.image_filename}"
        return None
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': float(self.price),
            'quantity': self.quantity,
            'unit_type': self.unit_type,
            'unit_display': self.unit_display,
            'unit_price': self.unit_price,
            'image_url': self.image_url,
            'is_active': self.is_active
        }

class Submission(db.Model):
    __tablename__ = 'submissions'
    
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    round_number = db.Column(db.SmallInteger, nullable=False)
    submission_data = db.Column(db.Text, nullable=False)  # JSON string
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    total_grams = db.Column(db.Integer, default=0)
    total_pieces = db.Column(db.Integer, default=0)
    score = db.Column(db.Numeric(10, 4), nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('team_id', 'round_number', name='unique_team_round'),)
    
    def get_items(self):
        """Parse the submission_data JSON string to get items list"""
        try:
            return json.loads(self.submission_data)
        except:
            return []
    
    def set_items(self, items_list):
        """Store items list as JSON string"""
        self.submission_data = json.dumps(items_list)
    
    def to_dict(self):
        team = Team.query.get(self.team_id)
        return {
            'id': self.id,
            'team_name': team.team_name if team else 'Unknown',
            'round_number': self.round_number,
            'items': self.get_items(),
            'total_price': float(self.total_price),
            'total_grams': self.total_grams,
            'total_pieces': self.total_pieces,
            'score': float(self.score),
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None
        }

class Setting(db.Model):
    __tablename__ = 'settings'
    
    id = db.Column(db.Integer, primary_key=True)
    setting_key = db.Column(db.String(50), unique=True, nullable=False)
    setting_value = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @staticmethod
    def get_setting(key, default=None):
        setting = Setting.query.filter_by(setting_key=key).first()
        return setting.setting_value if setting else default
    
    @staticmethod
    def set_setting(key, value, description=None):
        setting = Setting.query.filter_by(setting_key=key).first()
        if setting:
            setting.setting_value = str(value)
            if description:
                setting.description = description
        else:
            setting = Setting()
            setting.setting_key = key
            setting.setting_value = str(value)
            if description:
                setting.description = description
            db.session.add(setting)
        db.session.commit()
        return setting
    
    def to_dict(self):
        return {
            'id': self.id,
            'setting_key': self.setting_key,
            'setting_value': self.setting_value,
            'description': self.description
        }

