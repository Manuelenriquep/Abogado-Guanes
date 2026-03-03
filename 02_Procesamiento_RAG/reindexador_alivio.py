import chromadb
from langchain_community.embeddings import OllamaEmbeddings
import json

def reindexar_alivio():
    print("🧹 Limpiando colección antigua...")
    client = chromadb.PersistentClient(path=r"c:\AbogadoVirtual\03_Motor_Core\db_guanes")
    
    # Intentar borrar para fresh start o simplemente añadir
    try:
        client.delete_collection("titulos_valores")
    except:
        pass
        
    collection = client.create_collection(name="titulos_valores")
    
    print("📖 Cargando vectores con ALIVIO...")
    with open(r'c:\AbogadoVirtual\03_Motor_Core\vectores_titulos_valores_alivio.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    documents = [item['resumen_solucion'] for item in data]
    metadatas = [{"articulo": item['articulo_origen'], "diagrama": item['diagrama_mermaid']} for item in data]
    ids = [f"id_{i}" for i in range(len(data))]
    
    print(f"🚀 Indexando {len(documents)} vectores en ChromaDB...")
    # Nota: ChromaDB maneja los embeddings internamente si se configura, 
    # pero aquí los pasaremos como textos para que use su default o lo manejemos en el engine.
    # Para consistencia con el Engine, usaremos query_texts después.
    
    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
    
    print("✅ Re-indexación existosa. El sistema ahora habla con ALIVIO.")

if __name__ == "__main__":
    reindexar_alivio()
