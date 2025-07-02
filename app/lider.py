from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash,check_password_hash
import sqlite3
import os
from werkzeug.utils import secure_filename

lider = Blueprint('lider', __name__)

# Crear tarea
@lider.route('/crear_tarea', methods=['POST'])
def crear_tarea():
    if 'usuario' not in session:
        return redirect(url_for('login.login'))

    conn = sqlite3.connect('gestor_de_tareas.db')
    cursor = conn.cursor()

    titulo = request.form['titulo']
    descripcion = request.form['descripcion']
    curso_destino = request.form['curso_destino']
    fecha_vencimiento = request.form['fecha_vencimiento']
    prioridad = request.form['prioridad']
    estado = request.form['estado']

    archivo = request.files['archivo']
    if archivo and archivo.filename != '':
        filename = secure_filename(archivo.filename)
        ruta_archivo = f"archivos_tareas/{filename}"
        # Crear directorio si no existe
        upload_dir = os.path.join('static', 'archivos_tareas')
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        archivo.save(os.path.join('static', ruta_archivo))
    else:
        ruta_archivo = None

    cursor.execute('INSERT INTO tareas (titulo, descripcion, curso_destino, fecha_vencimiento, prioridad, estado, ruta_archivo, fecha_registro) VALUES (?, ?, ?, ?, ?, ?, ?, DATE("now"))', 
                   (titulo, descripcion, curso_destino, fecha_vencimiento, prioridad, estado, ruta_archivo))

    conn.commit()
    conn.close()

    flash('Tarea creada exitosamente')
    return redirect(url_for('lider.lideres'))

# Mostrar tareas
@lider.route('/lideres')
def lideres():
    if 'usuario' not in session:
        return redirect(url_for('login.login'))

    conn = sqlite3.connect('gestor_de_tareas.db')
    conn.row_factory = sqlite3.Row

    grupo_lider = session.get('grupo')
    nombre_lider = session.get('usuario')

    # Tareas solo del grupo del líder (ignorando mayúsculas y minúsculas)
    tareas = conn.execute('SELECT * FROM tareas WHERE LOWER(curso_destino) = LOWER(?)', (grupo_lider,)).fetchall()

    # Proyectos solo del grupo del líder (ignorando mayúsculas y minúsculas)
    proyectos = conn.execute('SELECT * FROM Proyecto WHERE LOWER(grupo) = LOWER(?)', (grupo_lider,)).fetchall()

    # Solo usuarios del grupo del líder (ignorando mayúsculas y minúsculas)
    usuarios_por_grupo = {grupo_lider: []}
    usuarios = conn.execute('SELECT nombre_completo, nombre_usuario, correo, grupo FROM Usuario WHERE LOWER(grupo) = LOWER(?)', (grupo_lider,)).fetchall()
    for usuario in usuarios:
        usuarios_por_grupo[grupo_lider].append(usuario)

    conn.close()

    return render_template('lider.html', tareas=tareas, proyectos=proyectos, usuarios_por_grupo=usuarios_por_grupo, nombre_usuario=nombre_lider)




# Editar tarea
@lider.route('/editar_tarea', methods=['POST'])
def editar_tarea():
    if 'usuario' not in session:
        return redirect(url_for('login.login'))

    id_tarea = request.form['id']
    titulo = request.form['titulo']
    descripcion = request.form['descripcion']
    curso_destino = request.form['curso_destino']
    fecha_vencimiento = request.form['fecha_vencimiento']
    prioridad = request.form['prioridad']
    estado = request.form['estado']

    archivo = request.files['archivo']
    ruta_archivo = None

    if archivo and archivo.filename != '':
        filename = secure_filename(archivo.filename)
        ruta_archivo = f"archivos_tareas/{filename}"
        # Crear directorio si no existe
        upload_dir = os.path.join('static', 'archivos_tareas')
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        archivo.save(os.path.join('static', ruta_archivo))

    conn = sqlite3.connect('gestor_de_tareas.db')
    cursor = conn.cursor()

    if ruta_archivo:
        cursor.execute('''
            UPDATE tareas 
            SET titulo = ?, descripcion = ?, curso_destino = ?, fecha_vencimiento = ?, prioridad = ?, estado = ?, ruta_archivo = ?
            WHERE id = ?
        ''', (titulo, descripcion, curso_destino, fecha_vencimiento, prioridad, estado, ruta_archivo, id_tarea))
    else:
        cursor.execute('''
            UPDATE tareas 
            SET titulo = ?, descripcion = ?, curso_destino = ?, fecha_vencimiento = ?, prioridad = ?, estado = ?
            WHERE id = ?
        ''', (titulo, descripcion, curso_destino, fecha_vencimiento, prioridad, estado, id_tarea))

    conn.commit()
    conn.close()

    flash('Tarea actualizada exitosamente')
    return redirect(url_for('lider.lideres'))

# Eliminar tarea
@lider.route('/eliminar_tarea/<int:id>', methods=['POST'])
def eliminar_tarea(id):
    if 'usuario' not in session:
        return redirect(url_for('login.login'))

    conn = sqlite3.connect('gestor_de_tareas.db')
    cursor = conn.cursor()

    cursor.execute('DELETE FROM tareas WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    flash('Tarea eliminada exitosamente')
    return redirect(url_for('lider.lideres'))

@lider.route('/crear_proyecto', methods=['POST'])
def crear_proyecto():
    if 'usuario' not in session:
        return redirect(url_for('login.login'))

    nombre = request.form['nombre']
    descripcion = request.form['descripcion']
    fecha_inicio = request.form['fecha_inicio']
    fecha_fin = request.form['fecha_fin']
    grupo_lider = session.get('grupo')  # Obtener el grupo del líder

    conn = sqlite3.connect('gestor_de_tareas.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO Proyecto (nombre, descripcion, grupo, fecha_inicio, fecha_fin) VALUES (?, ?, ?, ?, ?)',
                   (nombre, descripcion, grupo_lider, fecha_inicio, fecha_fin))
    conn.commit()
    conn.close()

    flash('Proyecto creado exitosamente', 'success')
    return redirect(url_for('lider.lideres'))  # Esto debe estar así para recargar la vista

@lider.route('/eliminar_proyecto/<int:id>', methods=['POST'])
def eliminar_proyecto(id):
    if 'usuario' not in session:
        return redirect(url_for('login.login'))

    conn = sqlite3.connect('gestor_de_tareas.db')
    cursor = conn.cursor()

    # Desvincular las tareas del proyecto eliminado
    cursor.execute('UPDATE tareas SET id_proyecto = NULL WHERE id_proyecto = ?', (id,))

    cursor.execute('DELETE FROM Proyecto WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    flash('Proyecto eliminado exitosamente', 'success')
    return redirect(url_for('lider.lideres'))

@lider.route('/asignar_tarea_a_proyecto', methods=['POST'])
def asignar_tarea_a_proyecto():
    if 'usuario' not in session:
        return redirect(url_for('login.login'))

    tarea_id = request.form['tarea_id']
    proyecto_id = request.form['proyecto_id']

    conn = sqlite3.connect('gestor_de_tareas.db')
    cursor = conn.cursor()

    cursor.execute('UPDATE tareas SET id_proyecto = ? WHERE id = ?', (proyecto_id, tarea_id))
    conn.commit()
    conn.close()

    flash('Tarea asignada exitosamente al proyecto', 'success')
    return redirect(url_for('lider.lideres'))

@lider.route('/notificaciones')
def ver_notificaciones():
    if 'usuario' not in session:
        return redirect(url_for('login.login'))
    usuario = session['usuario']
    conn = sqlite3.connect('gestor_de_tareas.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    # Obtener id del usuario actual (líder)
    cur.execute('SELECT id FROM Usuario WHERE nombre_usuario = ?', (usuario,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return 'Usuario no encontrado', 404
    id_lider = row['id']
    # Obtener notificaciones para el líder
    cur.execute('SELECT * FROM notificaciones WHERE id_usuario = ? ORDER BY id DESC', (id_lider,))
    notificaciones = cur.fetchall()
    conn.close()
    return {'notificaciones': [dict(n) for n in notificaciones]}

@lider.route('/notificaciones/marcar_leida', methods=['POST'])
def marcar_notificacion_leida():
    if 'usuario' not in session:
        return {'success': False, 'error': 'No autenticado'}, 401
    data = request.get_json()
    notificacion_id = data.get('id')
    if not notificacion_id:
        return {'success': False, 'error': 'ID requerido'}, 400
    conn = sqlite3.connect('gestor_de_tareas.db')
    cur = conn.cursor()
    cur.execute('UPDATE notificaciones SET leido = 1 WHERE id = ?', (notificacion_id,))
    conn.commit()
    conn.close()
    return {'success': True}

@lider.route('/api/tarea/<int:tarea_id>/archivos')
def obtener_archivos_tarea(tarea_id):
    if 'usuario' not in session:
        return jsonify({'error': 'No autorizado'}), 401

    conn = sqlite3.connect('gestor_de_tareas.db')
    cursor = conn.cursor()

    try:
        # Obtener información de la tarea
        cursor.execute('SELECT titulo, curso_destino FROM tareas WHERE id = ?', (tarea_id,))
        tarea_info = cursor.fetchone()
        
        if not tarea_info:
            return jsonify({'error': 'Tarea no encontrada'}), 404

        titulo_tarea, curso_destino = tarea_info

        # Obtener archivos subidos por trabajadores
        cursor.execute('''
            SELECT 
                ta.nombre_archivo,
                ta.ruta_archivo,
                ta.fecha_subida,
                u.nombre_completo,
                u.nombre_usuario
            FROM tarea_archivos ta
            JOIN Usuario u ON ta.usuario_id = u.id
            WHERE ta.tarea_id = ?
            ORDER BY ta.fecha_subida DESC
        ''', (tarea_id,))
        
        archivos_raw = cursor.fetchall()
        archivos = []
        for archivo in archivos_raw:
            nombre_archivo, ruta_archivo, fecha_subida, nombre_completo, usuario = archivo
            archivos.append({
                'nombre': nombre_archivo,
                'url': f'/static/{ruta_archivo}' if ruta_archivo else '#',
                'fecha_subida': fecha_subida,
                'usuario': nombre_completo or usuario
            })

        # Estadísticas
        cursor.execute('SELECT COUNT(*) FROM Usuario WHERE grupo = ?', (curso_destino,))
        total_trabajadores = cursor.fetchone()[0]

        cursor.execute('''
            SELECT COUNT(DISTINCT ta.usuario_id) 
            FROM tarea_archivos ta 
            WHERE ta.tarea_id = ?
        ''', (tarea_id,))
        tareas_completadas = cursor.fetchone()[0]

        tareas_pendientes = total_trabajadores - tareas_completadas

        estadisticas = {
            'total_trabajadores': total_trabajadores,
            'tareas_completadas': tareas_completadas,
            'tareas_pendientes': tareas_pendientes
        }

        return jsonify({
            'archivos': archivos,
            'estadisticas': estadisticas,
            'tarea': {
                'id': tarea_id,
                'titulo': titulo_tarea,
                'curso': curso_destino
            }
        })

    except Exception as e:
        print(f"Error al obtener archivos de tarea {tarea_id}: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500
    finally:
        conn.close()

@lider.route('/obtener_perfil_lider')
def obtener_perfil_lider():
    if 'usuario' not in session:
        return {'success': False}

    conn = sqlite3.connect('gestor_de_tareas.db')
    conn.row_factory = sqlite3.Row

    usuario = session.get('usuario')
    user = conn.execute('SELECT nombre_completo, correo FROM Usuario WHERE nombre_usuario = ?', (usuario,)).fetchone()
    conn.close()

    if user:
        return {'success': True, 'nombre': user['nombre_completo'], 'correo': user['correo']}
    else:
        return {'success': False}


@lider.route('/actualizar_perfil_lider', methods=['POST'])
def actualizar_perfil_lider():
    if 'usuario' not in session:
        return redirect(url_for('login.login'))

    usuario = request.form['usuario']
    nombre = request.form['nombre']
    correo = request.form['correo']
    contraseña_actual = request.form['contraseña_actual']
    nueva_contraseña = request.form['nueva_contraseña']
    confirmar_contraseña = request.form['confirmar_contraseña']

    conn = sqlite3.connect('gestor_de_tareas.db')
    conn.row_factory = sqlite3.Row  # Esto es lo que te faltaba
    cursor = conn.cursor()

    # Verificar si el usuario existe
    user = cursor.execute('SELECT * FROM Usuario WHERE nombre_usuario = ?', (usuario,)).fetchone()

    if not user:
        conn.close()
        return 'Usuario no encontrado'

    # Si el usuario quiere cambiar la contraseña
    if contraseña_actual and nueva_contraseña and confirmar_contraseña:
        if nueva_contraseña != confirmar_contraseña:
            conn.close()
            return 'Las contraseñas nuevas no coinciden'

        if not check_password_hash(user['contraseña'], contraseña_actual):
            conn.close()
            return 'La contraseña actual es incorrecta'

        # Cambiar contraseña
        nueva_contraseña_hash = generate_password_hash(nueva_contraseña)
        cursor.execute('UPDATE Usuario SET nombre_completo = ?, correo = ?, contraseña = ? WHERE nombre_usuario = ?', 
                       (nombre, correo, nueva_contraseña_hash, usuario))
    else:
        # Solo actualizar nombre y correo
        cursor.execute('UPDATE Usuario SET nombre_completo = ?, correo = ? WHERE nombre_usuario = ?', 
                       (nombre, correo, usuario))

    conn.commit()
    conn.close()

    return redirect(url_for('lider.lideres'))



