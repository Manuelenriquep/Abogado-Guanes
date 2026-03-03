import os
import glob
import hashlib
from datetime import datetime
import chromadb
from langchain_community.embeddings import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Rutas Centrales del Ecosistema
DIR_BIBLIOTECA = r"c:\AbogadoVirtual\01_Ingesta_Datos\biblioteca_completa"
DIR_CEREBRO = r"c:\AbogadoVirtual\03_Motor_Core\db_guanes"
DIR_REGISTROS = r"c:\AbogadoVirtual\01_Ingesta_Datos\registro_inyeccion"

# Diccionarios de clasificación por nombre
PREFIJOS_URBANISMO = ["pot_", "eot_", "ley_675", "decreto_1077", "decreto_768", "ley_1796"]

def configurar_entorno():
    if not os.path.exists(DIR_REGISTROS):
        os.makedirs(DIR_REGISTROS)
    print(f"🔧 Iniciando Inyector RAG - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def obtener_hash_archivo(ruta_archivo):
    """Calcula el hash SHA-256 de un archivo para saber si su contenido cambió."""
    hasher = hashlib.sha256()
    with open(ruta_archivo, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def leer_hash_guardado(nombre_base):
    ruta_hash = os.path.join(DIR_REGISTROS, f"{nombre_base}.hash")
    if os.path.exists(ruta_hash):
        with open(ruta_hash, 'r') as f:
            return f.read().strip()
    return ""

def guardar_nuevo_hash(nombre_base, nuevo_hash):
    ruta_hash = os.path.join(DIR_REGISTROS, f"{nombre_base}.hash")
    with open(ruta_hash, 'w') as f:
        f.write(nuevo_hash)

def inyectar_en_chroma(nombre_archivo, texto_contenido, cliente_db, embeddings):
    """Segmenta el texto y lo inyecta en la colección correspondiente (titulos o urbanismo)"""
    nombre_base = os.path.splitext(nombre_archivo)[0].lower()
    
    # Determinar a qué colección va
    es_urbanismo = any(prefijo in nombre_base for prefijo in PREFIJOS_URBANISMO)
    nombre_coleccion = "urbanismo_territorial" if es_urbanismo else "titulos_valores"
    
    print(f"   📥 Destino: Colección '{nombre_coleccion}'")
    coleccion = cliente_db.get_or_create_collection(name=nombre_coleccion)
    
    # Text Splitter: Pedazos medianos para no perder contexto normativo
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,
        chunk_overlap=300,
        separators=["\n\n", "\n", ".", " "]
    )
    
    fragmentos = text_splitter.split_text(texto_contenido)
    total_fragmentos = len(fragmentos)
    print(f"   ✂️ Documento fragmentado en {total_fragmentos} vectores.")
    
    # Preparar lotes para evitar sobrecargar ChromaDB
    batch_size = 100
    for i in range(0, total_fragmentos, batch_size):
        lote_textos = fragmentos[i:i+batch_size]
        
        # Generar IDs únicos que ligan el fragmento al documento origen
        ids = [f"{nombre_base}_chunk_{i+j}" for j in range(len(lote_textos))]
        metadatos = [{"fuente": nombre_archivo, "fecha_inyeccion": datetime.now().strftime("%Y-%m-%d"), "chunk": i+j} for j in range(len(lote_textos))]
        
        # Calcular sus vectores usando local nomic-embed-text
        try:
            print(f"      Calculando embeddings para lote {i//batch_size + 1}...")
            vectores = embeddings.embed_documents(lote_textos)
            
            # Upsert: Si el ID ya existe, lo actualiza (ideal para cuando el Centinela modifica una ley)
            coleccion.upsert(
                documents=lote_textos,
                embeddings=vectores,
                metadatas=metadatos,
                ids=ids
            )
        except Exception as e:
             print(f"      ❌ Error inyectando lote {i//batch_size + 1}: {e}")

    print(f"   ✅ Inyección completada para {nombre_archivo}.")


def ejecutar_inyeccion_diaria():
    configurar_entorno()
    archivos_md = glob.glob(os.path.join(DIR_BIBLIOTECA, "*.md"))
    
    if not archivos_md:
        print(f"⚠️ No hay archivos Markdown en {DIR_BIBLIOTECA}")
        return

    try:
        # Precalentamos ChromaDB y los Embeddings
        print("🧠 Conectando al Cerebro Local (ChromaDB & OllamaEmbeddings)...")
        cliente_chroma = chromadb.PersistentClient(path=DIR_CEREBRO)
        embeddings = OllamaEmbeddings(model="nomic-embed-text")
    except Exception as e:
        print(f"❌ Error crítico conectando al motor RAG: {e}")
        return

    archivos_procesados = 0

    for ruta_md in archivos_md:
        nombre_archivo = os.path.basename(ruta_md)
        nombre_base = os.path.splitext(nombre_archivo)[0]
        
        hash_actual = obtener_hash_archivo(ruta_md)
        hash_guardado = leer_hash_guardado(nombre_base)
        
        if hash_actual == hash_guardado:
            print(f"💤 {nombre_archivo} - Sin cambios desde la última inyección.")
            continue
            
        print(f"\n🚀 Detectado archivo nuevo o modificado: {nombre_archivo}")
        
        try:
            with open(ruta_md, 'r', encoding='utf-8') as f:
                contenido = f.read()
                
            if len(contenido.strip()) < 50:
                print("   ⚠️ Archivo demasiado corto, omitiendo.")
                continue

            # Inyectar al RAG
            inyectar_en_chroma(nombre_archivo, contenido, cliente_chroma, embeddings)
            
            # Registrar que ya lo procesamos para no repetirlo mañana
            guardar_nuevo_hash(nombre_base, hash_actual)
            archivos_procesados += 1
            
        except Exception as e:
            print(f"   ❌ Error al leer o procesar {nombre_archivo}: {e}")

    print(f"\n=======================================================")
    print(f"✅ OPERACIÓN RAG FINALIZADA. Archivos inyectados/actualizados hoy: {archivos_procesados}")
    print(f"=======================================================\n")

if __name__ == "__main__":
    ejecutar_inyeccion_diaria()
