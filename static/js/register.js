document.addEventListener('DOMContentLoaded', function() {
    feather.replace();
    
    const form = document.getElementById('registerForm');
    const usernameInput = document.getElementById('username');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const termsCheckbox = document.getElementById('terms');
    
    const usernameError = document.getElementById('usernameError');
    const emailError = document.getElementById('emailError');
    
    const usernamePattern = /^[A-Za-z0-9_]+$/;
    const emailPattern = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$/;

    const checkUsernameUrl = document.body.dataset.checkUsername;
    const checkEmailUrl = document.body.dataset.checkEmail;
    
    function validateUsername() {
        const isValid = usernamePattern.test(usernameInput.value);
        if (usernameInput.value) {
            if (usernameInput.value && !isValid) {
                usernameInput.classList.add('focus:ring-red-500');
                usernameInput.classList.add('border-red-500');
                usernameInput.classList.remove('focus:ring-gray-300');
                usernameInput.classList.remove('focus:ring-green-500');
                usernameError.classList.remove('hidden');
                return false;
            } else {
                usernameInput.classList.remove('focus:ring-red-500');
                usernameInput.classList.remove('focus:ring-gray-300');
                usernameInput.classList.remove('border-red-500');
                usernameInput.classList.add('focus:ring-green-500');
                usernameError.classList.add('hidden');
                return true;
            }
        } else {
            // EMPTY FIELD
            usernameInput.classList.remove('focus:ring-red-500');
            usernameInput.classList.remove('focus:ring-green-500');
            usernameInput.classList.remove('border-red-500');
            usernameInput.classList.add('focus:ring-gray-300');
        }
    }
    
    function validateEmail() {
        const isValid = emailPattern.test(emailInput.value);
        if (emailInput.value && !isValid) {
            emailInput.classList.add('focus:ring-red-500');
            emailInput.classList.add('border-red-500');
            emailInput.classList.remove('focus:ring-gray-300');
            emailInput.classList.remove('focus:ring-green-500');
            emailError.classList.remove('hidden');
            return false;
        } else {
            emailInput.classList.remove('focus:ring-red-500');
            emailInput.classList.remove('focus:ring-gray-300');
            emailInput.classList.remove('border-red-500');
            emailInput.classList.add('focus:ring-green-500');
            emailError.classList.add('hidden');
            return true;
        }
    }
    
    function validatePassword() {
        const password = passwordInput.value;
        const cleanPassword = password.replace(/\s/g, '');

        const hasMinLength = cleanPassword.length >= 8;
        const hasUppercase = /[A-Z]/.test(cleanPassword);
        const hasNumber = /[0-9]/.test(cleanPassword);
        const hasSpecial = /[^a-zA-Z0-9]/.test(cleanPassword);
        
        // FIELD NOT EMPTY
        if (password) {
            if (hasMinLength && hasUppercase && hasNumber && hasSpecial) {
                passwordInput.classList.remove('focus:ring-red-500');
                passwordInput.classList.remove('focus:ring-gray-300');
                passwordInput.classList.remove('border-red-500');
                passwordInput.classList.add('focus:ring-green-500');
            } else {
                passwordInput.classList.add('focus:ring-red-500');
                passwordInput.classList.add('border-red-500');
                passwordInput.classList.remove('focus:ring-green-500');
                passwordInput.classList.remove('focus:ring-gray-300');
            }
        } else {
            // EMPTY FIELD
            passwordInput.classList.remove('focus:ring-red-500');
            passwordInput.classList.remove('focus:ring-green-500');
            passwordInput.classList.remove('border-red-500');
            passwordInput.classList.add('focus:ring-gray-300');
        }
        
        return hasMinLength && hasUppercase && hasNumber && hasSpecial;
    }
    
    // real-time validation, event listenre
    usernameInput.addEventListener('input', validateUsername);
    emailInput.addEventListener('input', validateEmail);
    passwordInput.addEventListener('input', validatePassword);
    
    form.addEventListener('submit', function(event) {
        const isUsernameValid = validateUsername();
        const isEmailValid = validateEmail();
        const isPasswordValid = validatePassword();
        const isTermsChecked = termsCheckbox.checked;
        
        if (!isUsernameValid || !isEmailValid || !isPasswordValid || !isTermsChecked) {
            event.preventDefault();
        }
    });

    // Check if username is already taken
    let usernameTimer;
    usernameInput.addEventListener('blur', function() {
        if (usernameInput.value && validateUsername()) {
            
            clearTimeout(usernameTimer);
            usernameTimer = setTimeout(function() {
                fetch(checkUsernameUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: JSON.stringify({ username: usernameInput.value })
                })
                .then(response => response.json())
                .then(data => {
                    if (!data.available) {
                        usernameInput.classList.add('focus:ring-red-500');
                        usernameInput.classList.add('border-red-500');
                        usernameInput.classList.remove('focus:ring-gray-300');
                        usernameInput.classList.remove('focus:ring-green-500');
                        usernameError.textContent = 'Username already taken.';
                        usernameError.classList.remove('hidden');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                });
            }, 500);
        }
    });
    
    // Check if email is already taken
    let emailTimer;
    emailInput.addEventListener('blur', function() {
        if (emailInput.value && validateEmail()) {
            
            clearTimeout(emailTimer);
            emailTimer = setTimeout(function() {
                fetch(checkEmailUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: JSON.stringify({ email: emailInput.value })
                })
                .then(response => response.json())
                .then(data => {
                    if (!data.available) {
                        emailInput.classList.add('focus:ring-red-500');
                        emailInput.classList.add('border-red-500');
                        emailInput.classList.remove('focus:ring-gray-300');
                        emailInput.classList.remove('focus:ring-green-500');
                        emailError.textContent = 'Email is already being used.';
                        emailError.classList.remove('hidden');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                });
            }, 500);
        }
    });
    
});