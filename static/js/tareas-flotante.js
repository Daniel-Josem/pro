const tareas = window.tareasUsuario || [];

let contenedorTarjetasFlotante = document.getElementById('contenedorTarjetasTareas');

function mostrarTarjetasTareas() {
  if (!contenedorTarjetasFlotante) {
    contenedorTarjetasFlotante = document.getElementById('contenedorTarjetasTareas');
  }
  if (!contenedorTarjetasFlotante) return;
  
  contenedorTarjetasFlotante.innerHTML = '';
  tareas.forEach(tarea => {
    const col = document.createElement('div');
    col.className = 'col-12 col-md-6 col-lg-4';
    const card = document.createElement('div');
    card.className = 'tarea-tarjeta';
    card.innerHTML = `
      <div class="tarea-titulo">${tarea.titulo}</div>
      <div class="tarea-prioridad">
        <span class="badge bg-${tarea.prioridad === 'alta' ? 'danger' : tarea.prioridad === 'media' ? 'warning' : 'secondary'} text-white">${tarea.prioridad.charAt(0).toUpperCase() + tarea.prioridad.slice(1)}</span>
        <span class="tarea-fecha"><i class="bi bi-calendar-event"></i> ${tarea.fecha_vencimiento}</span>
      </div>
      <div class="icono-estado">
        ${tarea.estado === 'completado' ? '<i class="bi bi-check-circle-fill text-success"></i>' : '<i class="bi bi-hourglass-split text-warning"></i>'}
      </div>
    `;
    // Mostrar detalles de la tarea en un modal centrado
    card.onclick = (e) => {
      e.stopPropagation();
      e.preventDefault();
      mostrarPanelDetalleTareaOverlay(tarea.id);
    };
    col.appendChild(card);
    contenedorTarjetasFlotante.appendChild(col);
  });
}

function marcarTareaCompletada(id) {
  const tarea = tareas.find(t => t.id === id);
  if (!tarea || tarea.estado === 'completado') return;
  fetch(`/api/tarea/completar/${id}`, {
    method: 'POST',
    headers: { 'X-Requested-With': 'XMLHttpRequest' }
  })
    .then(resp => resp.json())
    .then(data => {
      if (data.ok) {
        tarea.estado = 'completado';
        mostrarPanelDetalleTareaOverlay(id);
        mostrarTarjetasTareas();
        alert('¡Tarea marcada como completada!');
      } else {
        alert('No se pudo marcar como completada: ' + (data.msg || ''));
      }
    })
    .catch(() => alert('Error de red al marcar como completada.'));
}

// === Overlay Fullscreen para Mis Tareas === 
// DESHABILITADO: Funciones comentadas para evitar overlay automático
let overlayTareas = null;

function crearOverlayTareas() {
  // Función deshabilitada - no crear overlay automático
  return;
  /*
  if (document.getElementById('overlayMisTareas')) return;
  // Elimina overlays de fondo sobrantes si existen
  document.querySelectorAll('.overlay-fondo').forEach(el => el.remove());
  overlayTareas = document.createElement('div');
  overlayTareas.id = 'overlayMisTareas';
  overlayTareas.innerHTML = `
    <div class="overlay-fondo"></div>
    <div class="overlay-contenido animate__animated animate__fadeInDown">
      <button id="cerrarOverlayTareas" class="btn btn-light btn-close-overlay" title="Cerrar"><i class="bi bi-x-lg"></i></button>
      <h2 class="overlay-titulo mb-4"><i class="bi bi-list-task"></i> Mis Tareas</h2>
      <div class="row g-3" id="contenedorTarjetasTareasOverlay"></div>
    </div>
  `;
  document.body.appendChild(overlayTareas);
  document.getElementById('cerrarOverlayTareas').onclick = cerrarOverlayTareas;
  overlayTareas.querySelector('.overlay-fondo').onclick = cerrarOverlayTareas;
  */
}

function mostrarOverlayTareas() {
  // Función deshabilitada - no mostrar overlay automático
  return;
  /*
  crearOverlayTareas();
  overlayTareas = document.getElementById('overlayMisTareas');
  overlayTareas.style.display = 'flex';
  document.body.classList.add('no-scroll');
  // Recargar tareas desde el backend antes de mostrar
  fetch('/api/tareas')
    .then(resp => resp.json())
    .then(data => {
      if (Array.isArray(data)) {
        // Actualizar el array global de tareas
        window.tareasUsuario = data;
        // Si la variable tareas es un const, no se puede reasignar, pero sí actualizar su contenido si es let/var
        if (typeof tareas !== 'undefined' && Array.isArray(tareas)) {
          tareas.length = 0;
          data.forEach(t => tareas.push(t));
        }
      }
      mostrarTarjetasTareasOverlay();
    })
    .catch(() => {
      // Si falla, mostrar las tareas actuales
      mostrarTarjetasTareasOverlay();
    });
  */
}

function cerrarOverlayTareas() {
  // Función simplificada para limpiar cualquier overlay residual
  if (overlayTareas) {
    overlayTareas.style.display = 'none';
    overlayTareas.remove();
    overlayTareas = null;
  }
  document.body.classList.remove('no-scroll');
  document.body.style.overflow = 'auto';
  // Elimina cualquier overlay de fondo sobrante
  document.querySelectorAll('.overlay-fondo').forEach(el => el.remove());
  document.querySelectorAll('#overlayMisTareas').forEach(el => el.remove());
}

function mostrarTarjetasTareasOverlay() {
  // Función deshabilitada - no se necesita sin overlay
  return;
  /*
  const contenedor = document.getElementById('contenedorTarjetasTareasOverlay');
  if (!contenedor) return;
  contenedor.innerHTML = '';
  tareas.forEach(tarea => {
    const col = document.createElement('div');
    col.className = 'col-12 col-md-6 col-lg-4';
    const card = document.createElement('div');
    card.className = 'tarea-tarjeta tarea-tarjeta-overlay';
    // Mostrar solo el archivo más reciente si hay varios
    let archivoHtml = '';
    if (tarea.archivos && tarea.archivos.length > 0) {
      const archivo = tarea.archivos[tarea.archivos.length - 1];
      archivoHtml = `
        <div class="tarea-archivo-overlay mt-2">
          <i class="bi bi-paperclip text-info"></i>
          <a href="${archivo.url}" class="ms-1 link-success fw-semibold text-truncate tarea-archivo-link" target="_blank" style="max-width: 140px; display: inline-block; vertical-align: middle;">
            <i class="bi bi-file-earmark-arrow-down me-1"></i>${archivo.nombre.length > 18 ? archivo.nombre.slice(0, 15) + '...' : archivo.nombre}
          </a>
        </div>
      `;
    }
    card.innerHTML = `
      <div class="tarea-titulo">${tarea.titulo}</div>
      <div class="tarea-prioridad">
        <span class="badge bg-${tarea.prioridad === 'alta' ? 'danger' : tarea.prioridad === 'media' ? 'warning' : 'secondary'} text-white">${tarea.prioridad.charAt(0).toUpperCase() + tarea.prioridad.slice(1)}</span>
        <span class="tarea-fecha"><i class="bi bi-calendar-event"></i> ${tarea.fecha_vencimiento}</span>
      </div>
      <div class="icono-estado">
        ${tarea.estado === 'completado' ? '<i class="bi bi-check-circle-fill text-success"></i>' : '<i class="bi bi-hourglass-split text-warning"></i>'}
      </div>
      ${archivoHtml}
    `;
    // Mostrar detalles de la tarea en un modal centrado
    card.onclick = (e) => {
      e.stopPropagation();
      e.preventDefault();
      // Cerrar el overlay de "Mis Tareas" antes de abrir el modal de detalles
      cerrarOverlayTareas();
      // Pequeño delay para evitar conflictos visuales
      setTimeout(() => {
        mostrarPanelDetalleTareaOverlay(tarea.id);
      }, 100);
    };
    col.appendChild(card);
    contenedor.appendChild(col);
  });
  */
}

function mostrarPanelDetalleTareaOverlay(id) {
  console.log(`=== ABRIENDO PANTALLA FLOTANTE para tarea ID: ${id} ===`);
  
  // Limpiar cualquier overlay residual (por seguridad)
  cerrarOverlayTareas();
  
  // Eliminar cualquier modal anterior
  const modalAnterior = document.getElementById('modalDetalleTarea');
  if (modalAnterior) {
    modalAnterior.remove();
  }
  
  // Crear el modal flotante
  const modal = document.createElement('div');
  modal.id = 'modalDetalleTarea';
  modal.innerHTML = `
    <div class="modal-backdrop-custom" id="backdropModal"></div>
    <div class="modal-container-custom">
      <div class="modal-content-custom">
        <div class="modal-header-custom">
          <h3 class="modal-title-custom">
            <i class="bi bi-clipboard-check text-white me-2"></i>
            Cargando detalles de la tarea...
          </h3>
          <button type="button" class="btn-close-custom" id="cerrarModalTarea">
            <i class="bi bi-x-lg"></i>
          </button>
        </div>
        <div class="modal-body-custom">
          <div class="text-center">
            <div class="spinner-border text-success" role="status">
              <span class="visually-hidden">Cargando...</span>
            </div>
            <p class="mt-3 text-muted">Obteniendo información de la tarea ${id}...</p>
          </div>
        </div>
      </div>
    </div>
  `;
  
  // Aplicar estilos al modal
  modal.style.position = 'fixed';
  modal.style.top = '0';
  modal.style.left = '0';
  modal.style.width = '100%';
  modal.style.height = '100%';
  modal.style.zIndex = '9999';
  modal.style.display = 'flex';
  modal.style.alignItems = 'center';
  modal.style.justifyContent = 'center';
  
  document.body.appendChild(modal);
  
  // Event listeners para cerrar el modal
  document.getElementById('cerrarModalTarea').onclick = function() {
    modal.remove();
    document.body.style.overflow = 'auto';
  };
  
  document.getElementById('backdropModal').onclick = function() {
    modal.remove();
    document.body.style.overflow = 'auto';
  };
  
  // Evitar que el modal se cierre al hacer clic en el contenido
  modal.querySelector('.modal-content-custom').onclick = function(e) {
    e.stopPropagation();
  };
  
  // Bloquear scroll del body
  document.body.style.overflow = 'hidden';
  
  // Obtener datos de la tarea
  fetch(`/api/tarea/${id}`)
    .then(resp => {
      console.log(`Respuesta de API para tarea ${id}:`, resp.status);
      return resp.json();
    })
    .then(tarea => {
      console.log('Datos de tarea recibidos:', tarea);
      if (!tarea || !tarea.id) {
        modal.querySelector('.modal-body-custom').innerHTML = `
          <div class="alert alert-danger text-center">
            <i class="bi bi-exclamation-triangle me-2"></i>
            Error: No se pudo cargar la información de la tarea
          </div>
        `;
        return;
      }
      
      // Actualizar el contenido del modal con los datos reales
      modal.querySelector('.modal-title-custom').innerHTML = `
        <i class="bi bi-clipboard-check text-success me-2"></i>
        ${tarea.titulo}
      `;
      
      modal.querySelector('.modal-body-custom').innerHTML = `
        <div class="tarea-detalles-container">
          <!-- Estado y prioridad -->
          <div class="row mb-3">
            <div class="col-6">
              <span class="badge bg-${tarea.estado === 'completado' ? 'success' : 'warning'} fs-6">
                <i class="bi bi-${tarea.estado === 'completado' ? 'check-circle' : 'hourglass-split'} me-1"></i>
                ${tarea.estado === 'completado' ? 'Completada' : 'Pendiente'}
              </span>
            </div>
            <div class="col-6 text-end">
              <span class="badge bg-${tarea.prioridad === 'alta' ? 'danger' : tarea.prioridad === 'media' ? 'warning' : 'secondary'} fs-6">
                <i class="bi bi-flag me-1"></i>
                ${tarea.prioridad.charAt(0).toUpperCase() + tarea.prioridad.slice(1)}
              </span>
            </div>
          </div>
          
          <!-- Descripción -->
          <div class="mb-4">
            <h6 class="text-muted mb-2">
              <i class="bi bi-file-text me-2"></i>Descripción
            </h6>
            <p class="task-description">${tarea.descripcion}</p>
          </div>
          
          <!-- Fecha de vencimiento -->
          <div class="mb-4">
            <h6 class="text-muted mb-2">
              <i class="bi bi-calendar-event me-2"></i>Fecha de vencimiento
            </h6>
            <p><strong>${tarea.fecha_vencimiento}</strong></p>
          </div>
          
          <!-- Archivos existentes -->
          <div class="mb-4">
            <h6 class="text-muted mb-2">
              <i class="bi bi-paperclip me-2"></i>Archivos adjuntos
            </h6>
            <div class="archivos-lista">
              ${tarea.archivos && tarea.archivos.length ? 
                tarea.archivos.map(a => `
                  <div class="archivo-item-modal">
                    <i class="bi bi-file-earmark text-primary me-2"></i>
                    <a href="${a.url}" target="_blank" class="text-decoration-none">
                      ${a.nombre}
                    </a>
                  </div>
                `).join('') : 
                '<p class="text-muted"><i class="bi bi-inbox me-2"></i>No hay archivos adjuntos</p>'
              }
            </div>
          </div>
          
          <!-- Subir archivo -->
          <div class="upload-section">
            <h6 class="text-success mb-3">
              <i class="bi bi-cloud-upload me-2"></i>Subir tu trabajo
            </h6>
            <form id="formSubirArchivo${tarea.id}" enctype="multipart/form-data">
              <div class="mb-3">
                <input type="file" name="archivo" class="form-control" id="archivoInput${tarea.id}" accept="*/*" required>
                <div class="form-text">
                  <i class="bi bi-info-circle me-1"></i>
                  Selecciona el archivo con tu trabajo completado
                </div>
              </div>
              <div class="d-grid gap-2">
                <button type="submit" class="btn btn-success btn-lg" id="btnSubirArchivo${tarea.id}">
                  <i class="bi bi-upload me-2"></i>
                  Subir archivo y marcar como completada
                </button>
                ${tarea.estado !== 'completado' ? 
                  `<button type="button" class="btn btn-outline-success" id="btnSoloCompletar${tarea.id}">
                    <i class="bi bi-check-circle me-2"></i>
                    Marcar como completada sin archivo
                  </button>` : ''
                }
              </div>
            </form>
          </div>
        </div>
      `;
      
      // Event listeners para el formulario
      const form = document.getElementById(`formSubirArchivo${tarea.id}`);
      const btnSubir = document.getElementById(`btnSubirArchivo${tarea.id}`);
      const btnSoloCompletar = document.getElementById(`btnSoloCompletar${tarea.id}`);
      
      form.onsubmit = async function(e) {
        e.preventDefault();
        const archivoInput = document.getElementById(`archivoInput${tarea.id}`);
        
        if (!archivoInput.files.length) {
          alert('Por favor, selecciona un archivo.');
          return;
        }
        
        // Cambiar estado del botón
        btnSubir.disabled = true;
        btnSubir.innerHTML = '<i class="bi bi-hourglass me-2"></i>Subiendo...';
        
        const formData = new FormData();
        formData.append('archivo', archivoInput.files[0]);
        
        try {
          const resp = await fetch(`/api/tarea/subir-archivo/${tarea.id}`, {
            method: 'POST',
            body: formData
          });
          const data = await resp.json();
          
          if (data.ok) {
            // Marcar como completada automáticamente
            await fetch(`/api/tarea/completar/${tarea.id}`, {
              method: 'POST',
              headers: { 'X-Requested-With': 'XMLHttpRequest' }
            });
            
            // Mostrar mensaje de éxito
            modal.querySelector('.modal-body-custom').innerHTML = `
              <div class="text-center py-4">
                <div class="success-animation mb-3">
                  <i class="bi bi-check-circle-fill text-success" style="font-size: 4rem;"></i>
                </div>
                <h4 class="text-success mb-3">¡Tarea completada!</h4>
                <p class="text-muted mb-4">Tu archivo se ha subido correctamente y la tarea ha sido marcada como completada.</p>
                <button class="btn btn-success" onclick="document.getElementById('modalDetalleTarea').remove(); document.body.style.overflow = 'auto'; location.reload();">
                  <i class="bi bi-arrow-left me-2"></i>Volver a mis tareas
                </button>
              </div>
            `;
          } else {
            alert('Error al subir archivo: ' + (data.msg || 'Error desconocido'));
            btnSubir.disabled = false;
            btnSubir.innerHTML = '<i class="bi bi-upload me-2"></i>Subir archivo y marcar como completada';
          }
        } catch (err) {
          alert('Error de red al subir archivo.');
          btnSubir.disabled = false;
          btnSubir.innerHTML = '<i class="bi bi-upload me-2"></i>Subir archivo y marcar como completada';
        }
      };
      
      // Botón para completar sin archivo
      if (btnSoloCompletar) {
        btnSoloCompletar.onclick = async function() {
          if (confirm('¿Estás seguro de que quieres marcar esta tarea como completada sin subir un archivo?')) {
            try {
              const resp = await fetch(`/api/tarea/completar/${tarea.id}`, {
                method: 'POST',
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
              });
              const data = await resp.json();
              
              if (data.ok) {
                modal.querySelector('.modal-body-custom').innerHTML = `
                  <div class="text-center py-4">
                    <div class="success-animation mb-3">
                      <i class="bi bi-check-circle-fill text-success" style="font-size: 4rem;"></i>
                    </div>
                    <h4 class="text-success mb-3">¡Tarea completada!</h4>
                    <p class="text-muted mb-4">La tarea ha sido marcada como completada.</p>
                    <button class="btn btn-success" onclick="document.getElementById('modalDetalleTarea').remove(); document.body.style.overflow = 'auto'; location.reload();">
                      <i class="bi bi-arrow-left me-2"></i>Volver a mis tareas
                    </button>
                  </div>
                `;
              } else {
                alert('Error al completar tarea: ' + (data.msg || 'Error desconocido'));
              }
            } catch (err) {
              alert('Error de red al completar tarea.');
            }
          }
        };
      }
    })
    .catch(err => {
      console.error('Error al obtener datos de la tarea:', err);
      modal.querySelector('.modal-body-custom').innerHTML = `
        <div class="alert alert-danger text-center">
          <i class="bi bi-exclamation-triangle me-2"></i>
          Error de conexión. No se pudo cargar la información de la tarea.
        </div>
      `;
    });
}

// Esperar a que el DOM esté listo para inicializar listeners
window.addEventListener('DOMContentLoaded', function () {
  console.log('DOM cargado, inicializando event listeners para tareas flotantes...');
  
  // Solo ejecutar si estamos en la página del trabajador
  if (!document.querySelector('.tarea-interactiva')) {
    console.log('No se encontraron tarjetas de tareas, saltando inicialización de tareas flotantes');
    return;
  }
  
  const btnMisTareas = document.getElementById('btn-mis-tareas');
  // Deshabilitar el overlay automático - el botón ya no abrirá ninguna pantalla flotante
  if (btnMisTareas) {
    // Remover cualquier listener existente
    btnMisTareas.removeEventListener('click', mostrarOverlayTareas);
    // No agregar ningún nuevo listener - el botón funcionará con su comportamiento por defecto
    console.log('Botón "Mis Tareas" configurado sin overlay automático');
  }
  
  // Usar event delegation para manejar clics en tarjetas de tareas
  document.addEventListener('click', function(e) {
    // Buscar el elemento padre con la clase tarea-interactiva
    const tarjetaTarea = e.target.closest('.tarea-interactiva[data-tarea-id]');
    if (tarjetaTarea) {
      // Verificar que no sea un clic en un botón o enlace dentro de la tarjeta
      const isButton = e.target.closest('button, a, .btn');
      if (!isButton) {
        e.preventDefault();
        e.stopPropagation();
        const tareaId = parseInt(tarjetaTarea.getAttribute('data-tarea-id'));
        console.log(`EVENT DELEGATION: Clic en tarjeta con ID: ${tareaId}`);
        if (tareaId) {
          mostrarPanelDetalleTareaOverlay(tareaId);
        }
      }
    }
  });
  
  // También agregar listeners directos como respaldo con delay
  setTimeout(() => {
    const tarjetasEstaticas = document.querySelectorAll('.tarea-interactiva[data-tarea-id]');
    console.log(`Encontradas ${tarjetasEstaticas.length} tarjetas estáticas`);
    
    tarjetasEstaticas.forEach((tarjeta, index) => {
      const tareaId = tarjeta.getAttribute('data-tarea-id');
      console.log(`Agregando listener directo a tarjeta ${index + 1} con ID: ${tareaId}`);
      // Agregar estilo de cursor pointer
      tarjeta.style.cursor = 'pointer';
      
      tarjeta.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        const tareaId = parseInt(this.getAttribute('data-tarea-id'));
        console.log(`LISTENER DIRECTO: Clic en tarjeta con ID: ${tareaId}`);
        if (tareaId) {
          mostrarPanelDetalleTareaOverlay(tareaId);
        }
      }, true); // Usar capturing phase
    });
  }, 1000); // Aumentar delay a 1 segundo
  
  // Forzar recarga de tarjetas al cargar la página solo si la función existe
  if (typeof mostrarTarjetasTareas === 'function') {
    console.log('Ejecutando mostrarTarjetasTareas al cargar la página');
    mostrarTarjetasTareas();
  } else {
    console.log('mostrarTarjetasTareas no está definida o no es necesaria');
  }
});
