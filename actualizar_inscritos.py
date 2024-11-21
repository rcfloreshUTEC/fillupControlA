import MySQLdb
from conn.conn_db import get_connection

def actualizar_inscritos():
    """Actualiza la columna Inscritos en la tabla academic_cargaacademica
    basada en los registros de academic_cargainscripcion."""
    connection = get_connection()
    if not connection:
        print("No se pudo establecer la conexión a la base de datos.")
        return

    try:
        with connection.cursor() as cursor:
            # Obtener todos los registros de academic_cargaacademica
            cursor.execute("""
                SELECT CodMat, Seccion, Ciclo 
                FROM academic_cargaacademica
            """)
            carga_academica = cursor.fetchall()

            for codmat, seccion, ciclo in carga_academica:
                # Contar el número de estudiantes inscritos con los mismos CodMat, Seccion y Ciclo
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM academic_cargainscripcion 
                    WHERE CodMat = %s AND Seccion = %s AND Ciclo = %s
                """, (codmat, seccion, ciclo))
                inscritos = cursor.fetchone()[0]

                # Actualizar la columna Inscritos en academic_cargaacademica
                cursor.execute("""
                    UPDATE academic_cargaacademica 
                    SET Inscritos = %s 
                    WHERE CodMat = %s AND Seccion = %s AND Ciclo = %s
                """, (inscritos, codmat, seccion, ciclo))

            # Confirmar los cambios
            connection.commit()
            print("Columna Inscritos actualizada correctamente.")
    except MySQLdb.Error as e:
        print(f"Error al actualizar la columna Inscritos: {e}")
        connection.rollback()
    finally:
        connection.close()

if __name__ == "__main__":
    actualizar_inscritos()