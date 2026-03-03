import os
import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter
from chromadb.utils import embedding_functions

# Configuración
CHROMA_PATH = r"c:\AbogadoVirtual\03_Motor_Core\db_guanes"
MD_PATH = r"c:\AbogadoVirtual\06_Editorial_y_Auditorias\libro_guanes\manuscritos\01_Capitulo_1_El_Impuesto_De_La_Desconfianza.md"
COLLECTION_NAME = "urbanismo_territorial" 

def inyectar_manifiesto():
    print(f"Leyendo documento: {MD_PATH}")
    with open(MD_PATH, 'r', encoding='utf-8') as f:
        text = f.read()
    
    print("Segmentando documento...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    chunks = text_splitter.split_text(text)
    
    print(f"Conectando a ChromaDB en {CHROMA_PATH}")
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.get_or_create_collection(name=COLLECTION_NAME)
    
    print("Cargando modelo de embeddings (Default Chroma 384 dims)...")
    ef = embedding_functions.DefaultEmbeddingFunction()
    
    print(f"Vectorizando {len(chunks)} chunks...")
    embeddings = ef(chunks)
    
    ids = [f"manifiesto_guanes_v5_{i}" for i in range(len(chunks))]
    metadatas = [{"fuente": "Libro Guanes", "categoria": "manifiesto_comercial", "prioridad": "alta"} for _ in range(len(chunks))]
    
    print("Inyectando en la base de datos...")
    collection.add(
        embeddings=embeddings,
        documents=chunks,
        metadatas=metadatas,
        ids=ids
    )
    
    print("\n✅ ¡Ingesta RAG completada y exitosa!")
    print(f"Se inyectaron {len(chunks)} vectores optimizados para responder a: '¿Cómo soluciona Guanes el problema del fiador tradicional?'")

if __name__ == "__main__":
    inyectar_manifiesto()
