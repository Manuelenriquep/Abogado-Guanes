import subprocess
import time
import os
import socket
import requests

# Configuración
PORT = 8000
BRIDGE_SCRIPT = r"c:\AbogadoVirtual\servidor_puente.py"
NGROK_DOMAIN = "hematozoic-icebound-ninfa.ngrok-free.dev"
LOG_FILE = r"c:\AbogadoVirtual\99_Logs_y_Temporales\guanes_guardian.log"

def log(mensaje):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {mensaje}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def is_port_open(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def check_ngrok():
    try:
        # Intentamos conectar a la URL de ngrok (vía el API local si está disponible o el endpoint público)
        # Una forma sencilla es checking if the process is running
        output = subprocess.check_output('tasklist /FI "IMAGENAME eq ngrok.exe"', shell=True).decode()
        return "ngrok.exe" in output
    except:
        return False

def start_bridge():
    log("🚀 Iniciando Servidor Puente...")
    subprocess.Popen(["py", BRIDGE_SCRIPT], creationflags=subprocess.CREATE_NEW_CONSOLE)

def start_ngrok():
    log("🚀 Iniciando Túnel Ngrok...")
    cmd = f"ngrok http --url={NGROK_DOMAIN} {PORT}"
    subprocess.Popen(cmd, shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)

def main():
    log("🛡️ Iniciando Guanes Guardián (Vigilante de Persistencia)...")
    
    # 1. Verificar Puente
    if not is_port_open(PORT):
        log("⚠️ Servidor Puente no detectado en puerto 8000.")
        start_bridge()
    else:
        log("✅ Servidor Puente operativo.")

    # 2. Verificar Ngrok
    if not check_ngrok():
        log("⚠️ Túnel Ngrok no detectado.")
        start_ngrok()
    else:
        log("✅ Túnel Ngrok operativo.")

if __name__ == "__main__":
    main()
