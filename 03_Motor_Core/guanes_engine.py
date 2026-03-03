import chromadb
import requests
import json
import hashlib
from datetime import datetime
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate

PROFILES = {
    "GLOSAS BLINDADAS": {
        "vectores": "Resolución 2284/2023, Circular 016/2015, Sentencia T-760/08.",
        "accion": "Auditoría de facturación salud y redacción de recursos de reposición."
    },
    "CONSTRUCTOR SEGURO": {
        "vectores": "POT/EOT Santander, Decreto 1077/2015, Ley 675 (PH).",
        "accion": "Revisión de reglamentos de PH y cumplimiento urbanístico 2026. [Bucaramanga: Renovación Urbana y Edificabilidad en Altura], [Floridablanca: Uso Mixto, Centros Comerciales y Cañaveral]."
    },
    "MINERO BLINDADO": {
        "vectores": "Resolución 3824 ANM, Código de Minas, RUCOM.",
        "accion": "Respuesta a requerimientos ANM/CAR y control de vencimientos."
    },
    "ABOGADO IA 24/7": {
        "vectores": "Códigos Civil, Laboral, General del Proceso y Familia.",
        "accion": "Generación de minutas, tutelas y contratos generales."
    },
    "INMOBILIARIO USB 2026": {
        "vectores": "POT/EOT Local, Ley 675 (PH), Código Civil, Estatuto Notarial, Ley 1676, Ley 527.",
        "accion": "Generación MASIVA DOCUMENTAL INMOBILIARIA. Módulo PH: Redactar Reglamentos bajo Ley 675. Módulo Notarial: Minutas de escrituración y promesas. Módulo Asambleas: Actas y consejos. Módulo Arriendos: Contratos blindados con multisig."
    },
    "USB_PH_SERGIO": {
        "rol": "Especialista en Administración de Propiedad Horizontal y Convivencia",
        "vectores": ["ley_675_2001", "decreto_768_2025", "contratos_civiles_laborales"],
        "instruccion": """
            Eres el auditor legal de Guanes Inmobiliario para copropiedades.
            Tu objetivo es resolver conflictos de convivencia, auditar actas de asambleas y redactar 
            comunicaciones administrativas bajo el 'Lenguaje del Respiro' (tono empático y resolutivo).
            REGLA DE ORO: Aplica estrictamente la Ley 675 y el Decreto 768 de 2025 (regulación Airbnb y mascotas).
            CIERRE OBLIGATORIO: 'Certificado de Auditoría Preventiva Guanes Legaltech - Garantía 2026'.
            PROHIBIDO: Mencionar que eres una IA, Qwen, o usar términos técnicos como RAG o vectores.
        """
    },
    
    "USB_CONSTR_OLGA": {
        "rol": "Especialista en Blindaje de Proyectos y Responsabilidad Constructiva",
        "vectores": ["ley_1796_2016", "decreto_1166_2025", "pot_licencias"],
        "instruccion": """
            Eres el auditor legal de Guanes Legaltech para constructoras y desarrolladores inmobiliarios.
            Tu objetivo es blindar la responsabilidad civil del constructor revisando contratos de obra, 
            actas de entrega y estructuración jurídica inicial de PH.
            REGLA DE ORO: Aplica estrictamente la Ley 1796 de 2016 (Vicios Ocultos) y el Decreto 1166 de 2025.
            CIERRE OBLIGATORIO: 'Certificado de Auditoría Preventiva Guanes Legaltech - Garantía 2026'.
            PROHIBIDO: Mencionar que eres una IA, Qwen, o usar términos técnicos de software.
        """
    }
}

class GuanesEngine:
    def __init__(self, db_path=r"c:\AbogadoVirtual\03_Motor_Core\db_guanes"):
        self.client = chromadb.PersistentClient(path=db_path)
        self.coll_titulos = self.client.get_or_create_collection(name="titulos_valores")
        self.coll_urbanismo = self.client.get_or_create_collection(name="urbanismo_territorial")
        self.embeddings = OllamaEmbeddings(model="nomic-embed-text")
        self.llm = Ollama(model="guanes-senior")
        
        self.rag_prompt = PromptTemplate(
            input_variables=["context", "question", "perfil_rol", "perfil_vectores", "perfil_instruccion", "extra_context"],
            template="""
Contexto de Jurisprudencia: {context}
Contexto Adicional: {extra_context}
Usuario: {question}

Instrucción de Guanes IA:
Analiza la pregunta usando el contexto de nuestras 229 fuentes de verdad. 
Responde con el 'Lenguaje del Respiro' y cita siempre la norma vigente 2026.
Si es una consulta inmobiliaria, aplica estrictamente el Decreto 768 de 2025.

ESTÁS OPERANDO BAJO EL PERFIL: [{perfil_rol}]
VECTORES DE CONOCIMIENTO ESPERADOS: {perfil_vectores}
INSTRUCCIÓN ESPECÍFICA: {perfil_instruccion}
"""
        )

    def query(self, user_input, perfil_nombre="ABOGADO IA 24/7", extra_context=""):
        if perfil_nombre not in PROFILES:
            perfil_nombre = "ABOGADO IA 24/7"
            
        perfil_data = PROFILES[perfil_nombre]
        
        # Mapeo de campos por compatibilidad con perfiles viejos vs nuevos
        rol = perfil_data.get("rol", perfil_nombre)
        
        if "vectores" in perfil_data and isinstance(perfil_data["vectores"], list):
            vectores_str = ", ".join(perfil_data["vectores"])
        else:
            vectores_str = perfil_data.get("vectores", "")
            
        instruccion = perfil_data.get("instruccion", perfil_data.get("accion", ""))
        
        # 1. Clasificación simple de Tema adaptada
        temas_urbanismo = ["pot", "eot", "bucaramanga", "zapatoca", "lote", "construccion", "urbanismo", "suelo", "constructor", "ph", "arriendo", "reglamento", "acta", "asamblea", "notaria"]
        es_urbanismo = any(t in user_input.lower() for t in temas_urbanismo) or perfil_nombre in ["CONSTRUCTOR SEGURO", "INMOBILIARIO USB 2026", "USB_PH_SERGIO", "USB_CONSTR_OLGA"]
        
        collection = self.coll_urbanismo if es_urbanismo else self.coll_titulos
        
        # 2. Búsqueda Semántica
        results = collection.query(
            query_texts=[user_input],
            n_results=3
        )
        
        context = ""
        if results['documents'] and len(results['documents'][0]) > 0:
            context = "\n".join(results['documents'][0])
        
        if not context:
            context = "No se encontraron vectores específicos en ChromaDB, usa tu base de conocimientos legal colombiana y los vectores de tu perfil."

        # 3. Generación RAG con Perfil
        prompt = self.rag_prompt.format(
            context=context, 
            question=user_input, 
            perfil_rol=rol,
            perfil_vectores=vectores_str,
            perfil_instruccion=instruccion,
            extra_context=extra_context
        )
        raw_response = self.llm.invoke(prompt)
        
        # 4. Retornar respuesta limpia
        # El hash de Integridad y Aviso de Privacidad se omiten en el chat público
        # para mantener el tono consultivo. Solo se generan en modo PDF/offline.
        return raw_response

if __name__ == "__main__":
    # Prueba rápida del motor configurado con perfiles
    engine = GuanesEngine()
    print("🦅 Probando Guanes Engine V3 - Multi-Módulo...")
    
    test_query = "Me están negando unos servicios que necesita mi madre con urgencia (glosas injustificadas), ¿qué puedo hacer?"
    perfil_test = "GLOSAS BLINDADAS"
    
    print(f"\n[{perfil_test}] Query: {test_query}")
    res = engine.query(test_query, perfil_nombre=perfil_test)
    print(f"\nResultado:\n{res}")
