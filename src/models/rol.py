from src.database.db_connection import db

class Rol(db.Model):
	__tablename__ = 'roles'

	id_rol = db.Column(db.Integer, primary_key=True)
	nombre = db.Column(db.String(20), nullable=False)

	personas = db.relationship('Persona', backref='rol', lazy=True) 