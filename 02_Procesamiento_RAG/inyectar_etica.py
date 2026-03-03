import os
import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter
from chromadb.utils import embedding_functions

# Configuración
CHROMA_PATH = r"c:\AbogadoVirtual\03_Motor_Core\db_guanes"
MD_PATH = r"c:\AbogadoVirtual\02_Procesamiento_RAG\etica_sistema.md"
COLLECTION_NAME = "urbanismo_territorial" # Inyectar en la colección global para búsquedas transversales

def inyectar_etica():
    print(f"Leyendo documento: {MD_PATH}")
    with open(MD_PATH, 'r', encoding='utf-8') as f:
        text = f.read()
    
    print("Segmentando documento de ética...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
        length_function=len,
    )
    chunks = text_splitter.split_text(text)
    
    print(f"Conectando a ChromaDB en {CHROMA_PATH}")
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.get_or_create_collection(name=COLLECTION_NAME)
    
    print("Cargando modelo de embeddings (Default Chroma 384 dims)...")
    ef = embedding_functions.DefaultEmbeddingFunction()
    
    print(f"Vectorizando {len(chunks)} chunks doctrinales...")
    embeddings = ef(chunks)
    
    ids = [f"etica_algoritmica_v5_{i}" for i in range(len(chunks))]
    metadatas = [{"fuente": "etica_sistema.md", "categoria": "etica_algoritmica", "prioridad": "maxima"} for _ in range(len(chunks))]
    
    print("Inyectando en la base de datos...")
    collection.add(
        embeddings=embeddings,
        documents=chunks,
        metadatas=metadatas,
        ids=ids
    )
    
    print("\n✅ ¡Ingesta RAG Ética completada y exitosa!")
    print(f"Se inyectaron {len(chunks)} vectores doctrinales. El nodo de consulta 'etica_algoritmica' ya está disponible.")

if __name__ == "__main__":
    inyectar_etica()
