
document.addEventListener("DOMContentLoaded", function () {
    const regform = document.getElementById("registration-form");

    regform.addEventListener("submit", function (event) {
        event.preventDefault(); // Prevent the form from submitting by default

        // Validate form fields here
        const name = document.getElementById("name").value;
        const username = document.getElementById("username").value;
        const email = document.getElementById("email").value;
        const password = document.getElementById("password").value; 
        const confirmation = document.getElementById("confirmation").value;

        

        // Example validation: Checking if the name field is empty
        if (name.trim() === "") {
            alert("Full Name cannot be empty");
            return;
        }
        else if (username.trim() === "") {
            alert("Username cannot be empty");
            return;
        }   
        else if (email.trim() === "") {
            alert("Email cannot be empty");
            return; 
        }
        else if (password.trim() === "") {
            alert("Password cannot be empty");
            return; 
        }
        else if (confirmation.trim() === "") {
            alert("Confirmation cannot be empty");
            return; 
        }
        else if (password != confirmation) {
            alert("Passwords do not match");
            return; 
        }

        

        // If all validation passes, you can submit the form
        regform.submit();
    });
    const loginform = document.getElementById("login-form");
    loginform.addEventListener("submit", function (event) {
        event.preventDefault(); // Prevent the form from submitting by default

        // Validate form fields here
        const username = document.getElementById("username").value;
        const password = document.getElementById("password").value; 

        // Example validation: Checking if the name field is empty
        if (username.trim() === "") {
            alert("Username cannot be empty");
            return;
        }
        else if (password.trim() === "") {
            alert("Password cannot be empty");
            return; 
        }

        // If all validation passes, you can submit the form
        loginform.submit();
    });
});