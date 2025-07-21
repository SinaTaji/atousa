window.addEventListener("load", () => {
    const swiper = new Swiper('.mini-product-slider', {
        slidesPerView: 'auto',
        spaceBetween: 10,
        freeModeMomentum: true,
        loop: true,
        touchRatio: 1,
        touchAngle: 45,
        simulateTouch: true,
        shortSwipes: true,
        longSwipes: true,
        longSwipesRatio: 0.2,
        longSwipesMs: 300,

        resistance: true,
        resistanceRatio: 0.5,

        freeMode: false,

        observer: true,
        observeParents: true,
        speed: 1000,
        autoplay: {
            delay: 2000,
            disableOnInteraction: false,
        },
        threshold: 5,
        allowTouchMove: true,
        watchSlidesProgress: true,
        slideToClickedSlide: true,

        // برای دسکتاپ فقط: ناوبری
        navigation: {
            nextEl: '.swiper-button-next',
            prevEl: '.swiper-button-prev',
        },

        breakpoints: {
            0: {
                spaceBetween: 21,
            },
            769: {
                spaceBetween: 30,
            }
        }
    });
});
