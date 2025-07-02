from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
import sqlite3
import os
from datetime import datetime
import smtplib
from email.mime.text import MIMEText



trabajador_blueprint = Blueprint('trabajador', __name__)

@trabajador_blueprint.route('/trabajador')
def trabajador():
    if 'usuario' not in session:
        return redirect(url_for('login.login'))

    usuario_id = session.get('usuario')
    grupo_usuario = session.get('grupo')
    print(f"ID usuario logueado: {usuario_id}, Grupo: '{grupo_usuario}'")

    conn = sqlite3.connect('gestor_de_tareas.db')
    conn.row_factory = sqlite3.Row

    proyecto_row = conn.execute(
        'SELECT proyecto FROM usuario WHERE id = ?', (usuario_id,)
    ).fetchone()

    nombre_proyecto = proyecto_row['proyecto'] if proyecto_row else "Sin proyecto asignado"

    cursos = conn.execute('SELECT DISTINCT curso_destino FROM tareas').fetchall()
    for c in cursos:
        print(f"'{c['curso_destino']}'")

    tareas = conn.execute('''
        SELECT * FROM tareas
        WHERE id_usuario_asignado = ? OR TRIM(LOWER(curso_destino)) = TRIM(LOWER(?))
    ''', (usuario_id, grupo_usuario)).fetchall()

    proyectos = conn.execute('SELECT * FROM Proyecto').fetchall()
    conn.close()

    print(f"Tareas encontradas: {tareas}")

    # Procesar tareas
    tareas_list = []
    for t in tareas:
        tarea_dict = dict(t)
        fecha = tarea_dict.get('fecha_vencimiento')
        dt = None
        if fecha:
            for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y'):
                try:
                    dt = datetime.strptime(fecha, fmt)
                    break
                except ValueError:
                    continue
        if dt:
            tarea_dict['fecha_vencimiento'] = dt.strftime('%Y-%m-%d')

        # Archivos relacionados
        archivos = []
        carpeta = os.path.join('static', 'archivos_tareas')
        if os.path.exists(carpeta):
            for nombre in os.listdir(carpeta):
                if nombre.startswith(f'{tarea_dict["id"]}_') or nombre.startswith(f'{tarea_dict["id"]}-') or nombre.startswith(f'{tarea_dict["id"]}'):
                    archivos.append({
                        'nombre': nombre,
                        'url': f'/static/archivos_tareas/{nombre}'
                    })
        tarea_dict['archivos'] = archivos
        tareas_list.append(tarea_dict)

    return render_template(
        'trabajador.html',
        tareas=tareas_list,
        proyectos=proyectos,
        nombre_proyecto=nombre_proyecto
    )

def notificar_lider_tarea_completada(tarea_id):
    conn = sqlite3.connect('gestor_de_tareas.db')
    cur = conn.cursor()
    # Obtener info de la tarea y el usuario asignado
    cur.execute('SELECT titulo, id_usuario_asignado, curso_destino FROM tareas WHERE id = ?', (tarea_id,))
    tarea = cur.fetchone()
    if not tarea:
        conn.close()
        return
    titulo, id_usuario_asignado, curso_destino = tarea
    # Buscar líder por grupo (curso_destino) o por proyecto si lo tienes
    cur.execute('''
        SELECT id, correo FROM Usuario
        WHERE rol = 'lider' AND TRIM(LOWER(grupo)) = TRIM(LOWER(?))
    ''', (curso_destino,))
    lider = cur.fetchone()
    if not lider:
        conn.close()
        return
    id_lider, correo_lider = lider
    # Insertar notificación en la base de datos
    mensaje = f'La tarea "{titulo}" ha sido completada por el trabajador.'
    cur.execute('INSERT INTO notificaciones (mensaje, id_usuario) VALUES (?, ?)', (mensaje, id_lider))
    conn.commit()
    conn.close()
    # Enviar correo
    try:
        from app.email_service import enviar_notificacion_lider
        enviar_notificacion_lider(correo_lider, 'Tarea completada', mensaje)
    except Exception as e:
        print('Error enviando email al líder:', e)

# --- API para marcar tarea como completada ---
@trabajador_blueprint.route('/api/tarea/completar/<int:tarea_id>', methods=['POST'])
def completar_tarea(tarea_id):
    if 'usuario' not in session:
        return jsonify({'ok': False, 'msg': 'No autorizado'}), 401
    try:
        conn = sqlite3.connect('gestor_de_tareas.db')
        cur = conn.cursor()
        cur.execute('UPDATE tareas SET estado = ? WHERE id = ?', ('completado', tarea_id))
        conn.commit()
        conn.close()
        notificar_lider_tarea_completada(tarea_id)
        return jsonify({'ok': True})
    except Exception as e:
        return jsonify({'ok': False, 'msg': str(e)}), 500

# --- API para subir archivo a tarea ---
@trabajador_blueprint.route('/api/tarea/subir-archivo/<int:tarea_id>', methods=['POST'])
def subir_archivo_tarea(tarea_id):
    if 'usuario' not in session:
        return jsonify({'ok': False, 'msg': 'No autorizado'}), 401
    if 'archivo' not in request.files:
        return jsonify({'ok': False, 'msg': 'No se envió archivo'}), 400
    archivo = request.files['archivo']
    if archivo.filename == '':
        return jsonify({'ok': False, 'msg': 'Nombre de archivo vacío'}), 400
    
    # Obtener información del usuario
    usuario_id = session.get('usuario_id')  # Asumiendo que tienes el ID del usuario en sesión
    if not usuario_id:
        # Si no tienes usuario_id en sesión, obtenerlo de la base de datos
        conn = sqlite3.connect('gestor_de_tareas.db')
        cur = conn.cursor()
        cur.execute('SELECT id FROM Usuario WHERE usuario = ?', (session.get('usuario'),))
        result = cur.fetchone()
        conn.close()
        if result:
            usuario_id = result[0]
        else:
            return jsonify({'ok': False, 'msg': 'Usuario no encontrado'}), 400
    
    carpeta_destino = os.path.join('static', 'archivos_tareas')
    if not os.path.exists(carpeta_destino):
        os.makedirs(carpeta_destino)
    
    # Crear nombre único para el archivo
    nombre_archivo_original = archivo.filename
    nombre_archivo = f"{tarea_id}_{usuario_id}_{archivo.filename}"
    ruta_destino = os.path.join(carpeta_destino, nombre_archivo)
    ruta_relativa = f"archivos_tareas/{nombre_archivo}"
    
    print(f"=== DEBUG SUBIDA DE ARCHIVO ===")
    print(f"Tarea ID: {tarea_id}")
    print(f"Usuario ID: {usuario_id}")
    print(f"Archivo original: {nombre_archivo_original}")
    print(f"Nombre final: {nombre_archivo}")
    print(f"Ruta destino: {ruta_destino}")
    print(f"Ruta relativa: {ruta_relativa}")
    
    # Guardar el archivo físicamente
    archivo.save(ruta_destino)
    print(f"Archivo guardado en: {ruta_destino}")
    
    # Verificar que el archivo se guardó
    if os.path.exists(ruta_destino):
        print(f"✅ Archivo confirmado en sistema de archivos")
    else:
        print(f"❌ ERROR: Archivo NO encontrado en sistema de archivos")
    
    try:
        conn = sqlite3.connect('gestor_de_tareas.db')
        cur = conn.cursor()
        
        # Insertar el archivo en la tabla tarea_archivos
        cur.execute('''
            INSERT INTO tarea_archivos (tarea_id, usuario_id, nombre_archivo, ruta_archivo)
            VALUES (?, ?, ?, ?)
        ''', (tarea_id, usuario_id, nombre_archivo_original, ruta_relativa))
        print(f"✅ Registro insertado en tarea_archivos")
        
        # Marcar la tarea como completada
        cur.execute('UPDATE tareas SET estado = ? WHERE id = ?', ('completado', tarea_id))
        print(f"✅ Tarea {tarea_id} marcada como completada")
        
        conn.commit()
        conn.close()
        
        # Notificar al líder
        notificar_lider_tarea_completada(tarea_id)
        
    except Exception as e:
        return jsonify({'ok': False, 'msg': f'Archivo subido pero error al actualizar base de datos: {str(e)}'}), 500
    
    return jsonify({
        'ok': True, 
        'nombre': nombre_archivo_original, 
        'url': '/' + ruta_destino.replace('\\', '/')
    })

# --- API para obtener detalles de tarea ---
@trabajador_blueprint.route('/api/tarea/<int:tarea_id>')
def api_tarea_detalle(tarea_id):
    if 'usuario' not in session:
        return jsonify({'ok': False, 'msg': 'No autorizado'}), 401
    conn = sqlite3.connect('gestor_de_tareas.db')
    conn.row_factory = sqlite3.Row
    tarea = conn.execute('SELECT * FROM tareas WHERE id = ?', (tarea_id,)).fetchone()
    archivos = []
    # Si tienes una tabla de archivos, aquí deberías consultarla. Si no, deja vacío o busca en carpeta.
    # Ejemplo: buscar archivos en static/archivos_tareas/ que empiecen con el id de la tarea
    carpeta = os.path.join('static', 'archivos_tareas')
    if os.path.exists(carpeta):
        for nombre in os.listdir(carpeta):
            if nombre.startswith(f'{tarea_id}_') or nombre.startswith(f'{tarea_id}-') or nombre.startswith(f'{tarea_id}'):  # Ajusta según tu convención
                archivos.append({
                    'nombre': nombre,
                    'url': f'/static/archivos_tareas/{nombre}'
                })
    conn.close()
    if not tarea:
        return jsonify({'ok': False, 'msg': 'Tarea no encontrada'}), 404
    tarea_dict = dict(tarea)
    tarea_dict['archivos'] = archivos
    return jsonify(tarea_dict)

# --- API para obtener todas las tareas del usuario ---
@trabajador_blueprint.route('/api/tareas')
def api_tareas_usuario():
    if 'usuario' not in session:
        return jsonify({'ok': False, 'msg': 'No autorizado'}), 401
    usuario_id = session.get('usuario')
    grupo_usuario = session.get('grupo')
    conn = sqlite3.connect('gestor_de_tareas.db')
    conn.row_factory = sqlite3.Row
    tareas = conn.execute('''
        SELECT * FROM tareas
        WHERE id_usuario_asignado = ? OR TRIM(LOWER(curso_destino)) = TRIM(LOWER(?))
    ''', (usuario_id, grupo_usuario)).fetchall()
    conn.close()
    tareas_list = []
    for t in tareas:
        tarea_dict = dict(t)
        fecha = tarea_dict.get('fecha_vencimiento')
        if fecha:
            try:
                dt = datetime.strptime(fecha, '%Y-%m-%d')
            except ValueError:
                try:
                    dt = datetime.strptime(fecha, '%d/%m/%Y')
                except ValueError:
                    try:
                        dt = datetime.strptime(fecha, '%d-%m-%Y')
                    except ValueError:
                        dt = None
            if dt:
                tarea_dict['fecha_vencimiento'] = dt.strftime('%Y-%m-%d')
        # Buscar todos los archivos asociados a la tarea
        carpeta = os.path.join('static', 'archivos_tareas')
        archivos = []
        if os.path.exists(carpeta):
            for nombre in os.listdir(carpeta):
                if nombre.startswith(f"{t['id']}_") or nombre.startswith(f"{t['id']}-") or nombre.startswith(f"{t['id']}"):
                    archivos.append({
                        'nombre': nombre,
                        'url': f'/static/archivos_tareas/{nombre}'
                    })
        tarea_dict['archivos'] = archivos
        # (Opcional) Mantener ruta_archivo para compatibilidad, pero solo el primero
        tarea_dict['ruta_archivo'] = archivos[0]['nombre'] if archivos else None
        tareas_list.append(tarea_dict)
    return jsonify(tareas_list)


# --- ENDPOINT DE DEPURACIÓN: Verificar archivos en base de datos ---
@trabajador_blueprint.route('/api/debug/archivos')
def debug_archivos():
    if 'usuario' not in session:
        return jsonify({'ok': False, 'msg': 'No autorizado'}), 401
    
    conn = sqlite3.connect('gestor_de_tareas.db')
    cursor = conn.cursor()
    
    # Verificar si la tabla existe
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tarea_archivos';")
    tabla_existe = cursor.fetchone()
    
    if not tabla_existe:
        conn.close()
        return jsonify({
            'ok': False, 
            'msg': 'La tabla tarea_archivos no existe',
            'archivos': []
        })
    
    # Obtener todos los archivos
    cursor.execute('''
        SELECT ta.*, u.usuario, t.titulo 
        FROM tarea_archivos ta
        LEFT JOIN Usuario u ON ta.usuario_id = u.id
        LEFT JOIN tareas t ON ta.tarea_id = t.id
        ORDER BY ta.fecha_subida DESC
    ''')
    archivos = cursor.fetchall()
    
    archivos_list = []
    for archivo in archivos:
        archivos_list.append({
            'id': archivo[0],
            'tarea_id': archivo[1],
            'usuario_id': archivo[2],
            'nombre_archivo': archivo[3],
            'ruta_archivo': archivo[4],
            'fecha_subida': archivo[5],
            'usuario': archivo[6] if len(archivo) > 6 else 'Desconocido',
            'titulo_tarea': archivo[7] if len(archivo) > 7 else 'Desconocido'
        })
    
    conn.close()
    
    return jsonify({
        'ok': True,
        'total_archivos': len(archivos_list),
        'archivos': archivos_list
    })


# --- ENDPOINT DE DEPURACIÓN: Listar archivos físicos ---
@trabajador_blueprint.route('/api/debug/archivos-fisicos')
def debug_archivos_fisicos():
    if 'usuario' not in session:
        return jsonify({'ok': False, 'msg': 'No autorizado'}), 401
    
    carpeta = os.path.join('static', 'archivos_tareas')
    archivos_fisicos = []
    
    if os.path.exists(carpeta):
        for nombre in os.listdir(carpeta):
            ruta_completa = os.path.join(carpeta, nombre)
            if os.path.isfile(ruta_completa):
                stat = os.stat(ruta_completa)
                archivos_fisicos.append({
                    'nombre': nombre,
                    'tamaño': stat.st_size,
                    'fecha_modificacion': stat.st_mtime
                })
    
    return jsonify({
        'ok': True,
        'carpeta': carpeta,
        'total_archivos': len(archivos_fisicos),
        'archivos': archivos_fisicos
    })

# --- API para obtener notificaciones del trabajador ---
@trabajador_blueprint.route('/api/notificaciones')
def api_notificaciones_trabajador():
    if 'usuario' not in session:
        return jsonify({'ok': False, 'msg': 'No autorizado'}), 401
    usuario_id = session.get('usuario')
    conn = sqlite3.connect('gestor_de_tareas.db')
    conn.row_factory = sqlite3.Row
    notificaciones = conn.execute('SELECT * FROM notificaciones WHERE id_usuario = ? ORDER BY id DESC', (usuario_id,)).fetchall()
    conn.close()
    return jsonify({'ok': True, 'notificaciones': [dict(n) for n in notificaciones]})



