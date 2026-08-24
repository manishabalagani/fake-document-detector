// =========================
// LOGIN FORM
// =========================

const loginForm = document.getElementById("loginForm");
const loginError = document.getElementById("loginError");

if (loginForm) {
    loginForm.addEventListener("submit", function (event) {
        event.preventDefault();

        const email = document.getElementById("email").value.trim();
        const password = document.getElementById("password").value.trim();

        loginError.textContent = "";

        if (!email || !password) {
            loginError.textContent =
                "Please enter your email and password.";
            return;
        }

        console.log("Login form submitted.");
        console.log("Email:", email);

        // Redirect to dashboard
        window.location.href = "dashboard.html";
    });
}