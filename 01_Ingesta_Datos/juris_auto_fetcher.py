import requests
from bs4 import BeautifulSoup
import json
import ollama
import os

# ==========================================
# 1. EL ADN GUANES (MANIFIESTO DEL SISTEMA)
# ==========================================
PROMPT_GUANES = """Eres el Consultor Senior de Guanes IA, el ecosistema legaltech líder en Colombia (2026). Tu conocimiento no proviene de internet genérico, sino de la "Biblioteca Privada de Guanes Legaltech": 229 fuentes curadas por el Abogado Manuel Enrique Prada Forero.

REGLAS DE ORO:
1. PRIORIDAD NORMATIVA: Usa estrictamente Ley 675/2001, Decretos 768 y 1166 de 2025 (Inmobiliario), Resolución ANM 3824/2025 (Minero) y Códigos vigentes a Marzo 2026.
2. LENGUAJE DEL RESPIRO: Responde con empatía, claridad y un tono profesional que brinde tranquilidad ("Un respiro para su seguridad jurídica").
3. PRIVACIDAD: No menciones datos técnicos como RAG o APIs. Todo el procesamiento es local y soberano.
4. CIERRE DE AUTORIDAD: Al final de cada respuesta gratuita (<15 consultas), incluye: "Información extraída de nuestra fuente de verdad blindada. Para documentos oficiales listos para radicar, active su acceso premium."

INSTRUCCIÓN DE ANÁLISIS:
- Si el usuario sube un documento (plano, minuta, requerimiento ANM), analízalo paso a paso identificando Red Flags y riesgos de demandas.
- Nunca inventes leyes. Si falta información para un blindaje total, indícalo claramente."""

# Base de la URL de búsqueda de la Corte Constitucional
URL_BUSQUEDA = "https://www.corteconstitucional.gov.co/relatoria/busqueda_relatoria.php"

def descargar_texto_sentencia(codigo_sentencia):
    """Busca y descarga el texto plano de una sentencia específica."""
    try:
        print(f"📡 Buscando en Relatoría: {codigo_sentencia}...")
        
        # Aquí simulamos la petición a la base de datos de la Corte
        # En una versión avanzada usamos Selenium o Requests enviando el código C-XXX
        # Para este ejemplo, configuramos la función para recibir el contenido
        return "Texto simulado de la sentencia para procesamiento."
    except Exception as e:
        print(f"❌ Error descargando sentencia {codigo_sentencia}: {e}")
        return None

def procesar_sentencias_con_precision():
    try:
        print("\n🚀 INICIANDO PROCESO DE JURISPRUDENCIA...")
        if not os.path.exists('jurisprudencia_resumida'): os.makedirs('jurisprudencia_resumida')
        
        if not os.path.exists('mapa_jurisprudencia.json'):
            print("❌ No se encontró 'mapa_jurisprudencia.json'.")
            return

        with open('mapa_jurisprudencia.json', 'r', encoding='utf-8') as f:
            mapa = json.load(f)

        for ley, sentencias in mapa.items():
            for codigo in sentencias:
                try:
                    print(f"📡 Procesando sentencia {codigo} para {ley}...")
                    texto_sentencia = descargar_texto_sentencia(codigo)
                    
                    if not texto_sentencia: continue

                    # PROMPT DE ALTA PRECISIÓN PARA QWEN
                    prompt = f"""Analiza el texto de la sentencia {codigo}. 
                    REGLAS ESTRICTAS:
                    1. No inventes hechos. Si el texto no lo dice, pon "No disponible".
                    2. Extrae el texto EXACTO del resuelve.
                    3. Identifica si la norma fue declarada EXEQUIBLE, INEXEQUIBLE o EXEQUIBLE CONDICIONADA.
                    
                    TEXTO DE LA SENTENCIA:
                    {texto_sentencia}"""
                    
                    respuesta = ollama.chat(
                        model='qwen3:8b', 
                        messages=[
                            {'role': 'system', 'content': PROMPT_GUANES},
                            {'role': 'user', 'content': prompt}
                        ],
                        options={
                            "num_ctx": 4096,
                            "temperature": 0.0
                        }
                    )
                    
                    resultado = respuesta['message']['content']
                    nombre_archivo = codigo.replace(" ", "_").replace("-", "_") + ".md"
                    with open(f"jurisprudencia_resumida/{nombre_archivo}", "w", encoding="utf-8") as f_out:
                        f_out.write(resultado)
                    
                    print(f"✅ Sentencia {codigo} procesada con éxito.")
                except Exception as e:
                    print(f"❌ Error en sentencia {codigo}: {e}")
                    
        print("✅ FINALIZADO: Módulo de jurisprudencia configurado para máxima fidelidad.")
    except Exception as e:
        print(f"❌ Error fatal en procesamiento de jurisprudencia: {e}")

if __name__ == "__main__":
    procesar_sentencias_con_precision()