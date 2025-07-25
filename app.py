import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from config import config

# Crear la aplicación Flask
app = Flask(__name__)

# Cargar configuración según el entorno
app.config.from_object(config[os.getenv('FLASK_ENV') or 'default'])

# Inicializar la base de datos
db = SQLAlchemy()
db.init_app(app)

# Configuración adicional
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Modelo de ejemplo
class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)
    descripcion = db.Column(db.String(200))
    precio = db.Column(db.Float, nullable=False)
    
    def __repr__(self):
        return f'<Producto {self.nombre}>'

# Crear tablas en la base de datos
with app.app_context():
    db.create_all()

# Ruta de prueba
import socket
import subprocess
import time

@app.route('/test-db', methods=['GET'])
def test_db():
    """Ruta para probar la conexión a la base de datos."""
    # 1. Verificar si el servicio de MariaDB está corriendo
    try:
        # Para sistemas Linux/Unix
        result = subprocess.run(
            ['systemctl', 'is-active', '--quiet', 'mariadb'],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            return jsonify({
                'status': 'error',
                'message': 'El servicio de MariaDB no está corriendo',
                'service_status': 'inactive'
            }), 500
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'No se pudo verificar el estado del servicio MariaDB: {str(e)}',
            'service_status': 'unknown'
        }), 500

    # 2. Verificar si el puerto 3306 está accesible
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)  # Timeout de 3 segundos
        result = sock.connect_ex(('127.0.0.1', 3306))
        sock.close()
        
        if result != 0:
            return jsonify({
                'status': 'error',
                'message': 'No se puede conectar al puerto 3306 (MySQL/MariaDB no está escuchando)',
                'port_status': 'closed'
            }), 500
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error al verificar el puerto 3306: {str(e)}',
            'port_status': 'error'
        }), 500

    # 3. Intentar autenticación con las credenciales
    try:
        from sqlalchemy import create_engine, text
        import time
        
        db_url = app.config.get('SQLALCHEMY_DATABASE_URI')
        if not db_url:
            return jsonify({
                'status': 'error',
                'message': 'Configuración de base de datos no encontrada',
                'config_status': 'missing'
            }), 500
            
        # Crear el motor con un timeout corto
        engine = create_engine(
            db_url,
            connect_args={"connect_timeout": 3}
        )
        
        # Probar la conexión
        start_time = time.time()
        with engine.connect() as connection:
            # Verificar que la base de datos existe
            result = connection.execute(text("SHOW DATABASES LIKE 'gorras_db'"))
            if not result.first():
                return jsonify({
                    'status': 'error',
                    'message': "La base de datos 'gorras_db' no existe",
                    'database_status': 'not_found'
                }), 500
                
            # Verificar permisos de escritura
            test_table = "test_" + str(int(time.time()))
            try:
                connection.execute(text(f"CREATE TABLE {test_table} (id INT);"))
                connection.execute(text(f"INSERT INTO {test_table} (id) VALUES (1);"))
                connection.execute(text(f"DROP TABLE {test_table};"))
            except Exception as e:
                return jsonify({
                    'status': 'error',
                    'message': f'Error de permisos: {str(e)}',
                    'database_status': 'permission_denied'
                }), 500
            
            # Si llegamos aquí, todo está bien
            connection_time = (time.time() - start_time) * 1000  # en milisegundos
            return jsonify({
                'status': 'success',
                'message': 'Conexión exitosa a la base de datos',
                'database': app.config.get('DB_NAME'),
                'connection_time_ms': round(connection_time, 2),
                'service_status': 'active',
                'port_status': 'open',
                'database_status': 'ok',
                'permissions': 'read_write'
            })
            
    except Exception as e:
        error_type = type(e).__name__
        error_message = str(e)
        
        # Detectar errores comunes
        if "Can't connect to MySQL server" in error_message:
            error_detail = 'El servidor MySQL/MariaDB no está aceptando conexiones'
        elif "Access denied" in error_message:
            error_detail = 'Credenciales incorrectas o permisos insuficientes'
        elif "Unknown database" in error_message:
            error_detail = 'La base de datos especificada no existe'
        else:
            error_detail = 'Error desconocido al conectar a la base de datos'
        
        return jsonify({
            'status': 'error',
            'message': f'Error de conexión: {error_detail}',
            'error_type': error_type,
            'error_details': error_message,
            'database': app.config.get('DB_NAME', 'No configurada'),
            'service_status': 'unknown',
            'port_status': 'unknown',
            'database_status': 'connection_failed'
        }), 500

if __name__ == '__main__':
    # Iniciar la aplicación
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=app.config.get('DEBUG', False))