document.addEventListener('DOMContentLoaded', (event) => {
    console.log('JavaScript loaded and running'); // Debug line

    document.getElementById('passwordForm').addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent default form submission

        const form = event.target;
        const formData = new FormData(form);

        fetch(form.action, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.prompt_again) {
                // Display an error message if the password is incorrect
                document.getElementById('message').innerHTML = '<p class="error">Invalid password</p>';
            } else {
                // If password is correct, reload the page or redirect as needed
                window.location.reload();
            }
        })
        .catch(error => {
            // Display an error message if there was an issue with the request
            document.getElementById('message').innerHTML = '<p class="error">Error: ' + error.message + '</p>';
        });
    });
});
