import os
import re
import json
import shutil
from collections import defaultdict

# ==========================================
# CONFIGURACIÓN Y RUTAS (v2.0 Kelseniana)
# ==========================================
CARPETA_PROYECTO = "biblioteca_limpia"
CARPETA_BACKUP = "backup_tejedor"
ARCHIVO_INDICE = "00_INDICE_GRAFO_GUANES.md"
ARCHIVO_PAQUETES = r"c:\AbogadoVirtual\03_Motor_Core\paquetes_sugeridos.json"
ARCHIVO_VACIOS = r"c:\AbogadoVirtual\03_Motor_Core\auditoria_vacios_locales.json"
ARCHIVO_SALIDA = r"c:\AbogadoVirtual\03_Motor_Core\vectores_de_ataque.json"
# Metadatos de Jerarquía (Estructura Kelseniana)
JERARQUIA_PESOS = {
    "Constitucion_Politica.md": 1,
    "Codigo_Civil.md": 2,
    "Codigo_de_Comercio.md": 2,
    "Codigo_General_del_Proceso.md": 2,
    "Codigo_Procedimiento_Administrativo_CPACA.md": 2,
    "Codigo_Penal.md": 2,
    "Codigo_Procedimiento_Penal.md": 2,
    "Codigo_Sustantivo_del_Trabajo.md": 2,
    "Estatuto_Tributario.md": 2,
    "Estatuto_del_Consumidor.md": 2,
    "Codigo_Nacional_de_Policia.md": 2,
    "Codigo_Nacional_de_Transito.md": 2,
    "Codigo_Infancia_y_Adolescencia.md": 2,
    "Ley_Propiedad_Horizontal.md": 2,
    # Futuros archivos
    "Estatuto_Tributario_Bucaramanga.md": 4,
    "Acuerdos_Municipales.md": 4
}

MAPEO_LEYES = {
    "Constitución Política": "Constitucion_Politica.md",
    "Código Civil": "Codigo_Civil.md",
    "Código de Comercio": "Codigo_de_Comercio.md",
    "Código General del Proceso": "Codigo_General_del_Proceso.md",
    "Código de Procedimiento Administrativo": "Codigo_Procedimiento_Administrativo_CPACA.md",
    "Código Penal": "Codigo_Penal.md",
    "Código de Procedimiento Penal": "Codigo_Procedimiento_Penal.md",
    "Código Sustantivo del Trabajo": "Codigo_Sustantivo_del_Trabajo.md",
    "Estatuto Tributario": "Estatuto_Tributario.md",
    "Estatuto del Consumidor": "Estatuto_del_Consumidor.md",
    "Código Nacional de Policía": "Codigo_Nacional_de_Policia.md",
    "Código Nacional de Tránsito": "Codigo_Nacional_de_Transito.md",
    "Código Infancia y Adolescencia": "Codigo_Infancia_y_Adolescencia.md",
    "Ley de Propiedad Horizontal": "Ley_Propiedad_Horizontal.md"
}

# ==========================================
# INYECCIONES DE PRODUCTO
# ==========================================
TIP_ARRIENDO = """
> [!TIP]
> **ESTRATEGIA GUANES:** Si busca arrendar sin fiador, el mecanismo de Garantía Mobiliaria (Ley 1676 de 2013) es su solución blindada. Validado por la Corte Constitucional (Sentencia C-145/18) para garantizar seguridad total al Arrendador. [Ver Procedimiento y Producto de Garantía Mobiliaria aquí].
"""

ALERTA_SANTANDER = """
> [!WARNING]
> 🚨 ALERTA GUANES - JURISDICCIÓN SANTANDER: Si usted tiene un establecimiento abierto al público en Bucaramanga o Floridablanca, está sujeto al cobro de ICA y Avisos y Tableros. Verifique si le están liquidando mal sus impuestos locales aquí: [Auditoría Tributaria Santander].
"""

# ==========================================
# MOTOR DE INFERENCIA Y TEJIDO
# ==========================================

def realizar_backup():
    if not os.path.exists(CARPETA_BACKUP): os.makedirs(CARPETA_BACKUP)
    for f in os.listdir(CARPETA_PROYECTO):
        if f.endswith(".md"): shutil.copy2(os.path.join(CARPETA_PROYECTO, f), CARPETA_BACKUP)

def evolucionar_v2():
    try:
        print("🚀 EVOLUCIONANDO A TEJEDOR LEGAL v2.0 (Motor Kelseniano) 🚀")
        realizar_backup()

        links_count = defaultdict(lambda: defaultdict(int))
        pain_score = defaultdict(int)
        vacios_locales = []
        archivos_procesados = []

        KEYWORDS_DOLOR = r'multa|sanción|desalojo|embargo|captura|infracción|policía'
        KEYWORDS_SANTANDER = r'establecimiento de comercio|registro mercantil|Cámara de Comercio|impuesto|tributo|contabilidad'
        KEYWORDS_CLANDESTINIDAD = r'según reglamente|autoridad local|concejo municipal|asamblea departamental'

        regex_link = re.compile(rf"({'|'.join(re.escape(k) for k in MAPEO_LEYES.keys())})\s+(?:artículo|Art\.|Art)\s+(\d+)", re.IGNORECASE)

        for archivo in os.listdir(CARPETA_PROYECTO):
            if not archivo.endswith(".md") or archivo == ARCHIVO_INDICE: continue
            
            ruta = os.path.join(CARPETA_PROYECTO, archivo)
            with open(ruta, "r", encoding="utf-8") as f: contenido = f.read()

            print(f"📡 Procesando {archivo}...")

            # 1. Auditoría de Clandestinidad (Vacíos Locales)
            matches_vacios = re.finditer(rf"((?:.*?\n?){{0,2}}.*?(?:{KEYWORDS_CLANDESTINIDAD}).*?(?:\n?.*?){{0,2}})", contenido, re.IGNORECASE)
            for m in matches_vacios:
                # Intentar extraer artículo cercano
                art_match = re.search(r"Artículo\s+(\d+)", m.group(1), re.IGNORECASE)
                vacios_locales.append({
                    "archivo": archivo,
                    "articulo": art_match.group(1) if art_match else "N/A",
                    "contexto": m.group(1).strip()
                })

            # 2. Nodo Santander (Específico Codigo de Comercio)
            if archivo == "Codigo_de_Comercio.md":
                if re.search(KEYWORDS_SANTANDER, contenido, re.IGNORECASE):
                    links_count[archivo]["Estatuto_Tributario_Bucaramanga.md"] += 1
                
                # Inyección Santander en Libro Primero
                patron_libro = re.compile(rf"(###\s+\*\*Artículo\s+.*Establecimientos de Comercio.*\*\*)", re.IGNORECASE)
                contenido = patron_libro.sub(rf"\1\n{ALERTA_SANTANDER}", contenido)

            # 3. Termómetro de Dolor
            if re.search(KEYWORDS_DOLOR, contenido, re.IGNORECASE): pain_score[archivo] = 1

            # 4. Tejido Cruzado y Metadatos Kelsen (Jerarquía)
            def inyectar_link(match):
                ley_txt, art = match.group(1), match.group(2)
                nombre_norm = next((k for k in MAPEO_LEYES if k.lower() in ley_txt.lower()), None)
                if nombre_norm:
                    arch_dest = MAPEO_LEYES[nombre_norm]
                    if arch_dest != archivo:
                        links_count[archivo][arch_dest] += 1
                        # Lógica Kelseniana de Etiquetas Jerárquicas
                        peso_orig = JERARQUIA_PESOS.get(archivo, 2)
                        peso_dest = JERARQUIA_PESOS.get(arch_dest, 2)
                        kelsen_tag = f"<!-- HIERARCHY_LINK: Nivel {peso_orig} -> Nivel {peso_dest} -->"
                        return f"[{ley_txt} artículo {art}]({arch_dest}#artículo-{art}) {kelsen_tag}"
                return match.group(0)

            contenido = regex_link.sub(inyectar_link, contenido)

            # 5. Inyección Arriendo Seguro (Codigo Civil)
            if archivo == "Codigo_Civil.md":
                for t in ["Prenda", "Fianza"]:
                    patron = re.compile(rf"(###\s+\*\*Artículo\s+.*{t}.*\*\*)", re.IGNORECASE)
                    contenido = patron.sub(rf"\1\n{TIP_ARRIENDO}", contenido)

            with open(ruta, "w", encoding="utf-8") as f: f.write(contenido)
            archivos_procesados.append(archivo)

        # GENERACIÓN DE ENTREGABLES
        with open(ARCHIVO_INDICE, "w", encoding="utf-8") as f:
            f.write("# 00_INDICE_GRAFO_GUANES\n\n- ")
            f.write("\n- ".join(f"[{a.replace('.md', '').replace('_', ' ')}]({a})" for a in sorted(archivos_procesados)))
        
        # Paquetes Sugeridos
        paquetes = {"Ecosistemas Locales": [], "Oportunidades de Negocio": []}
        for f, dests in links_count.items():
            for d, c in dests.items():
                es_urgente = pain_score[f] or pain_score[d]
                prioridad = "Prioridad de Venta 1 (Landing page inmediata)" if es_urgente else "Prioridad de Venta 2 (Nutrición / B2B)"
                obj = {"origen": f, "destino": d, "densidad": c, "Nivel de Urgencia": prioridad}
                
                if "Bucaramanga" in d or "Santander" in f:
                    obj["producto"] = "Defensa Fiscal para Comerciantes - Santander (C. de Comercio + Impuestos Locales)"
                    paquetes["Ecosistemas Locales"].append(obj)
                else:
                    paquetes["Oportunidades de Negocio"].append(obj)

        with open(ARCHIVO_PAQUETES, "w", encoding="utf-8") as f: json.dump(paquetes, f, indent=4, ensure_ascii=False)
        with open(ARCHIVO_VACIOS, "w", encoding="utf-8") as f: json.dump(vacios_locales, f, indent=4, ensure_ascii=False)

        print("\n✨ ✅ EVOLUCIÓN COMPLETADA. Motor v2.0 Activo.")
    except Exception as e:
        print(f"❌ Error crítico: {e}")

if __name__ == "__main__":
    evolucionar_v2()
