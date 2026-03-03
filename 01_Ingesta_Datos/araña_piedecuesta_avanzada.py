import os
import requests
import urllib3
import time
from bs4 import BeautifulSoup
import re

# Desactivar advertencias SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ==========================================
# CONFIGURACIÓN TÁCTICA PIEDECUESTA
# ==========================================
DEST_DIR = r"c:\AbogadoVirtual\01_Ingesta_Datos\datos_crudos\jurisdiccion_local\Piedecuesta"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
}

# Configuramos adaptador para forzar compatibilidad SSL / Bypass simple
class TLSAdapter(requests.adapters.HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        ctx = urllib3.util.ssl_.create_urllib3_context()
        ctx.check_hostname = False
        ctx.verify_mode = 0
        ctx.options |= 0x4  # OP_LEGACY_SERVER_CONNECT en OpenSSL
        kwargs['ssl_context'] = ctx
        return super(TLSAdapter, self).init_poolmanager(*args, **kwargs)

def inicializar_entorno():
    if not os.path.exists(DEST_DIR):
        os.makedirs(DEST_DIR)

def descargar_pdf(url_pdf, nombre_base):
    try:
        session = requests.Session()
        session.mount('https://', TLSAdapter())
        
        print(f"  📥 Descargando: {nombre_base}.pdf ...")
        res = session.get(url_pdf, headers=HEADERS, verify=False, timeout=30)
        
        if res.status_code == 200 and 'pdf' in res.headers.get('Content-Type', '').lower():
            ruta = os.path.join(DEST_DIR, f"{nombre_base}.pdf")
            with open(ruta, "wb") as f:
                f.write(res.content)
            print("  ✅ Exitoso.")
            return True
        else:
            print(f"  ⚠️ No es un PDF válido o fallo status: {res.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ Fallo descarga: {e}")
        return False

def raspar_con_fuerza():
    inicializar_entorno()
    session = requests.Session()
    session.mount('https://', TLSAdapter())
    
    url_pot = "https://concejopiedecuesta.gov.co/pot-plan-de-ordenamiento-territorial-2024"
    url_acuerdos = "https://concejopiedecuesta.gov.co/acuerdos"
    
    urls_a_raspar = [url_pot, url_acuerdos]
    
    total_descargas = 0
    
    for url in urls_a_raspar:
        print(f"\n📡 Rastreando sitio blindado: {url}")
        try:
            res = session.get(url, headers=HEADERS, verify=False, timeout=30)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")
                
                # Buscar todo enlace que sospechosamente sea un PDF o contenga palabras clave
                enlaces = soup.find_all("a", href=True)
                for enlace in enlaces:
                    href = enlace["href"]
                    texto = enlace.get_text().strip().replace("/", "_").replace("\\", "_")
                    
                    if not texto:
                        texto = "Documento_Piedecuesta_" + str(int(time.time()))
                    
                    if href.lower().endswith('.pdf') or 'drive.google.com' in href.lower() or 'descargar' in href.lower():
                        # Si es un enlace relativo lo hacemos absoluto
                        if href.startswith("/"):
                            href = "https://concejopiedecuesta.gov.co" + href
                            
                        # Si es google drive, omitimos por ahora a menos que sea directo
                        if 'drive.google.com' in href:
                            print(f"  ⚠️ Enlace a Google Drive interceptado (requiere parseo manual): {href}")
                            continue

                        if descargar_pdf(href, texto[:50]):
                            total_descargas += 1
            else:
                print(f"❌ Error de red: {res.status_code}")
        except Exception as e:
            print(f"❌ Excepción crítica de red: {e}")
            
    print(f"\n🏁 Total capturado por la Araña Especial: {total_descargas} PDFs")

if __name__ == "__main__":
    raspar_con_fuerza()
