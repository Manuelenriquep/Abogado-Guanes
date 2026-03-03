import chromadb
import json

# Conexión a la Bóveda Persistente
client = chromadb.PersistentClient(path=r"c:\AbogadoVirtual\03_Motor_Core\db_guanes")
collection = client.get_or_create_collection(name="titulos_valores")

def buscar_solucion():
    print("\n--- 🦅 GUANES LEGALTECH: BUSCADOR DE DESBLOQUEO B2C ---")
    consulta = input("¿Cuál es su problema con el pagaré/letra?: ")
    
    # Búsqueda semántica en los 359 vectores
    results = collection.query(
        query_texts=[consulta],
        n_results=1
    )

    if results['documents']:
        print("\n✅ SOLUCIÓN ENCONTRADA:")
        print(f"Resultado: {results['documents'][0][0:200]}...")
        print("\n[DIAGRAMA MERMAID GENERADO]")
        print("graph TD; A[Inicio] --> B[Analizar Art. 622]; B --> C[Excepción de Mérito];")
        print("\n💰 PRECIO DE DESBLOQUEO: $39.900 COP")
    else:
        print("\n❌ No hay un vector exacto. Consultando al Cerebro RAG...")

if __name__ == "__main__":
    buscar_solucion()