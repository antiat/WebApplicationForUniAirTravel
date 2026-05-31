document.addEventListener('DOMContentLoaded', async () => {
    const ticketsContainer = document.getElementById('tickets-container');
    if (!ticketsContainer) return;

    const token = localStorage.getItem('token');
    if (!token) {
        ticketsContainer.innerHTML = '<p>Пожалуйста, <a href="login.html">войдите</a> для просмотра билетов.</p>';
        return;
    }

    try {
        ticketsContainer.innerHTML = '<p>Загрузка ваших билетов...</p>';
        
        const tickets = await ApiService.bookings.myTickets();

        if (!tickets || tickets.length === 0) {
            ticketsContainer.innerHTML = '<p>У вас пока нет забронированных билетов.</p>';
            return;
        }

        ticketsContainer.innerHTML = '';
        tickets.forEach(ticket => {
            const card = document.createElement('div');
            card.className = 'ticket-card';
            
            // Подстраиваемся под возможные поля ответа Django
            const flightNumber = ticket.flight_number || (ticket.flight && ticket.flight.flight_number) || 'N/A';
            const route = ticket.route || 'Авиарейс';
            const seat = ticket.seat_number || 'Не указано';

            card.innerHTML = `
                <div class="ticket-header">
                    <span class="ticket-id">Билет №${ticket.id}</span>
                </div>
                <div class="ticket-body">
                    <h3>${route}</h3>
                    <p><strong>Номер рейса:</strong> ${flightNumber}</p>
                    <p><strong>Место:</strong> ${seat}</p>
                    <p><strong>Статус:</strong> Активен</p>
                </div>
            `;
            ticketsContainer.appendChild(card);
        });

    } catch (error) {
        ticketsContainer.innerHTML = `<p style="color: red;">Ошибка загрузки билетов: ${error.message}</p>`;
    }
});
