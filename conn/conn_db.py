import MySQLdb

db_config = {
    'host': 'localhost',
    'user': 'root',
    'passwd': 'Charlie551!@',
    'db': 'controla',
    'charset': 'utf8mb4'
}

def get_connection():
    """Establece y retorna la conexión a la base de datos."""
    try:
        connection = MySQLdb.connect(**db_config)
        return connection
    except MySQLdb.Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None