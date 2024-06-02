// Ensure the script executes after the DOM is fully loaded
document.addEventListener('DOMContentLoaded', (event) => {
    // Get the expiry time from the data attribute
    const timerElement = document.getElementById('timer');
    const expiryTime = parseFloat(timerElement.getAttribute('data-expiry'));

    // Update the timer every second
    setInterval(updateTimer, 1000);

    function updateTimer() {
        // Calculate the remaining time until expiration
        const currentTime = Math.floor(Date.now() / 1000); // Convert to seconds
        const remainingTime = expiryTime - currentTime;

        // Check if the paste has expired
        if (remainingTime <= 0) {
            timerElement.textContent = 'Paste has expired';
        } else {
            // Convert remaining time to hours, minutes, and seconds
            const hours = Math.floor(remainingTime / 3600);
            const minutes = Math.floor((remainingTime % 3600) / 60);
            const seconds = remainingTime % 60;

            // Format the remaining time and display it
            const formattedTime = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            timerElement.textContent = `Time until expiration: ${formattedTime}`;
        }
    }

    // Initial call to update timer
    updateTimer();
});
