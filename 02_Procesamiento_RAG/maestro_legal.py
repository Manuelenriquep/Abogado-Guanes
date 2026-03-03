import os
import csv
import math
import ollama
import requests
from bs4 import BeautifulSoup

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

# ==========================================
# 2. CONFIGURACIÓN DEL SISTEMA
# ==========================================
ARCHIVO_CSV = 'lista_codigos.csv'  # Tu lista con las leyes (Nombre, URL)
CARPETA_SALIDA = r"c:\AbogadoVirtual\01_Ingesta_Datos\Leyes_Markdown"
TAMANO_BLOQUE = 6000 # Caracteres por bloque para no ahogar a la IA

# Crear la carpeta de salida si no existe
if not os.path.exists(CARPETA_SALIDA):
    os.makedirs(CARPETA_SALIDA)

# ==========================================
# 3. FUNCIONES DEL "MAESTRO LEGAL"
# ==========================================
def descargar_texto_bruto(url):
    """Descarga el texto bruto de la web (o ajusta esto si usas PDFs locales)"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        respuesta = requests.get(url, headers=headers)
        respuesta.raise_for_status()
        soup = BeautifulSoup(respuesta.text, 'html.parser')
        return soup.get_text(separator='\n', strip=True)
    except Exception as e:
        print(f"❌ Error descargando la URL: {e}")
        return None

def dividir_en_bloques(texto, tamano):
    """Corta el texto gigante en pedazos digeribles para la IA"""
    return [texto[i:i+tamano] for i in range(0, len(texto), tamano)]

def procesar_con_qwen(texto_bloque):
    """Envía el bloque a Qwen 3 local con memoria expandida y cero alucinaciones"""
    try:
        respuesta = ollama.chat(
            model='qwen3:8b', 
            messages=[
                {'role': 'system', 'content': PROMPT_GUANES},
                {'role': 'user', 'content': texto_bloque}
            ],
            options={
                "num_ctx": 4096,     # <--- EL BLINDAJE: 4 MIL TOKENS DE MEMORIA RAM
                "temperature": 0.0   # <--- Cero creatividad, 100% precisión legal
            }
        )
        return respuesta['message']['content']
    except Exception as e:
        return f"\n❌ ERROR DE SERVIDOR EN ESTE BLOQUE: {e}\n"

# ==========================================
# 4. EL MOTOR PRINCIPAL (EL BUCLE)
# ==========================================
def iniciar_fabrica():
    print("\n🚀 INICIANDO MAESTRO LEGAL - GUANES LEGAL TECH 🚀\n")
    
    if not os.path.exists(ARCHIVO_CSV):
        print(f"❌ No se encontró el archivo '{ARCHIVO_CSV}'.")
        return

    with open(ARCHIVO_CSV, mode='r', encoding='utf-8') as archivo:
        lector_csv = csv.reader(archivo)
        
        for fila in lector_csv:
            if len(fila) < 2:
                continue
            
            nombre_ley = fila[0].strip()
            url_ley = fila[1].strip()
            ruta_md = os.path.join(CARPETA_SALIDA, f"{nombre_ley}.md")

            print(f"\n📡 Descargando: {nombre_ley}...")
            texto_bruto = descargar_texto_bruto(url_ley)
            
            if not texto_bruto:
                continue

            bloques = dividir_en_bloques(texto_bruto, TAMANO_BLOQUE)
            total_bloques = len(bloques)
            
            print(f"   -> Qwen 3 procesando {nombre_ley} (esto puede tardar según el tamaño)...")
            
            # Abrir el archivo MD e ir guardando bloque a bloque
            with open(ruta_md, 'w', encoding='utf-8') as archivo_md:
                archivo_md.write(f"# {nombre_ley.replace('_', ' ')}\n\n")
                
                for i, bloque in enumerate(bloques):
                    print(f"      📡 Procesando bloque {i+1} de {total_bloques}...")
                    texto_limpio = procesar_con_qwen(bloque)
                    archivo_md.write(texto_limpio + "\n\n")
            
            print(f"✅ FINALIZADO: {nombre_ley}")

if __name__ == "__main__":
    iniciar_fabrica()