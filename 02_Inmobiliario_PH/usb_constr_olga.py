import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(os.path.join(parent_dir, "03_Motor_Core"))

from guanes_engine import GuanesEngine

def iniciar_interfaz_olga():
    print("===================================================================")
    print("🏗️ USB_CONSTR_OLGA: Blindaje de Proyectos e Ingeniería Jurídica")
    print("⚖️ Sello: Derecho Preventivo con Garantía de Ley 2026")
    print("===================================================================")
    print("✅ Unidad Operativa. Escriba 'salir' para terminar.\n")
    
    # Suprimimos logs técnicos si los hubiera importando
    import logging
    logging.getLogger().setLevel(logging.ERROR)

    engine = GuanesEngine()
    
    while True:
        try:
            consulta = input(" Olga (Consulta Construcción) > ")
            if consulta.lower() in ['salir', 'exit', 'quit']:
                break
                
            if consulta.strip() == "":
                continue
                
            respuesta = engine.query(consulta, perfil_nombre="USB_CONSTR_OLGA")
            
            print("\n-------------------------------------------------------------------")
            print(f"⚖️ Respuesta Autorizada:\n{respuesta}")
            print("-------------------------------------------------------------------\n")
            
        except KeyboardInterrupt:
            print("\nSaliendo del sistema prevencionista...")
            break
        except Exception as e:
            print(f"\n❌ Error de consulta: {e}\n")

if __name__ == "__main__":
    iniciar_interfaz_olga()
