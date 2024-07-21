document.addEventListener('DOMContentLoaded', function() {
    // MaterializeCSS initialization
    initializeMaterialize();

    // Delete modal functionality
    setupDeleteModal();

    // Password matching on Register page
    setupPasswordMatching();

    // Password visibility toggle on Login page
    setupPasswordVisibility();
});

function initializeMaterialize() {
    M.AutoInit();
    M.updateTextFields();

    $(".sidenav").sidenav({edge: "right"});
    $(".collapsible").collapsible();
    $(".tooltipped").tooltip();
    $("select").formSelect();
    $(".datepicker").datepicker({
        format: "dd mmmm, yyyy",
        yearRange: 3,
        showClearBtn: true,
        i18n: {
            done: "Select"
        }
    });
}

function setupDeleteModal() {
    var elems = document.querySelectorAll('.modal');
    var instances = M.Modal.init(elems);

    var deleteButtons = document.querySelectorAll('.delete-place, .delete-cuisine');
    var confirmDelete = document.getElementById('confirmDelete');
    var deleteUrl;

    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            deleteUrl = this.getAttribute('href');
            var instance = M.Modal.getInstance(document.getElementById('deleteModal'));
            instance.open();
        });
    });

    confirmDelete.addEventListener('click', function() {
        if (deleteUrl) {
            window.location.href = deleteUrl;
        }
    });
}

function setupPasswordMatching() {
    const password = document.getElementById('password');
    const confirmPassword = document.getElementById('confirm_password');
    const passwordMatch = document.getElementById('password-match');
    const submitBtn = document.getElementById('submitBtn');
    const form = document.getElementById('registerForm');

    if (!password || !confirmPassword) return; // Exit if not on register page

    function validatePasswords() {
        if (password.value !== confirmPassword.value) {
            passwordMatch.textContent = 'Passwords do not match';
            passwordMatch.style.color = 'red';
            submitBtn.disabled = true;
        } else {
            passwordMatch.textContent = 'Passwords match';
            passwordMatch.style.color = 'green';
            submitBtn.disabled = false;
        }
    }

    password.addEventListener('input', validatePasswords);
    confirmPassword.addEventListener('input', validatePasswords);

    form.addEventListener('submit', function(e) {
        if (password.value !== confirmPassword.value) {
            e.preventDefault();
            passwordMatch.textContent = 'Passwords do not match';
            passwordMatch.style.color = 'red';
        }
    });
}

function setupPasswordVisibility() {
    const togglePassword = document.querySelector('#togglePassword');
    const password = document.querySelector('#password');

    if (!togglePassword || !password) return; // Exit if not on login page

    togglePassword.addEventListener('click', function () {
        const type = password.getAttribute('type') === 'password' ? 'text' : 'password';
        password.setAttribute('type', type);
        this.textContent = type === 'password' ? 'visibility_off' : 'visibility';
    });
}