document.addEventListener('DOMContentLoaded', () => {
    const bookingForm = document.getElementById('booking-form');
    
    const flightId = localStorage.getItem('selectedFlightId');

    if (!flightId) {
        alert('Рейс не выбран. Возврат на главную страницу.');
        window.location.href = 'index.html';
        return;
    }

    if (bookingForm) {
        bookingForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const token = localStorage.getItem('token');
            if (!token) {
                alert('Пожалуйста, авторизуйтесь для бронирования!');
                window.location.href = 'login.html';
                return;
            }

            // Получаем номер места из формы (убедитесь, что в HTML есть id="seat-number")
            const seatInput = document.getElementById('seat-number');
            const seatNumber = seatInput ? seatInput.value : "1A"; // Если поля нет, ставим заглушку 1A

            try {
                // ВЫЗОВ СТРОГО ПО СТРУКТУРЕ CLAUDE: ApiService.bookings.create(...)
                await ApiService.bookings.create(parseInt(flightId), seatNumber);
                alert('Успешно забронировано!');
                
                localStorage.removeItem('selectedFlightId');
                window.location.href = 'my-tickets.html'; 
            } catch (error) {
                alert(`Ошибка: ${error.message}`);
            }
        });
    }
});
