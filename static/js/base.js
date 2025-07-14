function showLoader() {
    document.getElementById('global-loader').classList.remove('hidden');
}


// اجرا بعد از بارگذاری کامل صفحه
document.addEventListener("DOMContentLoaded", function () {
    const allForms = document.querySelectorAll("form");

    allForms.forEach(form => {
        form.addEventListener("submit", function (event) {
            if (form.id === "gift-code-form" || form.id === "search-form" || form.id === "search-form-mobile") {
                return;
            }
            // بررسی اعتبار فرم
            if (!form.checkValidity()) {
                // فرم نامعتبره، لودر نشون نده
                return;
            }

            // فرم معتبره، لودر رو نشون بده
            showLoader();
        });
    });
});
document.addEventListener('DOMContentLoaded', function () {
    // همه فلش‌ها را انتخاب می‌کنیم با کلاس toggle-arrow
    document.querySelectorAll('.toggle-arrow').forEach(function (arrow) {
        arrow.addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();

            const arrowEl = e.currentTarget;
            // ul بعد از a (زیرمنو) را پیدا می‌کنیم
            const parentLi = arrowEl.closest('li');
            const submenu = parentLi.querySelector('ul');

            if (!submenu) return;

            // نمایش یا مخفی کردن زیرمنو
            if (submenu.style.display === 'block') {
                submenu.style.display = 'none';
                arrowEl.classList.remove('active');
            } else {
                submenu.style.display = 'block';
                arrowEl.classList.add('active');
            }
        });
    });
});
document.addEventListener('DOMContentLoaded', function () {
    const openBtn = document.getElementById('open-search');
    const closeBtn = document.getElementById('close-search');
    const overlay = document.getElementById('search-overlay');
    const input = document.getElementById('search-input-mobile');
    const clearBtn = document.getElementById('clear-search-input');
    const searchForm = document.getElementById('search-form-mobile');
    const searchIcon = document.getElementById('search-submit-icon');

    openBtn.addEventListener('click', () => {
        overlay.classList.add('active');
        document.body.style.overflow = 'hidden';

        setTimeout(() => input?.focus(), 100);
    });

    closeBtn.addEventListener('click', () => {
        overlay.classList.remove('active');
        document.body.style.overflow = '';
    });

    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) {
            overlay.classList.remove('active');
            document.body.style.overflow = '';
        }
    });

    // نمایش یا مخفی کردن دکمه پاک کردن متن
    input.addEventListener('input', () => {
        if (input.value.trim() !== '') {
            clearBtn.style.display = 'block';
        } else {
            clearBtn.style.display = 'none';
        }
    });

    // پاک کردن متن وقتی روی ضربدر کلیک شد
    clearBtn.addEventListener('click', () => {
        input.value = '';
        clearBtn.style.display = 'none';
        input.focus();
    });

    // وقتی روی آیکن ذره‌بین کلیک شد، فرم رو سابمیت کن
    searchIcon.addEventListener('click', () => {
        if (input.value.trim() !== '') {
            searchForm.submit();
        }
    });
});

document.addEventListener('DOMContentLoaded', function () {
    const input = document.getElementById('search-input-burger');
    const form = document.getElementById('search-form-mobile');
    const clearBtn = document.getElementById('clear-search-burger');
    const submitIcon = document.getElementById('search-submit-burger');

    if (!input || !form || !clearBtn || !submitIcon) return;

    // نمایش یا مخفی کردن دکمه پاک کردن متن
    input.addEventListener('input', () => {
        if (input.value.trim() !== '') {
            clearBtn.style.display = 'block';
        } else {
            clearBtn.style.display = 'none';
        }
    });

    // کلیک روی ضربدر: پاک کردن فیلد
    clearBtn.addEventListener('click', () => {
        input.value = '';
        clearBtn.style.display = 'none';
        input.focus();
    });

    // کلیک روی آیکن سرچ: سابمیت فرم اگر مقدار وارد شده باشه
    submitIcon.addEventListener('click', () => {
        if (input.value.trim() !== '') {
            form.submit();
        }
    });
});

document.addEventListener('DOMContentLoaded', function () {
    const searchConfigs = [
        {
            inputId: 'search-input-overlay',
            suggestionId: 'search-suggestions-overlay'
        },
        {
            inputId: 'search-input-burger',
            suggestionId: 'search-suggestions-burger'
        },
        {
            inputId: 'search-input',
            suggestionId: 'search-suggestions-desktop'
        }
    ];

    searchConfigs.forEach(({inputId, suggestionId}) => {
        const input = document.getElementById(inputId);
        const box = document.getElementById(suggestionId);
        if (!input || !box) return;

        input.addEventListener('input', function () {
            const query = input.value.trim();

            if (query.length < 2) {
                box.style.display = 'none';
                box.innerHTML = '';
                return;
            }

            fetch(`/product/ajax/search-suggestions/?q=${encodeURIComponent(query)}`)
                .then(res => res.json())
                .then(data => {
                    const {categories, products} = data;

                    if ((!categories?.length) && (!products?.length)) {
                        box.style.display = 'none';
                        box.innerHTML = '';
                        return;
                    }

                    let html = '';

                    if (categories?.length) {
                        html += `<div class="suggestion-section"><strong>دسته‌بندی‌ها</strong>`;
                        html += categories.map(cat =>

                            `<div class="suggestion-item category" data-url="${cat.url}" style= cursor:pointer;">
                               <img src="/static/image/icons/search-.svg" alt=""> ${cat.name}</div>`
                        ).join('');
                        html += `</div>`;
                    }

                    if (products?.length) {
                        html += `<div class="suggestion-section"><strong>محصولات</strong>`;
                        html += products.map(prod =>
                            `<div class="suggestion-item product" data-url="${prod.url}" style="display:flex; align-items:center; padding:5px; cursor:pointer;">
                                <img src="${prod.image}" alt="${prod.name}" style="width:50px; height:50px; object-fit:cover; margin-left:10px; border-radius:3px;">
                                <span>${prod.name}</span>
                            </div>`
                        ).join('');
                        html += `</div>`;
                    }

                    box.innerHTML = html;
                    box.style.display = 'block';
                })
                .catch(err => {
                    console.error('Error fetching suggestions:', err);
                    box.style.display = 'none';
                    box.innerHTML = '';
                });
        });

        document.addEventListener('click', function (e) {
            const item = e.target.closest('.suggestion-item');
            if (item && item.dataset.url) {
                window.location.href = item.dataset.url;
            } else if (!box.contains(e.target) && e.target !== input) {
                box.style.display = 'none';
                box.innerHTML = '';
            }
        });
    });
});

function updateCounts() {
    fetch("/us/ajax/user-counts/")
        .then(res => res.json())
        .then(data => {
            // هر دو حالت دسکتاپ و موبایل آی‌دی های یکسان دارن
            const wishlist = document.getElementById("wishlist_count");
            const messages = document.querySelectorAll("#messages_count");  // ممکن چندتا باشه
            const carts = document.querySelectorAll("#cart-count");         // ممکن چندتا باشه

            if (wishlist) {
                wishlist.textContent = data.wishlist_count;
                wishlist.style.display = data.wishlist_count > 0 ? 'inline-block' : 'none';
            }

            messages.forEach(el => {
                el.textContent = data.messages_count;
                el.style.display = data.messages_count > 0 ? 'inline-block' : 'none';
            });

            carts.forEach(el => {
                el.textContent = data.cart_item_count;
                el.style.display = data.cart_item_count > 0 ? 'inline-block' : 'none';
            });
        })
        .catch(err => console.error('AJAX Error:', err));
}

function toggleSupportMenu() {
    const menu = document.getElementById('supportMenu');
    if (menu.style.display === 'flex') {
        menu.style.display = 'none';
    } else {
        menu.style.display = 'flex';
    }
}

function showMessage({type = "success", text = "", buttons = [], timeout = 5000}) {
    const container = document.getElementById("custom-message-container");
    const messageBox = document.getElementById("custom-message");
    const messageText = document.getElementById("message-text");
    const messageButtons = document.getElementById("message-buttons");

    if (!container || !messageBox || !messageText || !messageButtons) {
        console.error("DOM elements for message not found!");
        return;
    }

    // ریست استایل‌ها و محتوا
    messageBox.className = "";
    messageBox.classList.add(`message-${type}`);
    messageText.textContent = text;
    messageButtons.innerHTML = "";

    // ساخت دکمه‌ها
    buttons.forEach(btn => {
        const button = document.createElement("button");
        button.textContent = btn.text;
        button.style.backgroundColor = btn.color || "#ccc";
        button.onclick = btn.onClick || (() => {
        });
        messageButtons.appendChild(button);
    });

    // نمایش پیام
    container.style.display = "block";

    // نوار پیشرفت انیمیشنی (4 ثانیه)
    const bar = messageBox.querySelector(".message-bar");
    bar.style.animation = "none";
    void bar.offsetWidth; // trigger reflow
    bar.style.animation = `progressBar 5000ms linear forwards`;

    // بسته شدن پیام بعد از timeout (مثلاً 6 ثانیه)
    clearTimeout(container.hideTimeout);
    container.hideTimeout = setTimeout(() => {
        container.style.display = "none";
    }, timeout);
}

// پردازش صف پیام‌های جنگو که توی base.html داخل window.messagesQueue ساختیم
window.addEventListener("DOMContentLoaded", () => {
    if (window.messagesQueue && window.messagesQueue.length) {
        // پیام‌ها را یکی یکی نمایش بده (می‌تونی صف درست کنی)
        window.messagesQueue.forEach(msg => {
            showMessage({
                type: msg.type || "info",
                text: msg.text || "",
                timeout: 5000
            });
        });
    }
});
document.addEventListener('DOMContentLoaded', function () {
    // تلاش برای گرفتن المان موبایل
    let input = document.getElementById('search-input-mobile');
    // اگر نبود، دسکتاپ را بگیر
    if (!input) {
        input = document.getElementById('search-input');
    }

    const suggestionBox = document.getElementById('search-suggestions');
    if (!input || !suggestionBox) return;

    input.addEventListener('input', function () {
        const query = input.value.trim();

        if (query.length < 2) {
            suggestionBox.style.display = 'none';
            suggestionBox.innerHTML = '';
            return;
        }

        fetch(`/product/ajax/search-suggestions/?q=${encodeURIComponent(query)}`)
            .then(res => res.json())
            .then(data => {
                const {categories, products} = data;

                if ((!categories || categories.length === 0) && (!products || products.length === 0)) {
                    suggestionBox.style.display = 'none';
                    suggestionBox.innerHTML = '';
                    return;
                }

                let html = '';

                if (categories && categories.length > 0) {
                    html += `<div class="suggestion-section"><strong>دسته‌بندی‌ها</strong>`;
                    html += categories.map(cat =>
                        `<div class="suggestion-item category" data-url="${cat.url}" style="padding:5px; cursor:pointer;">${cat.name}</div>`
                    ).join('');
                    html += `</div>`;
                }

                if (products && products.length > 0) {
                    html += `<div class="suggestion-section"><strong>محصولات</strong>`;
                    html += products.map(prod =>
                        `<div class="suggestion-item product" data-url="${prod.url}" style="display:flex; align-items:center; padding:5px; cursor:pointer;">
                            <img src="${prod.image}" alt="${prod.name}" style="width:30px; height:30px; object-fit:cover; margin-left:10px; border-radius:3px;">
                            <span>${prod.name}</span>
                        </div>`
                    ).join('');
                    html += `</div>`;
                }

                suggestionBox.innerHTML = html;
                suggestionBox.style.display = 'block';
            })
            .catch(err => {
                console.error('Error fetching suggestions:', err);
                suggestionBox.style.display = 'none';
                suggestionBox.innerHTML = '';
            });
    });

    document.addEventListener('click', function (e) {
        const item = e.target.closest('.suggestion-item');
        if (item) {
            const url = item.dataset.url;
            if (url) {
                window.location.href = url;
            }
        } else if (!suggestionBox.contains(e.target) && e.target !== input) {
            suggestionBox.style.display = 'none';
            suggestionBox.innerHTML = '';
        }
    });
});

function toggleMobileMenu() {
    const menu = document.getElementById('mobileMenu');
    const overlay = document.getElementById('menuOverlay');
    const btn = document.getElementById('hamburgerBtn');

    const isOpen = menu.classList.contains('active');

    if (isOpen) {
        menu.classList.remove('active');
        overlay.classList.remove('active');
        btn.classList.remove('active');
    } else {
        menu.classList.add('active');
        overlay.classList.add('active');
        btn.classList.add('active');
    }
}

function closeMobileMenu() {
    document.getElementById('mobileMenu').classList.remove('active');
    document.getElementById('menuOverlay').classList.remove('active');
    document.getElementById('hamburgerBtn').classList.remove('active');
}

function toggleSubMenu(el) {
    el.classList.toggle('active');
    const submenu = el.nextElementSibling;
    submenu.style.maxHeight = submenu.style.maxHeight ? null : submenu.scrollHeight + "px";
}

// بستن منو با زدن ESC
document.addEventListener('keydown', function (e) {
    if (e.key === "Escape") {
        closeMobileMenu();
    }
});