document.addEventListener('DOMContentLoaded', (event) => {
    console.log('JavaScript loaded and running');

    document.getElementById('passwordForm').addEventListener('submit', function(event) {
        event.preventDefault();

        const form = event.target;
        const formData = new FormData(form);

        fetch(form.action, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.prompt_again) {
                document.getElementById('message').innerHTML = '<p class="error">Invalid password</p>';
            } else if (data.redirect_url) {
                // Redirect to the specified URL
                window.location.href = data.redirect_url;
            }
        })
        .catch(error => {
            document.getElementById('message').innerHTML = '<p class="error">Error: ' + error.message + '</p>';
        });
    });
});