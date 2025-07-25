"""
Módulo que define el modelo Gorra y sus operaciones CRUD.
"""
from typing import List, Optional, Dict, Any
from sqlalchemy import Column, Integer, String, Float, Text, Boolean
from sqlalchemy.orm import validates
import logging
import os
from werkzeug.utils import secure_filename
from datetime import datetime

from src.database.db_connection import db

# Configuración de logging
logger = logging.getLogger(__name__)

class Gorra(db.Model):
	__tablename__ = 'gorras'

	id_gorra = db.Column(db.Integer, primary_key=True)
	nombre = db.Column(db.String(100), nullable=False)
	descripcion = db.Column(db.Text, nullable=False)
	color = db.Column(db.String(50), nullable=False)
	precio = db.Column(db.Float, nullable=False)
	stock = db.Column(db.Integer, nullable=False)
	imagen_url = db.Column(db.String(255))
	activo = db.Column(db.Boolean, default=True)

	detalles_venta = db.relationship('DetalleVenta', backref='gorra', lazy=True)

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

	# Métodos CRUD
	@classmethod
	def crear(cls, datos: Dict[str, Any]) -> 'Gorra':
		"""
		Crea una nueva gorra en la base de datos.

		Args:
			datos: Diccionario con los datos de la gorra

		Returns:
			Gorra: La gorra creada
		"""
		try:
			# Validar y procesar la imagen si se proporciona
			if 'imagen' in datos and datos['imagen']:
				datos['imagen_url'] = cls._guardar_imagen(datos['imagen'])
				del datos['imagen']

			gorra = cls(**datos)
			db.session.add(gorra)
			db.session.commit()
			logger.info(f"Gorra creada exitosamente: {gorra.nombre}")
			return gorra
		except Exception as e:
			db.session.rollback()
			logger.error(f"Error al crear gorra: {str(e)}")
			raise

	@classmethod
	def obtener_por_id(cls, id_gorra: int) -> Optional['Gorra']:
		"""
		Obtiene una gorra por su ID.

		Args:
			id_gorra: ID de la gorra a buscar

		Returns:
			Optional[Gorra]: La gorra encontrada o None si no existe
		"""
		return cls.query.get(id_gorra)

	@classmethod
	def obtener_todas(cls, activas: bool = True) -> List['Gorra']:
		"""
		Obtiene todas las gorras, opcionalmente solo las activas.

		Args:
			activas: Si es True, devuelve solo gorras activas

		Returns:
			List[Gorra]: Lista de gorras
		"""
		query = cls.query
		if activas:
			query = query.filter_by(activo=True)
		return query.order_by(cls.nombre).all()

	def actualizar(self, datos: Dict[str, Any]) -> 'Gorra':
		"""
		Actualiza los datos de la gorra.

		Args:
			datos: Diccionario con los datos a actualizar

		Returns:
			Gorra: La gorra actualizada
		"""
		try:
			# Actualizar campos
			for campo, valor in datos.items():
				if hasattr(self, campo) and campo != 'id_gorra':
					setattr(self, campo, valor)

			# Actualizar fecha de actualización
			self.fecha_actualizacion = datetime.utcnow()

			db.session.commit()
			logger.info(f"Gorra actualizada: {self.id_gorra}")
			return self
		except Exception as e:
			db.session.rollback()
			logger.error(f"Error al actualizar gorra {self.id_gorra}: {str(e)}")
			raise

	def eliminar(self):
		"""
		Elimina la gorra de la base de datos.
		"""
		try:
			# Eliminar la imagen asociada si existe
			if self.imagen_url:
				self._eliminar_imagen()

			db.session.delete(self)
			db.session.commit()
			logger.info(f"Gorra eliminada: {self.id_gorra}")
		except Exception as e:
			db.session.rollback()
			logger.error(f"Error al eliminar gorra {self.id_gorra}: {str(e)}")
			raise

	def desactivar(self):
		"""
		Desactiva la gorra (borrado lógico).
		"""
		self.activo = False
		self.fecha_actualizacion = datetime.utcnow()
		db.session.commit()
		logger.info(f"Gorra desactivada: {self.id_gorra}")

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
		"""Elimina la imagen asociada a la gorra del sistema de archivos."""
		if self.imagen_url:
			try:
				filepath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), self.imagen_url)
				if os.path.exists(filepath):
					os.remove(filepath)
					logger.info(f"Imagen eliminada: {filepath}")
			except Exception as e:
				logger.error(f"Error al eliminar imagen {self.imagen_url}: {str(e)}")

	# Representación del objeto
	def __repr__(self):
		return f"<Gorra {self.nombre} (ID: {self.id_gorra})>"

	# Método para serializar el objeto a diccionario (útil para APIs)
	def to_dict(self):
		"""
		Convierte el objeto Gorra a un diccionario.

		Returns:
			dict: Diccionario con los datos de la gorra
		"""
		return {
			'id_gorra': self.id_gorra,
			'nombre': self.nombre,
			'descripcion': self.descripcion,
			'precio': float(self.precio),
			'color': self.color,
			'stock': self.stock,
			'imagen_url': self.imagen_url,
			'fecha_creacion': self.fecha_creacion.isoformat(),
			'fecha_actualizacion': self.fecha_actualizacion.isoformat(),
			'activo': self.activo
		}
