import random
import string
from conn.conn_db import get_connection


def generar_codinscripcion():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8)) + '-' + random.choice(
        string.ascii_uppercase)

connection = get_connection()
if connection:
    cursor = connection.cursor()

    try:
        cursor.execute("SELECT carnet FROM custom_alumnos")
        carnets = cursor.fetchall()

        for carnet_tuple in carnets:
            carnet = carnet_tuple[0]

            cursor.execute("""
                SELECT CodMat, Seccion, Cupo 
                FROM academic_cargaacademica 
                WHERE Aula != 'AULA VIRTUAL' 
                ORDER BY RAND() 
                LIMIT 4
            """)
            materias = cursor.fetchall()

            codinscripcion = generar_codinscripcion()

            for codmat, seccion, cupo in materias:
                cursor.execute('''
                    SELECT COUNT(*) 
                    FROM academic_cargainscripcion 
                    WHERE CodMat = %s AND Seccion = %s
                ''', (codmat, seccion))
                inscripcion_count = cursor.fetchone()[0]

                if inscripcion_count < cupo:
                    cursor.execute('''
                        INSERT INTO academic_cargainscripcion (Carnet, CodMat, Seccion, CodInscripcion)
                        VALUES (%s, %s, %s, %s)
                    ''', (carnet, codmat, seccion, codinscripcion))
                else:
                    print(
                        f"Materia {codmat} en sección {seccion} ya ha alcanzado el límite de cupos ({cupo}). Se omite la inscripción.")

        # Confirmar las inserciones
        connection.commit()
        print("Registros de inscripción generados exitosamente.")

    except Exception as e:
        print(f"Error al procesar los registros de inscripción: {e}")
        connection.rollback()

    finally:
        cursor.close()
        connection.close()
else:
    print("No se pudo establecer la conexión a la base de datos.")