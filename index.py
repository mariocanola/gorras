"""
Punto de entrada principal de la aplicación Gorras.
"""
import os
from flask import Flask, jsonify
from src.database.db_connection import init_db, db, test_db_connection
from config import config

def create_app(config_name=None):
    """
    Factory function que crea y configura la aplicación Flask.
    
    Args:
        config_name (str): Nombre de la configuración a usar ('development', 'production', etc.)
    
    Returns:
        Flask: La aplicación Flask configurada
    """
    # Crear la aplicación Flask
    app = Flask(__name__)
    
    # Cargar configuración
    if config_name is None:
        config_name = os.getenv('FLASK_ENV') or 'development'
    app.config.from_object(config[config_name])
    
    # Inicializar la base de datos
    init_db(app)
    
    # Registrar blueprints (rutas)
    register_blueprints(app)
    
    # Ruta de prueba
    @app.route('/')
    def index():
        return jsonify({
            'status': 'success',
            'message': 'API de Gorras en funcionamiento',
            'version': '1.0.0'
        })
    
    # Ruta de prueba de base de datos
    @app.route('/test-db', methods=['GET'])
    def test_db_route():
        """Ruta para probar la conexión a la base de datos."""
        test_result = test_db_connection()
        return jsonify(test_result)
    
    return app

def register_blueprints(app):
    """
    Registra los blueprints de la aplicación.
    
    Args:
        app: Instancia de la aplicación Flask
    """
    # Importar blueprints aquí para evitar importaciones circulares
    # from src.routes.gorras import gorras_bp
    # app.register_blueprint(gorras_bp, url_prefix='/api/gorras')
    pass

if __name__ == '__main__':
    # Crear y ejecutar la aplicación
    app = create_app()
    
    # Configuración del puerto
    port = int(os.getenv('PORT', 5000))
    
    # Iniciar la aplicación
    app.run(host='0.0.0.0', port=port, debug=app.config.get('DEBUG', False))