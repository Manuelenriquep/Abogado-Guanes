import os
import re
import subprocess
import glob

# Rutas de entrada y salida
directorio_backups = r"c:\AbogadoVirtual\06_Editorial_y_Auditorias\libro_guanes\procesados"
archivo_salida_md = r"c:\AbogadoVirtual\06_Editorial_y_Auditorias\libro_guanes\epub_output\Libro_Limpio.md"
archivo_salida_epub = r"c:\AbogadoVirtual\06_Editorial_y_Auditorias\libro_guanes\epub_output\Libro_Codigo_y_Confianza.epub"

def limpiar_texto(texto):
    """
    Limpia el texto de artefactos residuales de generación de IA
    y bloques de código de markdown.
    """
    # Eliminar bloques xml tipo <think>...</think> si existen
    texto = re.sub(r'<think>.*?</think>', '', texto, flags=re.DOTALL)
    
    # Remover las etiquetas de código markdown de inicio y fin si el texto completo está en uno solo
    # o si las usó la IA para envolver la respuesta
    texto = re.sub(r'^```[a-zA-Z]*\n', '', texto, flags=re.MULTILINE)
    texto = re.sub(r'^```\s*$', '', texto, flags=re.MULTILINE)

    # Remover líneas separadoras (---) que Pandoc confunde con bloques YAML de metadatos
    texto = re.sub(r'^\s*---\s*$', '', texto, flags=re.MULTILINE)
    
    # Remover dobles espacios en blanco excesivos y líneas en blanco excesivas
    texto = re.sub(r'\n{3,}', '\n\n', texto)
    
    # Limpiamos espacios en blanco al inicio o al final
    return texto.strip()

def procesar_capitulos():
    # Obtener y ordenar los archivos .md en la carpeta de backups
    archivos = sorted(glob.glob(os.path.join(directorio_backups, "*.md")))

    if not archivos:
        print("[Error] No se encontraron archivos .md en la carpeta de backups.")
        return

    texto_completo = ""

    print("[Info] Procesando los siguientes capitulos:")
    for archivo in archivos:
        nombre_base = os.path.basename(archivo)
        print(f"   - {nombre_base}")
        with open(archivo, "r", encoding="utf-8", errors="ignore") as f:
            contenido = f.read()
            contenido_limpio = limpiar_texto(contenido)
            # Agregar un salto de página (opcional, pandoc lo maneja con los H1 # y ##) y el contenido
            # Por consistencia, aseguramos que siempre haya dos saltos de línea entre capítulos
            texto_completo += contenido_limpio + "\n\n\n"

    print("---")
    print(f"[Info] Guardando libro unificado limpio en: {archivo_salida_md}")
    with open(archivo_salida_md, "w", encoding="utf-8") as f:
        f.write(texto_completo)

    print("[Info] Generando EPUB con Pandoc...")
    # Llamar a pandoc
    # -o especifica el output
    # --toc genera una tabla de continidos
    comando = [
        "pandoc", 
        archivo_salida_md, 
        "-o", archivo_salida_epub,
        "--metadata", "title=El Impuesto de la Desconfianza",
        "--metadata", "author=Diego Guanes",
        "--toc",
        "--split-level=1"
    ]
    
    try:
        resultado = subprocess.run(comando, check=True, capture_output=True, text=True)
        if os.path.exists(archivo_salida_epub):
            print(f"[OK] El libro EPUB se ha generado correctamente en:")
            print(f"-> {archivo_salida_epub}")
        else:
            print("[Advertencia] El comando parecio ejecutarse sin errores, pero el archivo EPUB no se encontro.")
    except subprocess.CalledProcessError as e:
        print("[Error] Error al ejecutar Pandoc:")
        print(e.stderr)

if __name__ == "__main__":
    procesar_capitulos()
