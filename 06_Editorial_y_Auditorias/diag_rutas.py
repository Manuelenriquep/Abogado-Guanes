import os

ORIGEN = r"c:\AbogadoVirtual\01_Ingesta_Datos\biblioteca_completa"
DESTINO = "biblioteca_limpia"

print(f"CWD: {os.getcwd()}")
print(f"Existe origen? {os.path.exists(ORIGEN)}")
if os.path.exists(ORIGEN):
    archivos = [f for f in os.listdir(ORIGEN) if f.endswith('.md')]
    print(f"Archivos .md encontrados: {len(archivos)}")
    print(f"Lista: {archivos}")

print(f"Existe destino? {os.path.exists(DESTINO)}")
