document.addEventListener('DOMContentLoaded', () => {
    const bookingForm = document.getElementById('booking-form');

    if (!bookingForm) return;

    bookingForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        if (!Auth.isLoggedIn()) {
            alert('Необходимо авторизоваться');
            window.location.href = 'login.html';
            return;
        }

        const flightId =
            new URLSearchParams(window.location.search)
                .get('flight_id');

        const seatNumber =
            document.getElementById('seat-number')?.value || '1A';

        try {
            await api.bookings.create({
                flight_id: Number(flightId),
                seat_number: seatNumber
            });

            alert('Бронирование успешно создано');

            window.location.href = 'my-tickets.html';

        } catch (err) {
            console.error(err);
            alert(err.message || 'Ошибка бронирования');
        }
    });
});