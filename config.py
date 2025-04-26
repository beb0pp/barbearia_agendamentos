import os
from dotenv import load_dotenv

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Diretamente pega a variável DATABASE_URL
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FLASK_ENV = os.environ.get('FLASK_ENV', 'production')
    FLASK_DEBUG = os.environ.get('FLASK_DEBUG', '0') == '1'
