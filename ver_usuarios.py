import sqlite3
from datetime import datetime

conn = sqlite3.connect('users.db')
cursor = conn.cursor()

cursor.execute('SELECT username, name, email, created_at FROM users')
users = cursor.fetchall()

print("\n" + "="*80)
print("👥 USUARIOS REGISTRADOS EN LA BASE DE DATOS")
print("="*80)

if users:
    print(f"\n{'Usuario':<15} {'Nombre':<25} {'Email':<30} {'Fecha':<20}")
    print("-"*90)
    for user in users:
        print(f"{user[0]:<15} {user[1]:<25} {user[2]:<30} {user[3]:<20}")
    print(f"\n📊 Total: {len(users)} usuario(s) registrado(s)")
else:
    print("\n❌ No hay usuarios registrados")

# Verificar estructura de la tabla
cursor.execute("PRAGMA table_info(users)")
columns = cursor.fetchall()

print("\n" + "="*80)
print("🗂️  ESTRUCTURA DE LA TABLA 'users'")
print("="*80)
for col in columns:
    print(f"  • {col[1]} ({col[2]})")

conn.close()

print("\n" + "="*80)
print("🔐 SISTEMA DE SEGURIDAD:")
print("="*80)
print("  ✅ Contraseñas encriptadas con bcrypt")
print("  ✅ Base de datos SQLite local (users.db)")
print("  ✅ Usuario por defecto: admin / admin123")
print("  ✅ Registro de nuevos usuarios habilitado")
print("="*80 + "\n")
