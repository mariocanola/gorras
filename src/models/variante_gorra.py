from src.database.db_connection import db

class VarianteGorra(db.Model):
	__tablename__ = 'variantes_gorra'

	id_gorra = db.Column(db.Integer, primary_key=True)
	id_tipo_gorra = db.Column(db.Integer, db.ForeignKey('tipos_gorra.id_tipo_gorra'), nullable=False)
	color = db.Column(db.String(50), nullable=False)
	talla = db.Column(db.String(10), nullable=False)
	precio = db.Column(db.Numeric(10,2), nullable=False)
	stock = db.Column(db.Integer, nullable=False)
	activo = db.Column(db.Boolean, default=True)

	detalles_pedido = db.relationship('DetallePedido', backref='variante_gorra', lazy=True) 