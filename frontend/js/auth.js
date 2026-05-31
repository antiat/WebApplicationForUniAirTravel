document.addEventListener('DOMContentLoaded', () => {
    // 1. Логика формы входа (login.html)
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const usernameInput = document.getElementById('username').value;
            const passwordInput = document.getElementById('password').value;
            const errorMessage = document.getElementById('error-message');

            try {
                const data = await ApiService.login(usernameInput, passwordInput);
                
                // Сохраняем имя и статус админа, если бэкенд их возвращает
                // (Если Django возвращает роль внутри токена, Клод обычно пишет логику декодирования)
                localStorage.setItem('username', usernameInput);
                
                // Проверяем, является ли пользователь админом (упрощенная проверка для демонстрации)
                if (usernameInput.toLowerCase() === 'admin') {
                    localStorage.setItem('is_staff', 'true');
                }

                window.location.href = 'index.html'; 
            } catch (error) {
                if (errorMessage) errorMessage.textContent = error.message;
                alert(error.message);
            }
        });
    }

    // 2. Логика динамического обновления элементов Navbar
    function updateNavbar() {
    const token = localStorage.getItem('token');
    const username = localStorage.getItem('username') || 'User';
    const isStaff = localStorage.getItem('is_staff') === 'true';

    // Элементы навигации из вашего нового HTML
    const navAuth = document.getElementById('nav-auth');
    const navAuthReg = document.getElementById('nav-auth-reg');
    const navUser = document.getElementById('nav-user');
    const navAdmin = document.getElementById('nav-admin');
    const navUsername = document.getElementById('nav-username');

    if (token) {
        // Если пользователь залогинен
        if (navAuth) navAuth.classList.add('d-none');
        if (navAuthReg) navAuthReg.style.display = 'none';
        
        if (navUser) {
            navUser.classList.remove('d-none');
            // Если Клод использует Bootstrap класс d-none, удаляем его
            navUser.style.display = 'block'; 
        }
        if (navUsername) navUsername.textContent = username;

        // Если это администратор — показываем кнопку Панель
        if (isStaff && navAdmin) {
            navAdmin.classList.remove('d-none');
            navAdmin.style.display = 'block';
        }
        } else {
        // Если пользователь ГОСТЬ
        if (navAuth) {
            navAuth.classList.remove('d-none');
            navAuth.style.display = 'block';
        }
        if (navAuthReg) navAuthReg.style.display = 'block';
        if (navUser) navUser.classList.add('d-none');
        if (navAdmin) navAdmin.classList.add('d-none');
        }
    }

});

// Функция, которая управляет отображением меню (Вход/Выход/Личный кабинет)
function updateNavbar() {
    const token = localStorage.getItem('token');
    const username = localStorage.getItem('username') || 'User';
    const isStaff = localStorage.getItem('is_staff') === 'true';

    // Элементы навигации из вашего HTML
    const navAuth = document.getElementById('nav-auth');
    const navAuthReg = document.getElementById('nav-auth-reg');
    const navUser = document.getElementById('nav-user');
    const navAdmin = document.getElementById('nav-admin');
    const navUsername = document.getElementById('nav-username');

    if (token) {
        // Если пользователь залогинен:
        if (navAuth) navAuth.classList.add('d-none'); // Скрываем "Войти"
        if (navAuthReg) navAuthReg.style.display = 'none'; // Скрываем "Регистрация"
        
        if (navUser) {
            navUser.classList.remove('d-none'); // Показываем выпадающее меню юзера
            if (navUsername) navUsername.textContent = username; // Подставляем имя
        }

        // Если это администратор — показываем кнопку Панель
        if (isStaff && navAdmin) {
            navAdmin.classList.remove('d-none');
        }
    } else {
        // Если пользователь ГОСТЬ:
        if (navAuth) navAuth.classList.remove('d-none');
        if (navAuthReg) navAuthReg.style.display = 'block';
        if (navUser) navUser.classList.add('d-none');
        if (navAdmin) navAdmin.classList.add('d-none');
    }
}

// Глобальная функция выхода (привязана к вашему onclick="logout()")
window.logout = function() {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    localStorage.removeItem('is_staff');
    window.location.href = 'index.html';
};
