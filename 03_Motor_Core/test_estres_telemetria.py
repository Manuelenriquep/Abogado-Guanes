import threading
import requests
import json
import time

URL_TELEMETRIA = "http://localhost:5678/webhook/usb-telemetry"
URL_VALIDACION = "http://localhost:5678/webhook/check-usb-status"

def disparar_ping_simultaneo(hilo_index):
    # Simular una USB de un agente comercial en Bucaramanga
    usb_id = f"USB-TEST-{hilo_index}"
    payload_tel = {
        "usb_id": usb_id,
        "tipo_documento": "PH",
        "municipio": "Bucaramanga",
        "timestamp": "2026-02-28T10:00:00"
    }
    
    # 1. Test de Validación (Kill Switch)
    print(f"[Hilo {hilo_index}] 🔍 Consultando estado de licencia...")
    try:
        req_val = requests.post(URL_VALIDACION, json={"usb_id": usb_id}, timeout=3)
        if req_val.status_code == 200:
            print(f"  ✅ [Hilo {hilo_index}] Licencia OK: {req_val.json()}")
        else:
            print(f"  ❌ [Hilo {hilo_index}] HTTP Error Validación: {req_val.status_code}")
    except Exception as e:
        print(f"  ❌ [Hilo {hilo_index}] Error red validación: {e}")

    # Simular que el motor demora 1 segundo en hacer el RAG
    time.sleep(1)
    
    # 2. Test de Envío de Telemetría
    print(f"[Hilo {hilo_index}] 📡 Disparando Telemetría Offline Batch...")
    try:
        req_tel = requests.post(URL_TELEMETRIA, json=payload_tel, timeout=3)
        if req_tel.status_code == 200:
            print(f"  ✅ [Hilo {hilo_index}] Batch Recibido: {req_tel.json()}")
        else:
            print(f"  ❌ [Hilo {hilo_index}] HTTP Error Telemetría: {req_tel.status_code}")
    except Exception as e:
        print(f"  ❌ [Hilo {hilo_index}] Error red telemetría: {e}")

if __name__ == "__main__":
    print("🧨 INICIANDO TEST DE ESTRÉS DE CONCURRENCIA MÚLTIPLE (5 USBs) 🧨")
    
    hilos = []
    # Lanzar 5 conexiones paralelas en tiempo real hacia N8N Mock
    for i in range(1, 6):
        h = threading.Thread(target=disparar_ping_simultaneo, args=(i,))
        hilos.append(h)
        h.start()
        
    for h in hilos:
        h.join()

    print("\n🏁 Test de Estrés concluido. Si hay puros '✅', el servidor aguantó la carga.")
