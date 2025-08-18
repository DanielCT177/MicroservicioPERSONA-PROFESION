from flask import jsonify, request
from db_config import get_db_connection
import uuid
import requests  # ✅ Solo porque lo usas en obtener_personas_profesiones

#TABLA PERSONA PROFESIONES
# Asignar profesión a persona
def asignar_profesion_persona():
    data = request.get_json()
    persona_id = data.get('persona_id')
    profesion_id = data.get('profesion_id')
    fecha_asignacion = data.get('fecha_asignacion')
    estatus_id = data.get('estatus_id')  # Nuevo campo

    if not persona_id or not profesion_id or not fecha_asignacion or not estatus_id:
        return jsonify({"message": "Faltan datos: persona_id, profesion_id, fecha_asignacion y estatus_id son requeridos"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = """
            INSERT INTO persona_profesion (persona_id, profesion_id, fecha_asignacion, estatus_id)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (persona_id, profesion_id, fecha_asignacion, estatus_id))
        conn.commit()
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({"message": "Asignación registrada correctamente"}), 201

# Obtener personas con su profesion
def obtener_personas_profesiones():
    try:
        # Llamadas a las APIs externas
        personas_response = requests.get("https://microservicioine.onrender.com/api/ine/obtenerPersonas")
        profesiones_response = requests.get("https://microservicioprofesiones.onrender.com/api/obtenerProfesiones")
        estatus_response = requests.get("https://microservicio-estatus.onrender.com/estatus/obtenerTodos")

        # Validación de respuestas
        personas_response.raise_for_status()
        profesiones_response.raise_for_status()
        estatus_response.raise_for_status()

        # Obtener los datos JSON
        personas = personas_response.json()
        profesiones = profesiones_response.json()
        estatuses = estatus_response.json()

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Error al consumir las APIs externas: {str(e)}"}), 500

    # Diccionarios por ID para acceso rápido
    personas_dict = {p["id_persona"]: p for p in personas}
    profesiones_dict = {p["id_profesion"]: p for p in profesiones}
    estatus_dict = {e["idStatus"]: e for e in estatuses}

    # Obtener relaciones desde la base de datos
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT persona_id, profesion_id, fecha_asignacion, estatus_id FROM persona_profesion")
    relaciones = cursor.fetchall()
    cursor.close()
    conn.close()

    # Construir el resultado
    resultado = []
    for persona_id, profesion_id, fecha_asignacion, estatus_id in relaciones:
        persona = personas_dict.get(persona_id)
        profesion = profesiones_dict.get(profesion_id)
        estatus = estatus_dict.get(estatus_id)

        if persona and profesion and estatus:
            resultado.append({
                "persona": persona,  # 🔹 Se agrega TODO el objeto de la persona
                "profesion": profesion,  # 🔹 Todo el objeto de profesión
                "fecha_asignacion": str(fecha_asignacion),
                "estatus": estatus  # 🔹 Todo el objeto de estatus
            })

    return jsonify(resultado), 200


def obtener_persona_profesion_por_id(persona_id):
    try:
        # Llamadas a las APIs externas
        personas_response = requests.get("https://microservicioine.onrender.com/api/ine/obtenerPersonas")
        profesiones_response = requests.get("https://microservicioprofesiones.onrender.com/api/obtenerProfesiones")
        estatus_response = requests.get("https://microservicio-estatus.onrender.com/estatus/obtenerTodos")

        personas_response.raise_for_status()
        profesiones_response.raise_for_status()
        estatus_response.raise_for_status()

        personas = personas_response.json()
        profesiones = profesiones_response.json()
        estatuses = estatus_response.json()

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Error al consumir las APIs externas: {str(e)}"}), 500

    personas_dict = {p["id_persona"]: p for p in personas}
    profesiones_dict = {p["id_profesion"]: p for p in profesiones}
    estatus_dict = {e["idStatus"]: e for e in estatuses}

    # Consulta solo para esa persona
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT persona_id, profesion_id, fecha_asignacion, estatus_id
        FROM persona_profesion
        WHERE persona_id = %s
    """, (persona_id,))
    relaciones = cursor.fetchall()
    cursor.close()
    conn.close()

    resultado = []
    for persona_id, profesion_id, fecha_asignacion, estatus_id in relaciones:
        persona = personas_dict.get(persona_id)
        profesion = profesiones_dict.get(profesion_id)
        estatus = estatus_dict.get(estatus_id)

        if persona and profesion and estatus:
            resultado.append({
                "persona_id": persona_id,
                "persona_nombre": f"{persona['nombre']} {persona['apellido_paterno']} {persona['apellido_materno']}",
                "profesion_id": profesion_id,
                "profesion_nombre": profesion["nombre"],
                "fecha_asignacion": str(fecha_asignacion),
                "estatus_id": estatus_id,
                "estatus_nombre": estatus["nombre"]
            })

    if not resultado:
        return jsonify({"message": "No se encontró relación para esa persona"}), 404

    return jsonify(resultado), 200

def eliminar_logicamente_profesion_persona():
    persona_id = request.args.get('persona_id')
    profesion_id = request.args.get('profesion_id')

    if not persona_id or not profesion_id:
        return jsonify({"message": "Faltan parámetros: persona_id y profesion_id son requeridos"}), 400

    estatus_inactivo_id = 'cc3d83a6-71b9-4b2e-acdc-f05d663e7cc7'

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = """
            UPDATE persona_profesion
            SET estatus_id = %s
            WHERE persona_id = %s AND profesion_id = %s
        """
        cursor.execute(query, (estatus_inactivo_id, persona_id, profesion_id))
        conn.commit()
        filas_afectadas = cursor.rowcount
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

    if filas_afectadas == 0:
        return jsonify({"message": "Asignación no encontrada"}), 404
    else:
        return jsonify({"message": "Asignación desactivada correctamente"}), 200
