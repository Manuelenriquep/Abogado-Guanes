import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# ==========================================
# CONFIGURACIÓN "ARAÑA GUANES"
# ==========================================
BASE_DIR = r"c:\AbogadoVirtual\01_Ingesta_Datos\datos_crudos\jurisdiccion_local"
MUNICIPALES = ["Floridablanca", "Bucaramanga", "Santander", "Piedecuesta"]
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
FAILURE_LOG = r"c:\AbogadoVirtual\99_Logs_y_Temporales\reporte_fallos_transparencia.txt"

# Palabras clave solicitadas
KEYWORDS = ["acuerdo", "resolución", "estatuto", "decreto"]

# Headers para el Sigilo (Anti-Ban)
HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9",
}

def inicializar_entorno():
    """Crea la estructura de carpetas necesaria"""
    for m in MUNICIPALES:
        ruta = os.path.join(BASE_DIR, m)
        if not os.path.exists(ruta):
            os.makedirs(ruta)
            print(f"📁 Carpeta creada: {ruta}")

def log_fallo(url, error_msg):
    """Registra fallos para acciones legales posteriores"""
    with open(FAILURE_LOG, "a", encoding="utf-8") as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] URL: {url} | ERROR: {error_msg}\n")

def descargar_archivo(url, destino):
    """Descarga un archivo (PDF u otro) de forma segura"""
    try:
        time.sleep(2) # Respeto al servidor
        res = requests.get(url, headers=HEADERS, stream=True, timeout=30, verify=False)
        if res.status_code == 200:
            nombre_archivo = os.path.basename(urlparse(url).path)
            if not nombre_archivo:
                nombre_archivo = f"descarga_{int(time.time())}.pdf"
            
            ruta_final = os.path.join(destino, nombre_archivo)
            with open(ruta_final, "wb") as f:
                for chunk in res.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"✅ Descargado: {nombre_archivo}")
        else:
            log_fallo(url, f"StatusCode {res.status_code}")
    except Exception as e:
        log_fallo(url, str(e))

def rastrear_municipio(municipio, urls):
    """Rastrea una lista de URLs para un municipio específico"""
    print(f"\n📡 INICIANDO RASTREO: {municipio}")
    destino = os.path.join(BASE_DIR, municipio)
    
    for url in urls:
        try:
            print(f"🔍 Escaneando: {url}...")
            time.sleep(2) # Sigilo
            res = requests.get(url, headers=HEADERS, timeout=30, verify=False)
            
            if res.status_code != 200:
                log_fallo(url, f"StatusCode {res.status_code}")
                continue

            soup = BeautifulSoup(res.text, "html.parser")
            enlaces = soup.find_all("a", href=True)
            
            hallazgos = 0
            for enlace in enlaces:
                href = enlace["href"]
                texto = enlace.get_text().lower()
                
                # Criterio de búsqueda: Keywords o Terminación .pdf
                cumple_keyword = any(k in texto for k in KEYWORDS)
                es_pdf = href.lower().endswith(".pdf")
                
                if cumple_keyword or es_pdf:
                    url_completa = urljoin(url, href)
                    descargar_archivo(url_completa, destino)
                    hallazgos += 1
            
            if hallazgos == 0:
                print(f"⚠️ No se encontraron documentos en: {url}")
                log_fallo(url, "Página vacía de documentos relevantes")
            else:
                print(f"✨ Se encontraron {hallazgos} documentos en esta sección.")

        except Exception as e:
            log_fallo(url, str(e))

if __name__ == "__main__":
    inicializar_entorno()
    
    # URLS TÁCTICAS - VERIFICADAS POR BÚSQUEDA
    TARGETS = {
        "Bucaramanga": [
            "https://www.bucaramanga.gov.co/transparencia/normatividad/leyes-y-decretos/",
            "https://concejodebucaramanga.gov.co/transparencia/normatividad/decretos-y-resoluciones/"
        ],
        "Floridablanca": [
            "https://www.floridablanca.gov.co/Transparencia/Paginas/POT.aspx",
            "https://concejomunicipalfloridablanca.gov.co/acuerdos/",
            "https://www.concejo-floridablanca-santander.gov.co/tema/normatividad",
            "https://portaltributario.floridablanca.gov.co/normatividad"
        ],
        "Santander": [
            "https://www.santander.gov.co/publicaciones/normatividad/"
        ],
        "Piedecuesta": [
            "https://www.alcaldiadepiedecuesta.gov.co/transparencia/normatividad/decretos",
            "https://www.alcaldiadepiedecuesta.gov.co/transparencia/normatividad/resoluciones",
            "https://concejopiedecuesta.gov.co/acuerdos",
            "https://concejopiedecuesta.gov.co/pot-plan-de-ordenamiento-territorial-2024"
        ]
    }
    
    print("🚀 ARAÑA GUANES v1.0 - RECOLECTOR DE LEY CLANDESTINA 🚀")
    
    # Por ahora el script queda listo, esperando las URLs tácticas del usuario
    for municipio, urls in TARGETS.items():
        if urls:
            rastrear_municipio(municipio, urls)
        else:
            print(f"⏩ Saltando {municipio} (Sin URLs configuradas)")
    
    print("\n🏁 OPERACIÓN FINALIZADA. Revisa 'reporte_fallos_transparencia.txt' si hay fallos.")
