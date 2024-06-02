// Populate the timer columns with options
const daysColumn = document.getElementById('days');
const hoursColumn = document.getElementById('hours');
const minutesColumn = document.getElementById('minutes');

for (let i = 0; i <= 30; i++) {
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
    const timestamp = new Date();
    const expirationTime = calculateExpirationTime(timestamp);
    const userAgent = navigator.userAgent;
    
    // Validate author input
    const authorPattern = /^[a-zA-Z0-9_@-]*$/;
    if (!authorPattern.test(authorInput)) {
        document.getElementById('responseMessage').textContent = 'Error: Author name can only contain letters, numbers, and _ @ -';
        return;
    }
    
    const formData = new URLSearchParams();
    formData.append('text', textInput);
    formData.append('expirationTime', expirationTime.getTime());
    formData.append('timestamp', timestamp.getTime());
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

function calculateExpirationTime(time_now) {
    const selectedDays = parseInt(document.getElementById('days').querySelector('.selected').textContent);
    const selectedHours = parseInt(document.getElementById('hours').querySelector('.selected').textContent);
    const selectedMinutes = parseInt(document.getElementById('minutes').querySelector('.selected').textContent);

    // Create a new Date object based on the current time
    const expirationDate = new Date(time_now);

    // Calculate expiration time by adding selected days, hours, and minutes
    expirationDate.setDate(expirationDate.getDate() + selectedDays);
    expirationDate.setHours(expirationDate.getHours() + selectedHours);
    expirationDate.setMinutes(expirationDate.getMinutes() + selectedMinutes);

    return expirationDate; // Return the expiration time as a Date object
}