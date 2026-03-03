from guanes_engine import GuanesEngine

def test_calidad_metadatos():
    engine = GuanesEngine()
    
    print("🔬 TEST 1: Consulta sobre Zapatoca")
    res_zap = engine.query("¿Cuál es el área mínima de vivienda en Zapatoca?")
    print(res_zap)
    print("\n" + "="*50 + "\n")
    
    print("🔬 TEST 2: Consulta sobre Medellín")
    res_med = engine.query("¿Qué restricciones de construcción hay en Medellín según el Acuerdo 48?")
    print(res_med)

if __name__ == "__main__":
    test_calidad_metadatos()
