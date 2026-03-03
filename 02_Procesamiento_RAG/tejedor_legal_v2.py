import os
import re
import json
import time
import ollama

# ==========================================
# CONFIGURACIÓN TÁCTICA v2.0 - CAZA-PAGARÉS
# ==========================================
ARCHIVO_ORIGEN = r"c:\AbogadoVirtual\01_Ingesta_Datos\biblioteca_completa\Codigo_de_Comercio_Completo.md"
ARCHIVO_SALIDA = r"c:\AbogadoVirtual\03_Motor_Core\vectores_titulos_valores.json"
MODELO_OLLAMA = 'qwen3:8b'
CTX_SIZE = 4096

KEYWORDS_RIESGO = r'pagaré|letra de cambio|carta de instrucciones|espacios en blanco|prescripción|excepciones'

PROMPT_INFERENCIA = """
Actúa como Ingeniero de IA y Abogado Senior de Guanes Legal Tech. Analiza el siguiente bloque legal del Código de Comercio de Colombia.

REGLA DE PRECEDENCIA COLOMBIANA (INQUEBRANTABLE):
Al analizar cualquier caso o artículo, aplica la jerarquía normativa estricta:
1. La Constitución Política y la jurisprudencia unificada prevalecen sobre las Leyes (Códigos).
2. Las Leyes prevalecen sobre los Decretos y Acuerdos Locales.
Si detectas una contradicción entre una norma local (ej. Municipal) y un Código Nacional, debes alertar la 'Inaplicabilidad por Inconstitucionalidad o Ilegalidad' y dar la razón al usuario basándote en la norma superior.

TAREAS:
1. Crea una solución empaquetada PERSUASIVA para el ciudadano sobre Títulos Valores.
2. Enfócate específicamente en detectar ANOMALÍAS COMERCIALES LUCRATIVAS:
   - Pagarés firmados en blanco sin carta de instrucciones.
   - Prescripción de la acción cambiaria (cuándo vence la deuda).
   - Excepciones cambiarias (cómo defenderse de un cobro).
3. Usa OBLIGATORIAMENTE el tag comercial: [DESBLOQUEO_B2C].
4. Genera un resumen ejecutivo persuasivo de la solución o procedimiento encontrado.
5. Sugiere un precio de venta para esta solución en el rango de $29,900 a $49,900 COP.
6. Genera OBLIGATORIAMENTE un diagrama de flujo paso a paso del procedimiento legal usando sintaxis estricta de Mermaid.js.

FORMATO DE RESPUESTA (Solo JSON raw, sin markdown extra):
{
  "tag_comercial": "[DESBLOQUEO_B2C]",
  "precio_sugerido": "...",
  "resumen_solucion": "...",
  "diagrama_mermaid": "..."
}
"""

def procesar_v2():
    try:
        print("🚀 INICIANDO OPERACIÓN CAZA-PAGARÉS - MOTOR v2.2 (BATCH MODE) 🚀")
        
        if not os.path.exists(ARCHIVO_ORIGEN):
            print(f"❌ Error: No se encuentra {ARCHIVO_ORIGEN}")
            return

        with open(ARCHIVO_ORIGEN, "r", encoding="utf-8") as f:
            contenido_completo = f.read()

        # OOM SHIELD: Segmentar solo Libro III
        print("🛡️  Activando Escudo OOM: Aislamiento de Libro III...")
        l3_start = contenido_completo.find('LIBRO TERCERO')
        if l3_start == -1: l3_start = contenido_completo.find('LIBRO III')
        
        l4_start = contenido_completo.find('LIBRO CUARTO')
        if l4_start == -1: l4_start = len(contenido_completo)
        
        if l3_start != -1:
            contenido = contenido_completo[l3_start:l4_start]
            print(f"📦 Segmento Libro III aislado ({len(contenido)} caracteres).")
        else:
            print("⚠️ Advertencia: No se encontró marcador de LIBRO III. Usando archivo completo.")
            contenido = contenido_completo

        # MOTOR 1: Python Regex (Filtro por Dolor)
        print("📡 Escaneando Títulos Valores con Regex Nativo...")
        
        hallazgos = []
        # Buscamos bloques de artículos
        bloques_articulos = re.split(r'(?i)(?=ARTÍCULO\s+\d+)', contenido)
        
        bloques_interes = []
        for bloque in bloques_articulos:
            if re.search(KEYWORDS_RIESGO, bloque, re.IGNORECASE):
                bloque_limpio = bloque.strip()
                if len(bloque_limpio) > 50:
                    bloques_interes.append(bloque_limpio)
        
        print(f"🎯 Se detectaron {len(bloques_interes)} bloques con alto potencial comercial.")

        resultados_finales = []
        if os.path.exists(ARCHIVO_SALIDA):
            with open(ARCHIVO_SALIDA, "r", encoding="utf-8") as f:
                try:
                    resultados_finales = json.load(f)
                    print(f"♻️  Cargados {len(resultados_finales)} hallazgos existentes. Resumiendo...")
                except:
                    pass

        articulos_procesados = {h["articulo_origen"] for h in resultados_finales}

        # MOTOR 2: LLM local (Batching con Respiración de RAM)
        for i, bloque in enumerate(bloques_interes):
            # Extraer número de artículo para referencia
            art_match = re.search(r'ARTÍCULO\s+(\d+)', bloque, re.IGNORECASE)
            num_articulo = art_match.group(1) if art_match else f"Desconocido_{i}"
            id_articulo = f"Artículo {num_articulo}"
            
            if id_articulo in articulos_procesados:
                print(f"⏩ Saltando {id_articulo} ({i+1}/{len(bloques_interes)}) - ya procesado.")
                continue

            print(f"🧠 Analizando {id_articulo} ({i+1}/{len(bloques_interes)})...")
            
            try:
                response = ollama.chat(
                    model=MODELO_OLLAMA,
                    messages=[
                        {'role': 'system', 'content': PROMPT_INFERENCIA},
                        {'role': 'user', 'content': bloque}
                    ],
                    options={
                        "num_ctx": CTX_SIZE,
                        "temperature": 0.0
                    }
                )
                
                # Intentar parsear el JSON de la respuesta del LLM
                output_txt = response['message']['content']
                # Limpiar posibles bloques de código markdown del LLM
                output_txt = re.sub(r'```json\n?|```', '', output_txt).strip()
                
                try:
                    data_llm = json.loads(output_txt)
                    hallazgo = {
                        "articulo_origen": id_articulo,
                        "tag_comercial": data_llm.get("tag_comercial", "[DESBLOQUEO_B2C]"),
                        "precio_sugerido": data_llm.get("precio_sugerido", "N/A"),
                        "resumen_solucion": data_llm.get("resumen_solucion", "N/A"),
                        "diagrama_mermaid": data_llm.get("diagrama_mermaid", "N/A")
                    }
                    resultados_finales.append(hallazgo)
                    # Guardado incremental para no perder progreso
                    with open(ARCHIVO_SALIDA, "w", encoding="utf-8") as f:
                        json.dump(resultados_finales, f, indent=4, ensure_ascii=False)
                    
                    # 🧘 PAUSA TÁCTICA: Dejar que la RAM respire
                    print("🧘 Pausa de 2s para estabilidad de RAM...")
                    time.sleep(2)
                    
                except Exception as e:
                    print(f"⚠️ Error parseando JSON del LLM para {id_articulo}: {e}")
                    
            except Exception as e:
                print(f"❌ Error en llamada LLM para {id_articulo}: {e}")

        print(f"\n✅ PROCESO COMPLETADO. Total hallazgos en '{ARCHIVO_SALIDA}': {len(resultados_finales)}")

    except Exception as e:
        print(f"❌ Error fatal en el motor v2.2: {e}")

if __name__ == "__main__":
    procesar_v2()
