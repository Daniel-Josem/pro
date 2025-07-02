import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def enviar_notificacion_lider(correo_destino, asunto, mensaje):
    """
    Función para enviar notificaciones por email a los líderes.
    
    Args:
        correo_destino (str): Email del destinatario
        asunto (str): Asunto del email
        mensaje (str): Contenido del mensaje
    """
    try:
        # Configuración del servidor de email (debes configurar estos valores)
        SMTP_SERVER = "smtp.gmail.com"  # Cambiar por tu servidor SMTP
        SMTP_PORT = 587
        EMAIL_USER = "tu_email@gmail.com"  # Cambiar por tu email
        EMAIL_PASSWORD = "tu_contraseña"  # Cambiar por tu contraseña de aplicación
        
        # Crear el mensaje
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = correo_destino
        msg['Subject'] = asunto
        
        # Agregar el cuerpo del mensaje
        msg.attach(MIMEText(mensaje, 'plain'))
        
        # Conectar al servidor y enviar el email
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Habilitar encriptación
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        
        text = msg.as_string()
        server.sendmail(EMAIL_USER, correo_destino, text)
        server.quit()
        
        print(f"Email enviado exitosamente a {correo_destino}")
        return True
        
    except Exception as e:
        print(f"Error al enviar email a {correo_destino}: {str(e)}")
        return False

def configurar_email(smtp_server, smtp_port, email_user, email_password):
    """
    Función para configurar los parámetros de email desde la aplicación principal.
    
    Args:
        smtp_server (str): Servidor SMTP
        smtp_port (int): Puerto SMTP
        email_user (str): Usuario de email
        email_password (str): Contraseña de email
    """
    global SMTP_SERVER, SMTP_PORT, EMAIL_USER, EMAIL_PASSWORD
    SMTP_SERVER = smtp_server
    SMTP_PORT = smtp_port
    EMAIL_USER = email_user
    EMAIL_PASSWORD = email_password
