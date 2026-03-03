import ollama
import os

# 2. ENTRADA DE DATOS (Variables mockeadas para la prueba)
nombre_arrendador = "Guanes Legal Tech SAS"
nombre_arrendatario = "Inversiones Tecnológicas S.A.S."
monto_canon_cop = "5.000.000"
monto_garantia_usdc = "2.500"
direccion_inmueble = "Calle 100 # 7-33, Bogotá D.C."

def generar_clausula():
    print("🚀 Iniciando redacción...")
    
    # 3. EL PROMPT DEL SISTEMA (Ingeniería Legal)
    prompt_sistema = f"""
    Actúa como un Abogado Senior especialista en Tecnología y Smart Contracts en Colombia.
    Tu misión es redactar una "Cláusula Anexa de Garantía Mobiliaria sobre Criptoactivos" para un contrato de arrendamiento.
    
    DATOS DEL CONTRATO:
    - Arrendador: {nombre_arrendador}
    - Arrendatario: {nombre_arrendatario}
    - Canon Mensual: ${monto_canon_cop} COP
    - Garantía en Solana: {monto_garantia_usdc} USDC
    - Inmueble: {direccion_inmueble}
    
    FUNDAMENTOS LEGALES OBLIGATORIOS:
    1. Ley 1676 de 2013: Estipular que se trata de una garantía mobiliaria sobre bienes incorporales (USDC) bajo el régimen de garantías mobiliarias. Aclarar que NO es un depósito en efectivo para evitar la restricción de la Ley 820 de 2003 (artículo 15).
    2. Ley 527 de 1999: Invocar la equivalencia funcional, integridad y validez de los mensajes de datos y la firma criptográfica en la red Solana como prueba de consentimiento y perfección del contrato.
    3. Ley 1563 de 2012: Designar a "Guanes Legal Tech" como el Amigable Componedor encargado de dirimir controversias sobre la ejecución de la garantía, actuando como la tercera llave en un esquema Multisig 2-de-3 (Protocolo Squads).
    
    ESTRUCTURA REQUERIDA:
    - Título profesional.
    - Identificación de las partes.
    - Objeto de la garantía.
    - Funcionamiento técnico (Multisig en Solana).
    - Fundamentación jurídica detallada.
    - Procedimiento de ejecución ante incumplimiento.
    
    Tono: Estrictamente jurídico, preciso, técnico y formal.
    """

    print("⚖️ Aplicando jurisprudencia...")
    
    try:
        # 1. MOTOR DE IA
        response = ollama.chat(
            model='qwen3:8b',
            messages=[{'role': 'user', 'content': prompt_sistema}],
            options={
                'num_ctx': 4096,
                'temperature': 0.2
            }
        )
        
        contenido = response['message']['content']
        
        # 4. SALIDA
        archivo_salida = r"c:\AbogadoVirtual\05_Contratos_Web3\borrador_clausula_multisig.md"
        with open(archivo_salida, "w", encoding="utf-8") as f:
            f.write(contenido)
            
        print(f"✅ Borrador guardado en: {archivo_salida}")
        
    except Exception as e:
        print(f"❌ Error durante la generación: {e}")

if __name__ == "__main__":
    generar_clausula()
