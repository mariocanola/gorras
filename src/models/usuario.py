from src.database.db_connection import db
from datetime import datetime

class Usuario(db.Model):
	__tablename__ = 'usuarios'

	id_usuario = db.Column(db.Integer, primary_key=True)
	nombre = db.Column(db.String(100), nullable=False)
	cedula = db.Column(db.String(20), unique=True, nullable=False)
	telefono = db.Column(db.String(20), nullable=False)
	correo = db.Column(db.String(100), unique=True, nullable=False)
	direccion = db.Column(db.String(200), nullable=False)
	password_hash = db.Column(db.String(128), nullable=False)
	rol = db.Column(db.String(20), nullable=False, default='cliente')
	fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
	activo = db.Column(db.Boolean, default=True)

	ventas = db.relationship('Venta', backref='usuario', lazy=True) 