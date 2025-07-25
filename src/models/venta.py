from src.database.db_connection import db
from datetime import datetime

class Venta(db.Model):
	__tablename__ = 'ventas'

	id_venta = db.Column(db.Integer, primary_key=True)
	id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
	fecha_venta = db.Column(db.DateTime, default=datetime.utcnow)
	total = db.Column(db.Float, nullable=False)
	metodo_pago = db.Column(db.String(50), nullable=False)
	comprobante_url = db.Column(db.String(255))
	estado = db.Column(db.String(20), default='pagada')

	detalles = db.relationship('DetalleVenta', backref='venta', lazy=True) 