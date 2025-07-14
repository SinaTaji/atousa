document.addEventListener('DOMContentLoaded', function () {
    const mainImage = document.getElementById('main-product-image');
    const thumbnails = document.querySelectorAll('.thumbnail');
    const colorContainer = document.getElementById('color-container');
    const priceDiv = document.querySelector('.product-price');
    const addToCartBtn = document.querySelector('.add-to-cart-btn');
    const quantityInput = document.getElementById('quantity');
    const productId = window.productId;
    const copyBtn = document.getElementById('copy-link-btn');
    const copyMsg = document.getElementById('copy-message');
    attachColorClickEvents();
    if (copyBtn && copyMsg) {
        const refLink = copyBtn.dataset.refLink;
        copyBtn.addEventListener('click', () => {
            navigator.clipboard.writeText(refLink).then(() => {
                copyMsg.style.display = 'block';
                setTimeout(() => {
                    copyMsg.style.display = 'none';
                }, 3000);
            }).catch(err => {
                alert('کپی کردن لینک با خطا مواجه شد');
                console.error(err);
            });
        });
    }

    // بزرگنمایی تصویر
    const zoomWrapper = document.getElementById('main-image');
    const zoomImage = document.getElementById('main-product-image');
    if (zoomWrapper && zoomImage) {
        zoomWrapper.addEventListener('mouseenter', () => {
            zoomWrapper.classList.add('zoomed');
        });
        zoomWrapper.addEventListener('mouseleave', () => {
            zoomWrapper.classList.remove('zoomed');
            zoomImage.style.transformOrigin = 'center center';
        });
        zoomWrapper.addEventListener('mousemove', (e) => {
            if (!zoomWrapper.classList.contains('zoomed')) return;
            const rect = zoomWrapper.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            const xPercent = (x / rect.width) * 100;
            const yPercent = (y / rect.height) * 100;
            zoomImage.style.transformOrigin = `${xPercent}% ${yPercent}%`;
        });
    }

    // دکمه‌های تعداد
    const decreaseBtn = document.querySelector(".decrease");
    const increaseBtn = document.querySelector(".increase");

    if (decreaseBtn && increaseBtn && quantityInput) {
        decreaseBtn.addEventListener("click", () => {
            let value = parseInt(quantityInput.value);
            if (value > 1) quantityInput.value = value - 1;
        });

        increaseBtn.addEventListener("click", () => {
            let value = parseInt(quantityInput.value);
            quantityInput.value = value + 1;
        });
    }
    let selectedSizeId = null;
    let selectedColorId = null;

    if (thumbnails.length > 0) thumbnails[0].classList.add('active');

    thumbnails.forEach(thumb => {
        thumb.addEventListener('click', () => {
            mainImage.src = thumb.dataset.image;
            thumbnails.forEach(t => t.classList.remove('active'));
            thumb.classList.add('active');
        });
    });

    function attachColorClickEvents() {
        const mainImage = document.getElementById('main-image');
        const mainProductImage = document.getElementById('main-product-image');
        const colorContainer = document.getElementById('color-container');
        const colorButtons = colorContainer.querySelectorAll('.color-swatch');

        if (!colorButtons.length) return;

        colorButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                const imageUrl = btn.dataset.imageUrl;
                if (imageUrl) {
                    mainProductImage.src = imageUrl;

                    colorButtons.forEach(s => s.classList.remove('active'));
                    btn.classList.add('active');

                    thumbnails.forEach(t => t.classList.remove('active'));
                    thumbnails.forEach(t => {
                        if (t.dataset.image === imageUrl) {
                            t.classList.add('active');
                        }
                    });

                    selectedColorId = btn.dataset.colorId;
                    const colorInput = document.getElementById('colorInput');
                    if (colorInput) colorInput.value = selectedColorId;

                    // ✅ اسکرول در موبایل
                    if (window.innerWidth <= 768 && mainImage) {
                        mainImage.scrollIntoView({
                            behavior: 'smooth',
                            block: 'start'
                        });
                    }
                }
            });
        });
    }

    function formatPrice(price) {
        // فرض می‌کنیم ورودی عدد یا رشته عددی است
        // اول به عدد تبدیل می‌کنیم
        const number = Number(price.toString().replace(/,/g, ''));
        if (isNaN(number)) return price; // اگر عدد نبود، بدون تغییر برگردون

        // جداکردن سه رقم سه رقم با toLocaleString و اضافه کردن تومان
        return number.toLocaleString('en-US') + ' تومان';
    }

    function updatePrice(data) {
        const discountBadge = document.getElementById('discount-badge');
        const discountedSpan = document.getElementById('discounted-price');
        const originalSpan = document.getElementById('original-price');
        const normalSpan = document.getElementById('normal-price');
        const dPriceWrapper = document.getElementById('d-p');

        if (!discountBadge || !discountedSpan || !originalSpan || !normalSpan || !dPriceWrapper) {
            console.warn("❗ عناصر قیمت در صفحه پیدا نشدند.");
            return;
        }

        if (!data.is_active) {
            discountBadge.style.display = 'none';
            dPriceWrapper.style.display = 'none';
            normalSpan.textContent = 'ناموجود';
            normalSpan.style.display = '';
            return;
        }

        if (data.has_discount) {
            discountBadge.textContent = `٪${data.discount} تخفیف`;
            discountBadge.style.display = '';

            discountedSpan.textContent = formatPrice(data.discounted_price);
            originalSpan.textContent = formatPrice(data.price);

            dPriceWrapper.style.display = '';
            normalSpan.style.display = 'none';
        } else {
            discountBadge.style.display = 'none';
            dPriceWrapper.style.display = 'none';

            normalSpan.textContent = formatPrice(data.price);
            normalSpan.style.display = '';
        }
    }

    function updateColorsAndPrice(sizeId) {
        selectedSizeId = sizeId;
        selectedColorId = null; // ← ریست رنگ

        fetch(`/product/get-variants/?product_id=${productId}&size_id=${sizeId}`)
            .then(res => res.json())
            .then(data => {
                if (!data.success) {
                    console.error('خطا در دریافت داده‌ها');
                    return;
                }

                updatePrice(data);
                if (data.main_image) {
                    mainImage.src = data.main_image;
                    thumbnails.forEach(t => t.classList.remove('active'));
                    thumbnails.forEach(t => {
                        if (t.dataset.image === data.main_image) t.classList.add('active');
                    });
                }

                colorContainer.innerHTML = '';
                data.colors.forEach(color => {
                    const btn = document.createElement('button');
                    btn.className = 'color-swatch tooltip-container';
                    btn.title = color.title;
                    btn.style.backgroundColor = color.hex_color;
                    btn.dataset.colorId = color.id;
                    btn.dataset.imageUrl = color.image_url;

                    const tooltipSpan = document.createElement('span');
                    tooltipSpan.className = 'tooltip-text';
                    tooltipSpan.textContent = color.title;
                    btn.appendChild(tooltipSpan);

                    colorContainer.appendChild(btn);
                });

                attachColorClickEvents();

                const firstNewColor = colorContainer.querySelector('.color-swatch');
                if (firstNewColor) {
                    firstNewColor.classList.add('active');
                    selectedColorId = firstNewColor.dataset.colorId;
                    mainImage.src = firstNewColor.dataset.imageUrl || mainImage.src;

                    const colorInput = document.getElementById('colorInput');
                    if (colorInput) {
                        colorInput.value = selectedColorId;
                    }
                }
            })
            .catch(err => {
                console.error('خطا در fetch:', err);
            });
    }

    document.querySelectorAll('.size-button').forEach(btn => {
        btn.addEventListener('click', () => {
            const sizeId = btn.dataset.sizeId;
            updateColorsAndPrice(sizeId);
            document.querySelectorAll('.size-button').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
        });
    });

    attachColorClickEvents();

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

    const link = document.getElementById("size-guide-link");
    const target = document.getElementById("size-guide-target");

    if (link && target) {
        link.addEventListener("click", function (e) {
            e.preventDefault();
            target.scrollIntoView({
                behavior: "smooth",
                block: "start"
            });
        });
    }
    if (addToCartBtn) {
        addToCartBtn.addEventListener('click', () => {
            const quantity = quantityInput ? parseInt(quantityInput.value) : 1;

            if (!selectedSizeId || !selectedColorId) {
                showMessage({
                    type: "error",
                    text: "لطفا رنگ و سایز را انتخاب کنید",
                    timeout: 5000
                });
                return;
            }
            if (quantityInput) {
                const max = parseInt(quantityInput.max);
                if (quantity > max) {
                    showMessage({
                        type: "error",
                        text: `از این محصول ${max} عدد باقی مانده.`,
                        timeout: 5000
                    });
                    return;
                }
                if (quantity < 1) {
                    showMessage({
                        type: "error",
                        text: "حداقل تعداد باید ۱ باشد.",
                        timeout: 5000
                    });
                    return;
                }
            }
            const csrfToken = getCookie('csrftoken');
            fetch('/cart/add-to-cart-ajax/', {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrfToken,
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    product_id: productId,
                    size_id: selectedSizeId,
                    color_id: selectedColorId,
                    quantity: quantity
                })
            })
                .then(res => res.json())
                .then(data => {
                    if (data.status === "ok") {

                        const cartCountMenu = document.getElementById('cart-count');
                        if (cartCountMenu && data.total_items !== undefined) {
                            cartCountMenu.textContent = data.total_items;
                            cartCountMenu.style.display = '';
                            cartCountMenu.classList.remove('animate');
                            void cartCountMenu.offsetWidth;
                            cartCountMenu.classList.add('animate');
                        }

                        showMessage({
                            type: "success",
                            text: "محصول با موفقیت به سبد خرید شما اضافه شد",
                            timeout: 8000,
                            buttons: [
                                {
                                    text: "ادامه خرید",
                                    color: "#9b9b8b",
                                    onClick: () => {
                                        document.getElementById("custom-message-container").style.display = "none";
                                    }
                                },
                                {
                                    text: "مشاهده سبد خرید",
                                    color: "#0c9800",
                                    onClick: () => {
                                        window.location.href = "/cart/detail/";
                                    }
                                }
                            ]
                        });

                        const cartItemsDiv = document.getElementById("cart-items");
                        if (cartItemsDiv && data.cart_html) {
                            cartItemsDiv.innerHTML = data.cart_html;
                        }

                    } else {
                        alert("خطا: " + data.message);
                    }
                });
        });
    }
});
document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('image-modal');
    const modalMainImage = document.getElementById('modal-main-image');
    const mainProductImage = document.getElementById('main-product-image');

    // باز کردن مودال با تصویر اصلی
    mainProductImage.addEventListener('click', () => {
        modalMainImage.src = mainProductImage.src;  // تصویر اصلی را به مودال می‌فرستیم
        modal.classList.remove('hidden');  // مودال نمایش داده می‌شود
        document.body.style.overflow = 'hidden';  // جلوگیری از اسکرول صفحه
    });

    // بستن مودال
    window.closeModal = function () {
        modal.classList.add('hidden');  // مخفی کردن مودال
        document.body.style.overflow = '';  // بازگشت اسکرول به صفحه
    };

    // تغییر تصویر اصلی مودال
    window.changeMainImage = function (src) {
        modalMainImage.src = src;  // تصویر جدید را نمایش می‌دهیم
    };

    // کلیک بیرون از مودال برای بستن آن
    modal.addEventListener('click', (e) => {
        // اگر کلیک خارج از تصویر اصلی بود، مودال بسته می‌شود
        if (e.target === modal) {
            closeModal();
        }
    });
});
