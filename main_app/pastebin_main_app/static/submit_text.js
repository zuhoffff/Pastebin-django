document.addEventListener("DOMContentLoaded", function() {
    // Calculate the date 2 days from now
    const twoDaysFromNow = new Date();
    twoDaysFromNow.setDate(twoDaysFromNow.getDate() + 2);

    flatpickr(".flatpickr", {
        enableTime: true,
        // dateFormat: "", # use default
        time_24hr: true,
        minuteIncrement: 1,
        defaultDate: twoDaysFromNow,
        minDate: "today",
        altInput: true,
        altFormat: "F j, Y H:i",
        allowInput: true
    });

    // Handle form submission
    document.getElementById("pasteSubmissionForm").addEventListener("submit", function(event) {
        event.preventDefault(); // Prevent default form submission

        const form = event.target;
        const formData = new FormData(form);
        let timezoneField = form.elements['timezone'];
        timezoneField.value = Intl.DateTimeFormat().resolvedOptions().timeZone;

        // Submit form data using Fetch API
        fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': formData.get('csrfmiddlewaretoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            // Process the response data
            document.getElementById('responseMessage').textContent = 'Success: ' + data.message;
            const url = window.location.origin + data.url;
            document.getElementById('responseUrl').innerHTML = `<a href="${url}" target="_blank">${url}</a>`;

            // Show the response with animation
            const responseElement = document.getElementById('response');
            responseElement.classList.add('show');

            // Scroll into view if needed (especially useful for small screens)
            responseElement.scrollIntoView({ behavior: 'smooth' });
        })
        .catch(error => {
            document.getElementById('responseMessage').textContent = 'Error: ' + error;

            // Show the response with animation
            const responseElement = document.getElementById('response');
            responseElement.classList.add('show');

            // Scroll into view if needed
            responseElement.scrollIntoView({ behavior: 'smooth' });
        });
    });
});
