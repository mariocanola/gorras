from app import app, db

with app.app_context():
    try:
        # Intentar conectar a la base de datos
        connection = db.engine.connect()
        print("✅ Conexión exitosa a la base de datos")
        print(f"📊 Base de datos: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        # Verificar si la tabla de productos existe
        if db.engine.dialect.has_table(db.engine, 'producto'):
            print("✅ Tabla 'producto' encontrada")
        else:
            print("⚠️  La tabla 'producto' no existe")
            
        connection.close()
    except Exception as e:
        print(f"❌ Error de conexión: {str(e)}")
