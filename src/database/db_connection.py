"""
Módulo para la gestión de la conexión a la base de datos.
Utiliza SQLAlchemy como ORM y sigue el patrón de diseño Singleton.
"""
import os
import logging
from flask_sqlalchemy import SQLAlchemy
from flask import current_app, jsonify
from sqlalchemy.exc import SQLAlchemyError
import socket
import subprocess

# Crear una instancia de SQLAlchemy
db = SQLAlchemy()

def test_db_connection():
    """
    Prueba la conexión a la base de datos y devuelve un diccionario con el estado.
    """
    if not current_app:
        return {'status': 'error', 'message': 'Aplicación no inicializada'}

    result = {
        'status': 'success', 
        'message': 'Conexión exitosa a la base de datos',
        'service_status': 'unknown',
        'port_status': 'unknown',
        'database_status': 'unknown',
        'permissions': 'unknown',
        'database': current_app.config.get('DB_NAME', 'gorras_db'),
        'version': 'unknown',
        'tables': []
    }
    
    try:
        # 1. Verificar si el servicio de MariaDB está corriendo
        try:
            # Para sistemas Linux/Unix
            if os.name != 'nt':  # No Windows
                service_check = subprocess.run(
                    ['systemctl', 'is-active', '--quiet', 'mariadb'],
                    capture_output=True,
                    text=True
                )
                if service_check.returncode != 0:
                    result.update({
                        'status': 'error',
                        'message': 'El servicio de MariaDB no está corriendo',
                        'service_status': 'inactive'
                    })
                    return result
                result['service_status'] = 'active'
        except Exception as e:
            result.update({
                'status': 'warning',
                'message': f'No se pudo verificar el estado del servicio MariaDB: {str(e)}',
                'service_status': 'unknown'
            })

        # 2. Verificar si el puerto 3306 está accesible
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            port_check = sock.connect_ex(('127.0.0.1', 3306))
            sock.close()
            
            if port_check != 0:
                return {
                    'status': 'error',
                    'message': 'No se puede conectar al puerto 3306 (MySQL/MariaDB no está escuchando)',
                    'port_status': 'closed',
                    'service_status': result.get('service_status', 'unknown')
                }
            result['port_status'] = 'open'
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error al verificar el puerto 3306: {str(e)}',
                'port_status': 'error',
                'service_status': result.get('service_status', 'unknown')
            }

        # 3. Verificar la conexión a la base de datos
        try:
            from sqlalchemy import text
            db_url = current_app.config.get('SQLALCHEMY_DATABASE_URI')
            if not db_url:
                return {
                    'status': 'error',
                    'message': 'Configuración de base de datos no encontrada',
                    'config_status': 'missing',
                    'service_status': result.get('service_status', 'unknown'),
                    'port_status': result.get('port_status', 'unknown')
                }

            # Probar la conexión
            with db.engine.connect() as connection:
                # Verificar que la base de datos existe
                db_name = current_app.config.get('DB_NAME', 'gorras_db')
                db_exists = connection.execute(text(f"SHOW DATABASES LIKE '{db_name}'")).first()
                if not db_exists:
                    return {
                        'status': 'error',
                        'message': f"La base de datos '{db_name}' no existe",
                        'database_status': 'not_found',
                        'service_status': result.get('service_status', 'unknown'),
                        'port_status': result.get('port_status', 'unknown')
                    }
                
                # Obtener información de la versión de la base de datos
                version_result = connection.execute(text("SELECT VERSION()")).first()
                if version_result:
                    result['version'] = version_result[0]
                
                # Obtener lista de tablas
                try:
                    tables_result = connection.execute(text(f"SHOW TABLES FROM `{db_name}`")).fetchall()
                    if tables_result and len(tables_result) > 0:
                        # Manejar diferentes formatos de resultado
                        if hasattr(tables_result[0], '_asdict'):
                            result['tables'] = [list(row._asdict().values())[0] for row in tables_result if row]
                        elif isinstance(tables_result[0], (list, tuple)):
                            result['tables'] = [row[0] for row in tables_result if row]
                        else:
                            result['tables'] = [row for row in tables_result if row]
                except Exception as e:
                    logging.warning(f"No se pudieron listar las tablas: {str(e)}")
                    result['tables'] = []
                
                # Actualizar estado final
                result.update({
                    'status': 'success',
                    'message': 'Conexión exitosa a la base de datos',
                    'database_status': 'ok',
                    'permissions': 'read_write',
                    'database': db_name
                })
                
                return result
                
        except SQLAlchemyError as e:
            error_type = type(e).__name__
            error_message = str(e)
            
            if "Can't connect to MySQL server" in error_message:
                error_detail = 'El servidor MySQL/MariaDB no está aceptando conexiones'
            elif "Access denied" in error_message:
                error_detail = 'Credenciales incorrectas o permisos insuficientes'
            elif "Unknown database" in error_message:
                error_detail = 'La base de datos especificada no existe'
            else:
                error_detail = 'Error desconocido al conectar a la base de datos'
            
            result.update({
                'status': 'error',
                'message': f'Error de conexión: {error_detail}',
                'error_type': error_type,
                'error_details': error_message,
                'database': current_app.config.get('DB_NAME', 'No configurada'),
                'database_status': 'connection_failed'
            })
            
    except Exception as e:
        result = {
            'status': 'error',
            'message': f'Error inesperado: {str(e)}',
            'error_type': type(e).__name__
        }
    
    return result

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
            # Importar todos los modelos para que SQLAlchemy los registre
            from ..models.tipo_documento import TipoDocumento
            from ..models.tipo_gorra import TipoGorra
            from ..models.variante_gorra import VarianteGorra
            from ..models.rol import Rol
            from ..models.persona import Persona
            from ..models.pedido import Pedido
            from ..models.detalle_pedido import DetallePedido
            
            # Crear todas las tablas definidas en los modelos
            db.create_all()
            logging.info("Base de datos inicializada correctamente")
            
            # Ejecutar prueba de conexión
            test_result = test_db_connection()
            if test_result.get('status') == 'error':
                logging.error(f"Advertencia en la inicialización de la base de datos: {test_result}")
            
    except Exception as e:
        logging.error(f"Error al inicializar la base de datos: {e}")
        raise

def get_db():
    """
    Obtiene la sesión actual de la base de datos.
    
    Returns:
        Sesión de la base de datos
    """
    return db

def close_db(e=None):
    """
    Cierra la conexión a la base de datos.
    
    Args:
        e: Excepción que pudo haber causado el cierre (opcional)
    """
    if db.session:
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
