document.addEventListener("DOMContentLoaded", function () {

    const themeToggle = document.getElementById("themeToggle");
    const savedTheme = localStorage.getItem("theme");

    // Apply saved theme to every page
    if (savedTheme === "dark") {
        document.documentElement.setAttribute("data-theme", "dark");

        if (themeToggle) {
            themeToggle.textContent = "☀️";
        }
    }

    // Change theme when button is clicked
    if (themeToggle) {
        themeToggle.addEventListener("click", function () {

            const isDark =
                document.documentElement.getAttribute("data-theme") === "dark";

            if (isDark) {
                document.documentElement.removeAttribute("data-theme");
                localStorage.setItem("theme", "light");
                themeToggle.textContent = "🌙";

            } else {
                document.documentElement.setAttribute("data-theme", "dark");
                localStorage.setItem("theme", "dark");
                themeToggle.textContent = "☀️";
            }

        });
    }

});