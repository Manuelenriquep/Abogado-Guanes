import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading
import sys
import os
sys.path.append(r"c:\AbogadoVirtual\03_Motor_Core")
from guanes_engine import GuanesEngine

# Configuración Estética Pro
COLOR_PRIMARIO = "#002D62"  # Azul Guanes
COLOR_SECUNDARIO = "#FFD700" # Dorado Legal
COLOR_FONDO = "#F4F7F6"      # Gris Suave Premium
COLOR_TEXTO = "#1A1A1A"      # Negro Elegante
COLOR_BOTON = "#0056b3"      # Azul Acción

class GuanesGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🦅 GUANES LEGALTECH - DESBLOQUEO B2C (PREMIUM)")
        self.root.geometry("800x700")
        self.root.configure(bg=COLOR_FONDO)
        
        # Inicializar el Engine
        self.engine = GuanesEngine()
        
        self.setup_ui()

    def setup_ui(self):
        # Header / Branding
        header_frame = tk.Frame(self.root, bg=COLOR_PRIMARIO, height=80)
        header_frame.pack(fill=tk.X)
        
        tk.Label(header_frame, text="🦅 GUANES LEGALTECH", 
                 font=("Helvetica", 20, "bold"), bg=COLOR_PRIMARIO, fg="white").pack(pady=10)
        tk.Label(header_frame, text="Arquitectura Legal: Títulos Valores & Urbanismo", 
                 font=("Helvetica", 10), bg=COLOR_PRIMARIO, fg="#E0E0E0").pack()

        # Input Section
        input_frame = tk.Frame(self.root, bg=COLOR_FONDO)
        input_frame.pack(pady=20, padx=40, fill=tk.X)

        tk.Label(input_frame, text="¿Cuál es su problema legal? (Pagarés o Lotes/POT)", 
                 font=("Helvetica", 12, "bold"), bg=COLOR_FONDO, fg=COLOR_TEXTO).pack(anchor=tk.W)

        self.entrada_busqueda = tk.Entry(input_frame, font=("Helvetica", 12), bd=2, relief=tk.FLAT)
        self.entrada_busqueda.pack(pady=10, fill=tk.X, ipady=10)
        self.entrada_busqueda.insert(0, "Ej: ¿Qué puedo construir en mi lote en Bucaramanga?")

        # Botón de Acción
        self.btn_buscar = tk.Button(input_frame, text="OBTENER SOLUCIÓN ESTRATÉGICA 🚀", 
                                  command=self.iniciar_busqueda_asincrona, 
                                  bg=COLOR_BOTON, fg="white", font=("Helvetica", 11, "bold"), 
                                  relief=tk.RAISED, bd=5, cursor="hand2")
        self.btn_buscar.pack(pady=10, fill=tk.X)

        # Output Section
        output_frame = tk.Frame(self.root, bg=COLOR_FONDO)
        output_frame.pack(pady=10, padx=40, fill=tk.BOTH, expand=True)

        tk.Label(output_frame, text="REPORTE DE ESTRATEGIA LEGAL:", 
                 font=("Helvetica", 10, "bold"), bg=COLOR_FONDO, fg=COLOR_TEXTO).pack(anchor=tk.W)

        self.texto_resultado = scrolledtext.ScrolledText(output_frame, height=15, 
                                                       font=("Consolas", 10), state=tk.DISABLED, 
                                                       bg="#FFFFFF", fg=COLOR_TEXTO, bd=2)
        self.texto_resultado.pack(pady=5, fill=tk.BOTH, expand=True)

        # Footer
        footer_label = tk.Label(self.root, text="Sincronizado con Guanes Senior v2.0 | ChromaDB Persistente © 2026", 
                                font=("Helvetica", 8), bg=COLOR_FONDO, fg="#888888")
        footer_label.pack(side=tk.BOTTOM, pady=10)

    def iniciar_busqueda_asincrona(self):
        consulta = self.entrada_busqueda.get()
        if not consulta or "Ej:" in consulta:
            messagebox.showwarning("Atención", "Por favor, detalle su caso para el análisis vectorizado.")
            return

        # Deshabilitar UI durante proceso
        self.btn_buscar.config(state=tk.DISABLED, text="CONSULTANDO CEREBRO RAG... 🧠")
        self.texto_resultado.config(state=tk.NORMAL)
        self.texto_resultado.delete(1.0, tk.END)
        self.texto_resultado.insert(tk.END, "Iniciando análisis semántico de 359 vectores...\nBuscando excepciones en el Art. 622...\nGenerando ruta crítica...\n")
        self.texto_resultado.config(state=tk.DISABLED)

        # Hilo para no congelar la GUI
        thread = threading.Thread(target=self.ejecutar_proceso, args=(consulta,))
        thread.start()

    def ejecutar_proceso(self, consulta):
        try:
            respuesta = self.engine.query(consulta)
            
            # Actualizar GUI en el hilo principal
            self.root.after(0, self.mostrar_resultado, respuesta)
        except Exception as e:
            self.root.after(0, self.mostrar_error, str(e))

    def mostrar_resultado(self, respuesta):
        self.texto_resultado.config(state=tk.NORMAL)
        self.texto_resultado.delete(1.0, tk.END)
        self.texto_resultado.insert(tk.END, respuesta)
        self.texto_resultado.config(state=tk.DISABLED)
        self.btn_buscar.config(state=tk.NORMAL, text="OBTENER SOLUCIÓN ESTRATÉGICA 🚀")

    def mostrar_error(self, error):
        messagebox.showerror("Error de Conexión", f"Error en el motor Guanes: {error}")
        self.btn_buscar.config(state=tk.NORMAL, text="REINTENTAR 🔄")

if __name__ == "__main__":
    root = tk.Tk()
    app = GuanesGUI(root)
    root.mainloop()
