"""
Script para probar la conexión a la base de datos y el estado de las tablas.
"""
import sys
import os
from sqlalchemy import inspect
from src.database.db_connection import db, test_db_connection
from index import create_app

def check_tables():
    """Verifica las tablas existentes en la base de datos."""
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    
    print("\n📊 Tablas en la base de datos:")
    if not tables:
        print("❌ No se encontraron tablas en la base de datos")
    else:
        for table in tables:
            print(f"✅ {table}")
            
            # Mostrar columnas de cada tabla
            columns = inspector.get_columns(table)
            for column in columns:
                print(f"   - {column['name']}: {column['type']}")
    
    return len(tables)

def main():
    """Función principal para probar la conexión a la base de datos."""
    # Crear la aplicación para el contexto
    app = create_app()
    
    with app.app_context():
        try:
            print("🔍 Probando conexión a la base de datos...")
            
            # Probar la conexión usando la función de prueba
            test_result = test_db_connection()
            
            if test_result.get('status') == 'success':
                print("\n✅ Conexión exitosa a la base de datos")
                print(f"📊 Base de datos: {app.config['SQLALCHEMY_DATABASE_URI']}")
                print(f"🔌 Versión del servidor: {test_result.get('version', 'desconocida')}")
                
                # Verificar tablas
                num_tables = check_tables()
                
                if num_tables == 0:
                    print("\n⚠️  No se encontraron tablas en la base de datos")
                    print("   Ejecute las migraciones o verifique sus modelos")
                else:
                    print(f"\n✅ Se encontraron {num_tables} tablas en la base de datos")
                
                # Mostrar información de tablas
                if 'tables' in test_result:
                    print("\n📋 Tablas detectadas:")
                    for table in test_result['tables']:
                        print(f"   - {table}")
                
                return 0  # Código de salida exitoso
                
            else:
                print("\n❌ Error al conectar a la base de datos:")
                print(f"   Mensaje: {test_result.get('message', 'Error desconocido')}")
                if 'error_details' in test_result:
                    print(f"   Detalles: {test_result['error_details']}")
                return 1  # Código de error
                
        except Exception as e:
            print(f"\n❌ Error inesperado: {str(e)}")
            import traceback
            traceback.print_exc()
            return 2  # Código de error

if __name__ == '__main__':
    sys.exit(main())
