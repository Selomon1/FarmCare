// Example JavaScript code for your Flask application

// Client-side validation for pharmacy registration form
document.addEventListener('DOMContentLoaded', function() {
    const pharmacyForm = document.querySelector('.registration-form');

    if (pharmacyForm) {
        pharmacyForm.addEventListener('submit', function(event) {
            const nameInput = document.getElementById('name');
            const locationInput = document.getElementById('location');
            const ownerNameInput = document.getElementById('owner_name');
            const emailInput = document.getElementById('email');
            const passwordInput = document.getElementById('password');
            const medicationsInput = document.getElementById('medications');

            const nameValue = nameInput.value.trim();
            const locationValue = locationInput.value.trim();
            const ownerNameValue = ownerNameInput.value.trim();
            const emailValue = emailInput.value.trim();
            const passwordValue = passwordInput.value.trim();
            const medicationsValue = medicationsInput.value.trim();

            if (nameValue === '' || locationValue === '' || ownerNameValue === '' || emailValue === '' || passwordValue === '' || medicationsValue === '') {
                event.preventDefault(); // Prevent form submission
                alert('Please fill in all fields.');
            }
        });
    }
});

// Example of using AJAX to send search request
document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.getElementById('search-form');

    if (searchForm) {
        searchForm.addEventListener('submit', function(event) {
            event.preventDefault(); // Prevent form submission

            const location = document.getElementById('location').value;
            const medication = document.getElementById('medication').value;

            // Make AJAX request to search for pharmacies
            fetch(`/api/search?location=${location}&medication=${medication}`)
                .then(response => response.json())
                .then(data => {
                    // Process the response data
                    console.log(data);
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        });
    }
});
