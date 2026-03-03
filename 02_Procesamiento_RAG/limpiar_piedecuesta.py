import chromadb

# ==========================================
# LIMPIEZA DE INTEGRIDAD CHROMADB (PIEDECUESTA)
# ==========================================
DB_PATH = r"c:\AbogadoVirtual\03_Motor_Core\db_guanes"

def limpiar_piedecuesta():
    print("🧹 INICIANDO LIMPIEZA DE INTEGRIDAD: PIEDECUESTA 🧹")
    try:
        client = chromadb.PersistentClient(path=DB_PATH)
        coleccion = client.get_collection(name="urbanismo_territorial")
        
        # Buscar vectores que tengan el municipio de Piedecuesta
        print("🔍 Buscando vectores residuales de Piedecuesta...")
        results = coleccion.get(where={"municipio": "Piedecuesta"})
        
        ids_a_borrar = results.get('ids', [])
        cantidad = len(ids_a_borrar)
        
        if cantidad > 0:
            print(f"⚠️ Se encontraron {cantidad} vectores de Piedecuesta. Procediendo a eliminar...")
            coleccion.delete(ids=ids_a_borrar)
            print("✅ Vectores eliminados exitosamente. Integridad restaurada.")
        else:
            print("✅ No se encontraron vectores de Piedecuesta. La base de datos está limpia.")
            
    except Exception as e:
        print(f"❌ Error durante la limpieza: {e}")

if __name__ == "__main__":
    limpiar_piedecuesta()
