const sidebar = document.getElementById('sidebar');

if (sidebar) {
  // Inicialmente colapsada
  sidebar.classList.add('sidebar-collapsed');

  // Expandir al pasar el mouse
  sidebar.addEventListener('mouseenter', function () {
    sidebar.classList.remove('sidebar-collapsed');
  });

  // Colapsar al quitar el mouse
  sidebar.addEventListener('mouseleave', function () {
    sidebar.classList.add('sidebar-collapsed');
  });

  // Alternar colapsado con la tecla "s" o "S"
  document.addEventListener('keydown', function(e) {
    if (e.key === 's' || e.key === 'S') {
      sidebar.classList.toggle('sidebar-collapsed');
    }
  });

  // Cambiar visualmente el enlace activo al hacer click
  document.querySelectorAll('.sidebar .nav-link').forEach(link => {
    link.addEventListener('click', function () {
      document.querySelectorAll('.sidebar .nav-link').forEach(l => l.classList.remove('active'));
      this.classList.add('active');
    });

    // Animación de salto al pasar el mouse por los botones de la sidebar
    link.addEventListener('mouseenter', function () {
      this.classList.add('saltito');
    });
    link.addEventListener('mouseleave', function () {
      this.classList.remove('saltito');
    });
  });
}

