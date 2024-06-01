// Populate the timer columns with options
const daysColumn = document.getElementById('days');
const hoursColumn = document.getElementById('hours');
const minutesColumn = document.getElementById('minutes');

for (let i = 1; i <= 30; i++) {
    daysColumn.innerHTML += `<div>${i} days</div>`;
}

for (let i = 0; i < 24; i++) {
    hoursColumn.innerHTML += `<div>${i} hours</div>`;
}

for (let i = 0; i < 60; i++) {
    minutesColumn.innerHTML += `<div>${i} minutes</div>`;
}

// Event listener for form submission
document.getElementById('textForm').addEventListener('submit', function(event) {
    event.preventDefault();

    const textInput = document.getElementById('textInput').value;
    const authorInput = document.getElementById('authorInput').value;
    const timestamp = new Date().toISOString();
    const userAgent = navigator.userAgent;

    // Calculate expiration time
    const days = parseInt(daysColumn.querySelector('.selected').innerText);
    const hours = parseInt(hoursColumn.querySelector('.selected').innerText);
    const minutes = parseInt(minutesColumn.querySelector('.selected').innerText);

    const expirationTime = new Date();
    expirationTime.setDate(expirationTime.getDate() + days);
    expirationTime.setHours(expirationTime.getHours() + hours);
    expirationTime.setMinutes(expirationTime.getMinutes() + minutes);
    
    // Validate author input
    const authorPattern = /^[a-zA-Z0-9_@-]*$/;
    if (!authorPattern.test(authorInput)) {
        document.getElementById('responseMessage').textContent = 'Error: Author name can only contain letters, numbers, and _ @ -';
        return;
    }
    
    const formData = new URLSearchParams();
    formData.append('text', textInput);
    formData.append('expirationTime', expirationTime.toISOString());
    formData.append('timestamp', timestamp);
    formData.append('userAgent', userAgent);
    formData.append('author', authorInput);


    // Send POST request with form data
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

// Add click event listener to timer columns
document.querySelectorAll('.column').forEach(column => {
    column.addEventListener('click', function(event) {
        const selected = column.querySelector('.selected');
        if (selected) selected.classList.remove('selected');
        event.target.classList.add('selected');
    });
});