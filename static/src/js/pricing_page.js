(function () {
    document.addEventListener('DOMContentLoaded', function () {
        var availabilityButtons = document.querySelectorAll('.check-availability');

        availabilityButtons.forEach(function (button) {
            button.addEventListener('click', function (event) {
                event.preventDefault(); // Prevent default form submission

                var productId = button.getAttribute('data-product-id');
                var bookingDateSelector = button.getAttribute('data-booking-date-selector');
                var numberOfTrucksSelector = button.getAttribute('data-number-of-trucks-selector');

                var bookingDate = document.getElementById(bookingDateSelector).value;
                var numberOfTrucks = document.getElementById(numberOfTrucksSelector).value;

                console.log('Product ID:', productId);
                console.log('Booking Date:', bookingDate);
                console.log('Number of Trucks:', numberOfTrucks);

                var url = '/fetch_available_slots?' +
                    'product_id=' + encodeURIComponent(productId) +
                    '&booking_date=' + encodeURIComponent(bookingDate) +
                    '&number_of_trucks=' + encodeURIComponent(numberOfTrucks);

                // Fetch API request
                fetch(url)
                    .then(response => response.json())
                    .then(data => {
                        // Handle the response data
                        console.log('Availability Response:', data);

                        // Clear previous availability messages and checkboxes
                        var availabilityMessage = document.querySelector('.availability-message');
                        availabilityMessage.innerHTML = ''; // Clear previous content

                        // Update UI with availability slots
                        if (data.length > 0) {
                            const formSelector = `form[data-product-id="${productId}"]`;
                            const form = document.querySelector(formSelector);
                            console.log(form);
                            var slotInputName = 'slot_id';

                            data.forEach(function (slot) {
                                var checkbox = document.createElement('input');
                                checkbox.type = 'checkbox';
                                checkbox.name = slotInputName;
                                checkbox.value = slot.id; // Assuming slot.id is available
                                checkbox.id = 'slot_' + slot.id; // Optional: Set an ID for the checkbox

                                var label = document.createElement('label');
                                label.setAttribute('for', 'slot_' + slot.id);
                                label.textContent = slot.name + ': ' + slot.start_time + ' - ' + slot.end_time;

                                var listItem = document.createElement('li');
                                listItem.appendChild(checkbox);
                                listItem.appendChild(label);

                                console.log(listItem);

                                // Append checkbox with slot id to form, if form exists
                                if (form) {
                                    form.appendChild(listItem);
                                } else {
                                    console.error('Form element not found.');
                                }
                            });
                        } else {
                            availabilityMessage.textContent = 'No available slots found.';
                        }

                        // Show availability message
                        availabilityMessage.style.display = 'block';
                    })
                    .catch(error => {
                        console.error('Error fetching availability:', error);
                        // Handle error display if needed
                    });
            });
        });
    });
})();
