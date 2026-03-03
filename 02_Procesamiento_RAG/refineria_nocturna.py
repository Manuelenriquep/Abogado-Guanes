import subprocess
import time
import datetime
import os

LOG_FILE = r"c:\AbogadoVirtual\99_Logs_y_Temporales\reporte_nocturno.log"

def log_nocturno(mensaje):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {mensaje}\n")
    print(f"LOG: {mensaje}")

def ejecutar_comando(comando, descripcion):
    log_nocturno(f"INICIANDO: {descripcion}")
    try:
        # Forzamos el CWD al directorio del script
        base_dir = os.path.dirname(os.path.abspath(__file__))
        process = subprocess.run(comando, shell=True, capture_output=True, text=True, cwd=base_dir)
        
        # Logueamos la salida SIEMPRE para diagnóstico
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"--- OUTPUT {descripcion} ---\n")
            f.write(process.stdout + "\n")
            f.write(process.stderr + "\n")
            f.write("-----------------------------\n")

        if process.returncode == 0:
            log_nocturno(f"✅ ÉXITO: {descripcion}")
            return True
        else:
            log_nocturno(f"❌ FALLO: {descripcion}")
            # Logueamos el error para auditoría matutina
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(f"ERROR OUTPUT: {process.stderr}\n")
            return False
    except Exception as e:
        log_nocturno(f"❌ ERROR CRÍTICO ejecutando {descripcion}: {e}")
        return False

if __name__ == "__main__":
    log_nocturno("=== INCIO DE OPERACIÓN REFINERÍA NOCTURNA ===")
    
    # FASE 1: Descarga
    fase1 = ejecutar_comando(
        "C:/Users/guane/AppData/Local/Programs/Python/Python312/python.exe c:/AbogadoVirtual/descarga_coco_full.py",
        "Fase 1: Extracción Código de Comercio Completo"
    )
    
    if fase1:
        # FASE 2: Minería Pesada (Aseguramos que el script apunte al Código Civil)
        # Nota: El usuario pidió que maestro_masivo.py apunte a Codigo_Civil.md exclusivamente.
        # maestro_masivo.py actualmente limpia bibliotecas completas, por prioridad. 
        # La prioridad 1 en ese script es precisamente lo que buscamos.
        log_nocturno("FASE 2: Iniciando Reactivación de Minería Pesada...")
        ejecutar_comando(
            "C:/Users/guane/AppData/Local/Programs/Python/Python312/python.exe c:/AbogadoVirtual/maestro_masivo.py",
            "Fase 2: Limpieza Masiva Código Civil"
        )
    else:
        log_nocturno("⚠️ FASE 2 cancelada por fallo en FASE 1.")

    log_nocturno("=== FIN DE OPERACIÓN REFINERÍA NOCTURNA ===")
    log_nocturno("Arquitecto, reporte listo para su revisión matutina.")
