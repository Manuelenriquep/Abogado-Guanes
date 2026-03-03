import os
import re
import json

def extraer_referencias_jurisprudenciales():
    try:
        print("🚀 INICIANDO EXTRACCIÓN DE JURISPRUDENCIA...")
        ruta_libros = r"c:\AbogadoVirtual\01_Ingesta_Datos\biblioteca_completa"
        
        if not os.path.exists(ruta_libros):
            print(f"❌ No se encontró la carpeta '{ruta_libros}'.")
            return

        # Patrón para detectar Sentencias de la Corte Constitucional (C, T, SU)
        patron_sentencias = r"(Sentencia\s+[C|T|SU|A|C|STC|SL|SP|CE|SC|SU]-\d{3}\s+de\s+\d{4})"
        
        referencias_encontradas = {}

        print("🔍 Escaneando biblioteca en busca de jurisprudencia citada...")

        archivos = [f for f in os.listdir(ruta_libros) if f.endswith('.md')]
        
        for archivo in archivos:
            try:
                with open(os.path.join(ruta_libros, archivo), 'r', encoding='utf-8') as f:
                    contenido = f.read()
                    citas = re.findall(patron_sentencias, contenido, re.IGNORECASE)
                    
                    if citas:
                        # Limpiar y quitar duplicados por ley
                        referencias_encontradas[archivo] = list(set(citas))
                        print(f"   📍 {archivo}: {len(referencias_encontradas[archivo])} sentencias detectadas.")
            except Exception as e:
                print(f"   ❌ Error leyendo archivo {archivo}: {e}")

        # Guardar la lista de "compras" de jurisprudencia
        with open('mapa_jurisprudencia.json', 'w', encoding='utf-8') as f:
            json.dump(referencias_encontradas, f, indent=4, ensure_ascii=False)
        
        print("\n✅ FINALIZADO: Mapa de jurisprudencia creado.")
    except Exception as e:
        print(f"❌ Error fatal en el extractor: {e}")

if __name__ == "__main__":
    extraer_referencias_jurisprudenciales()