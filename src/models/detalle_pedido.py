from src.database.db_connection import db

class DetallePedido(db.Model):
	__tablename__ = 'detalle_pedido'

	id_detalle = db.Column(db.Integer, primary_key=True)
	id_pedido = db.Column(db.Integer, db.ForeignKey('pedidos.id_pedido'), nullable=False)
	id_gorra = db.Column(db.Integer, db.ForeignKey('variantes_gorra.id_gorra'), nullable=False)
	cantidad = db.Column(db.Integer, nullable=False)
	precio_unitario = db.Column(db.Numeric(10,2), nullable=False) 