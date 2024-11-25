// Asegúrate de que el DOM esté completamente cargado antes de ejecutar el script
document.addEventListener("DOMContentLoaded", function () {
    const toggleButton = document.getElementById("toggle-theme");
    const body = document.body;

    // Verifica si hay una preferencia guardada en localStorage
    const savedTheme = localStorage.getItem("theme");

    if (savedTheme) {
        body.classList.toggle("dark-mode", savedTheme === "dark");
        toggleButton.textContent = savedTheme === "dark" ? "Modo Día" : "Modo Noche";
    }

    // Agrega un evento al botón para alternar entre modos
    toggleButton.addEventListener("click", function () {
        const isDarkMode = body.classList.toggle("dark-mode");

        // Actualiza el texto del botón
        toggleButton.textContent = isDarkMode ? "Modo Día" : "Modo Noche";

        // Guarda la preferencia en localStorage
        localStorage.setItem("theme", isDarkMode ? "dark" : "light");
    });
});
