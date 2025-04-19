import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = 'sua_chave_secreta'
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(basedir, 'database', 'db.sqlite3')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
