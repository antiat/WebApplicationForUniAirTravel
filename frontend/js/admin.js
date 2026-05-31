document.addEventListener('DOMContentLoaded', () => {
    const adminBookingsContainer = document.getElementById('admin-bookings-list');
    const statFlights = document.getElementById('stat-flights-count');
    const statUsers = document.getElementById('stat-users-count');
    const statBookings = document.getElementById('stat-bookings-count');

    initDashboard();

    async function initDashboard() {
        try {
            // Асинхронное получение данных со всех системных эндпоинтов параллельно
            const [flightsRes, usersRes, bookingsRes] = await Promise.all([
                api.flights.list(),
                api.adminUsers.list(),
                api.bookings.myBookings()
            ]);

            // Разбор структуры ответа с поддержкой Django REST Framework пагинации
            const flightsArray = Array.isArray(flightsRes) ? flightsRes : (flightsRes.results || []);
            const usersArray = Array.isArray(usersRes) ? usersRes : (usersRes.results || []);
            const bookingsArray = Array.isArray(bookingsRes) ? bookingsRes : (bookingsRes.results || []);

            // Запись вычисленных счетчиков в UI карточки метрик
            if (statFlights) statFlights.textContent = flightsArray.length;
            if (statUsers) statUsers.textContent = usersArray.length;
            if (statBookings) statBookings.textContent = bookingsArray.length;

            // Генерация строк таблицы истории
            if (adminBookingsContainer) {
                renderBookingsTable(bookingsArray);
            }

        } catch (error) {
            console.error('Ошибка инициализации панели администратора:', error);
            if (adminBookingsContainer) {
                adminBookingsContainer.innerHTML = `<tr><td colspan="4" class="text-danger">Ошибка загрузки данных API: ${error.message}</td></tr>`;
            }
        }
    }

    function renderBookingsTable(bookings) {
        if (bookings.length === 0) {
            adminBookingsContainer.innerHTML = '<tr><td colspan="4" class="text-center text-muted py-3">История бронирований в системе пуста.</td></tr>';
            return;
        }

        adminBookingsContainer.innerHTML = '';
        
        bookings.forEach(booking => {
            const route = booking.route || (booking.flight && booking.flight.route) || 'Маршрут не указан';
            const flightNum = booking.flight_number || (booking.flight && booking.flight.flight_number) || 'N/A';
            const username = booking.user_username || booking.user || 'Системный клиент';
            const displayStatus = booking.status === 'confirmed' ? 'Оплачен' : 'Забронирован';

            const row = document.createElement('tr');
            row.innerHTML = `
                <td><strong class="text-primary">№ ${booking.id}</strong></td>
                <td><i class="bi bi-person me-2 text-secondary"></i>${username}</td>
                <td><strong>${flightNum}</strong> <span class="text-muted small">(${route})</span></td>
                <td>
                    <span class="badge ${booking.status === 'confirmed' ? 'bg-success' : 'bg-warning'} bg-opacity-10 ${booking.status === 'confirmed' ? 'text-success' : 'text-warning'} px-2 py-1 rounded">
                        ${displayStatus}
                    </span>
                </td>
            `;
            adminBookingsContainer.appendChild(row);
        });
    }
});
