import os
import glob
import json
import re
from datetime import datetime

DIR_ALERTAS = r"c:\AbogadoVirtual\Alertas_Negocio"
DIR_FRONTEND = r"c:\AbogadoVirtual\07_Cloud_Abogado\js"
ARCHIVO_JSON = os.path.join(DIR_FRONTEND, "noticias.json")

def extraer_seccion(texto, cabecera):
    """Extrae el contenido debajo de una cabecera de markdown hasta la siguiente cabecera."""
    # Buscar la cabecera (ignorando case y posibles variaciones menores)
    patron = re.compile(rf"###\s*\d*\.?\s*{cabecera}.*?\n(.*?)((?=\n###)|$)", re.IGNORECASE | re.DOTALL)
    match = patron.search(texto)
    if match:
        contenido = match.group(1).strip()
        # Limpiar saltos de linea extra
        return " ".join(contenido.split())
    return "Información técnica en procesamiento."

def generar_feed():
    print("📰 Iniciando Generador de Radar Guanes...")
    
    if not os.path.exists(DIR_FRONTEND):
        os.makedirs(DIR_FRONTEND)
        
    archivos_md = glob.glob(os.path.join(DIR_ALERTAS, "*.md"))
    
    # Ordenar por fecha de modificación (los más recientes primero)
    archivos_md.sort(key=os.path.getmtime, reverse=True)
    
    noticias = []
    
    # Tomar los 4 más recientes
    for ruta in archivos_md[:4]:
        try:
            nombre_archivo = os.path.basename(ruta)
            # Extraer fecha y titulo de 'Oportunidad_Ley_100_2026_03_01.md'
            partes = nombre_archivo.replace("Oportunidad_", "").replace(".md", "").split("_")
            
            # Asumiendo que las ultimas 3 partes son Año_Mes_Dia
            if len(partes) >= 4:
                fecha_str = f"{partes[-3]}-{partes[-2]}-{partes[-1]}"
                titulo_ley = " ".join(partes[:-3]).replace("_", " ")
            else:
                fecha_str = datetime.fromtimestamp(os.path.getmtime(ruta)).strftime("%Y-%m-%d")
                titulo_ley = nombre_archivo.replace("Oportunidad_", "").replace(".md", "")
            
            with open(ruta, 'r', encoding='utf-8') as f:
                contenido = f.read()
                
            impacto = extraer_seccion(contenido, "IMPACTO JURÍDICO")
            oportunidad = extraer_seccion(contenido, "COPY PARA MARKETING")
            
            # Si el impacto es muy largo, cortarlo
            if len(impacto) > 150:
                impacto = impacto[:147] + "..."
                
            noticias.append({
                "id": nombre_archivo,
                "fecha": fecha_str,
                "titulo": f"Alerta Normativa: {titulo_ley}",
                "impacto": impacto,
                "accion": oportunidad
            })
            
            print(f"   ✅ Extraída {titulo_ley}")
            
        except Exception as e:
            print(f"   ❌ Error parseando {ruta}: {e}")

    # Si no hay noticias, ponemos unas por defecto
    if not noticias:
        print("   ⚠️ No hay alertas en la carpeta. Generando Mockups de autoridad.")
        noticias = [
            {
                "id": "mock_1",
                "fecha": datetime.now().strftime("%Y-%m-%d"),
                "titulo": "Auditoría Inteligente: Ley 675",
                "impacto": "Guanes IA analiza constantemente actas y asambleas para garantizar el blindaje legal en Propiedad Horizontal.",
                "accion": "🔒 Asegure hoy su Propiedad Horizontal con una revisión gratuita de su reglamento en Guanes IA."
            },
               {
                "id": "mock_2",
                "fecha": datetime.now().strftime("%Y-%m-%d"),
                "titulo": "Alerta: Decreto 768 (Airbnb)",
                "impacto": "El sistema detectó modificaciones en la regulación turística inmobiliaria.",
                "accion": "🏢 ¿Renta su apartamento por días? Conozca los riesgos y evite multas consultando ahora gratis."
            }
        ]

    try:
        with open(ARCHIVO_JSON, 'w', encoding='utf-8') as f:
            json.dump(noticias, f, ensure_ascii=False, indent=4)
        print(f"✅ Feed JSON guardado en: {ARCHIVO_JSON}")
    except Exception as e:
         print(f"❌ Error guardando el JSON: {e}")

if __name__ == "__main__":
    generar_feed()
