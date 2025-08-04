from src.database.db_connection import db
from sqlalchemy.orm import validates
from typing import List, Optional, Dict, Any
from datetime import datetime
import os
import logging
from werkzeug.utils import secure_filename

class VarianteGorra(db.Model):
	__tablename__ = 'variantes_gorra'

	id_gorra = db.Column(db.Integer, primary_key=True)
	nombre = db.Column(db.String(100), nullable=False)
	id_tipo_gorra = db.Column(db.Integer, db.ForeignKey('tipos_gorra.id_tipo_gorra'), nullable=False)
	color = db.Column(db.String(50), nullable=False)
	talla = db.Column(db.String(10), nullable=False)
	precio = db.Column(db.Numeric(10,2), nullable=False)
	stock = db.Column(db.Integer, nullable=False)
	imagen_url = db.Column(db.String(255))

	detalles_pedido = db.relationship('DetallePedido', backref='variante_gorra', lazy=True) 

	# Validaciones
	@validates('precio')
	def validate_precio(self, key, precio):
		if precio <= 0:
			raise ValueError("El precio debe ser mayor que cero")
		return precio

	@validates('stock')
	def validate_stock(self, key, stock):
		if stock < 0:
			raise ValueError("El stock no puede ser negativo")
		return stock

	@validates('nombre')
	def validate_nombre(self, key, nombre):
		if not nombre:
			raise ValueError("El nombre es obligatorio")
		return nombre

	# Métodos CRUD
	@classmethod
	def crear(cls, datos: Dict[str, Any]) -> 'VarianteGorra':
		"""
		Crea una nueva variante de gorra en la base de datos.

		Args:
			datos: Diccionario con los datos de la variante de gorra.

		Returns:
			VarianteGorra: La variante de gorra creada.
		"""
		try:
			# Validar y procesar la imagen si se proporciona
			if 'imagen' in datos and datos['imagen']:
				datos['imagen_url'] = cls._guardar_imagen(datos['imagen'])

			# Filtrar solo las columnas que existen en el modelo
			columnas_validas = {k: v for k, v in datos.items() if hasattr(cls, k) and k != 'id_gorra'}

			variante = cls(**columnas_validas)
			db.session.add(variante)
			db.session.commit()
			logging.info(f"Variante de gorra creada exitosamente: ID {variante.id_gorra}")
			return variante
		except Exception as e:
			db.session.rollback()
			logging.error(f"Error al crear la variante de gorra: {str(e)}")
			raise

	@classmethod
	def obtener_por_id(cls, id_gorra: int) -> Optional['VarianteGorra']:
		"""
		Obtiene una variante de gorra por su ID.

		Args:
			id_gorra: ID de la variante de gorra a buscar

		Returns:
			Optional[VarianteGorra]: La variante de gorra encontrada o None si no existe
		"""
		return cls.query.get(id_gorra)

	@classmethod
	def obtener_todas(cls, activas: bool = True) -> List['VarianteGorra']:
		"""
		Obtiene todas las variantes de gorra, opcionalmente solo las activas.

		Args:
			activas: Si es True, devuelve solo variantes de gorra activas

		Returns:
			List[VarianteGorra]: Lista de variantes de gorra
		"""
		query = cls.query
		if activas:
			query = query.filter_by(activo=True)
		return query.order_by(cls.id_gorra).all()

	def actualizar(self, datos: Dict[str, Any]) -> 'VarianteGorra':
		"""
		Actualiza los datos de la variante de gorra.

		Args:
			datos: Diccionario con los datos a actualizar

		Returns:
			VarianteGorra: La variante de gorra actualizada
		"""
		try:
			# Actualizar campos
			for campo, valor in datos.items():
				if hasattr(self, campo) and campo != 'id_gorra':
					setattr(self, campo, valor)

			# Actualizar fecha de actualización
			self.fecha_actualizacion = datetime.utcnow()

			db.session.commit()
			logging.info(f"Variante de gorra actualizada: {self.id_gorra}")
			return self
		except Exception as e:
			db.session.rollback()
			logging.error(f"Error al actualizar variante de gorra {self.id_gorra}: {str(e)}")
			raise

	def eliminar(self):
		"""
		Elimina la variante de gorra de la base de datos.
		"""
		try:
			# Eliminar la imagen asociada si existe
			if self.imagen_url:
				self._eliminar_imagen()

			db.session.delete(self)
			db.session.commit()
			logging.info(f"Variante de gorra eliminada: {self.id_gorra}")
		except Exception as e:
			db.session.rollback()
			logging.error(f"Error al eliminar variante de gorra {self.id_gorra}: {str(e)}")
			raise

	def desactivar(self):
		"""
		Desactiva la variante de gorra (borrado lógico).
		"""
		self.activo = False
		self.fecha_actualizacion = datetime.utcnow()
		db.session.commit()
		logging.info(f"Variante de gorra desactivada: {self.id_gorra}")

	# Métodos de utilidad para manejo de imágenes
	@staticmethod
	def _guardar_imagen(imagen) -> str:
		"""
		Guarda la imagen en el sistema de archivos y devuelve la ruta relativa.

		Args:
			imagen: Objeto FileStorage de Flask

		Returns:
			str: Ruta relativa de la imagen guardada
		"""
		from flask import current_app

		# Crear nombre de archivo seguro
		filename = secure_filename(imagen.filename)
		# Añadir timestamp para evitar colisiones
		unique_filename = f"{datetime.now().timestamp()}_{filename}"

		# Crear directorio de subidas si no existe
		upload_folder = os.path.join(current_app.root_path, '..', 'static', 'uploads')
		os.makedirs(upload_folder, exist_ok=True)

		# Guardar la imagen
		filepath = os.path.join(upload_folder, unique_filename)
		imagen.save(filepath)

		# Devolver ruta relativa para almacenar en la base de datos
		return os.path.join('static', 'uploads', unique_filename)

	def _eliminar_imagen(self):
		"""Elimina la imagen asociada a la variante de gorra del sistema de archivos."""
		if self.imagen_url:
			try:
				filepath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), self.imagen_url)
				if os.path.exists(filepath):
					os.remove(filepath)
					logging.info(f"Imagen eliminada: {filepath}")
			except Exception as e:
				logging.error(f"Error al eliminar imagen {self.imagen_url}: {str(e)}")

	# Representación del objeto
	def __repr__(self):
		return f"<VarianteGorra {self.id_gorra} (ID: {self.id_gorra}, nombre: {self.nombre})>"

	# Método para serializar el objeto a diccionario (útil para APIs)
	def to_dict(self):
		"""
		Convierte el objeto VarianteGorra a un diccionario.

		Returns:
			dict: Diccionario con los datos de la variante de gorra
		"""
		return {
			'id_gorra': self.id_gorra,
			'nombre': self.nombre,
			'id_tipo_gorra': self.id_tipo_gorra,
			'color': self.color,
			'talla': self.talla,
			'precio': float(self.precio),
			'stock': self.stock,
			'imagen_url': self.imagen_url,
			'activo': self.activo
		}