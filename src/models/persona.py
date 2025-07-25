from src.database.db_connection import db
from datetime import datetime

class Persona(db.Model):
	__tablename__ = 'personas'

	id_usuario = db.Column(db.Integer, primary_key=True)
	primer_nombre = db.Column(db.String(50), nullable=False)
	segundo_nombre = db.Column(db.String(50))
	primer_apellido = db.Column(db.String(50), nullable=False)
	segundo_apellido = db.Column(db.String(50))
	id_tipo_documento = db.Column(db.Integer, db.ForeignKey('tipos_documento.id_tipo_documento'), nullable=False)
	documento = db.Column(db.String(10), nullable=False)
	telefono = db.Column(db.String(10), nullable=False)
	correo = db.Column(db.String(100), unique=True, nullable=False)
	direccion = db.Column(db.String(50), nullable=False)
	password_hash = db.Column(db.String(50), nullable=False)
	activo = db.Column(db.Boolean, default=True)
	fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
	id_rol = db.Column(db.Integer, db.ForeignKey('roles.id_rol'), nullable=False)

	pedidos = db.relationship('Pedido', backref='persona', lazy=True) 