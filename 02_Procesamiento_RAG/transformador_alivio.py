import json
import re

def transformar_a_alivio(texto):
    # Reglas de transformación (Lenguaje del Respiro)
    reemplazos = [
        (r"seguridad financiera", "quitarse el dolor de cabeza"),
        (r"jerarquía normativa", "explicamos clarito"),
        (r"sujeto procesal", "usted"),
        (r"validez legal", "defender su platica"),
        (r"cumplimiento normativo", "respirar tranquilo"),
        (r"acción cambiaria", "frenar el abuso"),
        (r"títulos valores", "pagarés o letras"),
        (r"anomalías comerciales lucrativas", "abusos con su plata"),
        (r"excepciones cambiarias", "formas de defenderse"),
        (r"prescripción", "vencimiento para que no le cobren"),
        (r"procedimiento legal", "pasos para estar tranquilo"),
    ]
    
    nuevo_texto = texto
    for patron, reemplazo in reemplazos:
        nuevo_texto = re.sub(patron, reemplazo, nuevo_texto, flags=re.IGNORECASE)
    
    # Estructura Sugerida: "Con esta solución usted podrá [Verbo] el problema de [Problema]. Le explicamos clarito cómo [Acción] para que no [Consecuencia]."
    # Intentamos forzar la estructura si detectamos patrones comunes
    if "Solución" in nuevo_texto or "paquete legal" in nuevo_texto:
        nuevo_texto = nuevo_texto.replace("Solución para ciudadanos que permite", "Con esta solución usted podrá frenar el abuso y")
        nuevo_texto = nuevo_texto.replace("Este paquete legal desbloquea", "Con esta solución usted podrá quitarse el dolor de cabeza de")
    
    if "Incluye" in nuevo_texto:
        nuevo_texto = nuevo_texto.replace("Incluye", "Le explicamos clarito cómo")
    
    if not nuevo_texto.endswith("."):
        nuevo_texto += "."
        
    if "dormir tranquilo" not in nuevo_texto and "respirar tranquilo" not in nuevo_texto:
        nuevo_texto += " Así podrá respirar tranquilo."
        
    return nuevo_texto

def procesar_boveda():
    try:
        with open(r'c:\AbogadoVirtual\03_Motor_Core\vectores_titulos_valores.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for item in data:
            original = item['resumen_solucion']
            item['resumen_solucion'] = transformar_a_alivio(original)
            
        with open(r'c:\AbogadoVirtual\03_Motor_Core\vectores_titulos_valores_alivio.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            
        print(f"✅ Transformación completada: {len(data)} vectores procesados.")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    procesar_boveda()
