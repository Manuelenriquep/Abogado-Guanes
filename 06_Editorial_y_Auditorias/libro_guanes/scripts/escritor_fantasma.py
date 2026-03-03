import os
import json
import requests
import time
import sys

def main():
    print("🏁 Iniciando MODO MARATÓN: Escribiendo el resto del libro...")
    
    # Configuración del modelo y parámetros
    model_name = "qwen3:8b"
    url = "http://localhost:11434/api/generate"
    
    system_prompt = (
        "Actúa como un autor de bestsellers de negocios y consultor senior en LegalTech. "
        "Tu estilo debe ser narrativo, persuasivo y empático, conectando profundamente con las frustraciones del lector. "
        "Evita la jerga técnica de programación. Usa un tono de autoridad pero accesible."
    )

    capitulos = [
        {
            "num": 4,
            "titulo": "Las Bóvedas Multisig (El Cofre de Tres Llaves)",
            "file": "04_Capitulo_4_Las_Bovedas_Multisig.md",
            "instrucciones": """
Concepto: Cómo funciona la seguridad 2-de-3. 
Analogía: Un cofre que requiere dos llaves diferentes de tres posibles para abrirse (Inquilino, Propietario y Guanes). 
Desarrollo: Explica la paz mental que esto genera. Ya no existe el riesgo de que el propietario se "desaparezca" con el depósito o que el inquilino no pague y el dinero quede bloqueado para siempre. Es el fin del robo de depósitos y de las disputas interminables.
"""
        },
        {
            "num": 5,
            "titulo": "La Notaría de Bolsillo (Registro Inmutable)",
            "file": "05_Capitulo_5_La_Notaria_De_Bolsillo.md",
            "instrucciones": """
Concepto: Registro inmutable en blockchain mediante el 'Hash'. 
Legalidad: Debes citar la Ley 527 de 1999 de Colombia y explicar el concepto de 'Equivalencia Funcional' en Latinoamérica. 
Desarrollo: Cómo logramos que un contrato físico tenga una huella digital eterna, imposible de alterar, y por qué esto tiene validez jurídica plena. Es llevar la fe pública al bolsillo del ciudadano.
"""
        },
        {
            "num": 6,
            "titulo": "El Puente a la Web3 (Ventanilla Única)",
            "file": "06_Capitulo_6_El_Puente_A_La_Web3.md",
            "instrucciones": """
Concepto: Abstracción de la complejidad (Guanes como puente).
Desarrollo: El usuario no necesita saber qué es una wallet o una 'gas fee'. Diego paga en pesos colombianos o moneda local, y por detrás, Guanes convierte a USDC y paga el costo de la red (SOL). Explica cómo facilitamos la adopción masiva quitando la fricción técnica.
"""
        },
        {
            "num": 7,
            "titulo": "El Futuro y DeFi (Haciendo rendir el depósito)",
            "file": "07_Capitulo_7_El_Futuro_Y_DeFi.md",
            "instrucciones": """
Concepto: Introducción a los rendimientos en dólares (Yield).
Desarrollo: Mientras el dinero está en garantía (en el cofre multisig), no tiene por qué estar ocioso. Explica cómo la tecnología permite que ese depósito genere rendimientos seguros en dólares, transformando un costo en un beneficio financiero para las partes.
"""
        },
        {
            "num": 8,
            "titulo": "Conclusión: La Nueva Era Inmobiliaria",
            "file": "08_Capitulo_8_Conclusion_La_Nueva_Era.md",
            "instrucciones": """
Resumen de la obra: El cierre de la historia de Diego (quien ahora vive tranquilo en su apartamento). 
Mensaje final: La tecnología no es una amenaza, es la herramienta de justicia más potente que hemos construido. 
Llamado a la acción: Invita al lector a ser parte de la revolución Guanes.
"""
        }
    ]

    for cap in capitulos:
        num = cap["num"]
        titulo = cap["titulo"]
        file_name = cap["file"]
        
        print(f"\n📘 Preparando Capítulo {num}: {titulo}...")
        
        user_prompt = f"""
Redacta el "Capítulo {num}: {titulo}" para el libro "Código y Confianza: El Fin del Fiador y la Revolución Web3".

INSTRUCCIONES ESPECÍFICAS PARA ESTE CAPÍTULO:
{cap["instrucciones"]}

REGLAS GENERALES PARA LA MARATÓN:
- Extensión: Escribe un capítulo extenso, detallado y persuasivo (mínimo 1500 palabras).
- Tono: Bestseller de negocios, empático, con autoridad.
- Escribe en español con un estilo cautivador que invite a seguir leyendo.
"""

        payload = {
            "model": model_name,
            "prompt": user_prompt,
            "system": system_prompt,
            "stream": True,
            "options": {
                "num_ctx": 4096,
                "temperature": 0.7
            }
        }

        try:
            print(f"✍️ La IA está escribiendo el Capítulo {num} (Modo Streaming)...")
            response = requests.post(url, json=payload, timeout=1800, stream=True)
            response.raise_for_status()
            
            full_text = ""
            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line.decode('utf-8'))
                    content = chunk.get("response", "")
                    full_text += content
                    print(content, end="", flush=True)
                    
                    if chunk.get("done"):
                        break
            
            print("\n")

            if full_text:
                folder_name = r"c:\AbogadoVirtual\libro_guanes\manuscritos"
                if not os.path.exists(folder_name):
                    os.makedirs(folder_name)
                    
                file_path = os.path.join(folder_name, file_name)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(full_text)
                print(f"✅ Capítulo {num} guardado con éxito en {file_path}")
            else:
                print(f"❌ Error: La respuesta para el Capítulo {num} está vacía.")

            # Espera de 5 segundos entre capítulos
            if num < 8:
                print("⏳ Esperando 5 segundos para iniciar el siguiente capítulo...")
                time.sleep(5)

        except requests.exceptions.Timeout:
            print(f"❌ Error: Se agotó el tiempo de espera en el Capítulo {num}.")
        except Exception as e:
            print(f"❌ Ocurrió un error en el Capítulo {num}: {e}")

    print("\n🏆 ¡Maratón Finalizada! El libro completo ha sido redactado.")

if __name__ == "__main__":
    main()
