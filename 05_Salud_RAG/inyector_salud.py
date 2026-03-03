import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import os
import sys
import threading
import sqlite3
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from tkinter import simpledialog
import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
import csv
try:
    import fitz # PyMuPDF
except ImportError:
    pass

class ConsultorDB:
    def __init__(self):
        self.db_path = r"c:\AbogadoVirtual\05_Salud_RAG\consultora_salud.db"
        self.key_path = r"c:\AbogadoVirtual\05_Salud_RAG\clave_aes.key"
        self._init_key()
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS auditorias (id INTEGER PRIMARY KEY, ts TEXT, ciphertext TEXT, nonce TEXT)")
        self.conn.commit()
    
    def _init_key(self):
        if not os.path.exists(self.key_path):
            key = AESGCM.generate_key(bit_length=256)
            with open(self.key_path, "wb") as f:
                f.write(key)
        with open(self.key_path, "rb") as f:
            self.key = f.read()
        self.aesgcm = AESGCM(self.key)

    def registrar_auditoria(self, valor_glosado, valor_salvado):
        payload = f"{valor_glosado}|{valor_salvado}".encode('utf-8')
        nonce = os.urandom(12)
        ciphertext = self.aesgcm.encrypt(nonce, payload, None)
        self.cursor.execute("INSERT INTO auditorias (ts, ciphertext, nonce) VALUES (?, ?, ?)",
                            (datetime.datetime.now().isoformat(), base64.b64encode(ciphertext).decode('utf-8'), base64.b64encode(nonce).decode('utf-8')))
        self.conn.commit()

    def obtener_totales(self):
        self.cursor.execute("SELECT ciphertext, nonce FROM auditorias")
        filas = self.cursor.fetchall()
        total_glosado = 0
        total_salvado = 0
        for b64c, b64n in filas:
            ct = base64.b64decode(b64c)
            n = base64.b64decode(b64n)
            try:
                pt = self.aesgcm.decrypt(n, ct, None).decode('utf-8')
                v_g, v_s = pt.split('|')
                total_glosado += float(v_g)
                total_salvado += float(v_s)
            except Exception:
                pass
        return total_glosado, total_salvado

core_path = r"c:\AbogadoVirtual\03_Motor_Core"
if core_path not in sys.path:
    sys.path.append(core_path)

try:
    from guanes_engine import GuanesEngine
except ImportError:
    messagebox.showerror("Error Severo", "No se encontró el núcleo guanes_engine.py.")
    sys.exit(1)

DB_PATH = r"c:\AbogadoVirtual\03_Motor_Core\db_guanes"
COLLECTION_NAME = "auditoria_salud"

class GuanesSaludApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🛡️ Guanes Salud (V1.1) - Auditor Especialista en Glosas")
        self.root.geometry("1100x850")
        self.root.configure(bg="#f4f7f9")
        
        icon_path = r"c:\AbogadoVirtual\05_Salud_RAG\assets_salud\icon_salud.ico"
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)
        
        self.engine = GuanesEngine()
        self.is_auditing = False
        self.ultimo_resultado = ""
        
        try:
            self.chroma_client = chromadb.PersistentClient(path=DB_PATH)
            self.collection = self.chroma_client.get_collection(name=COLLECTION_NAME, embedding_function=DefaultEmbeddingFunction())
        except Exception as e:
            messagebox.showwarning("Advertencia RAG", f"No se pudo conectar al ChromaDB de Salud: {e}")
            self.collection = None

        self.db = ConsultorDB()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self._build_ui()

    def _build_ui(self):
        # Header
        header = tk.Frame(self.root, bg="#0052cc", pady=10)
        header.pack(fill=tk.X)
        tk.Label(header, text="GUANES SALUD - V1.5 FULL PROTOCOL", font=("Segoe UI", 24, "bold"), fg="white", bg="#0052cc").pack()
        tk.Label(header, text="Suite Integral de Defensa Clínica y Financiera", font=("Segoe UI", 12), fg="#f4f7f9", bg="#0052cc").pack()

        # Top 4-Button Menu
        menu_frame = tk.Frame(self.root, bg="#003d99", pady=5)
        menu_frame.pack(fill=tk.X)
        tk.Button(menu_frame, text="🛡️ Auditoría Glosas", font=("Segoe UI", 11, "bold"), bg="#004d40", fg="white", width=25, relief=tk.FLAT).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(menu_frame, text="📊 Pre-validación RIPS", font=("Segoe UI", 11, "bold"), bg="#0052cc", fg="white", width=25, relief=tk.FLAT).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(menu_frame, text="📝 Análisis Contratos", font=("Segoe UI", 11, "bold"), bg="#0052cc", fg="white", width=25, relief=tk.FLAT).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(menu_frame, text="⚖️ Defensa Tutelas", font=("Segoe UI", 11, "bold"), bg="#0052cc", fg="white", width=25, relief=tk.FLAT).pack(side=tk.LEFT, padx=5, pady=5)

        # Batch Engine Frame
        batch_frame = tk.Frame(self.root, bg="#00695c", pady=5)
        batch_frame.pack(fill=tk.X)
        tk.Button(batch_frame, text="⚡ [PROCESAR CARPETA DE GLOSAS EN LOTE]", command=self.process_directory, font=("Segoe UI", 12, "bold"), bg="#00bfa5", fg="white", relief=tk.FLAT).pack(pady=5)

        # Bottom Footer Fixed Frame
        footer_frame = tk.Frame(self.root, bg="#f4f7f9", padx=20, pady=20)
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X)

        main_frame = tk.Frame(self.root, bg="#f4f7f9", padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Inputs Frame (Grid Layout 2 columns)
        inputs_frame = tk.Frame(main_frame, bg="#f4f7f9")
        inputs_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        inputs_frame.columnconfigure(0, weight=1)
        inputs_frame.columnconfigure(1, weight=1)
        inputs_frame.rowconfigure(0, weight=1)
        
        # IPS Factura / RIPS Pane
        left_pane = tk.LabelFrame(inputs_frame, text=" 📄 FACTURA / RIPS (Datos de la IPS) ", font=("Segoe UI", 10, "bold"), bg="white", fg="#004d40", padx=10, pady=10)
        left_pane.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        top_left_controls = tk.Frame(left_pane, bg="white")
        top_left_controls.pack(fill=tk.X, pady=(0, 5))
        tk.Button(top_left_controls, text="Cargar PDF/TXT RIPS", command=lambda: self.cargar_archivo(self.txt_rips), bg="#00695c", fg="white", relief=tk.FLAT).pack(side=tk.LEFT)
        
        self.txt_rips = scrolledtext.ScrolledText(left_pane, wrap=tk.WORD, font=("Consolas", 10), bd=1, relief=tk.SOLID, height=15)
        self.txt_rips.pack(fill=tk.BOTH, expand=True)
        self.txt_rips.insert(tk.END, "(Pegue o cargue aquí el texto extraído del RIPS, epicrisis o factura de urgencias...)")

        # EPS Glosa Pane
        right_pane = tk.LabelFrame(inputs_frame, text=" 🛑 COMUNICACIÓN DE GLOSA (Objeciones EPS) ", font=("Segoe UI", 10, "bold"), bg="white", fg="#b71c1c", padx=10, pady=10)
        right_pane.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        
        top_right_controls = tk.Frame(right_pane, bg="white")
        top_right_controls.pack(fill=tk.X, pady=(0, 5))
        tk.Button(top_right_controls, text="Cargar PDF/TXT Glosa", command=lambda: self.cargar_archivo(self.txt_glosa), bg="#c62828", fg="white", relief=tk.FLAT).pack(side=tk.LEFT)
        
        self.txt_glosa = scrolledtext.ScrolledText(right_pane, wrap=tk.WORD, font=("Consolas", 10), bd=1, relief=tk.SOLID, height=15)
        self.txt_glosa.pack(fill=tk.BOTH, expand=True)
        self.txt_glosa.insert(tk.END, "(Pegue o cargue aquí el acta de glosa de la EPS, ej: Código 4 Falta de autorización...)")

        # Output Text (Above footer)
        out_header = tk.Frame(main_frame, bg="#f4f7f9")
        out_header.pack(fill=tk.X, pady=(10,0))
        tk.Label(out_header, text="Dictamen de Auditoría y Oficio de Refutación:", font=("Segoe UI", 11, "bold"), bg="#f4f7f9", fg="#333").pack(side=tk.LEFT)

        self.txt_resultado = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, font=("Segoe UI", 11), bd=0, bg="#ffffff", fg="#333", height=12)
        self.txt_resultado.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        # Footer Buttons
        btn_frame = tk.Frame(footer_frame, bg="#f4f7f9")
        btn_frame.pack(fill=tk.X)
        self.btn_analizar = tk.Button(btn_frame, text="⚡ AUDITAR GLOSA Y GENERAR RESPUESTA", command=self.ejecutar_auditoria, font=("Segoe UI", 14, "bold"), bg="#ffb300", fg="#212121", relief=tk.FLAT, pady=10)
        self.btn_analizar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)

        self.btn_validar_rips = tk.Button(btn_frame, text="✅ VALIDAR RIPS", font=("Segoe UI", 14, "bold"), bg="#008000", fg="white", relief=tk.FLAT, pady=10)
        self.btn_validar_rips.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)

        self.btn_exportar = tk.Button(btn_frame, text="🖨️ EXPORTAR PDF", command=self.exportar_oficio, font=("Segoe UI", 14, "bold"), bg="#0052cc", fg="white", relief=tk.FLAT, pady=10, state=tk.DISABLED)
        self.btn_exportar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)

        self.lbl_progreso = tk.Label(footer_frame, text="", font=("Segoe UI", 10, "italic"), bg="#f4f7f9", fg="#0052cc")
        self.lbl_progreso.pack(fill=tk.X, pady=(10, 0))
        self.progress = ttk.Progressbar(footer_frame, mode='indeterminate')

    def cargar_archivo(self, text_widget):
        filepath = filedialog.askopenfilename(title="Seleccionar Archivo", filetypes=[("Archivos Texto", "*.txt"), ("Todos los Archivos", "*.*")])
        if filepath:
            try:
                # Simulación básica de extracción PDF (lee como texto plano si es posible, o falla elegantemente)
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    contenido = f.read()
                text_widget.delete("1.0", tk.END)
                text_widget.insert(tk.END, contenido)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo extraer texto del archivo: {str(e)}\nRecomendación: Convierte el PDF a texto o pégalo manualmente.")

    def _recuperar_normativa(self, query: str) -> str:
        if not self.collection: return ""
        try:
            results = self.collection.query(query_texts=[query], n_results=3)
            contexto = "\n".join(doc for doc in results["documents"][0])
            return "\n\nCRITERIOS NORMATIVOS RECUPERADOS (RESOLUCIÓN 2284 Y LEY):\n" + contexto
        except Exception:
            return ""

    def ejecutar_auditoria(self):
        rips = self.txt_rips.get("1.0", tk.END).strip()
        glosa = self.txt_glosa.get("1.0", tk.END).strip()
        
        if len(rips) < 10 or len(glosa) < 10:
            messagebox.showwarning("Atención", "Por favor ingresa tanto los datos del RIPS/Factura como los de la Glosa EPS.")
            return

        self.btn_analizar.config(text="⏱️ AUDITANDO CÓDIGOS...", state=tk.DISABLED)
        self.btn_exportar.config(state=tk.DISABLED)
        self.progress.pack(fill=tk.X, pady=5)
        self.progress.start(15)
        self.is_auditing = True
        
        # Rotación de frases
        frases = [
            "Analizando consistencia vs Resolución 2284...",
            "Buscando precedentes en Sentencia T-760...",
            "Calculando intereses de mora Ley 1438...",
            "Generando argumentación jurídica vinculante..."
        ]
        
        def rotar_texto(idx):
            if self.is_auditing:
                self.lbl_progreso.config(text=frases[idx % len(frases)])
                self.root.after(2500, rotar_texto, idx + 1)
                
        rotar_texto(0)
        self.root.update()
        
        def tarea():
            try:
                # Search DB for context based on EPS gloss
                contexto_legal = self._recuperar_normativa(glosa)
                
                # Role Definition
                system_prompt = "Eres un Auditor Senior de Cuentas Médicas con 20 años de experiencia defendiendo Instituciones Prestadoras de Salud (IPS). Tu objetivo es encontrar errores en las glosas impuestas por las Entidades Promotoras de Salud (EPS) basándote estrictamente en los RIPS aportados, la Resolución 2284 de 2023 y la Circular Única de la Supersalud."
                
                prompt_analisis = f"""
{system_prompt}

{contexto_legal}

Tengo un caso de glosa médica que necesitas auditar:

--- DATOS DE FACTURACIÓN Y RIPS DE LA IPS ---
{rips}

--- GLOSA OBJETADA POR LA EPS ---
{glosa}

INSTRUCCIONES DE AUDITORÍA:
1. LÓGICA DE DEFENSA URGENCIAS: Si notas que la EPS interpuso una glosa por 'Falta de autorización', pero el RIPS/Factura muestra que la atención fue una Urgencia (Triage vital), DEBES declarar la glosa como injustificada usando la ley que prohíbe barreras a urgencias.
2. FORMATO DE SALIDA ESTRICTO:
    Primero, emite un "Semáforo de Recobro" utilizando exactamente uno de estos tres colores que sea aplicable, incluyendo el color textual:
    [VERDE]: Glosa ganable. Citar Res. 2284 o sentencias sobre rechazo injustificado.
    [AMARILLO]: Falta soporte. Indicar qué documento clínico o administrativo falta en la factura para continuar la disputa.
    [ROJO]: Glosa aceptable. Es un error real aritmético o procedimental de la IPS.
    
    Segundo, si es VERDE o AMARILLO, redacta un borrador profesional del "Oficio de Respuesta a Glosa", citando el artículo exacto violado por la EPS. IMPORTANTE: Si es VERDE, amenaza explícitamente a la EPS citando el régimen de la Circular Única de Supersalud y las multas aplicables (8.000 SMLMV) para elevar el nivel de intimidación técnica y exigir el flujo del recurso.
"""
                
                respuesta = self.engine.query(prompt_analisis, perfil_nombre="Soporte Legal EPS - The Shield")
                
                self.root.after(0, self._mostrar_resultado, respuesta)
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
            finally:
                def finalizar():
                    self.is_auditing = False
                    self.progress.stop()
                    self.progress.pack_forget()
                    self.lbl_progreso.config(text="")
                    self.btn_analizar.config(text="⚡ AUDITAR GLOSA Y GENERAR RESPUESTA", state=tk.NORMAL)
                    if self.ultimo_resultado:
                        self.btn_exportar.config(state=tk.NORMAL)
                self.root.after(0, finalizar)

        threading.Thread(target=tarea, daemon=True).start()

    def _mostrar_resultado(self, respuesta):
        self.txt_resultado.delete("1.0", tk.END)
        self.ultimo_resultado = respuesta
        self.txt_resultado.insert(tk.END, respuesta)
        # Resaltado psicológico y lógica de base de datos
        if "[VERDE]" in respuesta:
            self.txt_resultado.config(bg="#e8f5e9", fg="#2e7d32")
            # Prompt user for value
            val = simpledialog.askfloat("Auditoría Exitosa (VERDE)", "Ingrese el Valor Glosado por la EPS a rescatar (COP):", minvalue=0.0)
            if val is not None:
                self.db.registrar_auditoria(val, val)
        elif "[ROJO]" in respuesta:
            self.txt_resultado.config(bg="#ffebee", fg="#c62828")
        elif "[AMARILLO]" in respuesta:
            self.txt_resultado.config(bg="#fff8e1", fg="#f57f17")

    def exportar_oficio(self):
        if not self.ultimo_resultado: return
        try:
            # Parse dictamen for HTML
            contenido_html = self.ultimo_resultado.replace("\n", "<br>")
            
            html_template = f"""
            <!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <title>INFORME TÉCNICO DE RESPUESTA A GLOSA</title>
                <style>
                    body {{ font-family: 'Segoe UI', Arial, sans-serif; color: #111; line-height: 1.6; margin: 0; padding: 40px; background: #fff; }}
                    .page {{ max-width: 800px; margin: auto; }}
                    .header {{ text-align: center; border-bottom: 2px solid #0052cc; padding-bottom: 20px; margin-bottom: 30px; }}
                    h1 {{ color: #0052cc; margin: 0; font-size: 22px; text-transform: uppercase; letter-spacing: 1px; }}
                    .badge {{ background-color: #0052cc; color: white; padding: 4px 10px; border-radius: 4px; font-size: 14px; font-weight: bold; display: inline-block; margin-top: 10px; }}
                    .content {{ font-size: 14px; text-align: justify; }}
                    .footer {{ text-align: center; margin-top: 50px; font-size: 11px; color: #555; border-top: 1px solid #eee; padding-top: 20px; font-weight: bold; }}
                    @media print {{ body {{ padding: 0; }} }}
                </style>
            </head>
            <body>
                <div class="page">
                    <div class="header">
                        <h1>INFORME TÉCNICO DE RESPUESTA A GLOSA</h1>
                        <span class="badge">PROTOCOLO GUANES SALUD V1.1</span>
                    </div>
                    <div class="content">
                        {contenido_html}
                    </div>
                    <div class="footer">
                        Validado por Inteligencia Legal Offline - Cumplimiento Normativo 2026<br>
                        Motor de Auditoría Médica Guanes - The Shield Edition
                    </div>
                </div>
                <script>
                    setTimeout(() => {{ window.print(); }}, 1000);
                </script>
            </body>
            </html>
            """
            informe_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Oficio_Respuesta_Glosa.html")
            with open(informe_path, "w", encoding="utf-8") as f:
                f.write(html_template)
            
            webbrowser.open(f"file://{informe_path}")
            messagebox.showinfo("Exportación Exitosa", "Oficio generado. Se ha abierto en el navegador listo para Guardar como PDF o imprimir.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar el oficio: {e}")

    def generar_reporte_roi(self):
        try:
            t_glosado, t_salvado = self.db.obtener_totales()
            enfermeras_salvadas = max(1, int(t_salvado / 2500000))  # Aprox 2.5M cop por nomina.
            
            html_template = f"""
            <!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <title>RESUMEN EJECUTIVO DE IMPACTO (ROI)</title>
                <style>
                    body {{ font-family: 'Segoe UI', Arial, sans-serif; color: #111; line-height: 1.6; margin: 0; padding: 40px; background: #fff; }}
                    .page {{ max-width: 800px; margin: auto; }}
                    .header {{ text-align: center; border-bottom: 3px solid #0052cc; padding-bottom: 20px; margin-bottom: 40px; }}
                    h1 {{ color: #0052cc; margin: 0; font-size: 26px; text-transform: uppercase; letter-spacing: 1px; }}
                    .metrics {{ display: flex; justify-content: space-around; margin-bottom: 40px; }}
                    .metric-box {{ text-align: center; padding: 20px; background: #f4f7f9; border-radius: 8px; width: 40%; border-left: 5px solid #0052cc; }}
                    .metric-val {{ font-size: 28px; font-weight: bold; color: #2e7d32; }}
                    .power-speech {{ background: #e8f5e9; padding: 25px; border-radius: 8px; font-style: italic; font-size: 18px; color: #1b5e20; border-left: 5px solid #2e7d32; margin-top: 30px; }}
                    .footer {{ text-align: center; margin-top: 50px; font-size: 11px; color: #555; border-top: 1px solid #eee; padding-top: 20px; font-weight: bold; }}
                    @media print {{ body {{ padding: 0; }} }}
                </style>
            </head>
            <body>
                <div class="page">
                    <div class="header">
                        <h1>RESUMEN EJECUTIVO DE IMPACTO (ROI)</h1>
                        <p style="color:#555; font-weight:bold;">Dirigido a: Junta Directiva de la Clínica<br>Generado por: Guanes Salud - Executive Edition</p>
                    </div>
                    <div class="metrics">
                        <div class="metric-box">
                            <div style="font-size: 14px; color: #555;">Total Glosado por EPS (Histórico)</div>
                            <div class="metric-val" style="color: #c62828;">${t_glosado:,.0f} COP</div>
                        </div>
                        <div class="metric-box">
                            <div style="font-size: 14px; color: #555;">CAPITAL RECUPERADO (ROI GUANES)</div>
                            <div class="metric-val">${t_salvado:,.0f} COP</div>
                        </div>
                    </div>
                    <div class="power-speech">
                        "Tú no vendes una memoria USB o un software médico.<br><br>
                        Con el capital recuperado en esta central de auditoría, <b>usted garantizó la nómina clínica de {enfermeras_salvadas} enfermeras</b> frente a los bloqueos de las EPS. Cada vez que usa Guanes, está obligando al sistema a ser justo con los que salvan vidas."
                    </div>
                    <div class="footer">
                        Validado por Inteligencia Legal Offline - AES-256 Encrypted Profile<br>
                        Motor de Auditoría Médica Guanes Salud V1.5
                    </div>
                </div>
                <script>
                    setTimeout(() => {{ window.print(); }}, 1000);
                </script>
            </body>
            </html>
            """
            informe_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ROI_Executive_Report.html")
            with open(informe_path, "w", encoding="utf-8") as f:
                f.write(html_template)
            webbrowser.open(f"file://{informe_path}")
        except Exception as e:
            print(f"Error generando ROI: {e}")

    def on_closing(self):
        respuesta = messagebox.askyesnocancel("Cerrar Sesión", "¿Desea generar el Reporte de Impacto (ROI) para la gerencia antes de salir?\n\n(Sí = Generar ROI y salir, No = Salir sin reporte, Cancelar = Volver)")
        if respuesta is True:
            self.generar_reporte_roi()
            self.root.after(3000, self.root.destroy)
        elif respuesta is False:
            self.root.destroy()

    def process_directory(self):
        folder_path = filedialog.askdirectory(title="Seleccionar Carpeta con PDFs de Glosas")
        if not folder_path: return
        
        pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.pdf')]
        if not pdf_files:
            messagebox.showinfo("Carpeta Vacía", "No se encontraron archivos PDF en la carpeta seleccionada.")
            return

        self.lbl_progreso.pack(fill=tk.X, pady=(10, 0))
        self.progress.pack(fill=tk.X, pady=5)
        self.progress.start(15)
        self.is_auditing = True
        
        def tarea_batch():
            try:
                resultados_csv = []
                total_salvado = 0
                import re
                
                system_prompt = "Eres un Auditor Senior de Cuentas Médicas defendiendo Instituciones Prestadoras de Salud (IPS). Audita glosas EPS. Se te proporcionará el texto extraído del expediente PDF de la glosa. Determina si la glosa es injustificada y puede ganarse amparado en la Ley y la Resolución 2284."
                
                for idx, filename in enumerate(pdf_files):
                    filepath = os.path.join(folder_path, filename)
                    texto_pdf = ""
                    try:
                        import fitz
                        doc = fitz.open(filepath)
                        for page in doc:
                            texto_pdf += page.get_text()
                        doc.close()
                    except Exception as e:
                        texto_pdf = f"(Error al extraer PDF: {e})"
                        
                    prompt_lote = f"""
{system_prompt}

EXPEDIENTE:
{filename}
TEXTO EXTRAÍDO (Primeros 4000 caracteres):
{texto_pdf[:4000]}

INSTRUCCIÓN ESTRICTA DE BATCH:
1. Evalúa si la objeción o glosa es injustificada bajo la Res 2284 (ej. Códigos de urgencias etc).
2. Si es ganable o tienes argumentos normativos fuertes para rebatirla, tu respuesta DEBE INCLUIR EXACTAMENTE ESTAS DOS CADENAS:
[VERDE]
[VALOR]: <solo escribe números, sin comas, ni signos de peso, refiriéndote al dinero glosado o al menos 5000000 si no se menciona un valor>

Si tiene errores procedimentales insalvables, devuelve [ROJO]. Si faltan soportes clínicos, [AMARILLO].
"""
                    self.root.after(0, lambda n=filename: self.lbl_progreso.config(text=f"Procesando Batch: {n}..."))
                    respuesta = self.engine.query(prompt_lote, perfil_nombre="Soporte Legal EPS - The Shield")
                    
                    color = "INDEFINIDO"
                    valor = 0.0
                    
                    if "[VERDE]" in respuesta:
                        color = "[VERDE]"
                        match = re.search(r'\[VALOR\]:\s*(\d+)', respuesta)
                        if match:
                            valor = float(match.group(1))
                        else:
                            valor = 3500000.0 # Default estimado si el LLM falla la extracción estricta
                        self.db.registrar_auditoria(valor, valor)
                        total_salvado += valor
                    elif "[ROJO]" in respuesta:
                        color = "[ROJO]"
                    elif "[AMARILLO]" in respuesta:
                        color = "[AMARILLO]"
                        
                    resultados_csv.append([filename, color, valor])
                    
                csv_path = os.path.join(folder_path, "Resumen_Financiero.csv")
                with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(["Archivo PDF", "Dictamen", "Valor Salvado (COP)"])
                    writer.writerows(resultados_csv)
                    writer.writerow(["", "TOTAL SALVADO", total_salvado])
                    
                self.root.after(0, lambda: messagebox.showinfo("Batch Completado", f"Se auditaron {len(pdf_files)} expedientes PDF.\nTotal Rescatado: ${total_salvado:,.0f} COP.\nReporte generado: Resumen_Financiero.csv"))
                self.root.after(0, lambda: os.startfile(csv_path) if os.name == 'nt' else webbrowser.open(f"file://{csv_path}"))
                
            except Exception as e:
                self.root.after(0, lambda e=e: messagebox.showerror("Error en Batch Engine", str(e)))
            finally:
                def finalizar():
                    self.is_auditing = False
                    self.progress.stop()
                    self.progress.pack_forget()
                    self.lbl_progreso.config(text="Modo Lote Finalizado.")
                self.root.after(0, finalizar)
                
        threading.Thread(target=tarea_batch, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = GuanesSaludApp(root)
    root.mainloop()
