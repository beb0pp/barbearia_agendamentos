import os
from dotenv import load_dotenv

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'chave-temporaria-desenvolvimento'
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(basedir, 'database', 'db.sqlite3')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FLASK_ENV = os.environ.get('FLASK_ENV', 'production')
    FLASK_DEBUG = os.environ.get('FLASK_DEBUG', '0') == '1'
