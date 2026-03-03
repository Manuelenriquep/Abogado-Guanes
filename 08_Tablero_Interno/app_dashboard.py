from flask import Flask, render_template, jsonify
import os
import sys

# Agregar ruta para poder importar generar_opml.py
BASE_DIR = r"c:\AbogadoVirtual"
sys.path.append(os.path.join(BASE_DIR, "99_Logs_y_Temporales"))
import generar_opml

app = Flask(__name__)

DIR_ALERTAS = os.path.join(BASE_DIR, "Alertas_Negocio")
LOG_FILE = os.path.join(BASE_DIR, "99_Logs_y_Temporales", "guanes_cronos.log")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/metrics')
def get_metrics():
    """Genera y devuelve las métricas y la estructura en HTML del proyecto"""
    try:
        ignore_list = {'venv', 'env', 'node_modules', 'db_guanes', 'chroma_db', 'dist', '99_Logs_y_Temporales', '.git', '__pycache__'}
        # generar_opml modificado para solo devolver data en lugar de escribir a disco
        metrics, html_tree = generar_opml.get_metrics_and_tree(BASE_DIR, ignore_list)
        return jsonify({"status": "success", "metrics": metrics, "tree_html": html_tree})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/alerts')
def get_alerts():
    """Devuelve las últimas alertas y oportunidades de negocio reales (incluyendo Oportunidad de Monetización)"""
    alerts = []
    if os.path.exists(DIR_ALERTAS):
        try:
            archivos = sorted(os.listdir(DIR_ALERTAS), key=lambda x: os.path.getmtime(os.path.join(DIR_ALERTAS, x)), reverse=True)
            for file_name in archivos[:10]: # Mostrar las 10 más recientes
                if file_name.endswith('.md'):
                    ruta = os.path.join(DIR_ALERTAS, file_name)
                    with open(ruta, 'r', encoding='utf-8', errors='ignore') as f:
                        contenido = f.read()
                        alerts.append({"filename": file_name, "content": contenido})
        except Exception as e:
            pass
    return jsonify({"alerts": alerts})

@app.route('/api/logs')
def get_logs():
    """Devuelve las últimas 50 líneas del log del Cronos"""
    logs = ""
    try:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                # Tomar ultimas 50 lineas
                logs = "".join(lines[-50:])
        else:
            logs = "No log file found yet."
    except Exception as e:
        logs = f"Error leyendo logs: {str(e)}"
    
    return jsonify({"logs": logs})

if __name__ == '__main__':
    print("==================================================")
    print(" 🦉 INICIANDO GUANES HUB (TABLERO INTERNO) 🦉")
    print("==================================================")
    # Hosteado en 127.0.0.1 para que solo sea accesible desde esta misma PC por seguridad
    app.run(host='127.0.0.1', port=5000, debug=True)
