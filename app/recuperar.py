from flask import Blueprint, render_template, request, flash, redirect, url_for, session
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import secrets
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

# Crear el blueprint
recuperar_bp = Blueprint('recuperar', __name__)

# Configuración para Gmail SMTP (opción 1)
GMAIL_HOST = 'smtp.gmail.com'
GMAIL_PORT = 587
GMAIL_USERNAME = 'senaproyecto980@gmail.com'
GMAIL_PASSWORD = 'riqf khmk inyc hdxa'

# Configuración de Mailtrap (opción 2)
MAILTRAP_HOST = 'live.smtp.mailtrap.io'
MAILTRAP_PORT = 587
MAILTRAP_USERNAME = 'api'
MAILTRAP_PASSWORD = 'smtp@mailtrap.io'

# Elegir cuál usar
USE_GMAIL = True  # 👈 True para Gmail, False para Mailtrap

def get_db_connection():
    """Obtener conexión a la base de datos"""
    conn = sqlite3.connect('gestor_de_tareas.db')
    conn.row_factory = sqlite3.Row
    return conn

def enviar_email_recuperacion(email, token):
    """Enviar email de recuperación usando Gmail o Mailtrap"""
    try:
        # Crear el mensaje
        msg = MIMEMultipart()
        msg['From'] = GMAIL_USERNAME if USE_GMAIL else 'noreply@gestortareas.com'
        msg['To'] = email
        msg['Subject'] = 'Recuperación de Contraseña - Gestor de Tareas'

        # Crear el enlace de recuperación
        enlace_recuperacion = f"http://127.0.0.1:5000/recuperar?token={token}"
        
        # Cuerpo del email en HTML
        cuerpo_html = f'''
        <html>
        <head></head>
        <body>
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #333;">🔐 Recuperación de Contraseña</h2>
                <p>Hola,</p>
                <p>Recibimos una solicitud para restablecer tu contraseña en el <strong>Gestor de Tareas</strong>.</p>
                <p>Haz clic en el siguiente enlace para crear una nueva contraseña:</p>
                <p style="margin: 20px 0; text-align: center;">
                    <a href="{enlace_recuperacion}" 
                       style="background-color: #007bff; color: white; padding: 15px 30px; 
                              text-decoration: none; border-radius: 5px; display: inline-block;
                              font-weight: bold;">
                        🔄 Restablecer Mi Contraseña
                    </a>
                </p>
                <p style="background-color: #fff3cd; padding: 10px; border-radius: 5px; border-left: 4px solid #ffc107;">
                    ⚠️ <strong>Importante:</strong> Este enlace expirará en <strong>1 hora</strong> por seguridad.
                </p>
                <p>Si no solicitaste esta recuperación, puedes ignorar este email de forma segura.</p>
                <hr style="margin: 20px 0; border: none; border-top: 1px solid #eee;">
                <p style="color: #666; font-size: 12px;">
                    Saludos,<br>
                    <strong>Equipo del Gestor de Tareas</strong><br>
                    📧 Este es un email automático, no responder.
                </p>
            </div>
        </body>
        </html>
        '''
        
        msg.attach(MIMEText(cuerpo_html, 'html'))

        # Configurar el servidor SMTP según la opción elegida
        if USE_GMAIL:
            print(f"📧 Enviando email via Gmail a {email}...")
            server = smtplib.SMTP(GMAIL_HOST, GMAIL_PORT)
            server.starttls()
            server.login(GMAIL_USERNAME, GMAIL_PASSWORD)
        else:
            print(f"📧 Enviando email via Mailtrap a {email}...")
            server = smtplib.SMTP(MAILTRAP_HOST, MAILTRAP_PORT)
            server.starttls()
            server.login(MAILTRAP_USERNAME, MAILTRAP_PASSWORD)
        
        # Enviar el email
        text = msg.as_string()
        server.sendmail(msg['From'], msg['To'], text)
        server.quit()
        
        print(f"✅ Email enviado exitosamente a {email}")
        return True
        
    except Exception as e:
        print(f"❌ Error enviando email: {e}")
        return False

def generar_token_recuperacion():
    """Generar un token único para la recuperación"""
    return secrets.token_urlsafe(32)

def guardar_token_recuperacion(email, token):
    """Guardar el token en la base de datos con tiempo de expiración"""
    conn = get_db_connection()
    expiracion = datetime.now() + timedelta(hours=1)  # Token válido por 1 hora
    
    try:
        print(f"🔍 Guardando token para {email}")
        print(f"🔍 Token: {token}")
        print(f"🔍 Expira: {expiracion}")
        
        # Eliminar tokens anteriores para este email
        conn.execute('DELETE FROM tokens_recuperacion WHERE email = ?', (email,))
        
        # Insertar nuevo token
        conn.execute('''
            INSERT INTO tokens_recuperacion (email, token, expiracion)
            VALUES (?, ?, ?)
        ''', (email, token, expiracion.isoformat()))
        
        conn.commit()
        conn.close()
        print("✅ Token guardado exitosamente")
        return True
    except Exception as e:
        print(f"❌ Error guardando token: {e}")
        conn.close()
        return False

def validar_token_recuperacion(token):
    """Validar si un token es válido y no ha expirado"""
    conn = get_db_connection()
    
    try:
        # Debug: Mostrar lo que estamos buscando
        print(f"🔍 Buscando token: {token}")
        
        resultado = conn.execute('''
            SELECT email, expiracion FROM tokens_recuperacion 
            WHERE token = ?
        ''', (token,)).fetchone()
        
        if resultado:
            print(f"🔍 Token encontrado para: {resultado['email']}")
            print(f"🔍 Expira: {resultado['expiracion']}")
            
            # Verificar si ha expirado manualmente
            from datetime import datetime
            expiracion = datetime.fromisoformat(resultado['expiracion'])
            ahora = datetime.now()
            
            print(f"🔍 Ahora: {ahora}")
            print(f"🔍 ¿Expirado?: {ahora > expiracion}")
            
            if ahora <= expiracion:
                conn.close()
                return resultado['email']
            else:
                print("❌ Token expirado")
                conn.close()
                return None
        else:
            print("❌ Token no encontrado en la base de datos")
            conn.close()
            return None
            
    except Exception as e:
        print(f"❌ Error validando token: {e}")
        conn.close()
        return None

def crear_tabla_tokens():
    """Crear la tabla de tokens de recuperación si no existe"""
    conn = get_db_connection()
    try:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS tokens_recuperacion (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                token TEXT NOT NULL UNIQUE,
                expiracion DATETIME NOT NULL,
                usado BOOLEAN DEFAULT FALSE
            )
        ''')
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error creando tabla tokens: {e}")
        conn.close()

# Crear la tabla al importar el módulo
crear_tabla_tokens()

@recuperar_bp.route('/recuperar', methods=['GET', 'POST'])
def recuperar():
    """Página para recuperación de contraseña - maneja todo el proceso"""
    token = request.args.get('token')
    
    # Debug: Mostrar información en consola
    if token:
        print(f"🔍 Token recibido: {token[:20]}...")
        email = validar_token_recuperacion(token)
        print(f"🔍 Email validado: {email}")
    else:
        print("🔍 No hay token - mostrando formulario de solicitud")
    
    # Si hay un token, mostrar formulario para nueva contraseña
    if token:
        email = validar_token_recuperacion(token)
        if not email:
            flash('El enlace de recuperación ha expirado o no es válido.', 'error')
            return redirect(url_for('recuperar.recuperar'))
        
        if request.method == 'POST':
            nueva_contrasena = request.form.get('nueva_contrasena')
            confirmar_contrasena = request.form.get('confirmar_contrasena')
            
            if not nueva_contrasena or not confirmar_contrasena:
                flash('Por favor, completa todos los campos.', 'error')
                return render_template('recuperar.html', token=token, email=email)
            
            if nueva_contrasena != confirmar_contrasena:
                flash('Las contraseñas no coinciden.', 'error')
                return render_template('recuperar.html', token=token, email=email)
            
            if len(nueva_contrasena) < 6:
                flash('La contraseña debe tener al menos 6 caracteres.', 'error')
                return render_template('recuperar.html', token=token, email=email)
            
            # Actualizar contraseña
            conn = get_db_connection()
            try:
                password_hash = generate_password_hash(nueva_contrasena)
                conn.execute('UPDATE Usuario SET contraseña = ? WHERE correo = ?', (password_hash, email))
                conn.execute('UPDATE tokens_recuperacion SET usado = TRUE WHERE token = ?', (token,))
                conn.commit()
                conn.close()
                
                flash('Contraseña actualizada exitosamente. Ya puedes iniciar sesión.', 'success')
                return redirect(url_for('login.login'))
            except Exception as e:
                print(f"Error actualizando contraseña: {e}")
                conn.close()
                flash('Error al actualizar la contraseña. Intenta nuevamente.', 'error')
                return render_template('recuperar.html', token=token, email=email)
        
        return render_template('recuperar.html', token=token, email=email)
    
    # Si no hay token, mostrar formulario para solicitar recuperación
    if request.method == 'POST':
        email = request.form.get('email')
        
        if not email:
            flash('Por favor, ingresa tu correo electrónico.', 'error')
            return render_template('recuperar.html')
        
        # Verificar si el email existe en la base de datos
        conn = get_db_connection()
        usuario = conn.execute('SELECT correo FROM Usuario WHERE correo = ?', (email,)).fetchone()
        conn.close()
        
        if usuario:
            # Generar token y enviar email
            token = generar_token_recuperacion()
            if guardar_token_recuperacion(email, token):
                if enviar_email_recuperacion(email, token):
                    flash('Se ha enviado un enlace de recuperación a tu correo electrónico.', 'success')
                else:
                    flash('Error al enviar el correo. Intenta nuevamente.', 'error')
            else:
                flash('Error al procesar la solicitud. Intenta nuevamente.', 'error')
        else:
            # Mostrar mensaje específico cuando el email no existe
            flash('El correo electrónico ingresado no se encuentra registrado en el sistema.', 'error')
        
        return render_template('recuperar.html')
    
    return render_template('recuperar.html')