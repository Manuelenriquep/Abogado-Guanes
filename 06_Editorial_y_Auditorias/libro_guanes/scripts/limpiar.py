import os

# 1. Definimos el diccionario de traducción (Mojibake a Español)
traducciones = {
    'Ã¡': 'á', 'Ã©': 'é', 'Ã­': 'í', 'Ã³': 'ó', 'Ãº': 'ú',
    'Ã±': 'ñ', 'Ã ': 'Á', 'Ã‰': 'É', 'Ã ': 'Í', 'Ã“': 'Ó',
    'Ãš': 'Ú', 'Ã‘': 'Ñ'
}

# 2. Leemos todos los archivos .md en orden
input_dir = r"c:\AbogadoVirtual\libro_guanes\manuscritos"
output_dir = r"c:\AbogadoVirtual\libro_guanes\procesados"
archivos = sorted([f for f in os.listdir(input_dir) if f.endswith('.md') and '_' in f])

with open(os.path.join(output_dir, "Libro_Final_Limpio.md"), "w", encoding="utf-8") as salida:
    for nombre in archivos:
        with open(os.path.join(input_dir, nombre), "r", encoding="utf-8", errors="ignore") as entrada:
            texto = entrada.read()
            # Aplicamos la traducción
            for roto, sano in traducciones.items():
                texto = texto.replace(roto, sano)
            salida.write(texto + "\n\n")

print("✅ Archivo 'Libro_Final_Limpio.md' creado con éxito y sin letras raras.")