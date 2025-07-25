"""
Módulo para comandos personalizados de la base de datos.
Permite ejecutar operaciones de base de datos desde la línea de comandos.
"""
from flask import current_app
from flask.cli import with_appcontext
import click
import logging
from ..db_connection import db

def init_app(app):
    """Registra los comandos de la base de datos en la aplicación."""
    app.cli.add_command(init_db_command)
    app.cli.add_command(seed_db_command)
    app.cli.add_command(drop_db_command)

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Crear tablas de la base de datos."""
    try:
        db.create_all()
        click.echo('Base de datos inicializada.')
    except Exception as e:
        logging.error(f"Error al inicializar la base de datos: {e}")
        click.echo(f'Error al inicializar la base de datos: {e}')

@click.command('seed-db')
@with_appcontext
def seed_db_command():
    """Insertar datos iniciales en la base de datos."""
    try:
        # Aquí iría el código para insertar datos iniciales
        click.echo('Datos iniciales insertados.')
    except Exception as e:
        logging.error(f"Error al insertar datos iniciales: {e}")
        click.echo(f'Error al insertar datos iniciales: {e}')

@click.command('drop-db')
@with_appcontext
def drop_db_command():
    """Eliminar todas las tablas de la base de datos."""
    if click.confirm('¿Estás seguro de que deseas eliminar todas las tablas de la base de datos?', abort=True):
        try:
            db.drop_all()
            click.echo('Todas las tablas han sido eliminadas.')
        except Exception as e:
            logging.error(f"Error al eliminar las tablas: {e}")
            click.echo(f'Error al eliminar las tablas: {e}')
