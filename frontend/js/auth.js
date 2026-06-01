document.addEventListener('DOMContentLoaded', () => {
    updateNavbar();
});

function updateNavbar() {
    const navAuth = document.getElementById('nav-auth');
    const navAuthReg = document.getElementById('nav-auth-reg');
    const navUser = document.getElementById('nav-user');
    const navAdmin = document.getElementById('nav-admin');
    const navUsername = document.getElementById('nav-username');

    if (Auth.isLoggedIn()) {
        navAuth?.classList.add('d-none');
        navAuthReg?.classList.add('d-none');

        navUser?.classList.remove('d-none');

        const user = Auth.getUser();

        if (navUsername) {
            navUsername.textContent =
                user?.username ||
                user?.email ||
                'User';
        }

        if (Auth.isAdmin()) {
            navAdmin?.classList.remove('d-none');
        }
    } else {
        navAuth?.classList.remove('d-none');
        navAuthReg?.classList.remove('d-none');

        navUser?.classList.add('d-none');
        navAdmin?.classList.add('d-none');
    }
}

function logout() {
    Auth.clearTokens();
    window.location.href = 'index.html';
}