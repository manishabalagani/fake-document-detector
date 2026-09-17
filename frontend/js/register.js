const registerForm = document.getElementById("registerForm");
const registerError = document.getElementById("registerError");

if (registerForm) {

    registerForm.addEventListener("submit", async function (event) {

        event.preventDefault();

        registerError.textContent = "";

        const name = document.getElementById("name").value.trim();
        const email = document.getElementById("email").value.trim();
        const password = document.getElementById("password").value;
        const confirmPassword =
            document.getElementById("confirmPassword").value;


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


        const registerButton =
            registerForm.querySelector("button[type='submit']");


        try {

            registerButton.disabled = true;
            registerButton.textContent = "Creating Account...";


            // Send registration request to backend
            const response =
                await registerUser(name, email, password);


            console.log("Registration response:", response);


            // Registration successful
            alert("Account created successfully! Please login.");

            window.location.href = "login.html";


        } catch (error) {

            console.error("Registration error:", error);

            registerError.textContent =
                error.message ||
                "Registration failed. Please try again.";

            registerButton.disabled = false;
            registerButton.textContent = "Create Account";
        }

    });

}
