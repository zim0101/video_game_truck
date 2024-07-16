(function () {
    document.addEventListener('DOMContentLoaded', function () {
        let availabilityButtons = document.querySelectorAll('.check-availability');

        availabilityButtons.forEach(function (button) {
            button.addEventListener('click', function (event) {
                event.preventDefault(); // Prevent default form submission

                let productId = button.getAttribute('data-product-id');
                let bookingDateSelector = button.getAttribute('data-booking-date-selector');
                let numberOfTrucksSelector = button.getAttribute('data-number-of-trucks-selector');

                let bookingDate = document.getElementById(bookingDateSelector).value;
                let numberOfTrucks = document.getElementById(numberOfTrucksSelector).value;

                console.log('Product ID:', productId);
                console.log('Booking Date:', bookingDate);
                console.log('Number of Trucks:', numberOfTrucks);

                let url = '/fetch_available_slots?' +
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
                        let availabilityMessage = document.querySelector('.availability-message');
                        availabilityMessage.innerHTML = ''; // Clear previous content

                        // Update UI with availability slots
                        if (data.length > 0) {
                            const slotDiv =document.querySelector('div.slot_card');
                            let slotInputName = 'slot_id'; // Assuming slot.id contains a unique identifier
                            let container = document.createElement('div');
                            container.classList.add('col-md-12')
                            container.classList.add('text-start')
                            container.classList.add('my-2')
                            container.classList.add('py-3')
                            container.setAttribute('role', 'radiogroup'); // Radio button group
                            container.classList.add('list-group-item')
                            data.forEach(function (slot) {
                                let checkbox = document.createElement('input');
                                checkbox.type = 'radio';
                                checkbox.name = `product_${productId}_slot`; // Unique name for each product
                                checkbox.value = slot.id;
                                checkbox.id = 'slot_' + slot.id;
                                checkbox.classList.add('mx-2')

                                let label = document.createElement('label');
                                label.setAttribute('for', 'slot_' + slot.id);
                                label.textContent = slot.name + ': ' + slot.start_time + ' - ' + slot.end_time;


                                let listItem = document.createElement('ul');
                                if(slot===data[data.length-1]){
                                    listItem.classList.add('mb-0')
                                }
                                listItem.appendChild(checkbox);
                                listItem.appendChild(label);
                                container.appendChild(listItem); // Add checkbox and label to container
                            });
                            if (slotDiv) {
                                slotDiv.innerHTML=''
                                slotDiv.appendChild(container);
                                let submitButton= slotDiv.closest('div.card-body').querySelector('.submit_button')
                                submitButton.style.display = 'inline-block'
                                button.style.display = 'None'
                            } else {
                                console.error('Form element not found.');
                            }
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
        //code for reversing
        let inputFields = document.querySelectorAll('.input');
        
        inputFields.forEach(function (input){
            input.addEventListener('change',function (){
                let slotCardHTML='<div class ="col-md-12 py-3 my-2 list-group-item">'
                slotCardHTML += '<p class="mt-1 mb-n1"><strong>'
                slotCardHTML += 'Please select the Booking Date, </br>'
                slotCardHTML += 'Number of Trucks & Click the </br>'
                slotCardHTML += 'Check Availability Button see </br>'
                slotCardHTML += 'the available slots'
                slotCardHTML += '</strong></p>'
                slotCardHTML += '</div>'

                let slotCard = input.closest('.card-body').querySelector('.slot_card');
                let submitButton = input.closest('.card-body').querySelector('.submit_button');
                let checkButton = input.closest('.card-body').querySelector('.check-availability');
                if(checkButton && submitButton && slotCard){
                    slotCard.innerHTML=slotCardHTML
                    submitButton.style.display = 'None'
                    checkButton.style.display = 'inline-block'
                }
            })
        });
    });
})();
