from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

login_blueprint = Blueprint('login', __name__)

# Crear tabla Usuario si no existe
def crear_tabla_usuario():
    conn = sqlite3.connect('gestor_de_tareas.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Usuario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_completo TEXT NOT NULL,
            nombre_usuario TEXT NOT NULL UNIQUE,
            documento TEXT NOT NULL UNIQUE,
            correo TEXT NOT NULL UNIQUE,
            contraseña TEXT NOT NULL,
            rol TEXT DEFAULT 'trabajador',
            estado TEXT DEFAULT 'activo',
            grupo TEXT
        )
    ''')

    conn.commit()
    conn.close()

def crear_usuarios_iniciales():
    usuarios = [
        {
            'nombre_completo': 'Admin Principal',
            'nombre_usuario': 'admin',
            'documento': '1001',
            'correo': 'admin@correo.com',
            'contraseña': generate_password_hash('admin123'),
            'rol': 'admin',
            'grupo': 'Administración'
        },
        {
            'nombre_completo': 'Líder Operativo',
            'nombre_usuario': 'lider',
            'documento': '1002',
            'correo': 'lider@correo.com',
            'contraseña': generate_password_hash('lider123'),
            'rol': 'lider',
            'grupo': 'Grupo 1'
        },
        {
            'nombre_completo': 'Usuario Prueba',
            'nombre_usuario': 'usuario1',
            'documento': '1003',
            'correo': 'prueba@correo.com',
            'contraseña': generate_password_hash('1234'),
            'rol': 'trabajador',
            'grupo': 'Grupo 1'
        }
    ]

    conn = sqlite3.connect('gestor_de_tareas.db')
    cursor = conn.cursor()

    for usuario in usuarios:
        # Verificar que ni el usuario, ni el documento ni el correo existan
        cursor.execute('''
            SELECT * FROM Usuario 
            WHERE nombre_usuario = ? OR documento = ? OR correo = ?
        ''', (usuario['nombre_usuario'], usuario['documento'], usuario['correo']))
        existente = cursor.fetchone()

        if not existente:
            cursor.execute('''
                INSERT INTO Usuario (nombre_completo, nombre_usuario, documento, correo, contraseña, rol, grupo)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                usuario['nombre_completo'],
                usuario['nombre_usuario'],
                usuario['documento'],
                usuario['correo'],
                usuario['contraseña'],
                usuario['rol'],
                usuario['grupo']
            ))
        else:
            print(f"El usuario '{usuario['nombre_usuario']}' ya existe.")

    conn.commit()
    conn.close()
    print('Usuarios iniciales creados correctamente.')


# Ejecutar al importar el blueprint
crear_tabla_usuario()
crear_usuarios_iniciales()

# Conexión a la base de datos
def get_db_connection():
    conn = sqlite3.connect('gestor_de_tareas.db')
    conn.row_factory = sqlite3.Row
    return conn

# Ruta del login
@login_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nombre_usuario = request.form['nombre_usuario']
        contrasena = request.form['contrasena']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Usuario WHERE nombre_usuario = ?', (nombre_usuario,))
        usuario = cursor.fetchone()
        conn.close()
       # Verifica si el usuario existe o esta inactivo y si la contraseña es correcta (Majo)
        if usuario is None:
            flash('El usuario es incorrecto.')
        elif usuario['estado'] != 'activo':
            flash('El usuario está inactivo. Contacta al administrador.')
        elif not check_password_hash(usuario['contraseña'], contrasena):
            flash('Contraseña incorrecta.')
        else:
            session['usuario'] = nombre_usuario
            session['usuario_id'] = usuario['id'] # ✅ Guardar el ID del usuario en la sesión
            session['grupo'] = usuario['grupo'] # ✅ Guardar el grupo en la sesión
            rol = usuario['rol']

            if rol == 'admin':
                return redirect(url_for('administrador'))
            elif rol == 'lider':
                return redirect(url_for('lider.lideres'))
            else:
                return redirect(url_for('trabajador.trabajador'))

    return render_template('login.html')


# Ruta del registro
@login_blueprint.route('/crear_usuario', methods=['GET', 'POST'])
def crear_usuario():
    if request.method == 'POST':
        nombre = request.form['nombre']
        nombre_usuario = request.form['nombre_usuario']
        documento = request.form['documento']
        correo = request.form['correo']
        contrasena = request.form['contrasena']
        # El grupo se asigna después del registro, no durante el proceso de creación

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO Usuario (nombre_completo, nombre_usuario, documento, correo, contraseña)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                nombre,
                nombre_usuario,
                documento,
                correo,
                generate_password_hash(contrasena)  # Encriptación
            ))
            conn.commit()
            flash('Usuario creado exitosamente.')
            return redirect(url_for('login.login'))
        except sqlite3.IntegrityError:
            flash('El nombre de usuario, documento o correo ya existe.')
        finally:
            conn.close()

    return render_template('crear_usuario.html')
