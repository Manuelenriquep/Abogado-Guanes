import os
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_core.documents import Document

# 1. Configuración de Memoria
print("🧠 Inicializando Cerebro RAG - Guanes Legal Tech...")

# Texto del Artículo 622 (Caza-Pagarés)
art_622_texto = """
ARTÍCULO 622. LLENO DE ESPACIOS EN BLANCO Y TÍTULOS EN BLANCO. 
Si en el título se dejan espacios en blanco podrá cualquier tenedor legítimo llenarlos, 
conforme a las instrucciones del suscriptor que los haya dejado, antes de presentar 
el título para el ejercicio del derecho que en él se incorpora. 
Si un título en blanco se llena contrariamente a las instrucciones recibidas, 
sólo podrá invocarse esa circunstancia contra quien haya participado en su llenado. 
El tenedor de buena fe exenta de culpa podrá cobrar el título por la suma que en él se exprese.
"""

doc = Document(page_content=art_622_texto, metadata={"fuente": "Código de Comercio Art. 622"})

# 2. Inicializar Vector Store (Chroma) con Ollama (Nomic)
embeddings = OllamaEmbeddings(model="nomic-embed-text")

# Crear DB en memoria para la prueba
vector_db = Chroma.from_documents(
    documents=[doc],
    embedding=embeddings,
    collection_name="guanes_memory"
)

# 3. Prueba de Fuego (Búsqueda por Similitud)
query = "El gota a gota me llenó el pagaré por 10 millones y yo solo le debía 2, ¿qué hago?"
print(f"🔥 Ejecutando Prueba de Fuego: '{query}'")

resultados = vector_db.similarity_search(query, k=1)

if resultados:
    res = resultados[0]
    print("\n✅ RESULTADO ENCONTRADO EN MEMORIA:")
    print(f"Fuente: {res.metadata['fuente']}")
    print(f"Contenido relevante:\n{res.page_content.strip()[:300]}...")
    
    # Análisis de Similitud - Inferencia lógica
    print("\n🔍 ANÁLISIS DEL CEREBRO RAG:")
    print("El caso coincide con la violación de las 'instrucciones de llenado' del Art. 622.")
    print("El usuario puede invocar la excepción de llenado contrario a las instrucciones.")
else:
    print("❌ No se encontraron coincidencias en la memoria.")
