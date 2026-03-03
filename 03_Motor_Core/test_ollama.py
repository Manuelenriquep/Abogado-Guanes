import ollama
try:
    res = ollama.chat(model='qwen3:8b', messages=[{'role': 'user', 'content': 'hola'}])
    print("SUCCESS")
    print(res['message']['content'])
except Exception as e:
    print(f"FAILURE: {e}")
