import os
import json
import pandas as pd
import chromadb
from langchain_community.embeddings import OllamaEmbeddings
import sys
import os
sys.path.append(r"c:\AbogadoVirtual\03_Motor_Core")
from guanes_engine import GuanesEngine

# Configuración
PATH_AREAS = r"c:\AbogadoVirtual\03_Motor_Core\data\urbanismo\datos_areas.csv"
PATH_CERTIFICADOS = r"c:\AbogadoVirtual\03_Motor_Core\data\urbanismo\certificados"
PATH_DB = r"c:\AbogadoVirtual\03_Motor_Core\db_guanes"

class CertificadorUrbanistico:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=PATH_DB)
        self.collection = self.client.get_collection(name="urbanismo_territorial")
        self.engine = GuanesEngine(db_path=PATH_DB)
        
        if not os.path.exists(PATH_CERTIFICADOS):
            os.makedirs(PATH_CERTIFICADOS)

    def validar_y_certificar(self, municipio, area_solicitada, uso_suelo):
        print(f"🧐 Iniciando validación para {municipio}...")
        
        # 1. Consultar restricciones en el POT (ChromaDB)
        query = f"¿Cuál es el área máxima permitida y restricciones para uso {uso_suelo} en {municipio}?"
        results = self.collection.query(
            query_texts=[query],
            n_results=3
        )
        
        contexto_pot = "\n".join(results['documents'][0])
        
        # 2. Análisis de IA para extraer límites numéricos (Simulado con Prompts)
        # En una versión real, usaríamos una extracción estructurada.
        # Por ahora, el Engine nos dará la respuesta técnica.
        
        respuesta_ia = self.engine.query(f"Analiza si puedo construir {area_solicitada} m2 para uso {uso_suelo} en {municipio} según este POT: {contexto_pot}")
        
        # 3. Inhibidor de Errores: Validación de Inconsistencia
        # Regla: Si el área solicitada parece exceder lo razonable o hay dudas, alertar.
        # (Aquí implementamos una lógica heurística o basada en la respuesta de la IA)
        
        es_inconsistente = "proscripto" in respuesta_ia.lower() or "no permitido" in respuesta_ia.lower() or "excede" in respuesta_ia.lower()
        
        if es_inconsistente:
            print("⚠️ ALERTA DE INCONSISTENCIA DETECTADA")
            return {
                "status": "ALERTA",
                "mensaje": f"Inconsistencia encontrada: El área de {area_solicitada} m2 para {uso_suelo} podría violar el POT de {municipio}.",
                "detalle": respuesta_ia
            }

        # 4. Sello de Autenticidad Digital (Qubic Placeholder)
        sello_qubic = self.generar_sello_qubic(municipio, area_solicitada)
        
        return {
            "status": "CERTIFICADO",
            "mensaje": f"Certificación Urbanística Exitosa para {municipio}.",
            "sello_digital": sello_qubic,
            "detalle": respuesta_ia
        }

    def generar_sello_qubic(self, municipio, area):
        # Simulación de anclaje en red Qubic
        import hashlib
        data_to_seal = f"GUANES_CERT_{municipio}_{area}_{os.urandom(8).hex()}"
        fingerprint = hashlib.sha256(data_to_seal.encode()).hexdigest()
        return f"QUBIC-VERIFIED-{fingerprint[:16].upper()}"

    def procesar_lote(self, path_csv):
        if not os.path.exists(path_csv):
            print(f"❌ No se encontró el archivo de áreas en {path_csv}")
            return

        df = pd.read_csv(path_csv)
        resultados = []
        
        for _, row in df.iterrows():
            res = self.validar_y_certificar(row['municipio'], row['area_m2'], row['uso_suelo'])
            resultados.append(res)
            
        return resultados

if __name__ == "__main__":
    cert = CertificadorUrbanistico()
    # Crear un CSV de ejemplo si no existe
    if not os.path.exists(PATH_AREAS):
        df_ejemplo = pd.DataFrame([
            {"municipio": "Bucaramanga", "area_m2": 500, "uso_suelo": "Residencial"},
            {"municipio": "Zapatoca", "area_m2": 2500, "uso_suelo": "Rural/Turismo"}
        ])
        df_ejemplo.to_csv(PATH_AREAS, index=False)
        print("📝 Creado archivo de ejemplo datos_areas.csv")

    print("📜 Iniciando Proceso de Certificación...")
    reporte = cert.procesar_lote(PATH_AREAS)
    for r in reporte:
        print(f"\n--- REPORTE ---\nSTATUS: {r['status']}\nINFO: {r['mensaje']}\nSELLO: {r.get('sello_digital', 'N/A')}")
