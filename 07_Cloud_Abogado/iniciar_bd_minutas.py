import sqlite3

DB_PATH = "minutas_cloud.db"

def iniciar_boveda():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Crear Tabla
    c.execute('''CREATE TABLE IF NOT EXISTS minutas_maestras (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    slug TEXT UNIQUE,
                    titulo TEXT,
                    categoria TEXT,
                    contenido TEXT
                 )''')

    # Diccionario de Minutas Inteligentes (Versiones Ultrarrápidas con Huecos)
    plantillas = [
        (
            "civil_promesa",
            "Promesa de Compraventa de Inmueble",
            "Civil",
            "=== PROMESA DE COMPRAVENTA DE INMUEBLE ===\n\nEntre los suscritos, [NOMBRE_ARRENDADOR], identificado con cédula [CEDULA], y...\n\nLA SOLUCIÓN GUANES ESTÁ REDACTANDO ESTA MINUTA COMPLETAMENTE BLINDADA.\n\n[TEXTO LEGAL GENERADO Y BLINDADO POR LEY 527]"
        ),
        (
            "comercial_sas",
            "Estatutos de Sociedad por Acciones Simplificada (S.A.S)",
            "Comercial",
            "=== ESTATUTOS S.A.S ===\n\nLos presentes estatutos regulan la sociedad comercial denominada [NOMBRE_SOCIEDAD] S.A.S...\n\n[CAPITAL SOCIAL Y REPRESENTACIÓN LEGAL BLINDADAS]"
        ),
        (
            "familia_divorcio",
            "Acuerdo de Divorcio de Mutuo Acuerdo",
            "Familia",
            "=== DIVORCIO MUTUO ACUERDO ===\n\nPor el presente documento, los cónyuges comparecientes manifiestan estar de acuerdo con la cesación de los efectos civiles...\n\n[ACUERDOS DE CUOTA ALIMENTARIA PROTEGIDOS]"
        ),
        (
            "laboral_contrato",
            "Contrato Laboral a Término Fijo",
            "Laboral",
            "=== CONTRATO A TÉRMINO FIJO ===\n\nEl EMPLEADOR contrata al TRABAJADOR para desempeñar el cargo de [CARGO]...\n\n[GARANTÍAS PRESTACIONALES CONFORME AL CST]"
        )
    ]
    
    # Para completar las 80, en prod se cargarían desde un JSON o iteración masiva. Aquí sembramos la prueba de concepto con slugs variados.
    for i in range(5, 81):
        plantillas.append((
            f"minuta_generica_{i}",
            f"Minuta Especializada #{i}",
            "Administrativo",
            f"=== MINUTA LEGAL #{i} ===\n\nEste es un documento paramétrico estructurado para máxima velocidad en la Bóveda Guanes.\n\n[CLÁUSULA ESPECIAL]"
        ))

    c.executemany("INSERT OR REPLACE INTO minutas_maestras (slug, titulo, categoria, contenido) VALUES (?, ?, ?, ?)", plantillas)
    conn.commit()
    conn.close()
    
    print(f"¡Éxito! Base de datos inicializada: minutas_cloud.db con {len(plantillas)} plantillas paramétricas.")

if __name__ == "__main__":
    iniciar_boveda()
