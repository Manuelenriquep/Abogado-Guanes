from flask import Flask, request, jsonify
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
DB_PATH = r"c:\AbogadoVirtual\03_Motor_Core\telemetria_global.db"

def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS logs_telemetria
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  usb_id TEXT, 
                  tipo_documento TEXT, 
                  municipio TEXT, 
                  email_lead TEXT,
                  timestamp TEXT)''')
                  
    # Agregar columna email_lead si la base de datos ya existía sin ella
    try:
        c.execute("ALTER TABLE logs_telemetria ADD COLUMN email_lead TEXT")
    except sqlite3.OperationalError:
        pass # La columna ya existe
                  
    c.execute('''CREATE TABLE IF NOT EXISTS control_licencias
                 (usb_id TEXT PRIMARY KEY, 
                  estado_licencia TEXT)''')
    conn.commit()
    conn.close()

@app.route('/webhook/usb-telemetry', methods=['POST'])
def recibir_telemetria():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No payload"}), 400
            
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        c = conn.cursor()
        
        # Inserción del Log
        c.execute("INSERT INTO logs_telemetria (usb_id, tipo_documento, municipio, email_lead, timestamp) VALUES (?, ?, ?, ?, ?)",
                  (data.get('usb_id', 'UNKNOWN'), 
                   data.get('tipo_documento', 'UNKNOWN'), 
                   data.get('municipio', 'UNKNOWN'), 
                   data.get('email_lead', 'N/A'),
                   data.get('timestamp', datetime.now().isoformat())))
        
        # Auto-registro en control si la USB es nueva
        c.execute("INSERT OR IGNORE INTO control_licencias (usb_id, estado_licencia) VALUES (?, 'active')", 
                  (data.get('usb_id', 'UNKNOWN'),))
                  
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Telemetría guardada"}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/webhook/check-usb-status', methods=['POST'])
def validar_killswitch():
    try:
        data = request.json
        usb_id = data.get('usb_id', 'UNKNOWN')
        
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        c = conn.cursor()
        
        c.execute("SELECT estado_licencia FROM control_licencias WHERE usb_id=?", (usb_id,))
        row = c.cursor.fetchone()
        conn.close()
        
        if row and row[0] == 'blocked':
            return jsonify({"status": "blocked", "command": "stop"}), 200
        else:
            return jsonify({"status": "active", "command": "proceed"}), 200
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/', methods=['GET'])
def index():
    return dashboard()

@app.route('/dashboard', methods=['GET'])
def dashboard():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT usb_id, tipo_documento, municipio, email_lead, timestamp FROM logs_telemetria ORDER BY timestamp DESC LIMIT 50")
    logs = c.fetchall()
    conn.close()
    
    html = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>HQ N8N Local Dashboard - Telemetría</title>
        <style>
            body { font-family: 'Segoe UI', sans-serif; background-color: #0f172a; color: #f8fafc; padding: 20px; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; background-color: #1e293b; }
            th, td { padding: 12px; border: 1px solid #334155; text-align: left; }
            th { background-color: #3b82f6; color: white; }
            tr:nth-child(even) { background-color: #0f172a; }
            .badge-cloud { background-color: #10b981; padding: 4px 8px; border-radius: 4px; font-size: 0.8em; font-weight: bold; }
            .badge-usb { background-color: #f59e0b; padding: 4px 8px; border-radius: 4px; font-size: 0.8em; font-weight: bold; }
        </style>
    </head>
    <body>
        <h2>📡 Centro de Comando - Leads y Telemetría USB</h2>
        <table>
            <tr>
                <th>Origen (USB/Cloud)</th>
                <th>Documento / Acción</th>
                <th>Municipio</th>
                <th>Email del Lead (Cloud)</th>
                <th>Fecha y Hora</th>
            </tr>
    """
    for log in logs:
        origen = log[0]
        badge = "<span class='badge-cloud'>CLOUD LEAD</span>" if origen == "CLOUD_WEB_LEAD" else "<span class='badge-usb'>USB OFFLINE</span>"
        try:
            fecha_str = datetime.fromisoformat(log[4]).strftime("%Y-%m-%d %H:%M:%S")
        except:
            fecha_str = log[4]
            
        html += f"""
            <tr>
                <td>{badge} <br/> <small>{origen}</small></td>
                <td>{log[1]}</td>
                <td>{log[2]}</td>
                <td><strong>{log[3] if log[3] else 'N/A'}</strong></td>
                <td>{fecha_str}</td>
            </tr>
        """
    html += "</table></body></html>"
    return html, 200

if __name__ == '__main__':
    print("📡 INICIANDO SERVIDOR MAESTRO DE LICENCIAS Y TELEMETRÍA (N8N Mock)")
    print("🛡️ Escuchando pings de los Ejecutables USB en puerto 5678...")
    init_db()
    app.run(host='0.0.0.0', port=5678, threaded=True)
