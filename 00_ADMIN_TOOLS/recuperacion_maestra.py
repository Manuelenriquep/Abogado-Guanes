import sys
import getpass
import time
import requests
import json
import sqlite3
import os

MASTER_KEY = "Guanes_Architect_Overlord_2026!"
N8N_BACKUP_URL = "http://localhost:5678/webhook/usb-backup-pull"
# Solana API simulada para el modelo Escrow (Arquitectura PDA / Multisig) 
SOLANA_RPC = "https://api.mainnet-beta.solana.com"

def verificar_credenciales():
    print("=====================================================")
    print("🛡️  CONSOLA DE MANDO ARQUITECTO - GUANES LEGALTECH 🛡️")
    print("=====================================================")
    intento = getpass.getpass("Ingrese la contraseña maestra (Master Key): ")
    if intento != MASTER_KEY:
        print("❌ Acceso Denegado. Protocolo de intrusión registrado.")
        sys.exit(1)
    print("✅ Autenticación de Arquitecto Exitosa.\n")

def paso_1_revocacion():
    print("--- [PASO 1] REVOCACIÓN DE AUTORIDAD VULNERADA ---")
    usb_id_comprometida = input("Ingrese el USB_ID reportado como comprometido/perdido: ").strip()
    if not usb_id_comprometida:
        print("Operación cancelada.")
        return None
    
    print(f"📡 Emitiendo transacción Blockchain de tipo 'SetAuthority' (Revoke) para USB '{usb_id_comprometida}'...")
    time.sleep(2) # Simulación I/O Blockchain
    print(f"✅ Llave pública asociada a '{usb_id_comprometida}' ha sido revocada exitosamente de todos los Smart Contracts activos.")
    return usb_id_comprometida

def paso_2_traspaso(usb_id_vieja):
    print("\n--- [PASO 2] TRASPASO DE AUTORIDAD A NUEVA LLAVE ---")
    usb_id_nueva = input("Ingrese el USB_ID de la unidad de reemplazo virgen (ej. USB-A1B2C3D4): ").strip()
    wallet_nueva = input("Ingrese la Solana Public Key de la Inmobiliaria para la nueva USB: ").strip()
    
    print(f"📡 Emitiendo transacción 'SetAuthority' transfiriendo el rol de Amigable Componedor a: {wallet_nueva}...")
    time.sleep(2)
    print(f"✅ ¡Arquitectura Escrow restaurada! Los contratos que pertenecían a {usb_id_vieja} ahora responden a {usb_id_nueva}.")
    return usb_id_nueva

def paso_3_restaurar_db(usb_id_nueva):
    print("\n--- [PASO 3] RE-INYECCIÓN DE DATOS DE CONTRACTOS ACTIVOS ---")
    print(f"📡 Típicamente conectaremos con N8N para recuperar los JSONs de '{usb_id_nueva}'...")
    try:
        # Simulamos una petición de fetch al data lake
        # res = requests.post(N8N_BACKUP_URL, json={"target_usb": usb_id_nueva})
        # data = res.json()
        data = [
            {"contrato_id": "B-842", "arrendador": "Juan Pérez", "canon": 1500000, "usdc": 1071.42},
            {"contrato_id": "B-911", "arrendador": "Ed. Majestic", "canon": 2000000, "usdc": 1428.57}
        ]
        print(f"✅ Se han encontrado {len(data)} contratos activos en el Backup.")
        
        # Inyección en la DB local (asumamos que conectamos la USB al puerto D: por ejemplo, aquí usaremos archivo local simulado)
        db_path = ".sys_guanes_usb_recuperada.db"
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS contratos_activos (id TEXT, data_json TEXT)")
        for record in data:
            cur.execute("INSERT INTO contratos_activos (id, data_json) VALUES (?, ?)", (record['contrato_id'], json.dumps(record)))
        conn.commit()
        conn.close()
        print(f"✅ JSONs inyectados correctamente en la nueva base de datos (.sys_guanes_usb_recuperada.db).")
        print("📦 La nueva memoria USB ya está lista para ser despachada a la agencia inmobiliaria.")
    except Exception as e:
        print(f"❌ Fallo al restaurar la base de datos: {e}")

def main():
    verificar_credenciales()
    vieja = paso_1_revocacion()
    if vieja:
        nueva = paso_2_traspaso(vieja)
        paso_3_restaurar_db(nueva)
    print("\n🚀 [OPERACIÓN DE RESILIENCIA FINALIZADA] 🚀")

if __name__ == "__main__":
    main()
