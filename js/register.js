const registerForm = document.getElementById("registerForm");
const registerError = document.getElementById("registerError");

registerForm.addEventListener("submit", function (event) {

    event.preventDefault();

    const name = document.getElementById("name").value.trim();
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;
    const confirmPassword =
        document.getElementById("confirmPassword").value;

    registerError.textContent = "";


    // Check empty fields
    if (!name || !email || !password || !confirmPassword) {

        registerError.textContent =
            "Please fill in all fields.";

        return;
    }


    // Check password length
    if (password.length < 6) {

        registerError.textContent =
            "Password must be at least 6 characters.";

        return;
    }


    // Check password match
    if (password !== confirmPassword) {

        registerError.textContent =
            "Passwords do not match.";

        return;
    }


    // Temporary testing
    console.log("Registration form submitted.");
    console.log("Name:", name);
    console.log("Email:", email);

});