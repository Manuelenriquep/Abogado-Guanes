import requests
from bs4 import BeautifulSoup
import os
import datetime

# ==========================================
# CONFIGURACIÓN: EXTRACCIÓN COCO FULL
# ==========================================
# Función Pública es más robusto para scraping directo que los frames de Senado
URL_FUN_PUB = "https://www.funcionpublica.gov.co/eva/gestornormativo/norma_pdf.php?i=41102"
ARCHIVO_SALIDA = r"c:\AbogadoVirtual\01_Ingesta_Datos\biblioteca_completa\Codigo_de_Comercio_Completo.md"

def log_nocturno(mensaje):
    with open(r"c:\AbogadoVirtual\99_Logs_y_Temporales\reporte_nocturno.log", "a", encoding="utf-8") as f:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {mensaje}\n")
    print(f"LOG: {mensaje}")

def descargar_codigo_completo():
    log_nocturno("FASE 1: Iniciando descarga del Código de Comercio (Versión Función Pública PDF)...")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }
    
    try:
        import pdfplumber
        from io import BytesIO
        
        # Descargar el PDF directamente
        res = requests.get(URL_FUN_PUB, headers=headers, verify=False, timeout=60)
        res.raise_for_status()
        
        log_nocturno("FASE 1: PDF descargado. Iniciando extracción de texto...")
        
        with pdfplumber.open(BytesIO(res.content)) as pdf:
            texto_completo = ""
            for pagina in pdf.pages:
                texto_completo += pagina.extract_text() + "\n"
        
        dir_completa = r"c:\AbogadoVirtual\01_Ingesta_Datos\biblioteca_completa"
        if not os.path.exists(dir_completa):
            os.makedirs(dir_completa)
            
        with open(ARCHIVO_SALIDA, "w", encoding="utf-8") as f:
            f.write(f"# CÓDIGO DE COMERCIO DE COLOMBIA (FULL)\n")
            f.write(f"Fuente: {URL_FUN_PUB}\n")
            f.write(texto_completo)
            
        log_nocturno(f"FASE 1: Completada. {len(texto_completo)} caracteres extraídos.")
        return True
    except Exception as e:
        log_nocturno(f"❌ FASE 1: Error crítico: {e}")
        return False

if __name__ == "__main__":
    descargar_codigo_completo()
