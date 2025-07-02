// Variables Globales
let userId = null;

// Función para obtener ID de usuario
function obtenerIdUsuario() {
  fetch('/mis-ajustes')
    .then(response => response.json())
    .then(data => {
      // Obtener ID del usuario actual desde la API
      userId = data.id;
      console.log("ID de usuario cargado:", userId);
      
      // Una vez que tenemos el ID, inicializamos las funciones que lo necesitan
      inicializarChat();
    })
    .catch(error => {
      console.error("Error al cargar datos de usuario:", error);
    });
}

// Inicializa el chat una vez que tenemos el ID
function inicializarChat() {
  const receptorSelect = document.getElementById("chat-receptor");
  // Cargar historial automáticamente del primer receptor válido
  for (let i = 0; i < receptorSelect.options.length; i++) {
    const option = receptorSelect.options[i];
    if (!option.disabled && option.value) {
      receptorSelect.selectedIndex = i;
      cargarMensajes(parseInt(option.value));
      break;
    }
  }
}

function handleStart() {
  alert("Redirigiendo al panel de tareas...");
  // Aquí podrías usar: window.location.href = "/login" o algo similar
}

// Función para mostrar/ocultar el chat
function toggleChat() {
  const chatbox = document.getElementById("chatbox");
  chatbox.classList.toggle("activo");
}

// Función para enviar mensaje
function enviarMensaje() {
  const mensaje = document.getElementById("chat-input").value.trim();
  const receptor = parseInt(document.getElementById("chat-receptor").value);

  if (!mensaje || isNaN(receptor)) {
    alert("Selecciona un receptor y escribe un mensaje.");
    return;
  }

  fetch("/enviar_mensaje", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      mensaje: mensaje,
      receptor_id: receptor
    })
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      document.getElementById("chat-input").value = "";
      cargarMensajes(receptor);
    } else {
      alert("Error al enviar mensaje.");
    }
  });
}

// Función para cargar historial de mensajes
function cargarMensajes(receptorId) {
  fetch(`/mensajes_con/${receptorId}`)
    .then(response => response.json())
    .then(mensajes => {
      console.log("Mensajes recibidos:", mensajes);  // 👈 DEBUG

      const contenedor = document.getElementById("chat-mensaje");
      contenedor.innerHTML = "";

      if (mensajes.length === 0) {
        contenedor.innerHTML = `<div class="text-muted text-center">Sin mensajes...</div>`;
        return;
      }

      mensajes.forEach(m => {
        console.log("Mensaje:", m);  // 👈 DEBUG
        const div = document.createElement("div");
        const clase = m.emisor_id === userId ? "derecha" : "izquierda";
        div.className = "mensaje " + clase;
        div.textContent = m.mensaje;
        contenedor.appendChild(div);
      });

      contenedor.scrollTop = contenedor.scrollHeight;
    });
}

// Configuración al cargar la página - Evento principal
document.addEventListener("DOMContentLoaded", function () {
  // Lo primero que hacemos es obtener el ID de usuario
  obtenerIdUsuario();
  
  // Configuración de la navegación en el sidebar
  document.getElementById('btn-inicio').addEventListener('click', function(e) {
    e.preventDefault();
    mostrarSeccion('seccion-inicio');
  });
  
  document.getElementById('btn-mis-tareas').addEventListener('click', function(e) {
    e.preventDefault();
    mostrarSeccion('seccion-mis-tareas');
  });
  
  document.getElementById('btn-calendario').addEventListener('click', function(e) {
    e.preventDefault();
    mostrarSeccion('contenido-calendario');
  });
  
  document.getElementById('btn-planificacion').addEventListener('click', function(e) {
    e.preventDefault();
    mostrarSeccion('contenido-planificacion');
  });
  
  document.getElementById('btn-estadisticas').addEventListener('click', function(e) {
    e.preventDefault();
    mostrarSeccion('seccion-estadisticas');
  });
  
  document.getElementById('btn-ayuda').addEventListener('click', function(e) {
    e.preventDefault();
    mostrarSeccion('seccion-ayuda');
  });
  
  // Inicializar chat
  const receptorSelect = document.getElementById("chat-receptor");
  if (receptorSelect) {
    // Cambiar receptor => cargar mensajes nuevos
    receptorSelect.addEventListener("change", function () {
      const receptorId = parseInt(this.value);
      if (!isNaN(receptorId)) {
        cargarMensajes(receptorId);
      }
    });
  }
  
  // Enviar con Enter
  const chatInput = document.getElementById("chat-input");
  if (chatInput) {
    chatInput.addEventListener("keydown", function (e) {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        enviarMensaje();
      }
    });
  }

  // Cargar proyectos asignados
  const tabla = document.getElementById('tabla-planificacion');
  if (tabla) {
    fetch('/api/proyectos_asignados')
      .then(response => response.json())
      .then(data => {
        tabla.innerHTML = ''; // Limpiar tabla
        if (data.length === 0) {
          tabla.innerHTML = '<tr><td colspan="5" class="text-center text-muted">Sin proyectos asignados.</td></tr>';
          return;
        }
        
        // También llenar el selector de proyectos en la barra superior
        const selectorProyectos = document.getElementById('proyecto-selector');
        if (selectorProyectos) {
          // Mantener la opción "Todos los proyectos"
          const opcionesTodas = selectorProyectos.innerHTML;
          selectorProyectos.innerHTML = opcionesTodas;
          
          data.forEach(p => {
            const opcion = document.createElement('option');
            opcion.value = p.id;
            opcion.textContent = p.nombre;
            selectorProyectos.appendChild(opcion);
          });
        }
        
        // Llenar la tabla de proyectos
        data.forEach(p => {
          tabla.innerHTML += `
            <tr>
              <td>${p.nombre}</td>
              <td>${p.descripcion || ''}</td>
              <td>${p.fecha_inicio || '-'}</td>
              <td>${p.fecha_fin || '-'}</td>
              <td><span class="badge bg-${p.estado === 'activo' ? 'success' : 'secondary'}">${p.estado}</span></td>
            </tr>
          `;
        });
      })
      .catch(err => {
        console.error('Error cargando proyectos:', err);
        tabla.innerHTML = '<tr><td colspan="5" class="text-danger text-center">Error al cargar proyectos.</td></tr>';
      });
  }
    
  // Configurar el dropdown de notificaciones
  const dropdownNotificaciones = document.getElementById('dropdownNotificaciones');
  if (dropdownNotificaciones) {
    dropdownNotificaciones.addEventListener('click', cargarNotificaciones);
  }
  
  // Formulario de soporte en la sección de ayuda
  const formularioSoporte = document.getElementById('formulario-soporte');
  if (formularioSoporte) {
    formularioSoporte.addEventListener('submit', function(e) {
      e.preventDefault();
      
      // En un entorno real, aquí enviaríamos los datos al servidor
      alert('Tu consulta ha sido enviada. Te responderemos a la brevedad.');
      
      // Limpiar el formulario
      formularioSoporte.reset();
    });
  }
});

// Función para mostrar una sección y ocultar las demás
function mostrarSeccion(idSeccion) {
  // Ocultar todas las secciones
  const secciones = document.querySelectorAll('main');
  secciones.forEach(seccion => {
    seccion.style.display = 'none';
  });
  
  // Mostrar la sección seleccionada
  document.getElementById(idSeccion).style.display = 'block';
  
  // Resaltar el elemento activo en el menú
  document.querySelectorAll('#sidebar .nav-link').forEach(link => {
    link.classList.remove('active');
  });
  
  // Buscar qué botón corresponde a esta sección
  let botonActivo;
  switch(idSeccion) {
    case 'seccion-inicio':
      botonActivo = document.getElementById('btn-inicio');
      break;
    case 'seccion-mis-tareas':
      botonActivo = document.getElementById('btn-mis-tareas');
      break;
    case 'contenido-calendario':
      botonActivo = document.getElementById('btn-calendario');
      break;
    case 'contenido-planificacion':
      botonActivo = document.getElementById('btn-planificacion');
      break;
    case 'seccion-estadisticas':
      botonActivo = document.getElementById('btn-estadisticas');
      break;
    case 'seccion-ayuda':
      botonActivo = document.getElementById('btn-ayuda');
      break;
  }
  
  if (botonActivo) {
    botonActivo.classList.add('active');
  }
}

//notificaciones
function cargarNotificaciones() {
  fetch('/api/notificaciones')
    .then(res => res.json())
    .then(data => {
      const menu = document.querySelector('[aria-labelledby="dropdownNotificaciones"]');
      menu.innerHTML = "";

      if (data.length === 0) {
        menu.innerHTML = '<li class="text-muted small">🔔 No hay notificaciones nuevas</li>';
      } else {
        data.forEach(n => {
          menu.innerHTML += `
            <li class="dropdown-item d-flex justify-content-between align-items-center ${n.leida ? 'text-muted' : ''}">
              <span>${n.mensaje}</span>
              ${!n.leida ? `<button class="btn btn-link p-0 ms-2" onclick="marcarNotificacionLeida(${n.id}, this)">Marcar leída</button>` : ''}
            </li>`;
        });
      }
    });
}

function marcarNotificacionLeida(id, btn) {
  fetch(`/api/notificaciones/${id}/leer`, { method: "POST" })
    .then(res => res.json())
    .then(() => {
      btn.parentElement.classList.add('text-muted');
      btn.remove();
    });
}

