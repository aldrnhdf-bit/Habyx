// Initialize theme on any page
function initTheme() {
    const saved = localStorage.getItem("habyx-theme");
    const isDark = saved === "dark";
    if (isDark) {
        document.body.classList.add("dark-mode");
        const icon = document.getElementById("themeIcon");
        if (icon) icon.innerText = "☀️";
    }
}

function toggleTheme() {
    const isDark = document.body.classList.toggle("dark-mode");
    localStorage.setItem("habyx-theme", isDark ? "dark" : "light");
    const icon = document.getElementById("themeIcon");
    if (icon) icon.innerText = isDark ? "☀️" : "🌙";
}

// Initialize on load
document.addEventListener("DOMContentLoaded", initTheme);