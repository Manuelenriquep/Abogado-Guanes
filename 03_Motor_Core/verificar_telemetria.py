import sqlite3
DB_PATH = r"c:\AbogadoVirtual\03_Motor_Core\telemetria_global.db"

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

print("--- REGISTROS DE TELEMETRÍA (Últimos 10) ---")
c.execute("SELECT * FROM logs_telemetria ORDER BY id DESC LIMIT 10")
for row in c.fetchall():
    print(row)

print("\n--- CONTROL DE LICENCIAS ---")
c.execute("SELECT * FROM control_licencias")
for row in c.fetchall():
    print(row)

conn.close()
