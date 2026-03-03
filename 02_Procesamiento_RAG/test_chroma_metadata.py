import chromadb

# ==========================================
# TESTER DE INTEGRIDAD CHROMADB
# ==========================================
DB_PATH = r"c:\AbogadoVirtual\03_Motor_Core\db_guanes"

def verificar_integridad():
    print("🔍 VERIFICANDO INTEGRIDAD EN CHROMADB 🔍")
    client = chromadb.PersistentClient(path=DB_PATH)
    
    coleccion = client.get_collection(name="urbanismo_territorial")
    print(f"Colección encontrada: urbanismo_territorial")
    
    count = coleccion.count()
    print(f"Total de vectores en colección: {count}")
    
    print("\n📦 Muestreo de los primeros 2 vectores específicos de Bucaramanga:")
    results = coleccion.get(where={"municipio": "Bucaramanga"}, limit=2)
    
    for i in range(len(results['ids'])):
        print(f"\nID: {results['ids'][i]}")
        print(f"Texto (Extracto): {results['documents'][i][:80]}...")
        print(f"Metadatos: {results['metadatas'][i]}")
        
    print("\n✅ Verificación concluida.")

if __name__ == "__main__":
    verificar_integridad()
