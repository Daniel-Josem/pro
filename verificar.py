import sqlite3

conn = sqlite3.connect('gestor_de_tareas.db')
cursor = conn.cursor()

print("=== USUARIOS Y SUS GRUPOS ===")
cursor.execute('SELECT nombre_usuario, grupo, rol FROM Usuario')
usuarios = cursor.fetchall()
for u in usuarios:
    print(f'{u[0]} - Grupo: {u[1]} - Rol: {u[2]}')

print("\n=== TAREAS Y SUS GRUPOS ===")
cursor.execute('SELECT titulo, curso_destino FROM tareas')
tareas = cursor.fetchall()
for t in tareas:
    print(f'Tarea: {t[0]} - Grupo: {t[1]}')

conn.close()
