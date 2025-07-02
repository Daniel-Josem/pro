import sqlite3

conn = sqlite3.connect('gestor_de_tareas.db')
cursor = conn.cursor()

# Estandarizar los grupos
cursor.execute('UPDATE Usuario SET grupo = "Grupo 1" WHERE nombre_usuario = "daniel"')
conn.commit()

print("Grupo de daniel actualizado a 'Grupo 1'")
conn.close()
