import os

folder = r"c:\AbogadoVirtual\libro_guanes\manuscritos"
output_dir = r"c:\AbogadoVirtual\libro_guanes\procesados"
archivos = sorted([f for f in os.listdir(folder) if f.endswith(".md") and "_" in f and not f.startswith("Libro_Completo")])

with open(os.path.join(output_dir, "Libro_Limpio.md"), "w", encoding="utf-8") as outfile:
    for filename in archivos:
        with open(os.path.join(folder, filename), "r", encoding="utf-8", errors="ignore") as infile:
            content = infile.read()
            # Limpieza básica de saltos de línea extra y caracteres raros
            outfile.write(f"\n\n# {filename}\n\n") # Esto ayuda a identificar dónde empieza cada cap
            outfile.write(content)
            outfile.write("\n\n---\n\n")

print("¡Archivo Libro_Limpio.md generado con codificación UTF-8 correcta!")