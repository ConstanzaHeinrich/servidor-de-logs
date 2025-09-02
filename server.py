from flask import Flask, request, jsonify
from datetime import datetime #para sellar hora y fecha cuando recibimos un log
import sqlite3 

app = Flask(__name__) 

# ---------------------------
# Configuración SQLite
# ---------------------------
DB_NAME = "logs.db"

def get_db_connection(): #abre la conexion
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # para devolver resultados como diccionarios
    return conn

# Crear tabla si no existe
with get_db_connection() as conn:
    conn.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        service TEXT NOT NULL,
        severity TEXT NOT NULL,
        message TEXT NOT NULL,
        received_at TEXT NOT NULL 
    )
    """)
    conn.commit()

# ---------------------------
# Tokens válidos por servicio
# ---------------------------
VALID_TOKENS = {
    "envio": "TOKEN123",
    "deposito": "TOKEN456",
    "auth": "TOKEN789",
    "notificaciones": "TOKEN999"
}

# ---------------------------
# Helper: validar token
# ---------------------------
def validate_token(auth_header): #revisa si el token que llega al header es valido o no y a que servicio pertenece
    if not auth_header: #si no recibe ningun token
        return None
    parts = auth_header.split(" ")
    if len(parts) == 2 and parts[0] == "Token": #Verifica que el header esté presente y tenga el formato correcto
        token = parts[1] #guarda el token
        for service, valid_token in VALID_TOKENS.items():
            if token == valid_token: #Revisa si ese token coincide con alguno de los tokens válidos y devuelve a qué servicio pertenece
                return service
    return None

# ---------------------------
# Endpoint POST /logs // endpoint es la ruta 
# ---------------------------
@app.route("/logs", methods=["POST"])  
def receive_logs():
    auth_header = request.headers.get("Authorization") #aca el valor del header Authorization que el cliente envió
    service_name = validate_token(auth_header) #usa la funcion anterior para ver si es valido el token

    if not service_name: #si no devuelve nada entonces el token es invalido
        return jsonify({"error": "Quién sos, bro?"}), 401 #no autorizado

    data = request.get_json() #convierte la peticion en json
    logs_to_save = data if isinstance(data, list) else [data] # si data es un solo log lo metemos a una lista 
    saved_logs = [] #lista vacía donde guardaremos los logs insertados.

    with get_db_connection() as conn: #abre la conexión a la BD y se asegura de cerrarla al final
        cursor = conn.cursor() #editar db
        for log in logs_to_save: #recorre los logs en la lista
            try:
                cursor.execute(
                    """
                    INSERT INTO logs (timestamp, service, severity, message, received_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        log.get("timestamp"),
                        log.get("service"),
                        log.get("severity"),
                        log.get("message"),
                        datetime.utcnow().isoformat()
                    )
                )
                saved_logs.append(log)
            except Exception as e: #por si falta un campo o hay un dato incorrecto etc
                return jsonify({"error": f"Log inválido: {str(e)}"}), 400 #solicitud incorrecta
        conn.commit()

    return jsonify({"status": "ok", "saved": saved_logs}), 201 #fue creado

# ---------------------------
# Endpoint GET /logs
# ---------------------------
@app.route("/logs", methods=["GET"]) #metodo usado cunado cliente pide info al servidor
def get_logs_by_severity(): #Todo lo que devuelva esta función será la respuesta HTTP
    query = "SELECT * FROM logs WHERE 1=1" #trae registros de tabla logs #base de la consulta; WHERE 1=1 facilita agregar filtros: severity = "error"
    params = [] #Lista de parámetros para la consulta SQL

    severity = request.args.get("severity")  # ej: "ERROR", "INFO", "DEBUG" #categoriza por importancia 

    if severity:
        query += " AND severity = ?" #agrega a la consulta principal 
        params.append(severity)

    query += " ORDER BY timestamp" #ordena segun timestamp

    with get_db_connection() as conn:
        cursor = conn.execute(query, params)
        rows = cursor.fetchall() #captura los resultados que cumplen con l aconsulta

    logs = [dict(row) for row in rows] #row es resultado 
    return jsonify(logs), 200 #todo ok


# ---------------------------
# Run server
# ---------------------------
if __name__ == "__main__":
    app.run(debug=True) #hace que flask arranque el servidor web para que se pueda ver en el navegador
            #debug true hace que se active el modo de depuracion de flask, sirve para que salgan mensajes de error mas claros y para que se reinicie sola cuandop se cambia el codigo