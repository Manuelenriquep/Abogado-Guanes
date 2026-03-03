import base64
ico_b64 = "AAABAAEAAQEAAAEAIAAwAAAAFgAAACgAAAABAAAAAgAAAAEAIAAAAAAACAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgAAAAA=="
with open(r'c:\AbogadoVirtual\04_Aplicaciones_UI\assets\icon.ico', 'wb') as f:
    f.write(base64.b64decode(ico_b64))
print("Icon written successfully")
