# models.py
from extensions import db
from flask_login import UserMixin
from datetime import datetime

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    email = db.Column(db.String(150), unique=True)
    senha = db.Column(db.String(200))
    is_admin = db.Column(db.Boolean, default=False)

class Agendamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    servico = db.Column(db.String(100))
    preco = db.Column(db.Float)
    data = db.Column(db.Date)
    hora = db.Column(db.Time)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
