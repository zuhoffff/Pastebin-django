 // Populate the timer columns with options
 const daysColumn = document.getElementById('days');
 const hoursColumn = document.getElementById('hours');
 const minutesColumn = document.getElementById('minutes');

 for (let i = 0; i <= 30; i++) {
     daysColumn.innerHTML += `<option value="${i}">${i} days</option>`;
 }

 for (let i = 0; i < 24; i++) {
     hoursColumn.innerHTML += `<option value="${i}">${i} hours</option>`;
 }

 for (let i = 0; i < 60; i++) {
     minutesColumn.innerHTML += `<option value="${i}">${i} minutes</option>`;
 }

 // Event listener for form submission
 document.getElementById('textForm').addEventListener('submit', function(event) {
     event.preventDefault();

     const textInput = document.getElementById('textInput').value;
     const userAgent = navigator.userAgent;

     const passwordInput = document.getElementById('passwordInput').value.trim();
     const authorInput = document.getElementById('authorInput').value.trim();
     
     // Validate author input
     const authorPattern = /^[a-zA-Z0-9_@-]*$/;
     if (!authorPattern.test(authorInput)) {
         document.getElementById('responseMessage').textContent = 'Error: Author name can only contain letters, numbers, and _ @ -';
         return;
     }

     const days = document.getElementById('days').value;
     const hours = document.getElementById('hours').value;
     const minutes = document.getElementById('minutes').value;
     const expiry = `${days}.${hours}.${minutes}`;

     const formData = new URLSearchParams();
     formData.append('text', textInput);
     formData.append('expiry', expiry);
     formData.append('userAgent', userAgent);
     if (authorInput) { formData.append('author', authorInput); }
     if (passwordInput) { formData.append('password', passwordInput); }
     
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