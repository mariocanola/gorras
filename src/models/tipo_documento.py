from src.database.db_connection import db

class TipoDocumento(db.Model):
	__tablename__ = 'tipos_documento'

	id_tipo_documento = db.Column(db.Integer, primary_key=True)
	nombre = db.Column(db.String(50), nullable=False)

	personas = db.relationship('Persona', backref='tipo_documento', lazy=True) 