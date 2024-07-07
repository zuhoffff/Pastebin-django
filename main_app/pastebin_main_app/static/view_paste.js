function initializeTimer(et,homeurl) {
    // Parse the expiry time passed from the backend in UTC
    var expiryTime = new Date(et).getTime(); // Convert to milliseconds since epoch
    var display = document.querySelector('#timer');
    updateTimer(expiryTime, display, homeurl); // Initial call to set the time
    var intervalId = setInterval(function() {
        updateTimer(expiryTime, display, intervalId, homeurl);
    }, 1000);
};

function updateTimer(expiryTime, display, intervalId,homeurl) {
    // Get the current time in UTC
    var now = new Date().getTime(); // Get current time in milliseconds since epoch (UTC)
    var remaining = expiryTime - now; // Calculate the remaining time in milliseconds

    if (remaining <= 0) {
        clearInterval(intervalId); // Stop the timer
        display.innerHTML = "00:00:00:00"; // Show expired
        showExpiredPage(homeurl); // Call function to display expired page
    } else {
        var days = Math.floor(remaining / (1000 * 60 * 60 * 24)).toString().padStart(2, '0');
        var hours = Math.floor((remaining % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60)).toString().padStart(2, '0');
        var minutes = Math.floor((remaining % (1000 * 60 * 60)) / (1000 * 60)).toString().padStart(2, '0');
        var seconds = Math.floor((remaining % (1000 * 60)) / 1000).toString().padStart(2, '0');
        display.innerHTML = `${days}:${hours}:${minutes}:${seconds}`;
    }
}

function showExpiredPage(homeurl) {
    document.body.innerHTML = `
        <div class="container">
            <h1>This Page Has Expired</h1>
            <p>Sorry, the content you are trying to access has expired.</p>
            <p>Please visit our <a href="${homeurl}">homepage</a>!</p>
        </div>
    `;
}