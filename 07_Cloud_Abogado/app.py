from flask import Flask, request, jsonify, render_template_string
import requests
import datetime
import threading
import sqlite3
import re

app = Flask(__name__)

# Configuración Base
# HQ_WEBHOOK apunta al entorno real de producción en Railway
HQ_WEBHOOK = "https://n8n-production-612f.up.railway.app/webhook/usb-telemetry"

# El código HTML se carga dinámicamente desde index.html

def reportar_telemetria(email, tipo_minuta):
    """Envía telemetría al servidor HQ para captación de leads en tiempo real"""
    payload = {
        "usb_id": "CLOUD_WEB_LEAD",
        "ubicacion": "abogado.guanes.biz",
        "tipo_documento": tipo_minuta,
        "email_lead": email,
        "timestamp": datetime.datetime.now().isoformat()
    }
    try:
        # PING AL HQ SILENCIOSO
        requests.post(HQ_WEBHOOK, json=payload, timeout=3)
    except:
        pass # Ignorar si el webhook falla en cloud

@app.route('/')
def index():
    with open('index.html', 'r', encoding='utf-8') as f:
        return render_template_string(f.read())

@app.route('/api/generar', methods=['POST'])
def generar():
    data = request.json
    email = data.get('email')
    tipo = data.get('tipo', 'generico')
    
    # 1. Report Lead to HQ asíncronamente
    threading.Thread(target=reportar_telemetria, args=(email, tipo)).start()
    
    # 2. Generar Minuta Stub (En prod, conectaría al LLM)
    minuta_texto = f"""*** DOCUMENTO LEGAL GENERADO ***
Tipo: {tipo.upper()}
Fecha: {datetime.datetime.now().strftime("%Y-%m-%d")}
Solicitante: {email}

[CLÁUSULA PRIMERA]: La presente minuta es generada por Guanes Abogado IA 24/7.
[CLÁUSULA SEGUNDA]: El documento está protegido por la Ley 527 de 1999 sobre Comercio Electrónico.
    
Aviso: Este es un borrador inteligente. Para la validez notarial, acuda a Guanes Inmobiliario V5.
"""
    return jsonify({"status": "success", "minuta": minuta_texto})

@app.route('/health')
def health():
    return "200 OK"

# --- NUEVA API PARA N8N: BÓVEDA DE MINUTAS ---

@app.route('/api/minutas', methods=['GET'])
def listar_minutas():
    """Devuelve a N8N la lista de las 80 minutas disponibles (slugs y títulos)"""
    try:
        conn = sqlite3.connect("minutas_cloud.db")
        c = conn.cursor()
        c.execute("SELECT slug, titulo, categoria FROM minutas_maestras")
        rows = c.fetchall()
        conn.close()
        
        minutas = [{"slug": r[0], "titulo": r[1], "categoria": r[2]} for r in rows]
        return jsonify({"status": "success", "total": len(minutas), "data": minutas})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/minutas/generar', methods=['POST'])
def generar_desde_boveda():
    """
    Recibe de N8N el slug de la minuta y un diccionario de variables.
    Ej: {"slug": "civil_promesa", "datos": {"NOMBRE_ARRENDADOR": "Juan", "CEDULA": "123"}}
    """
    payload = request.json
    slug = payload.get('slug')
    datos = payload.get('datos', {})
    
    if not slug:
        return jsonify({"status": "error", "message": "Falta el slug de la minuta"}), 400
        
    try:
        conn = sqlite3.connect("minutas_cloud.db")
        c = conn.cursor()
        c.execute("SELECT titulo, contenido FROM minutas_maestras WHERE slug=?", (slug,))
        row = c.fetchone()
        conn.close()
        
        if not row:
            return jsonify({"status": "error", "message": "Minuta no encontrada en la Bóveda"}), 404
            
        titulo = row[0]
        contenido = row[1]
        
        # Reemplazo ultra-rápido de variables 
        # Busca tokens [LLAVE] y los reemplaza. Si no manda la llave, lo deja como "[LLAVE (pendiente)]"
        def repl(match):
            llave = match.group(1)
            return str(datos.get(llave, f"[{llave} (pendiente)]"))
            
        documento_final = re.sub(r'\[([^\]]+)\]', repl, contenido)
        
        # Telemetría
        threading.Thread(target=reportar_telemetria, args=(datos.get("email", "API_N8N"), slug)).start()
        
        return jsonify({
            "status": "success", 
            "titulo": titulo, 
            "documento_compilado": documento_final,
            "metadata": {"latencia": "0ms", "costo_tokens": "$0"}
        })
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

def reportar_telemetria(email, tipo_minuta):
    """Envía telemetría al servidor HQ para captación de leads en tiempo real"""
    payload = {
        "usb_id": "CLOUD_WEB_N8N_API",
        "ubicacion": "abogado.guanes.biz",
        "tipo_documento": tipo_minuta,
        "email_lead": email,
        "timestamp": datetime.datetime.now().isoformat()
    }
    try:
        requests.post(HQ_WEBHOOK, json=payload, timeout=3)
    except:
        pass

import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
