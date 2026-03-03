"""
Módulo de Notificaciones WhatsApp — Guanes IA
Envia alertas de leads al abogado cuando el detector de compra se activa.
"""
import os
import requests
import logging

# Cargar credenciales desde .env.whatsapp
def _cargar_env():
    env = {}
    ruta = r"c:\AbogadoVirtual\.env.whatsapp"
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip()
    except Exception as e:
        logging.warning(f"No se pudo leer .env.whatsapp: {e}")
    return env

_ENV = _cargar_env()
WA_TOKEN    = _ENV.get("WA_TOKEN", "")
WA_PHONE_ID = _ENV.get("WA_PHONE_ID", "")
WA_DESTINO  = _ENV.get("WA_DESTINO", "")


def notificar_lead(sesion_id: str, resumen_consulta: str, especialidad: str = "General"):
    """
    Envía un mensaje de WhatsApp al abogado cuando se detecta un lead premium.
    Retorna True si se envió correctamente, False si falló.
    """
    if not all([WA_TOKEN, WA_PHONE_ID, WA_DESTINO]):
        logging.warning("WhatsApp: Credenciales incompletas, no se envió notificación.")
        return False

    url = f"https://graph.facebook.com/v19.0/{WA_PHONE_ID}/messages"
    
    mensaje = (
        f"🦉 *LEAD PREMIUM — Guanes IA*\n\n"
        f"📋 Sesión: `{sesion_id}`\n"
        f"⚖️ Área: *{especialidad}*\n"
        f"💬 Consulta:\n_{resumen_consulta[:200]}..._\n\n"
        f"📌 El cliente pidió acceso premium. ¡Atender pronto!"
    )

    payload = {
        "messaging_product": "whatsapp",
        "to": WA_DESTINO,
        "type": "text",
        "text": {"body": mensaje}
    }

    headers = {
        "Authorization": f"Bearer {WA_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        r = requests.post(url, json=payload, headers=headers, timeout=10)
        if r.status_code == 200:
            logging.info(f"✅ WhatsApp enviado: lead {sesion_id}")
            return True
        else:
            logging.error(f"WhatsApp error {r.status_code}: {r.text[:200]}")
            return False
    except Exception as e:
        logging.error(f"WhatsApp excepción: {e}")
        return False


if __name__ == "__main__":
    print("Probando notificación WhatsApp...")
    ok = notificar_lead(
        sesion_id="test-001",
        resumen_consulta="El cliente preguntó sobre reglamentos de propiedad horizontal y necesita radicar documentos urgente.",
        especialidad="Propiedad Horizontal"
    )
    print("✅ Enviado!" if ok else "❌ Falló — revisa credenciales o número destino.")
