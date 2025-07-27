"""
Punto de entrada de la aplicación Gorras.

Este archivo se mantiene para compatibilidad con sistemas que esperan un app.py.
Se recomienda usar index.py como punto de entrada principal.
"""
from index import create_app

# Crear la aplicación Flask
app = create_app()

if __name__ == '__main__':
    # Iniciar la aplicación
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=app.config.get('DEBUG', False))