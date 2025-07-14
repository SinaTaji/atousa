window.addEventListener("load", () => {
    const swiper = new Swiper('.mini-product-slider', {
        slidesPerView: 'auto',
        spaceBetween: 10,
        loop: true,
        speed: 800,
        autoplay: {
            delay: 3000,
            disableOnInteraction: false,
        },
        freeMode: false,
        resistance: false,
        touchRatio: 1.5,
        threshold: 5,
        allowTouchMove: true,
        watchSlidesProgress: true,

        // بهبود کیفیت انتقال بین اسلایدها:
        slideToClickedSlide: true,

        // برای دسکتاپ فقط: ناوبری
        navigation: {
            nextEl: '.swiper-button-next',
            prevEl: '.swiper-button-prev',
        },

        breakpoints: {
            0: {
                spaceBetween: 20,
            },
            769: {
                spaceBetween: 30,
            }
        }
    });
});