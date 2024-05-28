document.getElementById('textForm').addEventListener('submit', function(event) {
    event.preventDefault();

    const textInput = document.getElementById('textInput').value;
    const timestamp = new Date().toISOString();
    const userAgent = navigator.userAgent;

    fetch('/submit-text', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            text: textInput,
            timestamp: timestamp,
            userAgent: userAgent,
        })
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