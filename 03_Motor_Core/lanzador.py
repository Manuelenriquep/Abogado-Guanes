import subprocess
import os
import time

def ejecutar_paso(nombre_script):
    try:
        print(f"\n🔔 🚀 INICIANDO: {nombre_script}")
        # Ejecuta el script de python y espera a que termine
        proceso = subprocess.run(['python', nombre_script], check=True)
        return proceso.returncode == 0
    except Exception as e:
        print(f"❌ Error ejecutando {nombre_script}: {e}")
        return False

def cargar_en_calibre(carpeta, etiqueta):
    try:
        print(f"\n📚 Cargando archivos de '{carpeta}' en Calibre...")
        if not os.path.exists(carpeta):
            print(f"⚠️ La carpeta '{carpeta}' no existe.")
            return

        archivos = [f for f in os.listdir(carpeta) if f.endswith('.md')]
        
        for archivo in archivos:
            ruta_completa = os.path.join(carpeta, archivo)
            # Comando para agregar a calibre con etiquetas automáticas
            comando = [
                'calibredb', 'add', ruta_completa,
                '--with-library', 'C:/Ruta/A/Tu/Biblioteca/Calibre', # Cambia esto por tu ruta
                '--tags', f'IA_Procesado, {etiqueta}'
            ]
            try:
                subprocess.run(comando, check=True)
                print(f"   ✅ {archivo} cargado y etiquetado como '{etiqueta}'.")
            except Exception as e:
                print(f"   ⚠️ Error al cargar {archivo}: {e}")
    except Exception as e:
        print(f"❌ Error en la carga a Calibre: {e}")

def orquestar_todo():
    try:
        print("🚀 INICIANDO ORQUESTADOR DE GUANES LEGAL TECH...")
        
        # PASO 2: Extraer citas de los nuevos códigos limpios
        if ejecutar_paso('juris_extractor.py'):
            
            # PASO 3: Descargar y resumir jurisprudencia
            if ejecutar_paso('juris_downloader_auto.py'):
                
                # PASO 4: Interconectar todo
                # ejecutar_paso('enlazador.py')
                
                # PASO 5: Carga masiva a Calibre
                cargar_en_calibre(r"c:\AbogadoVirtual\01_Ingesta_Datos\biblioteca_completa", 'Ley_Vigente')
                cargar_en_calibre('jurisprudencia_resumida', 'Jurisprudencia')
                
        print("\n✨ ✅ ¡MISIÓN CUMPLIDA! Tu Legis local está actualizado.")
    except Exception as e:
        print(f"❌ Error fatal en el lanzador: {e}")

if __name__ == "__main__":
    orquestar_todo()