document.addEventListener('DOMContentLoaded', function () {
    const tabs = {
        cart: document.getElementById('orders-b'),
        packing: document.getElementById('wish-b'),
        sending: document.getElementById('address-b'),
        finished: document.getElementById('contacts-b'),
    };

    const ordersContainer = document.getElementById('current-o'); // اینجا هدف اسکروله

    let loading = false;
    let currentStatus = 'cart';

    function setActiveTab(status) {
        Object.keys(tabs).forEach(key => {
            tabs[key].classList.toggle('active-tab', key === status);
        });
    }

    function scrollToOrdersContainer() {
        if (ordersContainer) {
            ordersContainer.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    }

    function loadOrdersByStatus(status, page = 1) {
        if (loading) return;
        loading = true;
        currentStatus = status;
        setActiveTab(status);
        ordersContainer.innerHTML = '<p class="loading-msg">در حال دریافت اطلاعات...</p>';

        fetch(`/us/ajax/orders/${status}/?page=${page}`)
            .then(response => {
                if (!response.ok) throw new Error('خطا در دریافت اطلاعات');
                return response.text();
            })
            .then(html => {
                ordersContainer.innerHTML = html;
                loading = false;

                // بعد از لود شدن داده‌ها، اسکرول کن به ordersContainer
                setTimeout(scrollToOrdersContainer, 100);
            })
            .catch(error => {
                ordersContainer.innerHTML = '<p class="error-msg text-danger">مشکلی پیش آمده. دوباره تلاش کنید.</p>';
                loading = false;
                console.error(error);
            });
    }

    // وصل کردن کلیک‌ها به باکس‌ها
    tabs.cart.addEventListener('click', () => loadOrdersByStatus('cart'));
    tabs.packing.addEventListener('click', () => loadOrdersByStatus('packing'));
    tabs.sending.addEventListener('click', () => loadOrdersByStatus('sending'));
    tabs.finished.addEventListener('click', () => loadOrdersByStatus('finished'));

    // صفحه‌بندی
    ordersContainer.addEventListener('click', function (event) {
        const target = event.target;
        if (!loading && target.classList.contains('pagination-btn') && !target.classList.contains('active')) {
            const page = target.dataset.page;
            const status = target.dataset.status || currentStatus;
            if (page && status) {
                loadOrdersByStatus(status, page);
            }
        }
    });

    // لود اولیه + اسکرول
    loadOrdersByStatus('cart');
});