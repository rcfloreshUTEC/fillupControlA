import random
import string
from conn.conn_db import get_connection

def generar_codinscripcion():
    """Genera un código de inscripción en el formato XXXXXXXX-X."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8)) + '-' + random.choice(string.ascii_uppercase)

# Establecer conexión
connection = get_connection()
if connection:
    cursor = connection.cursor()
    try:
        # Seleccionar todos los carnets de custom_alumnos
        cursor.execute("SELECT carnet FROM custom_alumnos")
        carnets = [c[0] for c in cursor.fetchall()]
        random.shuffle(carnets)  # Mezclar los carnets aleatoriamente
        print(f"Se encontraron {len(carnets)} carnets para procesar.")

        registros_insertados = 0  # Contador de registros para commits periódicos

        for carnet in carnets:
            # Obtener el año del carnet (últimos cuatro dígitos)
            anio_carnet = int(carnet[-4:])

            # Generar un código de inscripción único para el carnet
            codinscripcion = generar_codinscripcion()
            print(f"\nAsignando materias para carnet: {carnet} (Año: {anio_carnet}) con CodInscripcion: {codinscripcion}")

            # Seleccionar aleatoriamente 4 materias de academic_cargaacademica que cumplan con el cupo
            cursor.execute("""
                SELECT CodMat, Seccion, Ciclo, Cupo
                FROM academic_cargaacademica
                WHERE Aula != 'AULA VIRTUAL'
                ORDER BY RAND()
                LIMIT 4
            """)
            materias = cursor.fetchall()

            # Inscribir el carnet en las 4 materias seleccionadas aleatoriamente
            for codmat, seccion, ciclo, cupo in materias:
                # Extraer el año del ciclo de la materia
                anio_ciclo = int(ciclo.split('-')[1])

                # Verificar que el año del ciclo es válido para el año del carnet
                if anio_carnet <= anio_ciclo:
                    # Verificar el cupo de la materia y sección
                    cursor.execute('''
                        SELECT COUNT(*) 
                        FROM academic_cargainscripcion 
                        WHERE CodMat = %s AND Seccion = %s AND Ciclo = %s
                    ''', (codmat, seccion, ciclo))
                    inscripcion_count = cursor.fetchone()[0]

                    # Solo inscribir si el cupo no ha sido alcanzado
                    if inscripcion_count < cupo:
                        cursor.execute('''
                            INSERT INTO academic_cargainscripcion (Carnet, CodMat, Seccion, Ciclo, CodInscripcion)
                            VALUES (%s, %s, %s, %s, %s)
                        ''', (carnet, codmat, seccion, ciclo, codinscripcion))
                        registros_insertados += 1
                        print(f"Inscripción registrada para carnet: {carnet}, CodMat: {codmat}, Seccion: {seccion}, Ciclo: {ciclo}")

                        # Realizar commit cada 1000 registros
                        if registros_insertados % 1000 == 0:
                            connection.commit()
                            print(f"{registros_insertados} registros insertados y confirmados en la base de datos.")
                    else:
                        print(f"Materia {codmat} en sección {seccion} y ciclo {ciclo} ya ha alcanzado el límite de cupos ({cupo}). No se inscribió para el carnet {carnet}.")
                else:
                    print(f"Materia {codmat} en ciclo {ciclo} no es elegible para carnet {carnet} (Año: {anio_carnet}).")

        # Confirmar cualquier cambio restante
        connection.commit()
        print("\nProceso completado y registros de inscripción generados exitosamente.")

    except Exception as e:
        print(f"Error al procesar los registros de inscripción: {e}")
        connection.rollback()

    finally:
        cursor.close()
        connection.close()
else:
    print("No se pudo establecer la conexión a la base de datos.")