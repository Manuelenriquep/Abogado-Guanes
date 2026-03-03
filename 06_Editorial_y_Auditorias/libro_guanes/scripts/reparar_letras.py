import os

def reparar_encoding(texto):
    # Diccionario de reparaciones comunes de Mojibake
    reparaciones = {
        'Ã¡': 'á', 'Ã©': 'é', 'Ã­': 'í', 'Ã³': 'ó', 'Ãº': 'ú',
        'Ã±': 'ñ', 'Ã ': 'Á', 'Ã‰': 'É', 'Ã ': 'Í', 'Ã“': 'Ó',
        'Ãš': 'Ú', 'Ã‘': 'Ñ', 'â€œ': '"', 'â€\x9d': '"', 'â€™': "'"
    }
    for roto, sano in reparaciones.items():
        texto = texto.replace(roto, sano)
    return texto

folder = r"c:\AbogadoVirtual\06_Editorial_y_Auditorias\libro_guanes\manuscritos"
output_dir = r"c:\AbogadoVirtual\06_Editorial_y_Auditorias\libro_guanes\procesados"
archivos_md = [f for f in os.listdir(folder) if f.endswith(".md")]

for nombre in archivos_md:
    with open(os.path.join(folder, nombre), 'r', encoding='utf-8', errors='ignore') as f:
        contenido = f.read()
    
    contenido_reparado = reparar_encoding(contenido)
    
    with open(os.path.join(output_dir, nombre), 'w', encoding='utf-8') as f:
        f.write(contenido_reparado)

print("¡Proceso de des-mojibake completado en todos los archivos!")