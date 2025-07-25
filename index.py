from flask import Flask
from src.database.db_connection import init_db

app = Flask(__name__)
app.config.from_pyfile('config.py')

init_db(app)

if __name__ == '__main__':
	app.run(debug=True)