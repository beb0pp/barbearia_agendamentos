# models.py
from extensions import db
from flask_login import UserMixin
from datetime import datetime

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    # Não precisa adicionar nada aqui, o `backref='cliente'` já conecta os dois


class Agendamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    servico = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    data = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)
    criado_em = db.Column(db.DateTime, default=db.func.current_timestamp())

    cliente = db.relationship('User', backref='agendamentos')
