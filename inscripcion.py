import random
import string
from conn.conn_db import get_connection


def generar_codinscripcion():
    """Genera un código de inscripción en el formato XXXXXXXX-X."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8)) + '-' + random.choice(
        string.ascii_uppercase)


# Establece la conexión a la base de datos
connection = get_connection()
if connection:
    cursor = connection.cursor()

    try:
        # Obtener todos los carnets de la tabla custom_alumnos
        cursor.execute("SELECT carnet FROM custom_alumnos")
        carnets = cursor.fetchall()

        for carnet_tuple in carnets:
            carnet = carnet_tuple[0]

            # Obtener 4 materias aleatorias de la tabla academic_cargaacademica
            cursor.execute("SELECT CodMat, Seccion FROM academic_cargaacademica ORDER BY RAND() LIMIT 4")
            materias = cursor.fetchall()

            # Generar un código de inscripción único para el carnet actual
            codinscripcion = generar_codinscripcion()

            for codmat, seccion in materias:
                # Verificar la cantidad de inscripciones para la materia seleccionada
                cursor.execute('''
                    SELECT COUNT(*) FROM academic_cargainscripcion 
                    WHERE CodMat = %s AND Seccion = %s
                ''', (codmat, seccion))
                inscripcion_count = cursor.fetchone()[0]

                # Solo insertar si hay menos de 100 inscripciones para esta materia y sección
                if inscripcion_count < 100:
                    cursor.execute('''
                        INSERT INTO academic_cargainscripcion (Carnet, CodMat, Seccion, CodInscripcion)
                        VALUES (%s, %s, %s, %s)
                    ''', (carnet, codmat, seccion, codinscripcion))
                else:
                    print(
                        f"Materia {codmat} en sección {seccion} ya tiene el máximo de 100 inscripciones. Se omite la inscripción.")

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