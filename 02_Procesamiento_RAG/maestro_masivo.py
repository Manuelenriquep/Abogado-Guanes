import ollama
import os
import time
import re

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
# 2. CONFIGURACIÓN DE DIRECTORIOS
# ==========================================
CARPETA_ORIGEN = r"c:\AbogadoVirtual\01_Ingesta_Datos\biblioteca_completa"
CARPETA_DESTINO = "biblioteca_limpia"
TAMANO_BLOQUE = 8000

def limpiar_con_qwen_local(texto_completo, nombre_archivo):
    """Procesa el texto por bloques usando Ollama con la configuración de Guanes"""
    try:
        print(f"   [AI] Qwen limpiando: {nombre_archivo}...")
        
        # Dividimos el texto en bloques para no saturar la memoria
        bloques = [texto_completo[i:i+TAMANO_BLOQUE] for i in range(0, len(texto_completo), TAMANO_BLOQUE)]
        
        resultado_final = ""
        
        for i, bloque in enumerate(bloques):
            try:
                print(f"      [INFO] Bloque {i+1}/{len(bloques)}...")
                
                respuesta = ollama.chat(
                    model='qwen3:8b', 
                    messages=[
                        {'role': 'system', 'content': PROMPT_GUANES},
                        {'role': 'user', 'content': bloque}
                    ],
                    options={
                        "num_ctx": 4096,
                        "temperature": 0.0
                    }
                )
                
                resultado_final += respuesta['message']['content'] + "\n\n"
                
            except Exception as e:
                print(f"      [ERROR] Bloque {i+1}: {e}")
                # En caso de error, mantenemos el texto original para no perder datos
                resultado_final += bloque + "\n\n"
                
        return resultado_final
    except Exception as e:
        print(f"   [ERROR FATAL] procesando bloques de {nombre_archivo}: {e}")
        return texto_completo

def ejecutar_procesamiento_batch():
    """Motor principal: Escanea, prioriza y procesa archivos locales"""
    try:
        print("\n[START] INICIANDO OPERACIÓN LIMPIEZA PRIORIZADA - GUANES LEGAL TECH")
        
        # Regex de Dolor para priorización
        KEYWORDS_DOLOR = r'multa|sanción|desalojo|embargo|captura|infracción|policía'
        
        # Asegurar que las carpetas existan
        if not os.path.exists(CARPETA_ORIGEN):
            print(f"[ERROR] La carpeta de origen '{CARPETA_ORIGEN}' no existe.")
            return
            
        if not os.path.exists(CARPETA_DESTINO):
            os.makedirs(CARPETA_DESTINO)
            print(f"[DIR] Carpeta de destino '{CARPETA_DESTINO}' creada.")

        # Obtener lista de archivos Markdown
        # CONFIGURACIÓN NOCTURNA: Solo procesamos el Código Civil hoy
        todos_archivos = ['Codigo_Civil.md'] if 'Codigo_Civil.md' in os.listdir(CARPETA_ORIGEN) else []
        
        if not todos_archivos:
            print(f"[SKIP] No se encontró Codigo_Civil.md en '{CARPETA_ORIGEN}'.")
            return

        # --- FASE DE PRIORIZACIÓN ---
        print("[SCAN] Escaneando prioridades (Termómetro de Dolor)...")
        prioritarios = []
        secundarios = []

        for archivo in todos_archivos:
            # Si ya existe en destino, lo ignoramos de ambas listas
            if os.path.exists(os.path.join(CARPETA_DESTINO, archivo)):
                continue

            ruta = os.path.join(CARPETA_ORIGEN, archivo)
            with open(ruta, 'r', encoding='utf-8') as f:
                # Leemos solo una parte para detectar palabras clave rápido
                inicio_texto = f.read(50000) 
                if re.search(KEYWORDS_DOLOR, inicio_texto, re.IGNORECASE):
                    prioritarios.append(archivo)
                else:
                    secundarios.append(archivo)

        lista_final = prioritarios + secundarios
        
        print(f"[TOTAL] Total a procesar: {len(lista_final)}")
        print(f"[PRIORITY 1] (Urgencia): {len(prioritarios)}")
        print(f"[PRIORITY 2] (Estándar): {len(secundarios)}\n")

        for archivo in lista_final:
            ruta_entrada = os.path.join(CARPETA_ORIGEN, archivo)
            ruta_salida = os.path.join(CARPETA_DESTINO, archivo)
            
            es_prioridad = "[PRIORIDAD 1]" if archivo in prioritarios else "[PRIORIDAD 2]"

            try:
                print(f"[PROCESS] Procesando {es_prioridad}: {archivo}...")
                
                with open(ruta_entrada, 'r', encoding='utf-8') as f:
                    contenido_sucio = f.read()

                if not contenido_sucio.strip():
                    print(f"[WARN] El archivo {archivo} está vacío. Saltando.")
                    continue

                contenido_limpio = limpiar_con_qwen_local(contenido_sucio, archivo)
                
                with open(ruta_salida, 'w', encoding='utf-8') as f:
                    f.write(contenido_limpio)
                
                print(f"[OK] Finalizado: {archivo}")

            except Exception as e:
                print(f"[ERROR] Error procesando {archivo}: {e}")
                print("[SKIP] Continuando con el siguiente archivo...")

        print("\n[DONE] OPERACIÓN LIMPIEZA PRIORIZADA COMPLETADA.")
        
    except Exception as e:
        print(f"[ERROR] Error crítico en el motor: {e}")

if __name__ == "__main__":
    ejecutar_procesamiento_batch()
