document.addEventListener('DOMContentLoaded', () => {
    const inputs = document.querySelectorAll('.otp');
    const otpFull = document.getElementById('otp_full');
    const form = document.getElementById('otp-form');
    const countdownEl = document.getElementById('countdown');
    const resendLink = document.getElementById('resend-link');

    // فوکوس خودکار روی اولین ورودی و باز کردن کیبورد عددی
    if (inputs.length > 0) {
        inputs[0].focus();
    }

    inputs.forEach((input, index) => {
        input.setAttribute('type', 'tel');         // باز شدن کیبورد عددی در موبایل
        input.setAttribute('inputmode', 'numeric');
        input.setAttribute('pattern', '[0-9]*');
        input.setAttribute('maxlength', '1');

        input.addEventListener('input', () => {
            // فقط اجازه ورود عدد
            input.value = input.value.replace(/[^0-9]/g, '');

            // اگر یک عدد وارد شد، به ورودی بعدی برو
            if (input.value.length === 1 && index < inputs.length - 1) {
                inputs[index + 1].focus();
            }

            // کد کامل رو جمع کن
            let code = '';
            inputs.forEach(inp => code += inp.value);
            otpFull.value = code;

            // اگر همه ورودی‌ها پر شد، فرم ارسال بشه
            if (code.length === inputs.length) {
                form.submit();
            }
        });

        // (می‌تونی این تکرار رو حذف کنی چون دو بار listener اضافه شده بود)
    });

    // مدیریت تایمر شمارش معکوس برای ارسال مجدد کد
    if (countdownEl && resendLink) {
        const countdownKey = 'otp_expiry_time';
        const countdownDuration = 2 * 60 * 1000; // ۲ دقیقه

        let expiryTime = localStorage.getItem(countdownKey);
        if (!expiryTime) {
            expiryTime = Date.now() + countdownDuration;
            localStorage.setItem(countdownKey, expiryTime);
        } else {
            expiryTime = parseInt(expiryTime);
        }

        const timer = setInterval(() => {
            const now = Date.now();
            const timeLeft = expiryTime - now;

            if (timeLeft > 0) {
                const minutes = Math.floor(timeLeft / 1000 / 60);
                const seconds = Math.floor((timeLeft / 1000) % 60);
                countdownEl.textContent =
                    `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            } else {
                clearInterval(timer);
                countdownEl.style.display = 'none';
                resendLink.style.display = 'inline-block';
                localStorage.removeItem(countdownKey);
            }
        }, 1000);
    }
});