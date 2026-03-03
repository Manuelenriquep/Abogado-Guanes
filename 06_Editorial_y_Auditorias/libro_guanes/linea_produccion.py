import os
import subprocess
import shutil

class LineaProduccion:
    def __init__(self):
        self.base_dir = r"c:\AbogadoVirtual\06_Editorial_y_Auditorias\libro_guanes"
        self.dirs = {
            "manuscritos": os.path.join(self.base_dir, "manuscritos"),
            "procesados": os.path.join(self.base_dir, "procesados"),
            "epub_output": os.path.join(self.base_dir, "epub_output"),
            "portadas": os.path.join(self.base_dir, "portadas"),
            "scripts": os.path.join(self.base_dir, "scripts"),
            "backups": os.path.join(self.base_dir, "backups")
        }
        
    def inicializar_carpetas(self):
        print("📁 Verificando estructura de directorios de producción...")
        for name, path in self.dirs.items():
            if not os.path.exists(path):
                os.makedirs(path)
                print(f"  + Creada carpeta: {name}")
                
    def importar_manuscritos_base(self):
        print("\n📥 Importando manuscritos base desde backups...")
        archivos_backup = [f for f in os.listdir(self.dirs["backups"]) if f.endswith(".md")]
        for archivo in archivos_backup:
            src = os.path.join(self.dirs["backups"], archivo)
            dst = os.path.join(self.dirs["manuscritos"], archivo)
            if not os.path.exists(dst):
                shutil.copy2(src, dst)
                print(f"  + Importado: {archivo}")
            else:
                print(f"  - Ya existe en manuscritos: {archivo}")

    def ejecutar_script(self, nombre_script):
        ruta_script = os.path.join(self.dirs["scripts"], nombre_script)
        print(f"\n⚙️ Ejecutando paso de producción: {nombre_script}...")
        try:
            import sys
            resultado = subprocess.run([sys.executable, ruta_script], check=True, capture_output=True, text=True)
            print(resultado.stdout)
            if resultado.stderr:
                print(resultado.stderr)
            print(f"✅ {nombre_script} finalizado correctamente.")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error ejecutando {nombre_script}:")
            print(e.stderr)

    def ejecutar_cadena(self):
        print("🚀 INICIANDO LÍNEA DE PRODUCCIÓN EDITORIAL 🚀\n" + "="*50)
        self.inicializar_carpetas()
        
        # 1. Cargar manuscritos crudos (simulando que el escritor_fantasma ya los generó)
        self.importar_manuscritos_base()
        
        # 2. Paso de limpieza y arreglo de codificación (Mojibake a UTF-8)
        self.ejecutar_script("reparar_letras.py")
        
        # 3. Ensamblaje y compilación a EPUB con Pandoc
        self.ejecutar_script("preparar_epub.py")
        
        print("\n🎉 LÍNEA DE PRODUCCIÓN COMPLETADA 🎉")
        print(f"El EPUB final se encuentra en: {self.dirs['epub_output']}")

if __name__ == "__main__":
    linea = LineaProduccion()
    linea.ejecutar_cadena()
