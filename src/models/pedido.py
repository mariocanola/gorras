from src.database.db_connection import db
from datetime import datetime

class Pedido(db.Model):
	__tablename__ = 'pedidos'

	id_pedido = db.Column(db.Integer, primary_key=True)
	id_usuario = db.Column(db.Integer, db.ForeignKey('personas.id_usuario'), nullable=False)
	fecha_pedido = db.Column(db.DateTime, default=datetime.utcnow)
	estado = db.Column(db.Enum('pendiente', 'enviado', 'entregado', 'cancelado'), default='pendiente')
	total = db.Column(db.Numeric(10,2), nullable=False)

	detalles = db.relationship('DetallePedido', backref='pedido', lazy=True) 