document.addEventListener('DOMContentLoaded', function() {
    const toggleSidebar = document.getElementById('toggleSidebar');
    const sidebar = document.getElementById('sidebar');
    const submenuToggles = document.querySelectorAll('.has-submenu > a');

    toggleSidebar.addEventListener('click', function() {
        sidebar.classList.toggle('closed');
    });

    submenuToggles.forEach(toggle => {
        toggle.addEventListener('click', function(event) {
            if (sidebar.classList.contains('closed')) {
                event.preventDefault();
            } else {
                const submenu = toggle.nextElementSibling;
                submenu.classList.toggle('open');
            }
        });
    });
});

