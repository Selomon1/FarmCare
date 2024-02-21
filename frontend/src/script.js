$(document).ready(function() {
    $('#loginForm').submit(function(event) {
        event.preventDefault();
        var username = $('#username').val();
        var password = $('#password').val();
        $.ajax({
            type: 'POST',
            url: '/login',
            contentType: 'application/json',
            data: JSON.stringify({ username: username, password: password }),
            success: function(response) {
                alert(response.message);
                // Redirect or do something else upon successful login
            },
            error: function(xhr, status, error) {
                var errorMessage = JSON.parse(xhr.responseText).message;
                alert(errorMessage);
            }
        });
    });

    $('#customerRegistrationForm').submit(function(event) {
        event.preventDefault();
        var username = $('#username').val();
        var password = $('#password').val();
        $.ajax({
            type: 'POST',
            url: '/register/customer',
            contentType: 'application/json',
            data: JSON.stringify({ username: username, password: password }),
            success: function(response) {
                alert(response.message);
                // Redirect or do something else upon successful registration
            },
            error: function(xhr, status, error) {
                var errorMessage = JSON.parse(xhr.responseText).message;
                alert(errorMessage);
            }
        });
    });

    $('#pharmacyRegistrationForm').submit(function(event) {
        event.preventDefault();
        var username = $('#username').val();
        var password = $('#password').val();
        $.ajax({
            type: 'POST',
            url: '/register/pharmacy',
            contentType: 'application/json',
            data: JSON.stringify({ username: username, password: password }),
            success: function(response) {
                alert(response.message);
                // Redirect or do something else upon successful registration
            },
            error: function(xhr, status, error) {
                var errorMessage = JSON.parse(xhr.responseText).message;
                alert(errorMessage);
            }
        });
    });

    $('#searchForm').submit(function(event) {
        event.preventDefault();
        var location = $('#location').val();
        var medication = $('#medication').val();
        $.ajax({
            type: 'GET',
            url: '/api/search',
            data: { location: location, medication: medication },
            success: function(response) {
                var pharmacies = response;
                var pharmaciesList = $('#pharmaciesList');
                pharmaciesList.empty();
                pharmacies.forEach(function(pharmacy) {
                    pharmaciesList.append('<p>Name: ' + pharmacy.name + ', Location: ' + pharmacy.location + '</p>');
                });
            },
            error: function(xhr, status, error) {
                var errorMessage = JSON.parse(xhr.responseText).message;
                alert(errorMessage);
            }
        });
    });
});
