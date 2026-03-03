import os
import json
import datetime
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import chromadb
from langchain_community.embeddings import OllamaEmbeddings

# Configuración de Rutas
PATH_FUENTES = r"c:\AbogadoVirtual\03_Motor_Core\data\urbanismo\fuentes"
PATH_PROCESADOS = r"c:\AbogadoVirtual\03_Motor_Core\data\urbanismo\procesados"
PATH_DB = r"c:\AbogadoVirtual\03_Motor_Core\db_guanes"
LOG_VERSIONES = r"c:\AbogadoVirtual\03_Motor_Core\data\urbanismo\version_log_urbanismo.json"

class RefineriaUrbanistica:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=PATH_DB)
        self.collection = self.client.get_or_create_collection(name="urbanismo_territorial")
        self.embeddings = OllamaEmbeddings(model="nomic-embed-text")
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1500,
            chunk_overlap=150,
            length_function=len,
        )
        self.inicializar_log()

    def inicializar_log(self):
        if not os.path.exists(LOG_VERSIONES):
            with open(LOG_VERSIONES, 'w', encoding='utf-8') as f:
                json.dump({"actualizaciones": []}, f)

    def registrar_version(self, nombre_archivo, municipio):
        with open(LOG_VERSIONES, 'r', encoding='utf-8') as f:
            log = json.load(f)
        
        entrada = {
            "fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "archivo": nombre_archivo,
            "municipio": municipio,
            "version_norma": "2024 (Vigente)" # Default solicitado
        }
        log["actualizaciones"].append(entrada)
        
        with open(LOG_VERSIONES, 'w', encoding='utf-8') as f:
            json.dump(log, f, indent=4, ensure_ascii=False)

    def procesar_nuevos_archivos(self):
        archivos = [f for f in os.listdir(PATH_FUENTES) if f.endswith('.pdf')]
        
        if not archivos:
            print("📭 No hay nuevos PDFs en la carpeta de fuentes.")
            return

        for archivo in archivos:
            path_completo = os.path.join(PATH_FUENTES, archivo)
            print(f"🚜 Procesando: {archivo}...")
            
            # 1. Extraer Texto
            reader = PdfReader(path_completo)
            texto_completo = ""
            for page in reader.pages:
                texto_completo += page.extract_text() + "\n"
            
            # 2. Fragmentar
            chunks = self.text_splitter.split_text(texto_completo)
            print(f"✂️ Fragmentado en {len(chunks)} pedazos.")
            
            # 3. Vectorizar
            municipio = archivo.split('.')[0].replace('_', ' ').title()
            ids = [f"{municipio}_{i}" for i in range(len(chunks))]
            metadatas = [{"fuente": archivo, "municipio": municipio, "tipo": "POT/EOT"} for _ in chunks]
            
            self.collection.add(
                documents=chunks,
                metadatas=metadatas,
                ids=ids
            )
            
            # 4. Registrar Versión y Mover
            self.registrar_version(archivo, municipio)
            os.rename(path_completo, os.path.join(PATH_PROCESADOS, archivo))
            print(f"✅ {archivo} indexado con éxito en 'urbanismo_territorial'.")

if __name__ == "__main__":
    print("🏙️ Iniciando Refinería Urbanística - Guanes LegalTech")
    refineria = RefineriaUrbanistica()
    refineria.procesar_nuevos_archivos()
