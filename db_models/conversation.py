from db_models.users import db
from sqlalchemy.dialects.postgresql import JSON
import uuid
import datetime
import sys


class Conversation(db.Model):
    __tablename__ = 'conversation'
    user_id = db.Column(db.String(128), primary_key=True)
    session_id = db.Column(db.String(128), primary_key=True)
    model = db.Column(db.String(128))
    dataset = db.Column(db.String(256))
    messages = db.Column(JSON)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now)

    def __init__(self, user_id, session_id, dataset, model, messages):
        self.user_id = user_id
        self.session_id = session_id
        self.dataset = dataset
        self.model = model
        self.messages = messages

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            print(str(e))
            sys.stdout.flush()
            db.session.rollback()

    @staticmethod
    def upsert(user_id, session_id, dataset, model, messages):
        conversation = db.session.query(Conversation).\
            filter(Conversation.user_id == user_id).\
            filter(Conversation.session_id == session_id).first()

        if not conversation:
            conversation = Conversation(
                user_id, session_id, dataset, model, messages)
        else:
            conversation.messages = messages

        conversation.save()

    @staticmethod
    def get_user_conversations(user_id):
        conversations = db.session.query(Conversation).\
            filter(Conversation.user_id == user_id).\
            order_by(Conversation.updated_at.desc()).all()
        return conversations
