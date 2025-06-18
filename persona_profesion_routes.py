from flask import Blueprint
from controllers import asignar_profesion_persona, obtener_personas_profesiones, obtener_persona_profesion_por_id

persona_profesion_bp = Blueprint('persona_profesion_bp', __name__)

# Asignar profesión a persona
@persona_profesion_bp.route('/persona_profesion', methods=['POST'])
def asignar_profesion():
    return asignar_profesion_persona()

# Eliminar asignación
@persona_profesion_bp.route('/persona_profesion', methods=['DELETE'])
def eliminar_asignacion():
    return eliminar_profesion_persona()

# Obtener todas las asignaciones
@persona_profesion_bp.route('/obtener_personas_profesion', methods=['GET'])
def obtener_personas_profesion():
    return obtener_personas_profesiones()

# Obtener asignacion por ID de persona
@persona_profesion_bp.route('/obtener_persona_profesion/<persona_id>', methods=['GET'])
def obtener_persona_profesion_por_id_route(persona_id):
    return obtener_persona_profesion_por_id(persona_id)