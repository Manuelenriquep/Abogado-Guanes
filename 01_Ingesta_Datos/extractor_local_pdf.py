import os
import pdfplumber
import time

# ==========================================
# CONFIGURACIÓN "EXTRACTOR UNIVERSAL V2"
# ==========================================
CONFIGURACIONES = [
    {
        "origen": r"c:\AbogadoVirtual\01_Ingesta_Datos\datos_crudos\jurisdiccion_local",
        "destino": r"c:\AbogadoVirtual\01_Ingesta_Datos\biblioteca_completa\jurisdiccion_local_textos"
    },
    {
        "origen": r"c:\AbogadoVirtual\01_Ingesta_Datos\ingesta_salud",
        "destino": r"c:\AbogadoVirtual\01_Ingesta_Datos\biblioteca_completa\salud_textos"
    }
]

def inicializar_entorno():
    """Crea la estructura de origen y salida si no existe"""
    for config in CONFIGURACIONES:
        if not os.path.exists(config["origen"]):
            os.makedirs(config["origen"])
            print(f"📁 Carpeta de origen creada: {config['origen']}")
        if not os.path.exists(config["destino"]):
            os.makedirs(config["destino"])
            print(f"📁 Carpeta de destino creada: {config['destino']}")

def convertir_pdf_a_markdown(ruta_pdf, nombre_salida, dest_dir):
    """Extrae texto de PDF y lo guarda como Markdown ligero"""
    try:
        texto_completo = f"# DOCUMENTO LOCAL: {nombre_salida}\n\n"
        
        with pdfplumber.open(ruta_pdf) as pdf:
            for i, pagina in enumerate(pdf.pages):
                texto_pag = pagina.extract_text()
                if texto_pag:
                    texto_completo += f"## Página {i+1}\n\n{texto_pag}\n\n"
        
        ruta_salida = os.path.join(dest_dir, f"{nombre_salida}.md")
        with open(ruta_salida, "w", encoding="utf-8") as f:
            f.write(texto_completo)
        
        return True
    except Exception as e:
        print(f"❌ Error convirtiendo {nombre_salida}: {e}")
        return False

def procesar_bibliotecas():
    """Recorre todas las configuraciones para extraer texto"""
    inicializar_entorno()
    
    total_procesados = 0
    
    for config in CONFIGURACIONES:
        base_dir = config["origen"]
        dest_dir = config["destino"]
        
        print(f"\n📡 Escaneando directorio: {base_dir}")
        for root, dirs, files in os.walk(base_dir):
            for file in files:
                if file.lower().endswith(".pdf"):
                    ruta_pdf = os.path.join(root, file)
                    carpeta_padre = os.path.basename(root)
                    nombre_base = os.path.splitext(file)[0]
                    
                    # Evitar nombres redundantes si la carpeta padre es el mismo origen
                    if base_dir.endswith(carpeta_padre):
                        nombre_id = nombre_base
                    else:
                        nombre_id = f"{carpeta_padre}_{nombre_base}"
                    
                    # Limpiamos nombre de espacios
                    nombre_id = nombre_id.replace(" ", "_")
                    
                    print(f"  📄 Procesando: {nombre_id}...")
                    if convertir_pdf_a_markdown(ruta_pdf, nombre_id, dest_dir):
                        total_procesados += 1

    print(f"\n✨ EXTRACCIÓN MASIVA COMPLETADA.")
    print(f"📊 Total archivos convertidos a 'Oro Markdown': {total_procesados}")

if __name__ == "__main__":
    print("🚀 EXTRACTOR UNIVERSAL PDF v2.0 - PREPARANDO EL ORO LEGAL 🚀")
    procesar_bibliotecas()
