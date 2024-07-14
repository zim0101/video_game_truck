(function() {
    document.addEventListener('DOMContentLoaded', function () {
        var availabilityButtons = document.querySelectorAll('.check-availability');

        availabilityButtons.forEach(function(button) {
            button.addEventListener('click', function(event) {
                event.preventDefault(); // Prevent default form submission

                var productId = button.getAttribute('data-product-id');
                var bookingDateSelector = button.getAttribute('data-booking-date-selector');
                var numberOfTrucksSelector = button.getAttribute('data-number-of-trucks-selector');

                var bookingDate = document.getElementById(bookingDateSelector).value;
                var numberOfTrucks = document.getElementById(numberOfTrucksSelector).value;

                console.log('Product ID:', productId);
                console.log('Booking Date:', bookingDate);
                console.log('Number of Trucks:', numberOfTrucks);

                // AJAX request
                odoo.define('video_game_truck.pricing_page', function (require) {
                    var ajax = require('web.ajax');

                    ajax.jsonRpc('/fetch_available_slots', 'call', {
                        'product_id': productId,
                        'booking_date': bookingDate,
                        'number_of_trucks': numberOfTrucks,
                    }).then(function (data) {
                        // Handle the response data
                        console.log('Availability Response:', data);
                    });
                });

            });
        });
  });
})();