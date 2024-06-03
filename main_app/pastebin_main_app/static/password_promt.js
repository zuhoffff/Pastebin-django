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
            // Prompt again
            document.getElementById('message').innerHTML = '<p class="error">Invalid password</p>';
        } else {
            // Reload page or perform other actions as needed
            window.location.reload();
        }
    })
    .catch(error => {
        document.getElementById('message').innerHTML = '<p class="error">Error: ' + error.message + '</p>';
    });
});
