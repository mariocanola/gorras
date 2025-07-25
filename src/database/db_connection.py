"""
Módulo para la gestión de la conexión a la base de datos.
Utiliza SQLAlchemy como ORM y sigue el patrón de diseño Singleton.
"""
from flask_sqlalchemy import SQLAlchemy
from flask import current_app
import logging

# Crear una instancia de SQLAlchemy
db = SQLAlchemy()


def init_db(app):
    """
    Inicializa la base de datos con la aplicación Flask.
    
    Args:
        app: Instancia de la aplicación Flask
    """
    try:
        # Configurar la conexión a la base de datos
        db.init_app(app)
        
        with app.app_context():
            # Crear todas las tablas definidas en los modelos
            db.create_all()
            logging.info("Base de datos inicializada correctamente")
            
    except Exception as e:
        logging.error(f"Error al inicializar la base de datos: {e}")
        raise


def get_db():
	"""
	Obtiene la sesión actual de la base de datos.
	
	Returns:
		Sesión de la base de datos
	"""
	# No es necesario chequear 'db' en current_app.extensions, ya que db es global y se inicializa con init_app
	return db


def close_db(e=None):
	"""
	Cierra la conexión a la base de datos.
	
	Args:
		e: Excepción que pudo haber causado el cierre (opcional)
	"""
	db.session.remove()
	logging.info("Conexión a la base de datos cerrada")


def init_app(app):
	"""
	Inicializa la extensión de la base de datos con la aplicación.
	
	Args:
		app: Instancia de la aplicación Flask
	"""
	# Registrar funciones para el manejo del ciclo de vida de la aplicación
	app.teardown_appcontext(close_db)
	
	# Inicializar la base de datos
	init_db(app)
	
	# Si tienes comandos personalizados, descomenta la siguiente línea y asegúrate de que el módulo exista
	# from . import commands
	# commands.init_app(app)
