import logging
import os
import re
import threading
from collections import defaultdict
from flask import Flask, request, jsonify
from flask_cors import CORS
import ollama

# Importar notificador WhatsApp (falla silenciosamente si no está disponible)
try:
    from whatsapp_notifier import notificar_lead as _notificar_lead
    WA_DISPONIBLE = True
except ImportError:
    WA_DISPONIBLE = False
    _notificar_lead = None

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)

# Contar fuentes reales en ChromaDB (se actualiza solo al reiniciar el servidor)
def contar_fuentes_chromadb():
    try:
        import chromadb
        from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
        DB_PATH = r"c:\AbogadoVirtual\03_Motor_Core\db_guanes"
        client = chromadb.PersistentClient(path=DB_PATH)
        cols = client.list_collections()
        total = sum(
            client.get_collection(c.name, embedding_function=DefaultEmbeddingFunction()).count()
            for c in cols
        )
        return total
    except Exception as e:
        logging.warning(f"No se pudo contar fuentes ChromaDB: {e}")
        return 434  # Valor conocido como respaldo

TOTAL_FUENTES = contar_fuentes_chromadb()
logging.info(f"📚 Base de conocimiento: {TOTAL_FUENTES} vectores activos en ChromaDB")

# Cargar catálogo de minutas desde SQLite
def cargar_catalogo_minutas():
    try:
        import sqlite3
        DB_MINUTAS = r"c:\AbogadoVirtual\07_Cloud_Abogado\minutas_cloud.db"
        if not os.path.exists(DB_MINUTAS):
            return "Catálogo no disponible actualmente."
            
        conn = sqlite3.connect(DB_MINUTAS)
        c = conn.cursor()
        c.execute("SELECT slug, titulo, categoria FROM minutas_maestras")
        rows = c.fetchall()
        conn.close()
        
        catalogo_str = ""
        categorias = {}
        for slug, titulo, categoria in rows:
            if categoria not in categorias:
                categorias[categoria] = []
            categorias[categoria].append(f"- {titulo} (ID: {slug})")
            
        for cat, docs in categorias.items():
            catalogo_str += f"\n[{cat.upper()}]\n" + "\n".join(docs) + "\n"
            
        return catalogo_str
    except Exception as e:
        logging.warning(f"No se pudo cargar el catálogo de minutas: {e}")
        return "Error cargando catálogo de documentos."

CATALOGO_MINUTAS = cargar_catalogo_minutas()
logging.info("📜 Catálogo de minutas cargado y listo para el chat.")

# Almacén de conversaciones por sesión (en memoria)
historial_sesiones = defaultdict(list)
contador_consultas = defaultdict(int)

# Palabras clave que indican "momento de compra"
PALABRAS_URGENTES = ["urgente", "demanda", "notaría", "notaria", "embargar", "tutela", "interponer",
                     "radicar", "juzgado", "fallo", "sentencia", "recurso", "apelación", "apelacion"]

PROMPT_GUANES = f"""Eres el Consultor Senior de Guanes IA, el ecosistema legaltech líder en Colombia (2026). Tu conocimiento no proviene de internet genérico, sino de la "Biblioteca Privada de Guanes Legaltech": un archivo blindado de {TOTAL_FUENTES // 10} Documentos Maestros y {TOTAL_FUENTES} Vectores de Inteligencia (nodos de conocimiento) estrictamente vigentes a 2026 por el Abogado Manuel Enrique Prada Forero.

MAPEO ESTRICTO DE ESPECIALIDADES:
- PROPIEDAD HORIZONTAL (PH): "Expertos en Derecho Inmobiliario y Civil (Ley 675)". PROHIBIDO asociar con Derecho Familiar.
- INMOBILIARIO / CONSTRUCCIÓN: "Expertos en Derecho Inmobiliario, Civil e Ingeniería Jurídica".
- MINERO: "Expertos en Derecho Minero-Energético y Ambiental (Ley 685)".
- LABORAL: "Expertos en Derecho Laboral y Seguridad Social (CST)".
- SALUD: "Expertos en Derecho a la Salud, EPS y Superintendencia de Salud".
- FAMILIAR: "Expertos en Derecho de Familia y Sucesiones".
- CIVIL: "Expertos en Derecho Civil y Responsabilidad Contractual".
- COMERCIAL: "Expertos en Derecho Mercantil y Societario".

TU PORTAFOLIO DE SOLUCIONES GENERALES:
- LABORAL: Calculadora Laboral Guanes, liquidaciones e indemnizaciones (Art 64 CST).
- SALUD: Tutelas automatizadas contra EPS, análisis Circular Única SuperSalud.
- FAMILIAR: Custodia, alimentos, divorcios, sucesiones y liquidación de sociedades conyugales.
- CIVIL: Contratos, responsabilidad civil, daños y perjuicios.
- COMERCIAL: Constitución societaria, contratos mercantiles y defensa de socios.
- NOTARÍA DIGITAL: Certificación de documentos mediante Hash y Blockchain (Solana).

AVISO DE SERVICIOS ESPECIALIZADOS (SOLO CONSULTA EXPERTA):
- PH, CONSTRUCCIÓN, MINERÍA & GLOSAS (SALUD): Los servicios de Reglamentos (PH), Blindaje de Obras (Olga), Auditoría Minera (RUCOM/ANM) y Recuperación de Glosas (Salud) son servicios PREMIUM de alta complejidad. NO están disponibles para descarga automática de $19.900. El usuario DEBE solicitar una "Consulta Experta" para estos casos.

TU PORTAFOLIO DE SOLUCIONES (MINUTAS DISPONIBLES EN TIEMPO REAL):
{CATALOGO_MINUTAS}

REGLAS DE ORO:
1. ESPECIALIDAD CORRECTA: Usa el MAPEO ESTRICTO. Nunca confundas ramas del derecho.
2. LENGUAJE DEL RESPIRO: Empatía, claridad y tono tranquilizador ("Un respiro para su seguridad jurídica").
3. VENTA ACTIVA: Si el usuario necesita un documento, busca en el CATÁLOGO DE MINUTAS el ID exacto y menciónalo con su nombre oficial.
4. RECOMENDACIÓN PRECISA: Indica que el documento está listo para descarga inmediata por $19.900.
5. PRIVACIDAD: Nunca menciones RAG, LLM, APIs o SQLite.
6. CIERRE DE AUTORIDAD: Al final siempre incluye: "Información extraída de nuestra fuente de verdad blindada. Para documentos oficiales listos para radicar, active su acceso premium."
7. FORMATO LIMPIO: Sin Markdown, negritas ni asteriscos. Solo texto plano.

INSTRUCCIÓN DE ANÁLISIS:
- Usa el historial de la conversación para dar respuestas coherentes y acumulativas.
- Vincula la respuesta con una MINUTA ESPECÍFICA de nuestro catálogo siempre que sea posible.
- CRÍTICO: Si el usuario pregunta por PH (Sergio), Construcción (Olga), Minería (RUCOM) o Glosas de Salud, NO ofrezcas minutas de $19.900. Indica que son casos técnicos que requieren el Blindaje Especializado de Guanes Legaltech y remítelos a una "Consulta Experta" de inmediato.
- Si no encuentras una minuta exacta en el catálogo para otras áreas, ofrece una similar.
- Nunca inventes leyes ni asumas hechos no descritos en la consulta."""

def detectar_momento_compra(mensaje, contador, session_id='default'):
    """Detecta si el cliente está listo para comprar, retorna CTA y notifica al abogado."""
    tiene_urgencia = any(p in mensaje.lower() for p in PALABRAS_URGENTES)
    muchas_consultas = contador >= 3
    
    if tiene_urgencia or muchas_consultas:
        # Notificar al abogado por WhatsApp en un hilo separado (no bloquea la respuesta)
        if WA_DISPONIBLE:
            threading.Thread(
                target=_notificar_lead,
                args=(session_id, mensaje, "Consulta Premium"),
                daemon=True
            ).start()
        return "\n\nNota de prioridad: Veo que su caso requiere atención especializada y documentos oficiales. Le invito a activar su acceso premium para que uno de nuestros abogados le atienda directamente y radique los documentos hoy mismo. ¿Desea que le agendemos una sesión?"
    return ""

# Inicializar el motor RAG
try:
    import importlib.util
    import sys
    import os
    
    path_motor = os.path.join(os.getcwd(), "03_Motor_Core")
    sys.path.append(path_motor)
    
    spec = importlib.util.spec_from_file_location("guanes_engine", os.path.join(path_motor, "guanes_engine.py"))
    guanes_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guanes_module)
    GuanesEngine = guanes_module.GuanesEngine
    logging.info("✅ Motor RAG cargado exitosamente mediante importlib.")
except Exception as e:
    logging.error(f"❌ Error crítico cargando GuanesEngine: {e}")
    # Fallback si falla
    class GuanesEngine:
        def query(self, *args, **kwargs): return "Error cargando motor RAG local."

engine_rag = GuanesEngine()

@app.route('/api/chat', methods=['POST'])
def chat_endpoint():
    try:
        data = request.json
        if not data or 'mensaje' not in data:
            return jsonify({"error": "Falta el campo 'mensaje' en el JSON"}), 400
        
        mensaje_usuario = data['mensaje']
        perfil = data.get('perfil', 'ABOGADO IA 24/7')
        session_id = data.get('session_id', 'default')
        
        # Incrementar contador de consultas de la sesión
        contador_consultas[session_id] += 1
        contador = contador_consultas[session_id]
        
        logging.info(f"[Sesión {session_id} | Consulta #{contador} | Perfil {perfil}] {mensaje_usuario[:60]}...")
        
        # Consulta al motor RAG local
        try:
            # Pasamos el PROMPT_GUANES (que incluye el catálogo) como contexto adicional
            respuesta_ai = engine_rag.query(mensaje_usuario, perfil_nombre=perfil, extra_context=PROMPT_GUANES)
            
            # Limpieza de Markdown (aunque GuanesEngine ya suele devolver texto limpio, reforzamos)
            respuesta_ai = re.sub(r'\*\*|\*|#+|`', '', respuesta_ai)
            
            # Detectar momento de compra y añadir CTA si corresponde
            cta = detectar_momento_compra(mensaje_usuario, contador, session_id)
            respuesta_final = respuesta_ai + cta
            
            # Guardar el intercambio en el historial de la sesión (opcional para RAG, pero útil)
            historial_sesiones[session_id].append({'role': 'user', 'content': mensaje_usuario})
            historial_sesiones[session_id].append({'role': 'assistant', 'content': respuesta_ai})
            
        except Exception as rag_err:
            logging.error(f"Error con GuanesEngine RAG: {rag_err}")
            respuesta_final = f"[ERROR NÚCLEO LOCAL] No se pudo procesar la consulta RAG. {rag_err}"
        
        return jsonify({
            "status": "success",
            "output": respuesta_final,
            "origen": "Cerebro RAG Guanes (I.A. Cognitiva)",
            "sesion": session_id,
            "consulta_num": contador,
            "fuentes_activas": TOTAL_FUENTES
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    sesiones_activas = len(historial_sesiones)
    return jsonify({"status": "online", "motor": "qwen3-8b-q4", "sesiones_activas": sesiones_activas}), 200

@app.route('/api/reset_session', methods=['POST'])
def reset_session():
    """Permite resetear la memoria de una sesión si el usuario lo pide."""
    data = request.json or {}
    session_id = data.get('session_id', 'default')
    historial_sesiones.pop(session_id, None)
    contador_consultas.pop(session_id, None)
    return jsonify({"status": "session_reset", "session_id": session_id}), 200

if __name__ == '__main__':
    import threading

    def warmup():
        """Pre-carga el modelo en RAM para evitar timeout en la primera consulta."""
        try:
            print("🔥 Pre-cargando guanes-senior en memoria (warmup)...")
            ollama.chat(
                model='guanes-senior',
                messages=[{'role': 'user', 'content': 'Hola'}],
                options={
                    "num_ctx": 512,       # Contexto mínimo para warmup
                    "temperature": 0.1,
                    "top_p": 0.95,
                    "top_k": 40,
                    "num_thread": 8
                }
            )
            print("✅ Modelo caliente y listo para atender consultas.")
        except Exception as e:
            print(f"⚠️ Warmup falló (no es crítico): {e}")

    threading.Thread(target=warmup, daemon=True).start()

    print("==================================================")
    print(" INICIANDO SERVIDOR PUENTE B2B (GUANES IA - QWEN3 Q4)")
    print(" Memoria de conversación: ACTIVA")
    print(" Detector de momento de compra: ACTIVO")
    print(" Warmup automático del modelo: ACTIVO")
    print("==================================================")
    app.run(host='0.0.0.0', port=8000, debug=False)
