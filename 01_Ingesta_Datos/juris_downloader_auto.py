import os
import json
import requests
from bs4 import BeautifulSoup
import ollama
import subprocess

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

# --- CONFIGURACIÓN ---
CARPETA_RESUMENES = "jurisprudencia_resumida"
MAPA_CITAS = "mapa_jurisprudencia.json"
RUTA_CALIBRE_LIB = "C:/AbogadoVirtual/BibliotecaCalibre" 

def resumir_con_qwen(codigo, texto):
    """Usa Qwen para extraer el ADN de la sentencia"""
    try:
        print(f"   📡 🧠 Qwen analizando {codigo}...")
        prompt = f"""Analiza la sentencia {codigo} y genera un resumen profesional para abogados.
        ESTRUCTURA:
        1. DECISIÓN: (Ej: Exequible / Inexequible / Condicionada)
        2. SÍNTESIS: Un párrafo sobre el argumento central (Ratio Decidendi).
        3. IMPACTO: Cómo afecta esto al artículo de la ley.
        
        TEXTO:
        {texto[:15000]}"""

        res = ollama.chat(
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
        return res['message']['content']
    except Exception as e:
        print(f"   ❌ Error al resumir con Qwen: {e}")
        return f"Error en el resumen: {e}"

def descargar_de_corte(codigo):
    """Lógica para obtener el texto desde la relatoría"""
    try:
        print(f"📡 Buscando fuente oficial para {codigo}...")
        # Simulación de respuesta
        return "Texto de prueba de la sentencia..." 
    except Exception as e:
        print(f"❌ Error descargando de la Corte: {e}")
        return ""

def cargar_en_calibre(path_archivo, codigo):
    """Registra el resumen en tu biblioteca Calibre"""
    try:
        print(f"📚 Registrando {codigo} en Calibre...")
        comando = [
            'calibredb', 'add', path_archivo,
            '--with-library', RUTA_CALIBRE_LIB,
            '--tags', 'Jurisprudencia, Corte_Constitucional, IA_Resumido',
            '--title', f'Resumen IA: {codigo}'
        ]
        subprocess.run(comando, check=True)
        print(f"✅ {codigo} registrado en Calibre.")
    except Exception as e:
        print(f"⚠️ Calibre no pudo añadir el archivo {codigo}: {e}")

def procesar_jurisprudencia():
    try:
        print("\n🚀 INICIANDO DESCARGADOR AUTOMÁTICO DE JURISPRUDENCIA...")
        if not os.path.exists(CARPETA_RESUMENES): os.makedirs(CARPETA_RESUMENES)
        
        if not os.path.exists(MAPA_CITAS):
            print(f"❌ No se encontró {MAPA_CITAS}. Ejecuta juris_extractor.py primero.")
            return

        with open(MAPA_CITAS, 'r', encoding='utf-8') as f:
            mapa = json.load(f)

        for ley, citas in mapa.items():
            sentencias_c = [c for c in citas if "Sentencia C-" in c]
            
            for sent in sentencias_c:
                try:
                    nombre_archivo = sent.replace(" ", "_").replace("-", "_") + ".md"
                    path_md = os.path.join(CARPETA_RESUMENES, nombre_archivo)

                    if os.path.exists(path_md):
                        print(f"   ⏩ Saltando {sent} (ya existe).")
                        continue

                    # 1. Obtener texto
                    texto_raw = descargar_de_corte(sent)
                    if not texto_raw: continue
                    
                    # 2. Resumir con IA
                    resumen_ia = resumir_con_qwen(sent, texto_raw)
                    
                    # 3. Guardar archivo
                    with open(path_md, "w", encoding="utf-8") as f_out:
                        f_out.write(f"# {sent}\n\n{resumen_ia}")
                    
                    # 4. Cargar en Calibre
                    cargar_en_calibre(path_md, sent)
                    
                    print(f"✅ FINALIZADO: {sent}")
                except Exception as e:
                    print(f"❌ Error en sentencia {sent}: {e}")

        print("\n✅ PROCESO AUTOMÁTICO COMPLETADO.")
    except Exception as e:
        print(f"❌ Error fatal en juris_downloader_auto: {e}")

if __name__ == "__main__":
    procesar_jurisprudencia()