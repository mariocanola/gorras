"""
Módulo para la gestión de la conexión a la base de datos.
Utiliza SQLAlchemy como ORM y sigue el patrón de diseño Singleton.
"""
import logging
from flask_sqlalchemy import SQLAlchemy
from flask import current_app

class Database:
    """
    Clase para la gestión de la conexión a la base de datos.
    
    Utiliza SQLAlchemy como ORM y sigue el patrón de diseño Singleton.
    """
    
    def __init__(self, app):
        self.app = app
        self.db = SQLAlchemy(app)
    
    def init_app(self):
        """
        Inicializa la base de datos con la aplicación Flask.
        """
        self.db.init_app(self.app)
        
        with self.app.app_context():
            # Importar todos los modelos para que SQLAlchemy los registre
            from ..models.tipo_documento import TipoDocumento
            from ..models.tipo_gorra import TipoGorra
            from ..models.variante_gorra import VarianteGorra
            from ..models.rol import Rol
            from ..models.persona import Persona
            from ..models.pedido import Pedido
            from ..models.detalle_pedido import DetallePedido
            
            # Crear todas las tablas definidas en los modelos
            self.db.create_all()
            logging.info("Base de datos inicializada correctamente")
        
    def get_db(self):
        """
        Obtiene la sesión actual de la base de datos.
        
        Returns:
            Sesión de la base de datos
        """
        return self.db
    
    def close_db(self, e=None):
        """
        Cierra la conexión a la base de datos.
        
        Args:
            e: Excepción que pudo haber causado el cierre (opcional)
        """
        if self.db.session:
            self.db.session.remove()
        logging.info("Conexión a la base de datos cerrada")


def init_app(app):
    """
    Inicializa la extensión de la base de datos con la aplicación.
    
    Args:
        app: Instancia de la aplicación Flask
    """
    # Crear una instancia de la base de datos
    db = Database(app)
    
    # Registrar funciones para el manejo del ciclo de vida de la aplicación
    app.teardown_appcontext(db.close_db)
    
    # Inicializar la base de datos
    db.init_app()
