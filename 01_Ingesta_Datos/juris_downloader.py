import ollama
import json
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

def resumir_sentencia_con_qwen(codigo_sentencia, texto_completo):
    try:
        print(f"   📡 🧠 Qwen analizando la {codigo_sentencia}...")
        
        prompt = f"""Analiza la sentencia {codigo_sentencia} y extrae:
        1. HECHOS RELEVANTES: Breve resumen de por qué surgió el caso.
        2. PROBLEMA JURÍDICO: La pregunta central que resolvió la Corte.
        3. RATIO DECIDENDI: El argumento principal de la decisión.
        4. DECISIÓN: (Ej: Exequible, Inexequible).
        
        Devuelve el resultado en Markdown profesional.
        
        TEXTO DE LA SENTENCIA:
        {texto_completo[:15000]}"""

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
        print(f"   ❌ Error al resumir {codigo_sentencia}: {e}")
        return f"Error al resumir: {e}"

def procesar_mapa_jurisprudencia():
    try:
        print("\n🚀 INICIANDO DESCARGADOR DE JURISPRUDENCIA...")
        if not os.path.exists('jurisprudencia_resumida'): 
            os.makedirs('jurisprudencia_resumida')
            
        if not os.path.exists('mapa_jurisprudencia.json'):
            print("❌ No se encontró 'mapa_jurisprudencia.json'.")
            return

        with open('mapa_jurisprudencia.json', 'r', encoding='utf-8') as f:
            mapa = json.load(f)

        for ley, sentencias in mapa.items():
            print(f"\n📂 Analizando citas en {ley}...")
            for codigo in sentencias:
                try:
                    nombre_limpio = codigo.replace(" ", "_").replace("-", "_")
                    path_resumen = f"jurisprudencia_resumida/{nombre_limpio}.md"
                    
                    if os.path.exists(path_resumen):
                        print(f"   ⏩ Saltando {codigo} (ya existe).")
                        continue

                    print(f"🔍 Buscando texto para {codigo}...")
                    
                    # Supongamos que ya tenemos el texto (paso técnico a seguir)
                    texto_sentencia = "Texto de ejemplo para la sentencia " + codigo
                    
                    resumen = resumir_sentencia_con_qwen(codigo, texto_sentencia)
                    with open(path_resumen, "w", encoding="utf-8") as f_out:
                        f_out.write(resumen)
                    
                    print(f"✅ FINALIZADO: {codigo}")
                except Exception as e:
                    print(f"   ❌ Error procesando {codigo}: {e}")
                    
        print("\n✅ PROCESO DE JURISPRUDENCIA COMPLETADO.")
    except Exception as e:
        print(f"❌ Error fatal en juris_downloader: {e}")

if __name__ == "__main__":
    procesar_mapa_jurisprudencia()