from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.dialects.postgresql import UUID, ARRAY, TEXT
import uuid
import sys
from flask_login import UserMixin, login_user
from db_models.databases import db


class User(db.Model, UserMixin):
    # primary keys are required by SQLAlchemy
    __tablename__ = 'Users'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = db.Column(db.String(255))
    email = db.Column(db.String(100), unique=True)
    password_hash = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, default=True)

    # New fields for survey information
    professional_role = db.Column(db.String(100))
    industry_sector = db.Column(db.String(100))
    expertise_level = db.Column(db.String(100))
    persona_prompt = db.Column(TEXT)
    follow_up_questions_prompt_1 = db.Column(TEXT)
    follow_up_questions_prompt_2 = db.Column(TEXT)
    system_prompt = db.Column(TEXT)
    prefix_prompt = db.Column(TEXT)
    technical_level = db.Column(db.String(100))
    bias_awareness = db.Column(db.String(100))
    areas_of_interest = db.Column(ARRAY(db.String(100)))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def signup(self):
        try:
            db.session.add(self)
            db.session.commit()
            login_user(self, remember=True)
        except Exception as e:
            print(str(e))
            sys.stdout.flush()
            db.session.rollback()
