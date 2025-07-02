// Mostrar solo la sección de calendario al hacer clic en el menú lateral
// Oculta las demás secciones principales
window.addEventListener('DOMContentLoaded', function () {
  const btnCalendario = document.getElementById('btn-calendario');
  const seccionCalendario = document.getElementById('contenido-calendario');
  const secciones = [
    document.getElementById('seccion-inicio'),
    document.getElementById('seccion-mis-tareas'),
    document.getElementById('contenido-planificacion'),
    document.getElementById('seccion-estadisticas'),
    document.getElementById('seccion-ayuda'),
    seccionCalendario
  ];
  if (btnCalendario && seccionCalendario) {
    btnCalendario.addEventListener('click', function (e) {
      e.preventDefault();
      secciones.forEach(sec => { if (sec) sec.style.display = 'none'; });
      seccionCalendario.style.display = 'block';
    });
  }
});
