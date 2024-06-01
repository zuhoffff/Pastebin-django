document.getElementById('textForm').addEventListener('submit', function(event) {
    event.preventDefault();

    const textInput = document.getElementById('textInput').value;
    const authorInput = document.getElementById('authorInput').value;
    const timestamp = new Date().toISOString();
    const userAgent = navigator.userAgent;

    const formData = new URLSearchParams();
    formData.append('text', textInput);
    formData.append('timestamp', timestamp);
    formData.append('userAgent', userAgent);
    formData.append('author', authorInput);

    // Validate author input
    const authorPattern = /^[a-zA-Z0-9_@-]*$/;
    if (!authorPattern.test(authorInput)) {
        document.getElementById('responseMessage').textContent = 'Error: Author name can only contain letters, numbers, and _ @ -';
        return;
    }

    fetch('/submit-text/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData.toString()
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('responseMessage').textContent = 'Success: ' + data.message;
        const url = window.location.origin + data.url;
        document.getElementById('responseUrl').innerHTML = `<a href="${url}" target="_blank">${url}</a>`;
    })
    .catch(error => {
        document.getElementById('responseMessage').textContent = 'Error: ' + error;
    });
});