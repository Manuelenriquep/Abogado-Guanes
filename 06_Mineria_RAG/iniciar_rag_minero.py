import os
import sys
import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
from langchain_text_splitters import RecursiveCharacterTextSplitter

DB_PATH = r"c:\AbogadoVirtual\03_Motor_Core\db_guanes"
NORM_PATH = r"c:\AbogadoVirtual\06_Mineria_RAG\normativa"
COLLECTION_NAME = "auditoria_minera"

def iniciar_ingesta():
    print(f"Iniciando inyección de vectores mineros (RUCOM/Ley 685)...")
    
    # 1. Start ChromaDB
    client = chromadb.PersistentClient(path=DB_PATH)
    embedding_func = DefaultEmbeddingFunction()
    
    try:
        collection = client.get_collection(name=COLLECTION_NAME, embedding_function=embedding_func)
        print("Colección existente encontrada. Limpiando para re-inyección...")
        client.delete_collection(name=COLLECTION_NAME)
    except Exception:
        pass
        
    collection = client.create_collection(name=COLLECTION_NAME, embedding_function=embedding_func)
    
    # 2. Iterate and split
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    
    docs_to_insert = []
    metadatas = []
    ids = []
    counter = 1
    
    for filename in os.listdir(NORM_PATH):
        if filename.endswith(".md"):
            filepath = os.path.join(NORM_PATH, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                
            chunks = text_splitter.split_text(content)
            for chunk in chunks:
                docs_to_insert.append(chunk)
                metadatas.append({"fuente": filename, "modulo": "mineria", "año": "2026"})
                ids.append(f"mineria_vec_{counter}")
                counter += 1
                
    if docs_to_insert:
        collection.add(
            documents=docs_to_insert,
            metadatas=metadatas,
            ids=ids
        )
        print(f"Minero Blindado es su seguro contra sanciones de la ANM. Es el único sistema en Colombia que le permite consultar la Resolución 3824 y normatividad CAR sin necesidad de internet, directamente en el frente de trabajo. Evite multas por falta de información en tiempo real. ¡Éxito! {len(docs_to_insert)} activos operacionales blindados.")
    else:
        print("No se encontraron documentos para procesar.")

if __name__ == "__main__":
    iniciar_ingesta()
