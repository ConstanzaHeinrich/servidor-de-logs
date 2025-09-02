import requests
import random
import time
from datetime import datetime

# ---------------------------
# Configuración del servidor
# ---------------------------
SERVER_URL = "http://127.0.0.1:5000/logs"

# Tokens por servicio (coinciden con server.py)
TOKENS = {
    "envio": "TOKEN123",
    "deposito": "TOKEN456",
    "auth": "TOKEN789",
    "notificaciones": "TOKEN999"
}

# Severidades posibles
SEVERITIES = ["INFO", "DEBUG", "WARNING", "ERROR"] #categoriza por importancia

# Mensajes falsos por servicio
MESSAGES = {
    "envio": [
        "Paquete enviado exitosamente",
        "Error en la dirección de envío",
        "El cliente solicitó reprogramar la entrega",
    ],
    "deposito": [
        "Depósito acreditado en la cuenta",
        "Fondos insuficientes para realizar depósito",
        "Depósito en espera de confirmación",
    ],
    "auth": [
        "Usuario inició sesión correctamente",
        "Intento de login fallido",
        "Token expirado, requiere renovación",
    ],
    "notificaciones": [
        "Notificación enviada al cliente",
        "Error en la cola de mensajes",
        "Notificación marcada como leída",
    ]
}

# ---------------------------
# Función para generar un log falso
# ---------------------------
def generar_log(servicio): #simulado de cliente
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "service": servicio,
        "severity": random.choice(SEVERITIES),
        "message": random.choice(MESSAGES[servicio])
    }

# ---------------------------
# Función para enviar logs al servidor
# ---------------------------
def enviar_logs(servicio, cantidad=5):
    headers = {"Authorization": f"Token {TOKENS[servicio]}"}
    logs = [generar_log(servicio) for _ in range(cantidad)]

    try:
        response = requests.post(SERVER_URL, json=logs, headers=headers)    #método de HTTP usado cuando el cliente quiere enviar información al servidor
        if response.status_code == 201: #fue creado
            print(f"[{servicio}] {cantidad} logs enviados correctamente ✅")
        else:
            print(f"[{servicio}] Error al enviar logs ❌ -> {response.text}")
    except Exception as e:
        print(f"[{servicio}] No se pudo conectar al servidor ❌ -> {str(e)}")

# ---------------------------
# Simulación principal
# ---------------------------
if __name__ == "__main__":
    servicios = list(TOKENS.keys())

    # Simula que cada servicio manda logs en bucle
    for _ in range(5):  # número de rondas
        servicio = random.choice(servicios)
        enviar_logs(servicio, cantidad=random.randint(1, 5))
        time.sleep(2)  # espera 2 segundos antes de la siguiente ronda
