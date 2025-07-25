from src.database.db_connection import db

class TipoGorra(db.Model):
	__tablename__ = 'tipos_gorra'

	id_tipo_gorra = db.Column(db.Integer, primary_key=True)
	nombre = db.Column(db.String(100), nullable=False)
	descripcion = db.Column(db.Text)

	variantes = db.relationship('VarianteGorra', backref='tipo_gorra', lazy=True) 