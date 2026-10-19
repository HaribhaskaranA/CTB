/**
 * static/js/otp.js
 * OTP input flow for CONNECT TO BUILD - Demo Mode
 */
document.addEventListener('DOMContentLoaded', function () {
    const otpBoxes = document.querySelectorAll('.otp-input-box');
    const hiddenInput = document.getElementById('otp-value');
    const otpForm = document.getElementById('otp-form');
    let timerInterval = null;

    // Initialize OTP boxes
    if (otpBoxes.length > 0) {
        otpBoxes[0].focus();

        otpBoxes.forEach((box, index) => {
            box.addEventListener('input', function () {
                this.value = this.value.replace(/[^0-9]/g, '').slice(-1);
                if (this.value && index < otpBoxes.length - 1) {
                    otpBoxes[index + 1].focus();
                }
                updateHiddenInput();
                if (getAllDigits().length === 6) {
                    setTimeout(() => { if (otpForm) otpForm.submit(); }, 200);
                }
            });

            box.addEventListener('keydown', function (e) {
                if (e.key === 'Backspace' && !this.value && index > 0) {
                    otpBoxes[index - 1].focus();
                }
            });

            box.addEventListener('paste', function (e) {
                e.preventDefault();
                const paste = (e.clipboardData || window.clipboardData).getData('text').replace(/[^0-9]/g, '');
                paste.split('').forEach((char, i) => {
                    if (otpBoxes[i]) {
                        otpBoxes[i].value = char;
                    }
                });
                updateHiddenInput();
                const lastFilled = Math.min(paste.length, otpBoxes.length) - 1;
                if (otpBoxes[lastFilled]) otpBoxes[lastFilled].focus();
                if (paste.length >= 6) {
                    setTimeout(() => { if (otpForm) otpForm.submit(); }, 300);
                }
            });
        });
    }

    function getAllDigits() {
        return Array.from(otpBoxes).map(b => b.value).join('');
    }

    function updateHiddenInput() {
        if (hiddenInput) hiddenInput.value = getAllDigits();
    }

    // Demo: auto-fill from displayed OTP
    const demoFillBtn = document.getElementById('demo-fill-btn');
    const demoOtpDisplay = document.getElementById('demo-otp-value');
    if (demoFillBtn && demoOtpDisplay) {
        demoFillBtn.addEventListener('click', function () {
            const otp = demoOtpDisplay.textContent.trim().replace(/\s/g, '');
            otp.split('').forEach((char, i) => {
                if (otpBoxes[i]) otpBoxes[i].value = char;
            });
            updateHiddenInput();
            this.textContent = 'Filled!';
            this.disabled = true;
        });
    }

    // Countdown timer (10 minutes = 600 seconds)
    const timerEl = document.getElementById('otp-timer');
    if (timerEl) {
        let seconds = 600;
        timerInterval = setInterval(function () {
            seconds--;
            const mins = Math.floor(seconds / 60);
            const secs = seconds % 60;
            timerEl.textContent = ${String(mins).padStart(2,'0')}:;
            if (seconds <= 0) {
                clearInterval(timerInterval);
                timerEl.textContent = 'Expired';
                timerEl.classList.add('text-danger');
                if (otpBoxes) {
                    otpBoxes.forEach(b => b.disabled = true);
                }
                const expiredMsg = document.getElementById('otp-expired-msg');
                if (expiredMsg) expiredMsg.classList.remove('d-none');
            }
        }, 1000);
    }
});
