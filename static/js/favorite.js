document.addEventListener("DOMContentLoaded", function () {

    // گرفتن CSRF token از کوکی
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    const csrftoken = getCookie('csrftoken');

    const btn = document.getElementById("favorite-btn");
    const icon = document.getElementById("heart-icon");

    if (!btn || !icon) return;  // اگر دکمه یا آیکن نبود، ادامه نده

    btn.addEventListener("click", function () {
        const productId = btn.getAttribute("data-product-id");

        fetch(`/account/favorite/toggle/${productId}/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": csrftoken,
                "Content-Type": "application/json"
            },
        })
            .then(response => {
                if (response.status === 401) {
                    // اگر کاربر وارد نشده
                    showMessage({
                        type: "error",
                        text: "برای افزودن به علاقه‌مندی‌ها باید وارد حساب کاربری شوید.",
                        timeout: 8000,
                        buttons: [
                            {
                                text: "ورود",
                                color: "rgba(121,0,73,0.68)",
                                onClick: () => window.location.href = "/user/login"
                            },
                            {
                                text: "ثبت نام",
                                color: "rgba(9,89,2,0.87)",
                                onClick: () => window.location.href = "/user/register"
                            }
                        ]
                    });
                    return null; // ادامه نده
                }
                return response.json(); // اگر اوکی بود، تبدیل کن به JSON
            })
            .then(data => {
                if (!data) return;  // اگر لاگین نبود یا خطا داشت، هیچی نشون نده

                if (data.status === "added") {
                    icon.classList.add("favorited", "animate");
                    setTimeout(() => icon.classList.remove("animate"), 300);
                    showMessage({
                        type: "info",
                        text: "✅ محصول به علاقه‌مندی‌ها اضافه شد.",
                        timeout: 5000,
                        buttons: [
                            {
                                text: "بستن",
                                color: "rgba(103,51,65,0.68)",
                                onClick: () => {
                                        document.getElementById("custom-message-container").style.display = "none";
                                    }
                            },
                            {
                                text: "مشاهده",
                                color: "rgba(87,119,133,0.87)",
                                onClick: () => window.location.href = "/account/wishlist"
                            }
                        ]
                    });
                } else if (data.status === "removed") {
                    icon.classList.remove("favorited");
                    showMessage({
                        type: "error",
                        text: "❌ محصول از علاقه‌مندی‌ها حذف شد.",
                        timeout: 5000
                    });
                }
            })
            .catch(error => {
                console.error("خطا در ارسال درخواست:", error);
                showMessage({
                    type: "error",
                    text: "مشکلی پیش آمد. لطفاً دوباره تلاش کنید.",
                    timeout: 5000
                });
            });
    });
});

const csrfToken = document.cookie.split('; ')
    .find(row => row.startsWith('csrftoken='))
    ?.split('=')[1];

document.querySelectorAll('.remove-favorite-btn').forEach(button => {
    button.addEventListener('click', function (e) {
        e.preventDefault();
        e.stopPropagation();

        const productId = this.getAttribute('data-product-id');

        fetch(`/account/favorite/toggle/${productId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json'
            }
        })
            .then(res => res.json())
            .then(data => {
                if (data.status === 'removed') {
                    // حذف از DOM
                    const card = document.getElementById(`card-wish-list-${productId}`);
                    if (card) card.remove();

                    // نمایش پیام موفقیت
                    if (typeof showMessage === 'function') {
                        showMessage({
                            type: 'error',
                            text: 'محصول از علاقه‌مندی‌ها حذف شد',
                            timeout: 4000,
                        });
                    }
                    // بررسی اینکه آیا لیست خالی شده؟
                    const list = document.querySelectorAll('.card-wish-container');
                    if (list.length === 0) {
                        const container = document.querySelector('.pagination-container');
                        if (container) container.remove(); // حذف صفحه‌بندی
                        document.body.insertAdjacentHTML('afterbegin', `
                            <div class="no-product">
                                <img src="/static/image/no_product.png" alt="محصولی وجود ندارد">
                                <p>لیست علاقه‌مندی‌ها خالی است.</p>
                            </div>
                        `);
                    }
                }

            })
            .catch(err => {
                console.error('خطا در حذف از علاقه‌مندی‌ها:', err);
            });
    });
});
