import subprocess
import os
import datetime
import sys

# Rutas de los scripts a ejecutar diariamente
SCRIPT_CENTINELA = r"c:\AbogadoVirtual\02_Procesamiento_RAG\centinela_actualizaciones.py"
SCRIPT_INYECTOR = r"c:\AbogadoVirtual\01_Ingesta_Datos\inyector_diario_rag.py"
LOG_FILE = r"c:\AbogadoVirtual\99_Logs_y_Temporales\guanes_cronos.log"

def log(mensaje):
    """Guarda en log y muestra por consola con timestamp."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linea = f"[{timestamp}] {mensaje}"
    print(linea)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(linea + "\n")

def ejecutar_paso(ruta_script, descripcion_paso):
    """Ejecuta un script de Python usando el intérprete actual del sistema."""
    log(f"Iniciando: {descripcion_paso}")
    try:
        # Usa el mismo python que está corriendo este orquestador (py o python.exe)
        python_exe = sys.executable 
        base_dir = os.path.dirname(ruta_script)
        
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        
        resultado = subprocess.run(
            [python_exe, ruta_script], 
            cwd=base_dir, 
            capture_output=True, 
            text=True,
            encoding='utf-8',
            env=env
        )
        
        # Guardar stdout y stderr
        if resultado.stdout:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(f"\n--- Output {descripcion_paso} ---\n{resultado.stdout}\n")
                
        if resultado.returncode == 0:
            log(f"[SUCCESS] PASO COMPLETADO EXITOSAMENTE: {descripcion_paso}")
            return True
        else:
            log(f"[ERROR] FALLO en PASO: {descripcion_paso}")
            if resultado.stderr:
                log(f"Detalle del error:\n{resultado.stderr}")
            return False
            
    except Exception as e:
        log(f"[CRITICAL ERROR] ejecutando {descripcion_paso}: {e}")
        return False

def inicio_cronos():
    # Asegurar que exista la carpeta de logs
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    
    log("=========================================================")
    log("INICIANDO GUANES CRONOS - RUTINA PREVENTIVA DIARIA")
    log("=========================================================")
    
    # PASO 0: Asegurar Persistencia de Servicios (Puente y Túnel)
    SCRIPT_GUARDIAN = r"c:\AbogadoVirtual\00_ADMIN_TOOLS\guanes_guardian.py"
    ejecutar_paso(SCRIPT_GUARDIAN, "Guanes Guardián (Verificación de Servicios)")
    
    # PASO 1: Descargar, detectar cambios y limpiar con IA
    exito_centinela = ejecutar_paso(SCRIPT_CENTINELA, "Centinela de Actualizaciones (Web Scraping & RAG Cleanering)")
    
    # PASO 2: Inyectar datos limpios al cerebro local
    if exito_centinela:
        ejecutar_paso(SCRIPT_INYECTOR, "Inyector Diario RAG (Actualización de ChromaDB)")
        
        # PASO 3: Generar Feed de Noticias para el Frontend
        SCRIPT_FEED = r"c:\AbogadoVirtual\07_Cloud_Abogado\generar_feed_noticias.py"
        ejecutar_paso(SCRIPT_FEED, "Radar Guanes (Exportación Noticias a JSON)")
        
        # PASO 4: Generar el Dashboard/Auditoría OPML actualizado
        SCRIPT_OPML = r"c:\AbogadoVirtual\99_Logs_y_Temporales\generar_opml.py"
        ejecutar_paso(SCRIPT_OPML, "Dashboard Legal (Generación OPML y Vista HTML)")
    else:
        log("[WARN] ABORTANDO INYECCIÓN RAG debido a fallos críticos en el Centinela.")
        
    log("=========================================================")
    log("FINALIZADA OPERACIÓN GUANES CRONOS")
    log("=========================================================\n")


if __name__ == "__main__":
    inicio_cronos()
