import requests
from bs4 import BeautifulSoup
import os
import pandas as pd
import hashlib
import time
import difflib
import ollama
from datetime import datetime
# Importamos la función pesada de tu otro script para no repetir código
try:
    from maestro_masivo import limpiar_con_qwen_local
except Exception as e:
    print(f"[ERROR] Error importando maestro_masivo: {e}")

# ==========================================
# 1. EL ADN GUANES (MANIFIESTO DEL SISTEMA)
# ==========================================
PROMPT_GUANES = """Eres el Consultor Senior de Guanes IA, el ecosistema legaltech líder en Colombia (2026). Tu conocimiento no proviene de internet genérico, sino de la "Biblioteca Privada de Guanes Legaltech": 229 fuentes curadas por el Abogado Manuel Enrique Prada Forero.

REGLAS DE ORO:
1. PRIORIDAD NORMATIVA: Usa estrictamente Ley 675/2001, Decretos 768 y 1166 de 2025 (Inmobiliario), Resolución ANM 3824/2025 (Minero) y Códigos vigentes a Marzo 2026.
2. LENGUAJE DEL RESPIRO: Responde con empatía, claridad y un tono profesional que brinde tranquilidad ("Un respiro para su seguridad jurídica").
3. PRIVACIDAD: No menciones datos técnicos como RAG o APIs. Todo el procesamiento es local y soberano.
4. CIERRE DE AUTORIDAD: Al final de cada respuesta gratuita (<15 consultas), incluye: "Información extraída de nuestra fuente de verdad blindada. Para documentos oficiales listos para radicar, active su acceso premium."

INSTRUCCIÓN DE ANÁLISIS:
- Si el usuario sube un documento (plano, minuta, requerimiento ANM), analízalo paso a paso identificando Red Flags y riesgos de demandas.
- Nunca inventes leyes. Si falta información para un blindaje total, indícalo claramente."""

CARPETA_HASHES = "registro_huellas"
CARPETA_BIBLIOTECA = r"c:\AbogadoVirtual\01_Ingesta_Datos\biblioteca_completa"
CARPETA_ALERTAS = "Alertas_Negocio"

def obtener_huella_digital(texto):
    """Crea un código único basado en el contenido del texto."""
    return hashlib.md5(texto.encode('utf-8')).hexdigest()

def analizar_oportunidad_negocio(texto_viejo, texto_nuevo, nombre_ley):
    print(f"   [INFO] Analizando oportunidades de negocio en {nombre_ley}...")
    
    try:
        # 1. Encontrar exactamente qué líneas cambiaron
        lineas_viejas = texto_viejo.splitlines()
        lineas_nuevas = texto_nuevo.splitlines()
        diff = difflib.unified_diff(lineas_viejas, lineas_nuevas, lineterm='')
        cambios = '\n'.join(list(diff))
        
        # Si el cambio es solo de formato web, lo ignoramos
        if len(cambios.strip()) < 10:
            print("   [SKIP] Cambios menores, no amerita reporte de negocio.")
            return
            
        # 2. El Prompt de "Socio de Negocios" para Qwen 3
        prompt = f"""El Congreso de Colombia acaba de modificar la ley: {nombre_ley}.
        
        Aquí están los cambios exactos (las líneas con '+' son nuevas, las '-' se eliminaron):
        {cambios[:8000]}
        
        Genera un REPORTE DE INTELIGENCIA ESTRATÉGICA con esta estructura:
        
        ### 1. IMPACTO JURÍDICO (En lenguaje sencillo)
        ¿Qué cambió exactamente y a qué sector de la población afecta?
        
        ### 2. OPORTUNIDAD DE MONETIZACIÓN 💰
        ¿Qué nuevo producto podemos crear hoy mismo para abogado.guanes.biz o Amazon? 
        (Ej: Un formato de contrato actualizado, un ebook explicativo, un servicio de revisión de multas).
        
        ### 3. COPY PARA MARKETING (Gancho)
        Escribe un post de 3 líneas para redes sociales alertando sobre este cambio e invitando a comprar nuestra solución.
        """

        res = ollama.chat(
            model='qwen3:8b', 
            messages=[
                {'role': 'system', 'content': PROMPT_GUANES},
                {'role': 'user', 'content': prompt}
            ],
            options={
                "num_ctx": 4096,
                "temperature": 0.0
            }
        )
        reporte = res['message']['content']
        
        # 3. Guardar el reporte en tu escritorio de trabajo
        if not os.path.exists(CARPETA_ALERTAS): os.makedirs(CARPETA_ALERTAS)
        fecha = datetime.now().strftime("%Y_%m_%d")
        
        with open(f"{CARPETA_ALERTAS}/Oportunidad_{nombre_ley}_{fecha}.md", "w", encoding="utf-8") as f:
            f.write(reporte)
            
        print(f"   [SUCCESS] ¡Nueva oportunidad de negocio guardada en {CARPETA_ALERTAS}!")
        
    except Exception as e:
        print(f"   [ERROR] Error al analizar oportunidad de negocio: {e}")

def revisar_actualizaciones():
    try:
        if not os.path.exists(CARPETA_HASHES): os.makedirs(CARPETA_HASHES)
        if not os.path.exists(CARPETA_BIBLIOTECA): os.makedirs(CARPETA_BIBLIOTECA)
        
        ruta_csv = r"c:\AbogadoVirtual\01_Ingesta_Datos\lista_codigos.csv"
        
        if not os.path.exists(ruta_csv):
            print(f"[ERROR] No se encontró '{ruta_csv}'.")
            return

        df = pd.read_csv(ruta_csv)
        print("[START] Iniciando el Centinela de Actualizaciones Jurídicas...")
        
        for index, row in df.iterrows():
            nombre = row['Nombre']
            url = row['URL']
            archivo_hash = os.path.join(CARPETA_HASHES, f"{nombre}.hash")
            archivo_md = os.path.join(CARPETA_BIBLIOTECA, f"{nombre}.md")
            
            print(f"\n[SEARCH] Verificando: {nombre}...")
            try:
                # 1. Descarga rápida (sin IA, solo texto crudo)
                r = requests.get(url, timeout=30)
                r.raise_for_status()
                r.encoding = 'utf-8'
                soup = BeautifulSoup(r.text, 'lxml')
                
                for tag in soup(['script', 'style', 'nav', 'header', 'footer']):
                    tag.decompose()
                    
                texto_sucio = (soup.find('div', {'id': 'Contenido'}) or soup.body).get_text(separator=' ')
                
                # 2. Calcular huella actual
                huella_actual = obtener_huella_digital(texto_sucio)
                
                # 3. Comparar con la huella guardada
                huella_guardada = ""
                if os.path.exists(archivo_hash):
                    with open(archivo_hash, 'r') as f:
                        huella_guardada = f.read().strip()
                
                if huella_actual == huella_guardada:
                    print(f"   [SKIP] Sin cambios. La huella coincide. Pasando al siguiente.")
                    continue 
                    
                # 4. SI HAY CAMBIOS (o es un archivo nuevo)
                print(f"   [WARN] ¡ATENCIÓN! Se detectaron cambios. Despertando a Qwen...")
                
                # PASO CLAVE: Leemos la versión vieja ANTES de que Qwen la actualice
                texto_viejo = ""
                if os.path.exists(archivo_md):
                    with open(archivo_md, "r", encoding="utf-8") as f:
                        texto_viejo = f.read()

                # Qwen limpia la versión nueva
                markdown_final = limpiar_con_qwen_local(texto_sucio, nombre)
                
                # Si teníamos una versión vieja, comparamos y generamos la idea de negocio
                if texto_viejo:
                    analizar_oportunidad_negocio(texto_viejo, markdown_final, nombre)
                
                # Guardamos el nuevo libro actualizado
                with open(archivo_md, "w", encoding="utf-8") as f:
                    f.write(markdown_final)
                    
                # Guardamos la nueva huella para el futuro
                with open(archivo_hash, "w") as f:
                    f.write(huella_actual)
                    
                print(f"   [SUCCESS] {nombre} actualizado y guardado.")
                
            except Exception as e:
                print(f"   [ERROR] Error verificando {nombre}: {e}")
        
        print("\n[DONE] PROCESO DE CENTINELA FINALIZADO.")
    except Exception as e:
        print(f"[ERROR FATAL] en el centinela: {e}")

if __name__ == "__main__":
    revisar_actualizaciones()
