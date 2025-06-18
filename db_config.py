import MySQLdb
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

# Configuración de conexión a MySQL desde variables de entorno
db_config = {
    'host': os.getenv("DB_HOST"),
    'port': int(os.getenv("DB_PORT")),
    'user': os.getenv("DB_USER"),
    'passwd': os.getenv("DB_PASSWORD"),
    'db': os.getenv("DB_NAME")
}

def get_db_connection():
    return MySQLdb.connect(**db_config)
