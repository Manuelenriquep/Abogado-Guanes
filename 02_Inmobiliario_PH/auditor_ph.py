import os
import glob
from langchain_community.llms import Ollama
from langchain_community.document_loaders import PyPDFLoader
from fpdf import FPDF
import datetime

# --- CONFIGURACIÓN ---
DIR_ENTRADA = r"c:\AbogadoVirtual\02_Inmobiliario_PH\Reglamentos_Entrada"
DIR_SALIDA = r"c:\AbogadoVirtual\02_Inmobiliario_PH\Informes_Auditoria"
MODELO_LLM = "qwen3:8b-q4_K_M"

os.makedirs(DIR_ENTRADA, exist_ok=True)
os.makedirs(DIR_SALIDA, exist_ok=True)

llm = Ollama(model=MODELO_LLM, temperature=0.1)

# --- PROMPT AUDITORÍA PH ---
PROMPT_AUDITORIA_PH = """
Eres el Consultor Senior de Guanes IA (2026), experto en Propiedad Horizontal.
Analiza el siguiente extracto de un Reglamento de Propiedad Horizontal (PH) y emite un concepto de legalidad estricto.

Reglas de Oro:
1. MASCOTAS: La prohibición absoluta de mascotas es ILEGAL (jurisprudencia constitucional consolidada).
2. AIRBNB/PLATAFORMAS: Busca regulación sobre arrendamiento a corto plazo. Si no se permite explícitamente o choca con el Decreto 768 de 2025, es una Red Flag.
3. COEFICIENTES: Verifica la mención a coeficientes de copropiedad (Ley 675 de 2001).

EXTRACTO DEL REGLAMENTO:
{texto}

INSTRUCCIÓN:
Redacta tu análisis en formato de viñetas claras abordando cada uno de los 3 puntos (Mascotas, Plataformas, Coeficientes). Usa el 'Lenguaje del Respiro' pero sé implacable con los hallazgos de ilegalidad.
"""

def procesar_reglamento(ruta_pdf):
    print(f"\n🔍 Procesando: {os.path.basename(ruta_pdf)}")
    try:
        loader = PyPDFLoader(ruta_pdf)
        pages = loader.load_and_split()
        
        texto_completo = " ".join([p.page_content for p in pages])
        # Tomar los primeros 8000 caracteres para no saturar el contexto si el PDF es muy grande
        texto_analisis = texto_completo[:8000] 

        prompt_final = PROMPT_AUDITORIA_PH.format(texto=texto_analisis)
        print("🧠 Consultando a Guanes IA...")
        respuesta = llm.invoke(prompt_final)
        return respuesta

    except Exception as e:
        return f"Error leyendo el PDF: {str(e)}"

def generar_pdf_informe(nombre_archivo_base, analisis_texto):
    fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d")
    nombre_informe = f"Informe_PH_{nombre_archivo_base}_{fecha_actual}.pdf"
    ruta_informe = os.path.join(DIR_SALIDA, nombre_informe)

    pdf = FPDF()
    pdf.add_page()
    
    # Fuentes y colores (Simulando branding)
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(0, 51, 102) # Azul oscuro profesional
    
    # Encabezado
    pdf.cell(0, 10, "Informe de Riesgos de Propiedad Horizontal", ln=True, align='C')
    pdf.set_font("Arial", 'I', 12)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, "Auditora: Guanes IA - Ecosistema Legaltech", ln=True, align='C')
    pdf.ln(10)
    
    # Metadatos
    pdf.set_font("Arial", 'B', 11)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(40, 10, f"Documento Base: {nombre_archivo_base}")
    pdf.ln(6)
    pdf.cell(40, 10, f"Fecha Análisis: {fecha_actual}")
    pdf.ln(15)

    # Contenido (Con manejo básico de tildes para PDF estandar)
    pdf.set_font("Arial", '', 11)
    # Reemplazo rapido de caracteres latinos no soportados nativamente por FPDF sin unicode
    texto_seguro = analisis_texto.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 6, texto_seguro)
    
    # Pie de pagina de autoridad
    pdf.ln(10)
    pdf.set_font("Arial", 'I', 9)
    pdf.set_text_color(150, 150, 150)
    footer_text = "Información extraída de nuestra fuente de verdad blindada. Para documentos oficiales listos para radicar, active su acceso premium."
    pdf.multi_cell(0, 5, footer_text.encode('latin-1', 'replace').decode('latin-1'))

    pdf.output(ruta_informe)
    print(f"📄 Informe guardado: {ruta_informe}")

if __name__ == "__main__":
    pdfs_entrada = glob.glob(os.path.join(DIR_ENTRADA, "*.pdf"))
    
    if not pdfs_entrada:
        print(f"⚠️ No hay archivos PDF en la bandeja de entrada: {DIR_ENTRADA}")
        print("💡 Por favor, coloca un Reglamento (.pdf) allí para probar la auditoría.")
    else:
        for pdf_path in pdfs_entrada:
            nombre_base = os.path.splitext(os.path.basename(pdf_path))[0]
            analisis = procesar_reglamento(pdf_path)
            generar_pdf_informe(nombre_base, analisis)
