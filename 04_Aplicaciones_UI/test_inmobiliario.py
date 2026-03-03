import sys
import os
sys.path.append(r"c:\AbogadoVirtual\03_Motor_Core")
from guanes_engine import GuanesEngine

engine = GuanesEngine()

prompt_enriquecido = "[MÓDULO PH]\nREGLA ESTRICTA: Redacta un documento estructurado de tipo PH. UTILIZA COMO BASE NORMATIVA LOCAL VIGENTE A 2026 recuperada de ChromaDB. Datos adicionales del usuario: Edificio en Bucaramanga con 20 apartamentos y terraza comunal."

print("🚀 ENGRANANDO MOTOR... consultando Bucaramanga para PH...")
respuesta = engine.query(prompt_enriquecido, perfil_nombre="INMOBILIARIO USB 2026")
print("\n--- RESULTADO OBTENIDO ---\n")
print(respuesta)
