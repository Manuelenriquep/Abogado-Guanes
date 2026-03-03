import os
import json
import datetime
import re
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import chromadb
from langchain_community.embeddings import OllamaEmbeddings

# Configuración de Rutas
PATH_FUENTES = r"c:\AbogadoVirtual\03_Motor_Core\data\urbanismo\fuentes"
PATH_PROCESADOS = r"c:\AbogadoVirtual\03_Motor_Core\data\urbanismo\procesados"
PATH_DB = r"c:\AbogadoVirtual\03_Motor_Core\db_guanes"
LOG_VERSIONES = r"c:\AbogadoVirtual\03_Motor_Core\data\urbanismo\version_log_legal_masivo.json"

class RefineriaLegalPro:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=PATH_DB)
        # Colecciones separadas por tema si es necesario, 
        # pero usaremos metadatos para diferenciar dentro de colecciones mayores.
        self.coll_urb = self.client.get_or_create_collection(name="urbanismo_territorial")
        self.coll_salud = self.client.get_or_create_collection(name="normatividad_salud")
        
        self.embeddings = OllamaEmbeddings(model="nomic-embed-text")
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1200,
            chunk_overlap=120,
            length_function=len,
        )
        self.inicializar_log()

    def inicializar_log(self):
        if not os.path.exists(LOG_VERSIONES):
            with open(LOG_VERSIONES, 'w', encoding='utf-8') as f:
                json.dump({"ingestas": []}, f)

    def limpiar_texto(self, texto):
        """Elimina ruido como encabezados repetitivos, firmas y sellos simulados."""
        # Eliminar números de página (ej: Página 1 de 500)
        texto = re.sub(r'Página \d+ de \d+', '', texto)
        # Eliminar fechas de impresión o firmas repetitivas (ej: "Firma Escaneada", "Sello de Alcaldía")
        texto = re.sub(r'(Firma Escaneada|Sello de Alcaldía|Documento Oficial)', '', texto, flags=re.I)
        # Eliminar múltiples saltos de línea y espacios excesivos
        texto = re.sub(r'\n{3,}', '\n\n', texto)
        texto = re.sub(r' {2,}', ' ', texto)
        return texto.strip()

    def clasificar_municipio(self, nombre_archivo):
        # Lógica de detección basada en nombre
        nombre = nombre_archivo.lower()
        if "bogota" in nombre: return "Bogotá D.C."
        if "medellin" in nombre: return "Medellín"
        if "cali" in nombre: return "Cali"
        if "barranquilla" in nombre: return "Barranquilla"
        if "zapatoca" in nombre: return "Zapatoca"
        if "betulia" in nombre: return "Betulia"
        return "General"

    def procesar_fuente(self, sub_tema="urbanismo"):
        target_path = PATH_FUENTES
        archivos = [f for f in os.listdir(target_path) if f.endswith('.pdf')]
        
        if not archivos:
            print(f"📭 No hay nuevos PDFs en {target_path}")
            return

        collection = self.coll_urb if sub_tema == "urbanismo" else self.coll_salud

        for archivo in archivos:
            path_completo = os.path.join(target_path, archivo)
            print(f"🚀 Refinando: {archivo} (Tema: {sub_tema})...")
            
            try:
                reader = PdfReader(path_completo)
                texto_sucio = ""
                for page in reader.pages:
                    content = page.extract_text()
                    if content:
                        texto_sucio += content + "\n"
                
                # Proceso de Limpieza "Anti-Ruido"
                texto_limpio = self.limpiar_texto(texto_sucio)
                
                # Fragmentación
                chunks = self.text_splitter.split_text(texto_limpio)
                print(f"✨ Fragmentado en {len(chunks)} pedazos limpios.")
                
                # Metadatos Master
                municipio = self.clasificar_municipio(archivo)
                ids = [f"{municipio}_{archivo}_{i}" for i in range(len(chunks))]
                metadatas = [{
                    "fuente": archivo, 
                    "municipio": municipio, 
                    "tema": sub_tema,
                    "fecha_ingesta": datetime.datetime.now().strftime("%Y-%m-%d"),
                    "calidad": "Limpio (Pro)"
                } for _ in chunks]
                
                # Inyección a Bóveda
                collection.add(
                    documents=chunks,
                    metadatas=metadatas,
                    ids=ids
                )
                
                # Log y Archivo
                self.registrar_ingesta(archivo, municipio, sub_tema)
                os.rename(path_completo, os.path.join(PATH_PROCESADOS, archivo))
                print(f"✅ {archivo} procesado y movido a 'procesados'.")
            
            except Exception as e:
                print(f"❌ Error procesando {archivo}: {e}")

    def registrar_ingesta(self, archivo, municipio, tema):
        with open(LOG_VERSIONES, 'r', encoding='utf-8') as f:
            log = json.load(f)
        
        log["ingestas"].append({
            "fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "archivo": archivo,
            "municipio": municipio,
            "tema": tema,
            "vigencia": "Actualizada 2024"
        })
        
        with open(LOG_VERSIONES, 'w', encoding='utf-8') as f:
            json.dump(log, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    print("🦅 ACTIVANDO REFINERÍA LEGAL PRO - Guanes LegalTech")
    refineria = RefineriaLegalPro()
    # Primero procesamos Urbanismo (lo que hay en la carpeta)
    refineria.procesar_fuente(sub_tema="urbanismo")
    # Nota: Para Salud se recomienda mover PDFs de salud a la carpeta antes de correr con sub_tema="salud"
