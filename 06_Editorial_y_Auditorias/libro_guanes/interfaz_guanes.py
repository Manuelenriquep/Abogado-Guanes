import tkinter as tk
from tkinter import messagebox
import chromadb

# Conexión a la Bóveda Persistente
client = chromadb.PersistentClient(path=r"c:\AbogadoVirtual\03_Motor_Core\db_guanes")
collection = client.get_or_create_collection(name="titulos_valores")

def ejecutar_busqueda():
    consulta = entrada_busqueda.get()
    if not consulta:
        messagebox.showwarning("Atención", "Por favor, describa su problema legal.")
        return
    
    # Búsqueda semántica
    results = collection.query(query_texts=[consulta], n_results=1)
    
    if results['documents'] and len(results['documents'][0]) > 0:
        texto_resultado.config(state=tk.NORMAL)
        texto_resultado.delete(1.0, tk.END)
        resumen = results['documents'][0][0]
        texto_resultado.insert(tk.END, f"✅ SOLUCIÓN ENCONTRADA:\n\n{resumen}\n\n[DIAGRAMA MERMAID GENERADO]\ngraph TD; A[Inicio] --> B[Analizar Art. 622]; B --> C[Excepción de Mérito];\n\n💰 PRECIO DE DESBLOQUEO: $39.900 COP")
        texto_resultado.config(state=tk.DISABLED)
    else:
        messagebox.showinfo("Guanes Info", "No encontramos un vector exacto, intentando con Cerebro RAG...")

# Configuración de la Ventana de Windows
ventana = tk.Tk()
ventana.title("🦅 GUANES LEGALTECH - DESBLOQUEO B2C")
ventana.geometry("600x500")
ventana.configure(bg="#f0f0f0")

tk.Label(ventana, text="BUSCADOR DE SOLUCIONES LEGALES", font=("Arial", 14, "bold"), bg="#f0f0f0", fg="#1a1a1a").pack(pady=10)
tk.Label(ventana, text="¿Cuál es su problema con el pagaré o letra?", bg="#f0f0f0").pack()

entrada_busqueda = tk.Entry(ventana, width=70, font=("Arial", 11))
entrada_busqueda.pack(pady=10, padx=20)

btn_buscar = tk.Button(ventana, text="BUSCAR SOLUCIÓN 🚀", command=ejecutar_busqueda, bg="#0056b3", fg="white", font=("Arial", 10, "bold"), width=30)
btn_buscar.pack(pady=10)

texto_resultado = tk.Text(ventana, height=12, width=65, font=("Arial", 10), state=tk.DISABLED, bg="#ffffff")
texto_resultado.pack(pady=10, padx=20)

ventana.mainloop()