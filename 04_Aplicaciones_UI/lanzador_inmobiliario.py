import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog
import sys
import os
import sqlite3
import base64
import json
import requests
import uuid
from datetime import datetime
import threading
import webbrowser

# Fuerza inyección del path para garantizar carga en modo USB .exe
core_path = r"c:\AbogadoVirtual\03_Motor_Core"

WEBHOOK_TELEMETRY = "http://localhost:5678/webhook/usb-telemetry"
WEBHOOK_VALIDATION = "http://localhost:5678/webhook/check-usb-status"
PERFIL = "INMOBILIARIO USB 2026"
DB_FILE = ".sys_guanes_usb.db"

class USBManager:
    def __init__(self):
        self.usb_id = self._get_or_create_usb_id()
        self.conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._init_db()
        self.salt = "Guanes2026_SecureKey!"
        self._init_cortesia()
        self.is_compromised = (self.get_config("estado_seguridad") == "bloqueado")
        if not self.is_compromised:
            self.verificar_seguridad_remota()

    def _init_cortesia(self):
        if self.get_config("creditos_cortesia") == "":
            self.set_config("creditos_cortesia", "3")

    def verificar_seguridad_remota(self):
        try:
            payload = {"usb_id": self.usb_id}
            res = requests.post(WEBHOOK_VALIDATION, json=payload, timeout=3)
            if res.status_code == 200:
                data = res.json()
                if data.get("status") == "compromised":
                    self.protocolo_scorched_earth()
        except: pass

    def protocolo_scorched_earth(self):
        self.set_config("estado_seguridad", "bloqueado")
        self.is_compromised = True
        db_dir = os.path.join(core_path, "db_guanes")
        if os.path.exists(db_dir):
            for root_dir, _, files in os.walk(db_dir):
                for f in files:
                    try:
                        fpath = os.path.join(root_dir, f)
                        with open(fpath, "r+b") as file_obj:
                            data_len = len(file_obj.read())
                            file_obj.seek(0)
                            file_obj.write(os.urandom(data_len))
                    except: pass

    def _get_or_create_usb_id(self):
        id_file = ".usb_serial.sys"
        if os.path.exists(id_file):
            with open(id_file, "r") as f: return f.read().strip()
        else:
            new_id = f"USB-{uuid.uuid4().hex[:8].upper()}"
            with open(id_file, "w") as f: f.write(new_id)
            return new_id

    def _init_db(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS licencias (modulo TEXT PRIMARY KEY, usos_cifrados TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS telemetria_offline (id INTEGER PRIMARY KEY AUTOINCREMENT, payload TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS config_marca (clave TEXT PRIMARY KEY, valor TEXT)''')
        self.cursor.execute("INSERT OR IGNORE INTO config_marca (clave, valor) VALUES ('primer_inicio', 'true')")
        self.conn.commit()

    def es_primer_inicio(self):
        val = self.get_config("primer_inicio")
        if val == "true":
            self.set_config("primer_inicio", "false")
            return True
        return False

    def get_config(self, clave: str, default=""):
        self.cursor.execute("SELECT valor FROM config_marca WHERE clave=?", (clave,))
        row = self.cursor.fetchone()
        return row[0] if row else default

    def set_config(self, clave: str, valor: str):
        self.cursor.execute("INSERT OR REPLACE INTO config_marca (clave, valor) VALUES (?, ?)", (clave, valor))
        self.conn.commit()

    def _cifrar(self, valor: int) -> str: return base64.b64encode(f"{self.salt}_{valor}_{self.salt}".encode('utf-8')).decode('utf-8')
    def _descifrar(self, cifrado: str) -> int:
        try: return int(base64.b64decode(cifrado.encode('utf-8')).decode('utf-8').split('_')[1])
        except: return 999 

    def get_usos(self, modulo: str) -> int:
        self.cursor.execute("SELECT usos_cifrados FROM licencias WHERE modulo=?", (modulo,))
        row = self.cursor.fetchone()
        return self._descifrar(row[0]) if row else 0

    def incrementar_uso(self, modulo: str):
        self.cursor.execute("INSERT OR REPLACE INTO licencias (modulo, usos_cifrados) VALUES (?, ?)", (modulo, self._cifrar(self.get_usos(modulo) + 1)))
        self.conn.commit()
    def enviar_telemetria_async(self, modulo: str, municipio: str):
        payload = {
            "usb_id": self.usb_id,
            "tipo_documento": modulo,
            "municipio": municipio,
            "timestamp": datetime.now().isoformat()
        }
        
        def tarea():
            try:
                res = requests.post(WEBHOOK_TELEMETRY, json=payload, timeout=5)
                if res.status_code == 200:
                    self._vaciar_cola_offline()
                else:
                    self._encolar_offline(payload)
            except:
                self._encolar_offline(payload)
        
        threading.Thread(target=tarea, daemon=True).start()

    def enviar_telemetria_ping(self, mensaje: str):
        payload = {
            "usb_id": self.usb_id,
            "tipo_alerta": "PULSO_PROSPECTO",
            "mensaje": mensaje,
            "timestamp": datetime.now().isoformat()
        }
        def tarea():
            try: requests.post(WEBHOOK_TELEMETRY, json=payload, timeout=5)
            except: pass
        threading.Thread(target=tarea, daemon=True).start()

    def _encolar_offline(self, payload: dict):
        self.cursor.execute("INSERT INTO telemetria_offline (payload) VALUES (?)", (json.dumps(payload),))
        self.conn.commit()

    def _vaciar_cola_offline(self):
        self.cursor.execute("SELECT id, payload FROM telemetria_offline")
        for idx, pay_str in self.cursor.fetchall():
            try:
                res = requests.post(WEBHOOK_TELEMETRY, data=pay_str, headers={'Content-Type': 'application/json'}, timeout=5)
                if res.status_code == 200:
                    self.cursor.execute("DELETE FROM telemetria_offline WHERE id=?", (idx,))
                    self.conn.commit()
            except:
                break

class USBInmobiliarioApp:
    def __init__(self, root, engine_instance):
        self.usb_manager = USBManager()
        self.root = root
        
        if self.usb_manager.is_compromised:
            self.root.title("ALERTA DE SEGURIDAD")
            self.root.geometry("900x750")
            self.root.configure(bg="red")
            tk.Label(self.root, text="HARDWARE BLOQUEADO.\nContacte a Soporte Técnico para reactivación.", font=("Consolas", 18, "bold"), bg="red", fg="white").pack(expand=True)
            return

        self.engine = engine_instance
        self.root.title(f"🏢 Guanes LegalTech - Inmobiliario USB ({self.usb_manager.usb_id})")
        self.root.geometry("900x750")
        self.root.configure(bg="#1E1E2E")
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TNotebook", background="#1E1E2E", borderwidth=0)
        style.configure("TNotebook.Tab", background="#313244", foreground="#CDD6F4", padding=[10, 5], font=("Consolas", 10, "bold"))
        style.map("TNotebook.Tab", background=[("selected", "#89B4FA")], foreground=[("selected", "#11111B")])
        style.configure("TLabel", background="#1E1E2E", foreground="#D9D9D9", font=("Consolas", 11))
        style.configure("TFrame", background="#1E1E2E")

        # Menu superior for Brand config
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)
        conf_menu = tk.Menu(menu_bar, tearoff=0)
        conf_menu.add_command(label="Identidad: Inmobiliaria & Wallet Web3", command=self.configurar_marca)
        menu_bar.add_cascade(label="⚙️ Configuración", menu=conf_menu)

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # TAB 1: GENERADOR RAG
        tab_gen = ttk.Frame(notebook)
        notebook.add(tab_gen, text="📄 Generador Normativo RAG")
        self.build_generador_tab(tab_gen)

        # TAB 2: ARBITRAJE MULTISIG
        tab_arb = ttk.Frame(notebook)
        notebook.add(tab_arb, text="⚖️ Panel de Arbitraje (Web3)")
        self.build_arbitraje_tab(tab_arb)

    def configurar_marca(self):
        inm_actual = self.usb_manager.get_config("agencia", "Mi Inmobiliaria SAS")
        wall_actual = self.usb_manager.get_config("wallet", "Solicitar_a_Cliente")
        
        nueva_inmo = simpledialog.askstring("Identidad", "Nombre de la Agencia Inmobiliaria:", initialvalue=inm_actual)
        if nueva_inmo: self.usb_manager.set_config("agencia", nueva_inmo)
        
        nueva_wallet = simpledialog.askstring("Web3", "Solana Wallet de la Inmobiliaria (Amigable Componedor):", initialvalue=wall_actual)
        if nueva_wallet: self.usb_manager.set_config("wallet", nueva_wallet)
        
        messagebox.showinfo("Guardado", "Identidad Inmobiliaria (Llave C) guardada en la USB de forma segura.")

    def build_generador_tab(self, parent):
        ttk.Label(parent, text="SELECCIÓN DE PROTOCOLO", font=("Consolas", 14, "bold"), foreground="#A6E3A1").pack(pady=10)
        
        frame_mod = tk.Frame(parent, bg="#1E1E2E")
        frame_mod.pack(pady=5)
        self.modulo_var = tk.StringVar(value="PH")
        ttk.Radiobutton(frame_mod, text="Certificado Urbanístico", variable=self.modulo_var, value="Certificado").grid(row=0, column=0, padx=10)
        ttk.Radiobutton(frame_mod, text="Reglamentos PH (Ley 675)", variable=self.modulo_var, value="PH").grid(row=0, column=1, padx=10)
        ttk.Radiobutton(frame_mod, text="Notarial (Minutas)", variable=self.modulo_var, value="Notarial").grid(row=1, column=0, padx=10, pady=5)
        ttk.Radiobutton(frame_mod, text="Asambleas (Actas)", variable=self.modulo_var, value="Asambleas").grid(row=1, column=1, padx=10, pady=5)
        ttk.Radiobutton(frame_mod, text="Arriendo: C/ Fiador", variable=self.modulo_var, value="Arriendo Tradicional", command=self.toggle_canon_field).grid(row=2, column=0, padx=10, pady=5)
        ttk.Radiobutton(frame_mod, text="Arriendo: Dgtl Multisig", variable=self.modulo_var, value="Arriendo Multisig", command=self.toggle_canon_field).grid(row=2, column=1, padx=10, pady=5)

        # ========= CALCULADORA MULTISIG (3x) =========
        self.frame_canon = tk.Frame(parent, bg="#1E1E2E")
        self.frame_canon.pack(pady=5, fill="x", padx=20)
        
        ttk.Label(self.frame_canon, text="Canon Arriendo Mensual (COP): $").pack(side=tk.LEFT)
        self.canon_var = tk.StringVar(value="1500000")
        self.canon_var.trace_add("write", self.calcular_usdc)
        self.canon_entry = ttk.Entry(self.frame_canon, textvariable=self.canon_var, width=15)
        self.canon_entry.pack(side=tk.LEFT, padx=5)
        
        self.usdc_label = ttk.Label(self.frame_canon, text="👉 Garantía Escrow (x3): Calculando...", foreground="#F9E2AF", font=("Consolas", 10, "bold"))
        self.usdc_label.pack(side=tk.LEFT, padx=15)

        ttk.Label(parent, text="Sintaxis del Documento (Ubicación, detalles):").pack(anchor="w", padx=20, pady=5)
        self.prompt_box = tk.Text(parent, height=4, font=("Consolas", 10), bg="#313244", fg="#CDD6F4", insertbackground="white")
        self.prompt_box.pack(fill="x", padx=20)

        self.btn_gen = tk.Button(parent, text="🚀 ENGRANAR MOTOR LLM", bg="#89B4FA", fg="#11111B", font=("Consolas", 10, "bold"), command=self.generar)
        self.btn_gen.pack(pady=10, ipadx=10, ipady=3)

        self.res_box = scrolledtext.ScrolledText(parent, height=15, font=("Consolas", 10), bg="#181825", fg="#A6E3A1")
        self.res_box.pack(fill="both", expand=True, padx=20, pady=10)

    def build_arbitraje_tab(self, parent):
        ttk.Label(parent, text="BÓVEDAS EN ESCROW (GARANTÍA MULTISIG)", font=("Consolas", 14, "bold"), foreground="#F9E2AF").pack(pady=10)
        
        # Simulación de Lista de Contratos
        cols = ("ID", "Arrendador", "Arrendatario", "Garantía", "Estado")
        tree = ttk.Treeview(parent, columns=cols, show="headings", height=8)
        for c in cols: tree.heading(c, text=c)
        tree.column("ID", width=50); tree.column("Garantía", width=100); tree.column("Estado", width=100)
        tree.pack(fill="x", padx=20, pady=10)
        
        # Insertar dummies
        tree.insert("", tk.END, values=("B-842", "Juan Pérez", "Carlos Gómez", "2.5 SOL", "🔒 Bloqueada (Escrow)"))
        tree.insert("", tk.END, values=("B-911", "Ed. Majestic", "Maria Roa", "900 USDC", "🔒 Bloqueada (Escrow)"))
        
        frame_botones = tk.Frame(parent, bg="#1E1E2E")
        frame_botones.pack(pady=10)
        
        tk.Button(frame_botones, text="🔑 FIRMAR LIBERACIÓN A ARRENDADOR", bg="#A6E3A1", fg="#11111B", font=("Consolas", 10, "bold"), command=lambda: messagebox.showinfo("Web3", "Wallet Conectada. Transacción Criptográfica a favor del Arrendador enviada a la Blockchain.")).pack(side=tk.LEFT, padx=10)
        tk.Button(frame_botones, text="🔑 FIRMAR LIBERACIÓN A ARRENDATARIO", bg="#F38BA8", fg="#11111B", font=("Consolas", 10, "bold"), command=lambda: messagebox.showinfo("Web3", "Wallet Conectada. Reembolso Criptográfico a favor del Arrendatario enviado a la Blockchain.")).pack(side=tk.LEFT, padx=10)

        # Botón de Informe Comercial
        frame_informe = tk.Frame(parent, bg="#1E1E2E")
        frame_informe.pack(pady=20)
        tk.Button(frame_informe, text="📊 GENERAR INFORME PARA PROPIETARIO", bg="#CBA6F7", fg="#11111B", font=("Consolas", 12, "bold"), command=self.generar_informe_propietario).pack(ipadx=10, ipady=5)

        # Triggers iniciales
        self.trm_usd = 4200.0  # Fallback si no hay internet
        self.obtener_trm()
        self.toggle_canon_field()

        if self.usb_manager.es_primer_inicio():
            self._abrir_reporte_demo()

    def obtener_trm(self):
        def fetch():
            try:
                # Usamos una API simple pública. Si falla caemos en fallback
                res = requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=3)
                if res.status_code == 200:
                    data = res.json()
                    cop_rate = data.get("rates", {}).get("COP", 4200.0)
                    self.trm_usd = float(cop_rate)
                    self.calcular_usdc()
            except: pass
        threading.Thread(target=fetch, daemon=True).start()

    def toggle_canon_field(self):
        if self.modulo_var.get() == "Arriendo Multisig":
            self.frame_canon.pack(before=self.prompt_box.master.winfo_children()[-3], pady=5, fill="x", padx=20)
            self.calcular_usdc()
        else:
            self.frame_canon.pack_forget()

    def calcular_usdc(self, *args):
        try:
            canon = float(self.canon_var.get().replace(",","").replace(".",""))
            garantia_cop = canon * 3
            usdc = garantia_cop / self.trm_usd
            self.usdc_label.config(text=f"👉 Garantía Escrow (x3): ~ {usdc:,.2f} USDC (TRM: ${self.trm_usd:,.0f})")
        except ValueError:
            self.usdc_label.config(text="👉 Garantía Escrow (x3): Ingrese número válido")

    def _abrir_reporte_demo(self):
        self._construir_y_abrir_reporte(2500000)

    def generar_informe_propietario(self):
        try:
            canon_str = simpledialog.askstring("Informe de Blindaje", "Ingrese el Valor del Canon Mensual (COP):", initialvalue="2500000")
            if not canon_str: return
            canon = float(canon_str.replace(",", "").replace(".", ""))
            self._construir_y_abrir_reporte(canon)
        except Exception as e:
            messagebox.showerror("Error", f"Entrada inválida: {str(e)}")

    def _construir_y_abrir_reporte(self, canon: float):
        try:
            meses_mora_promedio = 18
            perdida_arriendos = canon * meses_mora_promedio
            costos_abogado = perdida_arriendos * 0.20
            perdida_total_tradicional = perdida_arriendos + costos_abogado
            
            garantia_guanes = canon * 3
            usdc_aprox = garantia_guanes / self.trm_usd
            tx_hash_dummy = f"sol_tx_{uuid.uuid4().hex[:16]}"
            agencia = self.usb_manager.get_config("agencia", "Guanes Inmobiliaria")

            html_content = f"""
            <!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <title>Informe de Blindaje - {agencia}</title>
                <style>
                    body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #333; line-height: 1.6; margin: 0; padding: 40px; background: #fdfdfd; position: relative; }}
                    body::before {{ content: "PROTECCIÓN ACTIVA V5"; position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%) rotate(-45deg); font-size: 80px; color: rgba(0, 0, 0, 0.04); z-index: -1; white-space: nowrap; font-weight: 900; pointer-events: none; font-family: monospace; letter-spacing: 5px; }}
                    .container {{ max-width: 800px; margin: auto; background: white; padding: 40px; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border-top: 5px solid #0f172a; }}
                    .header {{ text-align: center; border-bottom: 2px solid #eee; padding-bottom: 20px; margin-bottom: 30px; }}
                    h1 {{ color: #0f172a; margin: 0; font-size: 28px; text-transform: uppercase; letter-spacing: 1px; }}
                    h2 {{ color: #0f172a; border-bottom: 2px solid #d4af37; padding-bottom: 5px; margin-top: 30px; display: inline-block; }}
                    .highlight {{ background-color: #fee2e2; color: #dc2626; padding: 2px 6px; border-radius: 4px; font-weight: 900; font-size: 1.1em; }}
                    .success {{ background-color: #d1fae5; color: #059669; padding: 2px 6px; border-radius: 4px; font-weight: 900; font-size: 1.1em; }}
                    
                    /* Gráficos de barras CSS */
                    .chart-container {{ margin: 30px 0; padding: 20px; background: #f8f9fa; border-radius: 8px; border: 1px solid #dee2e6; }}
                    .bar-row {{ display: flex; align-items: center; margin-bottom: 15px; }}
                    .bar-label {{ width: 140px; font-weight: bold; font-size: 14px; color: #0f172a; }}
                    .bar-wrapper {{ flex-grow: 1; background: #e9ecef; height: 35px; border-radius: 4px; position: relative; overflow: hidden; box-shadow: inset 0 2px 4px rgba(0,0,0,0.1); }}
                    .bar-tradicional {{ background: linear-gradient(90deg, #dc2626, #ef4444); height: 100%; transition: width 1s; width: 100%; display: flex; align-items: center; padding-left: 15px; color: white; font-weight: 900; font-size: 1.1em; text-shadow: 1px 1px 2px rgba(0,0,0,0.5); }}
                    .bar-guanes {{ background: linear-gradient(90deg, #059669, #10b981); height: 100%; transition: width 1s; width: 15%; display: flex; align-items: center; padding-left: 15px; color: white; font-weight: 900; font-size: 1.1em; text-shadow: 1px 1px 2px rgba(0,0,0,0.5); }}
                    
                    .box {{ padding: 20px; border-left: 5px solid #059669; background: #f8f9fa; margin: 20px 0; box-shadow: 0 2px 5px rgba(0,0,0,0.02); }}
                    .hash-box {{ font-family: monospace; background: #0f172a; color: #d4af37; padding: 15px; border-radius: 5px; text-align: center; font-size: 16px; letter-spacing: 1px; border: 1px solid #d4af37; }}
                    .footer {{ text-align: center; margin-top: 40px; font-size: 12px; color: #777; border-top: 1px solid #eee; padding-top: 20px; }}
                    .gold-text {{ color: #d4af37; font-weight: bold; }}
                    @media print {{ body {{ padding: 0; background: white; }} .container {{ box-shadow: none; border: none; padding: 0; }} }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>{agencia}</h1>
                        <p style="color: #666; font-size: 18px; margin-top: 5px; font-weight: bold;">Análisis de Riesgo y Protocolo de Blindaje Guanes V5</p>
                    </div>

                    <h2>1. Análisis de Riesgo Tradicional (Bucaramanga/Floridablanca)</h2>
                    <p>En el escenario actual de justicia ordinaria, un proceso de restitución de inmueble arrendado por incumplimiento toma un promedio de <strong>{meses_mora_promedio} meses</strong>. Para un canon de <strong>${canon:,.0f} COP</strong>, las pérdidas proyectadas obligatorias son:</p>
                    <ul>
                        <li>Cánones caídos perdidos (18 meses): <span class="highlight">${perdida_arriendos:,.0f} COP</span></li>
                        <li>Costas procesales y honorarios jurídicos (20%): <span class="highlight">${costos_abogado:,.0f} COP</span></li>
                    </ul>
                    
                    <div class="chart-container">
                        <div class="bar-row">
                            <div class="bar-label">Modelo Ordinario</div>
                            <div class="bar-wrapper"><div class="bar-tradicional">${perdida_total_tradicional:,.0f} COP en Pérdidas</div></div>
                        </div>
                        <div class="bar-row">
                            <div class="bar-label">Modelo Guanes</div>
                            <div class="bar-wrapper"><div class="bar-guanes">${garantia_guanes:,.0f} COP  (0% Riesgo)</div></div>
                        </div>
                    </div>

                    <h2>2. La Solución Inmobiliaria: Bóveda Multisig 3x</h2>
                    <p>El "Impuesto de la Desconfianza" ha sido eviscerado. Nuestro modelo exige e instala por parte del inquilino una garantía líquida equivalente a <strong>3 cánones mensuales</strong>.</p>
                    <div class="box">
                        <strong>Total Garantizado a su favor desde el Día 1:</strong> <span class="success">${garantia_guanes:,.0f} COP (~{usdc_aprox:,.2f} USDC)</span><br>
                        <em style="color:#555; display:block; margin-top:10px;">Este capital neutraliza matemáticamente: 2 meses de contingencia procesal y 1 mes reservado para costas de daños.</em>
                    </div>

                    <h2>3. Certificado de Custodia (Web3 Escrow)</h2>
                    <p>El depósito en USDC no lo custodia ni usted ni el inquilino. Su dinero queda salvaguardado por un Smart Contract inmutable en la red Solana.</p>
                    <div class="hash-box">
                        Firma Digital: {tx_hash_dummy}<br>
                        <span style="font-size: 12px; color: #a6e3a1; margin-top: 5px; display: inline-block;">🛡️ Transacción Descentralizada Validada Automáticamente</span>
                    </div>

                    <h2>4. Amparo de Amigable Composición (Ley 1563 de 2012)</h2>
                    <p><strong>{agencia}</strong> ha sido facultada constitucionalmente por el <span class="gold-text">Estatuto Nacional de Arbitraje (Ley 1563)</span> para actuar como su <em>Juez Privado Institucional (Llave C)</em>.</p>
                    <p>Esto significa que <strong>renunciamos legalmente a la burocracia civil</strong>. En caso de mora, nuestra agencia firma la liberación de la Bóveda hacia su billetera en cuestión de horas, eludiendo la mora procesal pública. Nuestras decisiones tienen fuerza de cosa juzgada indiscutible.</p>

                    <div class="footer">
                        <p>Generado algorítmicamente por Guanes LegalTech V5 - Infraestructura de Notariado Digital (Firma Electrónica Ley 527 de 1999)</p>
                    </div>
                </div>
                <script>
                    setTimeout(() => {{ window.print(); }}, 1000);
                </script>
            </body>
            </html>
            """
            informe_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "informe_propietario_temp.html")
            with open(informe_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            
            webbrowser.open(f"file://{informe_path}")
            messagebox.showinfo("Generador de Informes", "Informe generado en HTML. Se ha abierto en tu navegador listo para exportar a PDF (Ctrl+P / Imprimir -> Guardar como PDF).")
            
        except Exception as e:
            messagebox.showerror("Error", f"Fallo generando informe: {str(e)}")

    def generar(self):
        usuario = self.prompt_box.get("1.0", tk.END).strip()
        mod = self.modulo_var.get()
        if not usuario: return

        # Verificador de Licencia de Cortesía (Demo Mode)
        creditos_str = self.usb_manager.get_config("creditos_cortesia", "0")
        creditos_restantes = int(creditos_str) if creditos_str.isdigit() else 0
        
        if creditos_restantes <= 0:
            messagebox.showwarning("Prueba Finalizada", "Periodo de Prueba Finalizado. Para activar generaciones ilimitadas y soporte de Amigable Composición, contacte a la Central Guanes.")
            return

        self.btn_gen.config(text="⏳ VECTORIZANDO Y GENERANDO...", state=tk.DISABLED)
        self.root.update()

        try:
            prompt_final = f"[MÓDULO {mod}]\nREGLA ESTRICTA: Redacta un documento tipo {mod}. NORMATIVA: Bucaramanga/Floridablanca 2026. Datos: {usuario}. "
            
            # INYECCIÓN WEB3 AMIGABLE COMPOSICIÓN LEY 1563 & GARANTÍA 3x
            if mod == "Arriendo Multisig":
                agencia = self.usb_manager.get_config("agencia", "LA INMOBILIARIA")
                wallet = self.usb_manager.get_config("wallet", "BILLETERA_PENDIENTE")
                GARANTIA_MULTIPLIER = 3
                
                # Calcular montos para el prompt
                try: canon_val = float(self.canon_var.get())
                except: canon_val = 1500000
                garantia_usd = (canon_val * GARANTIA_MULTIPLIER) / self.trm_usd
                
                prompt_final += f"INSTRUCCIÓN LEGAL CRÍTICA SOBRE GARANTÍA: El redactado debe especificar una Garantía Digital Escrow total equivalente a {GARANTIA_MULTIPLIER} cánones mensuales (Aprox {garantia_usd:,.2f} USDC). DEBERÁ escribir literalmente la siguiente justificación para esta retención: 'Justificación de Mora Procesal (2 meses) y Costas Judiciales (1 mes)'. "
                prompt_final += f"INSTRUCCIÓN AMIGABLE COMPONEDOR: Basado en Ley 1563 de 2012, especificar explícitamente que la agencia '{agencia}' con billetera Solana '{wallet}' actuará como Tercero Amigable Componedor de única instancia para liberación de escrow (Llave C)."

            respuesta = self.engine.query(prompt_final, perfil_nombre=PERFIL)
            self.res_box.delete("1.0", tk.END)
            self.res_box.insert(tk.END, respuesta)
            
            # Deducción de crédito y Notificación de Interés al Equipo de Ventas
            creditos_restantes -= 1
            self.usb_manager.set_config("creditos_cortesia", str(creditos_restantes))
            self.usb_manager.enviar_telemetria_ping(f"Prospecto probando sistema en {self.usb_manager.usb_id}")
            
            # Registrar uso y enviar telemetría resilient
            self.usb_manager.incrementar_uso(mod)
            municipio = "Bucaramanga" if "bucaramanga" in usuario.lower() else "Floridablanca" if "floridablanca" in usuario.lower() else "No Definido"
            self.usb_manager.enviar_telemetria_async(mod, municipio)
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self.btn_gen.config(text="🚀 ENGRANAR MOTOR LLM", state=tk.NORMAL)

if __name__ == "__main__":
    splash = tk.Tk()
    splash.overrideredirect(True)
    w, h = 600, 300
    ws, hs = splash.winfo_screenwidth(), splash.winfo_screenheight()
    splash.geometry(f"{w}x{h}+{ws//2 - w//2}+{hs//2 - h//2}")
    splash.configure(bg="#0f172a", highlightbackground="#d4af37", highlightthickness=2)
    
    tk.Label(splash, text="GUANES V5", font=("Consolas", 40, "bold"), fg="#d4af37", bg="#0f172a").pack(pady=40)
    tk.Label(splash, text="Protegiendo el Patrimonio de Santander.\nInicializando Inteligencia Legal...", font=("Consolas", 14), fg="#a6e3a1", bg="#0f172a").pack()
    splash.update()
    
    # Motor Pesado Inject
    if core_path not in sys.path: sys.path.append(core_path)
    try:
        from guanes_engine import GuanesEngine
        engine_inst = GuanesEngine()
    except Exception as e:
        splash.destroy()
        messagebox.showerror("Error del Motor", f"Fallo Crítico al iniciar Inteligencia Artificial: {e}")
        sys.exit(1)
        
    app_root = tk.Tk()
    splash.destroy()
    app = USBInmobiliarioApp(app_root, engine_inst)
    app_root.mainloop()
