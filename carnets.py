from faker import Faker
import MySQLdb
import random
import re
from conn.conn_db import get_connection

connection = get_connection()
if connection:
    cursor = connection.cursor()

    fake = Faker()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS custom_alumnos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            carnet VARCHAR(12) UNIQUE,
            nombres VARCHAR(50),
            apellidos VARCHAR(50),
            email VARCHAR(50)
        )
    ''')
    connection.commit()


    def generar_carnet_unico():
        while True:
            carnet = f"25-{random.randint(1000, 9999)}-2018"
            cursor.execute("SELECT COUNT(*) FROM custom_alumnos WHERE carnet = %s", (carnet,))
            (exists,) = cursor.fetchone()
            if not exists:
                return carnet


    for _ in range(1000):
        carnet = generar_carnet_unico()
        nombres = fake.first_name()
        apellidos = fake.last_name()

        email = f"{re.sub(r'[-]', '', carnet)}@mail.utec.edu.sv"

        cursor.execute('''
            INSERT INTO custom_alumnos (carnet, nombres, apellidos, email)
            VALUES (%s, %s, %s, %s)
        ''', (carnet, nombres, apellidos, email))

    connection.commit()

    cursor.close()
    connection.close()
    print("Datos de prueba generados exitosamente.")