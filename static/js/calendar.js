// Calendario animado y resaltado de tareas
// Requiere que window.tareasUsuario esté disponible
(function() {
  const calendarDays = document.getElementById('calendar-days');
  const calendarDate = document.getElementById('calendar-date');
  const btnPrev = document.getElementById('btn-prev');
  const btnNext = document.getElementById('btn-next');
  const tooltip = document.getElementById('tooltip-evento');
  const tareas = window.tareasUsuario || [];

  let fechaActual = new Date();

  function getTareasPorFecha(fechaStr) {
    return tareas.filter(t => t.fecha_vencimiento === fechaStr);
  }

  function renderCalendar(fecha) {
    calendarDays.innerHTML = '';
    const year = fecha.getFullYear();
    const month = fecha.getMonth();
    const primerDia = new Date(year, month, 1);
    const ultimoDia = new Date(year, month + 1, 0);
    const primerDiaSemana = (primerDia.getDay() + 6) % 7; // Lunes=0
    const diasMes = ultimoDia.getDate();
    const hoy = new Date();
    // Días del mes anterior para rellenar
    for (let i = 0; i < primerDiaSemana; i++) {
      const li = document.createElement('li');
      li.className = 'calendar__day calendar__day--otro-mes';
      calendarDays.appendChild(li);
    }
    // Días del mes actual
    for (let d = 1; d <= diasMes; d++) {
      const fechaStr = `${year}-${String(month+1).padStart(2,'0')}-${String(d).padStart(2,'0')}`;
      const li = document.createElement('li');
      li.className = 'calendar__day';
      li.textContent = d;
      // Hoy
      if (d === hoy.getDate() && month === hoy.getMonth() && year === hoy.getFullYear()) {
        li.classList.add('calendar__day--hoy');
      }
      // Tareas
      const tareasDia = getTareasPorFecha(fechaStr);
      if (tareasDia.length) {
        li.classList.add('calendar__day--tarea');
        li.dataset.tareas = JSON.stringify(tareasDia);
        li.addEventListener('mouseenter', e => mostrarTooltipTarea(e, tareasDia));
        li.addEventListener('mouseleave', ocultarTooltipTarea);
        li.addEventListener('click', e => mostrarTooltipTarea(e, tareasDia, true));
      }
      calendarDays.appendChild(li);
    }
    // Días del siguiente mes para rellenar
    const totalCeldas = primerDiaSemana + diasMes;
    for (let i = totalCeldas; i < 7*6; i++) {
      const li = document.createElement('li');
      li.className = 'calendar__day calendar__day--otro-mes';
      calendarDays.appendChild(li);
    }
    // Animación de transición
    calendarDays.classList.remove('animate__fadeInRight','animate__fadeInLeft');
    void calendarDays.offsetWidth;
    calendarDays.classList.add(fecha > fechaActual ? 'animate__fadeInRight' : 'animate__fadeInLeft');
    // Título
    const meses = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'];
    calendarDate.textContent = `${meses[month]} ${year}`;
  }

  function mostrarTooltipTarea(e, tareasDia, fijo) {
    if (!tareasDia.length) return;
    tooltip.innerHTML = tareasDia.map(t => `
      <div style="margin-bottom:10px;">
        <div class="tarea-tooltip-titulo">${t.titulo}</div>
        <div class="tarea-tooltip-desc">${t.descripcion}</div>
        <div class="tarea-tooltip-info"><i class='bi bi-calendar-event me-1'></i><span>Vence:</span> <b>${t.fecha_vencimiento}</b></div>
        <div class="tarea-tooltip-info"><i class='bi bi-flag me-1'></i><span>Prioridad:</span> <b>${t.prioridad ? t.prioridad.charAt(0).toUpperCase() + t.prioridad.slice(1) : ''}</b></div>
        <div class="tarea-tooltip-info"><i class='bi bi-clipboard-check me-1'></i><span>Estado:</span> <b>${t.estado ? t.estado.charAt(0).toUpperCase() + t.estado.slice(1) : ''}</b></div>
        <div class="tarea-tooltip-estado"><i class='bi bi-info-circle me-1'></i>${t.estado ? t.estado.charAt(0).toUpperCase() + t.estado.slice(1) : ''}</div>
      </div>
    `).join('<hr>');
    tooltip.style.display = 'block';
    const rect = e.target.getBoundingClientRect();
    // Centrar la nube sobre el día, pero que no se salga de la pantalla
    let left = rect.left + rect.width/2 - 180;
    left = Math.max(10, Math.min(left, window.innerWidth - 400));
    tooltip.style.left = left + 'px';
    tooltip.style.top = (rect.top + window.scrollY - tooltip.offsetHeight - 22) + 'px';
    setTimeout(() => {
      tooltip.classList.add('show');
    }, 10);
    if (fijo) {
      tooltip.style.pointerEvents = 'auto';
      tooltip.onclick = () => tooltip.style.display = 'none';
    }
  }
  function ocultarTooltipTarea() {
    tooltip.classList.remove('show');
    setTimeout(() => { tooltip.style.display = 'none'; }, 120);
  }

  btnPrev.addEventListener('click', () => {
    fechaActual = new Date(fechaActual.getFullYear(), fechaActual.getMonth()-1, 1);
    renderCalendar(fechaActual);
  });
  btnNext.addEventListener('click', () => {
    fechaActual = new Date(fechaActual.getFullYear(), fechaActual.getMonth()+1, 1);
    renderCalendar(fechaActual);
  });

  // Inicializar
  renderCalendar(fechaActual);
})();
