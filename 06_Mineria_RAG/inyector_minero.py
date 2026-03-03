import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import os
import sys
import threading
import webbrowser
import datetime

core_path = r"c:\AbogadoVirtual\03_Motor_Core"
if core_path not in sys.path:
    sys.path.append(core_path)

try:
    from guanes_engine import GuanesEngine
except ImportError:
    messagebox.showerror("Error Severo", "No se encontró el núcleo guanes_engine.py.")
    sys.exit(1)

try:
    import chromadb
    from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False

DB_PATH = r"c:\AbogadoVirtual\03_Motor_Core\db_guanes"
COLLECTION_NAME = "auditoria_minera"

class GuanesMineroApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Guanes Minero Pro V1.0 - Evaluación Títular y RUCOM")
        self.root.geometry("1100x800")
        self.root.configure(bg="#2d3436") # Dark theme for mining
        
        self.engine = GuanesEngine()
        self.is_auditing = False
        
        self.collection = None
        if RAG_AVAILABLE:
            try:
                self.chroma_client = chromadb.PersistentClient(path=DB_PATH)
                self.collection = self.chroma_client.get_collection(name=COLLECTION_NAME, embedding_function=DefaultEmbeddingFunction())
            except Exception as e:
                print(f"Warning RAG Minero no cargado: {e}")
        
        self._build_ui()

    def _build_ui(self):
        header = tk.Frame(self.root, bg="#d63031", pady=15) # Red/Dark Header
        header.pack(fill=tk.X)
        tk.Label(header, text="GUANES MINERO PRO V1.0", font=("Segoe UI", 24, "bold"), fg="#ffffff", bg="#d63031").pack()
        tk.Label(header, text="Auditoría Legal de Exploración, Trazabilidad RUCOM y Explotación (Ley 685)", font=("Segoe UI", 12), fg="#f1f2f6", bg="#d63031").pack()

        # Split Screen Frame
        main_frame = tk.Frame(self.root, bg="#2d3436", padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        inputs_frame = tk.Frame(main_frame, bg="#2d3436")
        inputs_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        inputs_frame.columnconfigure(0, weight=1)
        inputs_frame.columnconfigure(1, weight=1)
        inputs_frame.rowconfigure(0, weight=1)
        
        # Left Pane: Título / Certificado RUCOM
        left_pane = tk.LabelFrame(inputs_frame, text=" 📜 CERTIFICADO RUCOM / TÍTULO MINERO ", font=("Segoe UI", 10, "bold"), bg="#636e72", fg="#ffffff", padx=10, pady=10)
        left_pane.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        top_left = tk.Frame(left_pane, bg="#636e72")
        top_left.pack(fill=tk.X, pady=(0, 5))
        tk.Button(top_left, text="Cargar Doc (Origen)", command=lambda: self.cargar_archivo(self.txt_origen), bg="#b2bec3", fg="#2d3436", relief=tk.FLAT).pack(side=tk.LEFT)
        
        self.txt_origen = scrolledtext.ScrolledText(left_pane, wrap=tk.WORD, font=("Consolas", 10), bd=1, relief=tk.SOLID, height=18)
        self.txt_origen.pack(fill=tk.BOTH, expand=True)
        self.txt_origen.insert(tk.END, "Pegue aquí el contenido del Certificado de Declaración de Producción o Inscripción RUCOM...")

        # Right Pane: Requerimiento ANM / Objeción
        right_pane = tk.LabelFrame(inputs_frame, text=" 🛑 REQUERIMIENTO ANM / OBJECCIÓN DE COMPRA ", font=("Segoe UI", 10, "bold"), bg="#a4b0be", fg="#2f3542", padx=10, pady=10)
        right_pane.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        
        top_right = tk.Frame(right_pane, bg="#a4b0be")
        top_right.pack(fill=tk.X, pady=(0, 5))
        tk.Button(top_right, text="Cargar Doc (Requerimiento)", command=lambda: self.cargar_archivo(self.txt_req), bg="#ffffff", fg="#2f3542", relief=tk.FLAT).pack(side=tk.LEFT)
        
        self.txt_req = scrolledtext.ScrolledText(right_pane, wrap=tk.WORD, font=("Consolas", 10), bd=1, relief=tk.SOLID, height=18)
        self.txt_req.pack(fill=tk.BOTH, expand=True)
        self.txt_req.insert(tk.END, "Pegue aquí la objeción de comercialización, orden de suspensión o requerimiento de la ANM / Alcaldía...")

        # Footer Actions
        footer_frame = tk.Frame(self.root, bg="#2d3436", padx=20, pady=10)
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.lbl_progreso = tk.Label(footer_frame, text="", font=("Segoe UI", 10, "italic"), bg="#2d3436", fg="#ffeaa7")
        self.lbl_progreso.pack(fill=tk.X, pady=(0, 5))
        self.progress = ttk.Progressbar(footer_frame, mode='indeterminate')

        btn_eval = tk.Button(footer_frame, text="⛏️ AUDITAR TRAZABILIDAD Y DERECHOS", command=self.ejecutar_evaluacion, font=("Segoe UI", 14, "bold"), bg="#e17055", fg="#ffffff", relief=tk.FLAT, pady=10)
        btn_eval.pack(fill=tk.X, pady=(10, 0))
        
    def cargar_archivo(self, text_widget):
        filepath = filedialog.askopenfilename(title="Seleccionar Archivo TXT", filetypes=[("Archivos Texto", "*.txt"), ("Todos", "*.*")])
        if filepath:
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                text_widget.delete("1.0", tk.END)
                text_widget.insert(tk.END, content)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo leer: {e}")

    def ejecutar_evaluacion(self):
        origen = self.txt_origen.get("1.0", tk.END).strip()
        req = self.txt_req.get("1.0", tk.END).strip()
        
        if len(origen) < 10 or len(req) < 10:
            messagebox.showwarning("Atención", "Proporcione datos completos de Origen del Mineral y del Requerimiento legal.")
            return

        self.progress.pack(fill=tk.X, pady=(0, 5))
        self.progress.start(15)
        self.is_auditing = True
        
        frases = [
            "Cruzando datos con SI.MINERO...",
            "Validando concordancia con Ley 685...",
            "Verificando cuotas RUCOM y trazabilidad comercial..."
        ]
        
        def rotar(idx):
            if self.is_auditing:
                self.lbl_progreso.config(text=frases[idx % len(frases)])
                self.root.after(2000, rotar, idx + 1)
        rotar(0)
        
        def tarea():
            try:
                contexto = ""
                if self.collection:
                    res = self.collection.query(query_texts=[req], n_results=3)
                    contexto = "\n".join(doc for doc in res["documents"][0])
                
                prompt = f"""Eres el "Minero Blindado", un auditor experto en el Código de Minas Colombiano (Ley 685) y la Resolución 3824 (RUCOM).
Tu objetivo es defender al titular minero o comercializador asegurando que se respete su derecho al debido proceso.

NORMATIVA RAG RECUPERADA:
{contexto}

--- DOCUMENTACIÓN DE ORIGEN (TÍTULO / CERTIFICADO COMERCIALIZADOR) ---
{origen}

--- REQUERIMIENTO O BLOQUEO DE LA ANM/ESTADO ---
{req}

INSTRUCCIONES:
1. Analiza las causales invocadas para bloquear el mineral de acuerdo a la Ley.
2. Determina si el Estado/Alcaldía está violando el derecho al trabajo y la libre comercialización (por ejemplo si el comercializador tiene su RUCOM al día).
3. Redacta de forma contundente (estilo "Abogado Minero Defensor") un Dictamen de Validación. Usa encabezados técnicos.
4. Indica si la suspensión/bloqueo es ILEGAL (Argumentable) o AJUSTADA A DERECHO.
"""
                resp = self.engine.query(prompt, perfil_nombre="Minero Blindado")
                self.root.after(0, self._mostrar, resp)
            except Exception as e:
                self.root.after(0, lambda e=e: messagebox.showerror("Error RAG/LLM", str(e)))
            finally:
                self.root.after(0, self._finalizar)

        threading.Thread(target=tarea, daemon=True).start()

    def _mostrar(self, resp):
        # Create a top level window with the result and export button
        top = tk.Toplevel(self.root)
        top.title("Dictamen Minero: Respuesta Jurídica")
        top.geometry("800x600")
        top.configure(bg="#f1f2f6")
        
        txt = scrolledtext.ScrolledText(top, wrap=tk.WORD, font=("Segoe UI", 11), bg="#ffffff", fg="#2d3436")
        txt.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        txt.insert(tk.END, resp)
        
    def _finalizar(self):
        self.is_auditing = False
        self.progress.stop()
        self.progress.pack_forget()
        self.lbl_progreso.config(text="")

if __name__ == "__main__":
    root = tk.Tk()
    app = GuanesMineroApp(root)
    root.mainloop()
