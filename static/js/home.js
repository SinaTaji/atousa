document.addEventListener("DOMContentLoaded", () => {
    function startTimer(elem, expiry) {
        if (!expiry) return;

        function updateTimer() {
            const now = new Date().getTime();
            const end = new Date(expiry).getTime();
            const diff = end - now;

            if (diff <= 0) {
                elem.textContent = "تخفیف به پایان رسید";
                return;
            }

            const days = Math.floor(diff / (1000 * 60 * 60 * 24));
            const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((diff % (1000 * 60)) / 1000);

            elem.textContent = `${seconds} : ${minutes} : ${hours} | ${days} `;
        }

        updateTimer();
        setInterval(updateTimer, 1000);
    }

    window.addEventListener("load", function () {
        new Swiper(".banner-swiper", {
            loop: true,
            autoplay: {
                delay: 5000,
                disableOnInteraction: false,
            },
            navigation: {
                nextEl: ".swiper-button-next",
                prevEl: ".swiper-button-prev",
            },
        });
    });
    // 🎯 برای تمام تایمرهای مربوط به محصولات
    document.querySelectorAll('.discount-timer').forEach(function (timerElem) {
        const expiry = timerElem.getAttribute('data-expiry');
        startTimer(timerElem, expiry);
    });

    // 🎯 برای تایمر کلی بالای صفحه (global timer)
    const globalElem = document.querySelector('.global-discount-timer');
    if (globalElem) {
        const expiry = globalElem.getAttribute('data-expiry');
        startTimer(globalElem, expiry);
    }
});