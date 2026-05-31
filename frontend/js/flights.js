document.addEventListener('DOMContentLoaded', () => {
    // Принудительный запуск обновления навигационной панели
    if (typeof updateNavbar === 'function') {
        updateNavbar();
    } else {
        const token = localStorage.getItem('access_token') || localStorage.getItem('token') || (typeof Auth !== 'undefined' && Auth.getToken());
        const navAuth = document.getElementById('nav-auth');
        const navAuthReg = document.getElementById('nav-auth-reg');
        const navUser = document.getElementById('nav-user');
        const navAdmin = document.getElementById('nav-admin');
        const navUsername = document.getElementById('nav-username');

        if (token) {
            if (navAuth) navAuth.classList.add('d-none');
            if (navAuthReg) navAuthReg.style.display = 'none';
            if (navUser) navUser.classList.remove('d-none');
            if (navUsername) navUsername.textContent = localStorage.getItem('username') || 'Администратор';
            if (navAdmin) navAdmin.classList.remove('d-none');
        }
    }

    const searchForm = document.getElementById('search-form');
    const flightsContainer = document.getElementById('flights-container');

    if (flightsContainer) {
        loadFlights();
    }

    if (searchForm) {
        searchForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const from = document.getElementById('from-location').value.trim();
            const to = document.getElementById('to-location').value.trim();
            const date = document.getElementById('departure-date').value;

            const params = {};
            if (from) params.departure_city = from;
            if (to) params.arrival_city = to;
            if (date) params.date = date;

            await loadFlights(params);
        });
    }

    async function loadFlights(filters = {}) {
        try {
            flightsContainer.innerHTML = '<p class="text-muted">Загрузка рейсов...</p>';
            const response = await api.flights.list(filters);

            const flightsArray = Array.isArray(response) ? response : (response.results || []);

            if (flightsArray.length === 0) {
                flightsContainer.innerHTML = '<div class="alert alert-info border-0 shadow-sm">Рейсов по заданному направлению не найдено.</div>';
                return;
            }

            flightsContainer.innerHTML = '';
            
            flightsArray.forEach(flight => {
                const flightCard = document.createElement('div');
                flightCard.className = 'card flight-card mb-3 p-4 border-0 shadow-sm bg-white';
                
                // Безопасный поиск полей городов из вашей реальной базы данных Django
                const fromCity = flight.departure_city || 
                                 (flight.departure_airport && (flight.departure_airport.city || flight.departure_airport.name)) || 
                                 flight.from_city || 'Уточняется';

                const toCity = flight.arrival_city || 
                               (flight.arrival_airport && (flight.arrival_airport.city || flight.arrival_airport.name)) || 
                               flight.to_city || 'Уточняется';
                
                // Извлекаем чистую стоимость
                let rawPrice = flight.base_price || flight.price_usd || flight.price || '0';
                let displayPrice = parseFloat(rawPrice);
                let formattedPrice = displayPrice.toLocaleString('ru-RU') + ' $';

                const flightNum = flight.flight_number || 'N/A';
                const seatsVal = flight.available_seats !== undefined ? flight.available_seats : '180';

                const flightDate = flight.departure_time ? new Date(flight.departure_time).toLocaleString('ru-RU', {
                    day: 'numeric', month: 'long', hour: '2-digit', minute: '2-digit'
                }) : 'Уточняется';

                flightCard.innerHTML = `
                    <div class="row align-items-center g-3">
                        <div class="col-md-8">
                            <div class="flight-route text-dark fs-4 mb-2">
                                ${fromCity} <i class="bi bi-arrow-right text-muted mx-2 fs-5"></i> ${toCity}
                            </div>
                            <div class="flight-meta small text-muted d-flex gap-3 flex-wrap">
                                <span><i class="bi bi-hash me-1"></i><strong>Рейс:</strong> ${flightNum}</span>
                                <span><i class="bi bi-person-workspace me-1"></i><strong>Свободно мест:</strong> ${seatsVal}</span>
                            </div>
                            <div class="flight-meta small text-muted mt-2">
                                <i class="bi bi-clock me-1"></i><strong>Вылет:</strong> ${flightDate}
                            </div>
                        </div>
                        <div class="col-md-4 text-md-end text-start border-start-md">
                            <div class="flight-price text-primary fs-3 fw-bold mb-2">${formattedPrice}</div>
                            <!-- Принудительно задаем тип button, чтобы клик не вызывал перезагрузку формы -->
                            <button type="button" class="btn btn-primary fw-bold px-4 rounded-3 book-btn shadow-sm w-100 w-md-auto" data-id="${flight.id}">
                                <i class="bi bi-ticket-perforated me-1"></i> Купить билет
                            </button>
                        </div>
                    </div>
                `;
                flightsContainer.appendChild(flightCard);
            });

            // КОРРЕКТНЫЙ ОБРАБОТЧИК КЛИКА С ПЕРЕДАЧЕЙ ID В АДРЕСНУЮ СТРОКУ КЛОДА
            document.querySelectorAll('.book-btn').forEach(button => {
                button.addEventListener('click', (e) => {
                    e.preventDefault(); // Полностью блокируем перезагрузку страницы браузером
                    
                    const buttonElement = e.target.closest('.book-btn');
                    if (buttonElement) {
                        const flightId = buttonElement.getAttribute('data-id');
                        
                        // Сохраняем и в память, и передаем в URL-параметры, как требует Клод!
                        localStorage.setItem('selectedFlightId', flightId);
                        
                        // Перенаправляем на страницу бронирования с точным параметром id
                        window.location.href = `booking.html?flight_id=${flightId}`; 
                    }
                });
            });

        } catch (error) {
            flightsContainer.innerHTML = `<div class="alert alert-danger border-0 shadow-sm">Ошибка: ${error.message}</div>`;
        }
    }
});
