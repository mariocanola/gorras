import os
import sys
import secrets
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

class Config:
    """Configuración base compatible con Linux y Windows"""
    
    # Directorio base
    BASE_DIR = Path(__file__).parent.parent
    
    # Configuración de la aplicación
    SECRET_KEY = os.getenv('SECRET_KEY', secrets.token_hex(32))
    DEBUG = os.getenv('FLASK_ENV', 'development').lower() in ('1', 'true', 'development')
    
    # Configuración de la base de datos
    DB_DRIVER = os.getenv('DB_DRIVER', 'mysql+mysqlconnector')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', '3306'))
    DB_NAME = os.getenv('DB_NAME', 'gorras_db')
    DB_USER = os.getenv('DB_USER', 'cristian')  # Usuario por defecto según tu .env
    DB_PASSWORD = os.getenv('DB_PASSWORD', '12345')  # Contraseña por defecto según tu .env
    
    # Configuración de rutas
    UPLOAD_FOLDER = str(BASE_DIR / 'static' / 'uploads')
    
    # Configuración de la conexión a la base de datos
    if os.name == 'nt':  # Windows
        SQLALCHEMY_DATABASE_URI = f"{DB_DRIVER}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    else:  # Linux/Unix
        # Intentar con socket si existe, de lo contrario usar TCP/IP
        DB_SOCKET = '/var/run/mysqld/mysqld.sock'  # Ruta típica en Linux
        if os.path.exists(DB_SOCKET):
            SQLALCHEMY_DATABASE_URI = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@/{DB_NAME}?unix_socket={DB_SOCKET}"
        else:
            SQLALCHEMY_DATABASE_URI = f"{DB_DRIVER}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    # Configuración de SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 280,
        'pool_pre_ping': True
    }
    SQLALCHEMY_ECHO = DEBUG

# Configuración para desarrollo
class DevelopmentConfig(Config):
    DEBUG = True
    DB_NAME = os.getenv('DB_NAME', 'gorras_dev')

# Configuración para producción
class ProductionConfig(Config):
    DEBUG = False
    DB_NAME = os.getenv('DB_NAME', 'gorras_prod')

# Seleccionar configuración según el entorno
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}