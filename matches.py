# matches.py
from firebase_config import db
from datetime import datetime

def create_match(user_id: str, sala: str):
    """
    Crea una partida en la sala seleccionada: 'sala1' o 'sala2'.
    """

    # Validación simple
    sala = sala.lower()
    if sala not in ["sala1", "sala2"]:
        raise ValueError("Sala inválida. Usa 'sala1' o 'sala2'.")

    try:
        match_data = {
            "host": user_id,
            "guest": None,
            "status": "waiting",  # waiting / ready / playing / finished
            "created_at": datetime.now().isoformat()
        }

        # Guardar en Firebase
        db.child("salas").child(sala).set(match_data)

        print(f"✔ Partida creada correctamente en {sala}")
        return True

    except Exception as e:
        print("❌ Error create_game:", e)
        return False


def join_match(user_id: str, sala: str):
    """
    Permite unirse a una sala existente.
    """

    sala = sala.lower()
    if sala not in ["sala1", "sala2"]:
        raise ValueError("Sala inválida. Usa 'sala1' o 'sala2'.")

    try:
        match = db.child("salas").child(sala).get().val()

        if match is None:
            print("❌ La sala no existe.")
            return False

        if match["guest"] is not None:
            print("❌ La sala ya está llena.")
            return False

        db.child("salas").child(sala).update({
            "guest": user_id,
            "status": "ready"
        })

        print(f"✔ Te uniste correctamente a {sala}")
        return True

    except Exception as e:
        print("❌ Error join_game:", e)
        return False


def get_match(sala: str):
    """
    Obtiene los datos de la partida de la sala.
    """
    sala = sala.lower()

    try:
        return db.child("salas").child(sala).get().val()
    except Exception as e:
        print("❌ Error get_match:", e)
        return None
