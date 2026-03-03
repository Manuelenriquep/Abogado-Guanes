import os
import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
from langchain_text_splitters import RecursiveCharacterTextSplitter

DB_PATH = r"c:\AbogadoVirtual\03_Motor_Core\db_guanes"
NORM_PATH = r"c:\AbogadoVirtual\05_Salud_RAG\normativa"
COLLECTION_NAME = "auditoria_salud"

def ingest_salud():
    print("Iniciando inyección de vectores de SALUD (The Shield Edition)...")
    
    # Init Chroma
    sys_client = chromadb.PersistentClient(path=DB_PATH)
    embed_fn = DefaultEmbeddingFunction()
    
    collection = sys_client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embed_fn
    )
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=150)
    
    docs_to_inject = []
    metas_to_inject = []
    ids_to_inject = []
    
    idx = 1
    
    for filename in os.listdir(NORM_PATH):
        if filename.endswith(".md"):
            filepath = os.path.join(NORM_PATH, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            
            chunks = text_splitter.split_text(content)
            
            for chunk in chunks:
                docs_to_inject.append(chunk)
                metas_to_inject.append({
                    "source": filename,
                    "categoria": "normativa_financiera_salud",
                    "prioridad": "maxima"
                })
                ids_to_inject.append(f"doc_salud_{idx}")
                idx += 1
                
    if docs_to_inject:
        collection.add(documents=docs_to_inject, metadatas=metas_to_inject, ids=ids_to_inject)
        print(f"¡Éxito! {len(docs_to_inject)} vectores médicos inyectados blindando el ecosistema.")
    else:
        print("No se encontraron documentos para inyectar.")

if __name__ == "__main__":
    ingest_salud()
