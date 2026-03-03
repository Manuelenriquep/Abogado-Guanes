import os
import time
import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings

# ==========================================
# CONFIGURACIÓN DEL TEJEDOR MASIVO RAG
# ==========================================
DB_PATH = r"c:\AbogadoVirtual\03_Motor_Core\db_guanes"

ORÍGENES = [
    {
        "path": r"c:\AbogadoVirtual\01_Ingesta_Datos\biblioteca_completa\jurisdiccion_local_textos",
        "collection": "urbanismo_territorial"
    },
    {
        "path": r"c:\AbogadoVirtual\01_Ingesta_Datos\biblioteca_completa\salud_textos",
        "collection": "titulos_valores" # Colección transversal para Glosas y otros perfiles no-urbanos
    }
]

def cargar_y_vectorizar():
    print("🕸️ INICIANDO TEJEDOR MASIVO RAG (VECTORIZACIÓN LOCAL) 🕸️")
    
    client = chromadb.PersistentClient(path=DB_PATH)
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    
    # Text Splitter estricto solicitado
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    
    total_chunks_generados = 0
    
    for origen in ORÍGENES:
        base_dir = origen["path"]
        nombre_coleccion = origen["collection"]
        
        if not os.path.exists(base_dir):
            print(f"⚠️ El directorio no existe, saltando: {base_dir}")
            continue
            
        coleccion = client.get_or_create_collection(name=nombre_coleccion)
        print(f"\n📂 Conectado a colección ChromaDB: '{nombre_coleccion}'")
        
        archivos_md = [f for f in os.listdir(base_dir) if f.endswith(".md")]
        
        if not archivos_md:
            print(f"📭 No hay archivos Markdown en {base_dir}")
            continue
            
        for archivo in archivos_md:
            ruta_completa = os.path.join(base_dir, archivo)
            print(f"  🚜 Ingestando: {archivo}...")
            
            with open(ruta_completa, "r", encoding="utf-8") as f:
                contenido = f.read()
                
            # 1. Segmentación
            chunks = text_splitter.split_text(contenido)
            num_chunks = len(chunks)
            total_chunks_generados += num_chunks
            
            # 2. Extracción y construcción de Metadatos
            # Asumimos formato "Municipio_NombreNorma.md" o solo "NombreNorma.md" si es nacional
            partes_nombre = archivo.split("_")
            municipio = "Nacional"
            if len(partes_nombre) > 1 and "Bucaramanga" in archivo or "Floridablanca" in archivo or "Santander" in archivo:
                municipio = partes_nombre[0]
            elif "salud" in base_dir.lower():
                municipio = "MinSalud"
                
            # Evita sobrepasar límites de batch en Chroma (max 5461 aprox, enviamos de 1000 en 1000)
            batch_size = 500
            for i in range(0, num_chunks, batch_size):
                batch_chunks = chunks[i:i+batch_size]
                
                # Armamos metadatos e ids para el batch
                metadatas = [
                    {
                        "fuente": archivo,
                        "municipio": municipio,
                        "año_2026": "true",
                        "tipo_procesamiento": "extraccion_masiva"
                    }
                    for _ in batch_chunks
                ]
                
                ids = [f"{archivo}_chunk_{i+j}_{int(time.time())}" for j in range(len(batch_chunks))]
                
                # 3. Inyección a ChromaDB
                coleccion.add(
                    documents=batch_chunks,
                    metadatas=metadatas,
                    ids=ids
                )
            
            print(f"  ✅ {num_chunks} vectores inyectados correctamente con metadatos (año_2026).")

    print(f"\n✨ VECTORIZACIÓN COMPLETADA. Total vectores inyectados: {total_chunks_generados}")

if __name__ == "__main__":
    cargar_y_vectorizar()
