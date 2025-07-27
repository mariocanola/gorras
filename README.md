Para correr el proyecto:

1. Primera mente se crea el entorno virtual con el comando: python -m venv venv 
2. Activar el entorno virtual con el comando: venv\Scripts\activate
3. Instalar las dependencias con el comando: pip install -r requirements.txt 
4. Se configura el archivo .env con la informacion de la base de datos: DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT.
5. Se debe tener un usuario en la base de datos.    
6. Correr la aplicacion con el comando: python index.py.

Este comando inicia el servidor de flask y se puede acceder a la aplicacion en el navegador en la direccion: http://127.0.0.1:5000. al iniciar el servidor se puede verificar que la base de datos se ha creado correctamente y se evidencian todas las tablas creadas.