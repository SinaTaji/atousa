document.addEventListener('DOMContentLoaded', function () {
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let cookie of cookies) {
                cookie = cookie.trim();
                if (cookie.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    const csrftoken = getCookie('csrftoken');
    const messageEl = document.getElementById('gift-code-message');

    document.getElementById('gift-code-form').addEventListener('submit', function (e) {
        e.preventDefault();

        const giftCodeInput = document.getElementById('gift_code');
        const gift_code = giftCodeInput.value.trim();

        if (!gift_code) {
            if (messageEl) {
                messageEl.style.color = 'red';
                messageEl.textContent = 'لطفاً کد تخفیف را وارد کنید.';
            }
            return;
        }

        fetch('/cart/apply-gift-code/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrftoken,
            },
            body: new URLSearchParams({
                'gift_code': gift_code
            })
        })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(data => Promise.reject(data));
                }
                return response.json();
            })
            .then(data => {
                if (messageEl) {
                    messageEl.style.color = 'green';
                    messageEl.textContent = data.message || 'کد تخفیف با موفقیت اعمال شد.';
                }

                // 🔽 به‌روزرسانی قیمت‌ها و تخفیف‌ها
                if (data.total_price !== undefined) {
                    const totalPriceEl = document.getElementById('total-price');
                    if (totalPriceEl) totalPriceEl.textContent = formatPrice(data.total_price);
                }

                if (data.total_discount !== undefined) {
                    const totalDiscountEl = document.getElementById('total-discount');
                    const totalDiscountWrapper = document.getElementById('total-discount-wrapper');
                    if (totalDiscountEl) totalDiscountEl.textContent = formatPrice(data.total_discount);
                    if (totalDiscountWrapper) {
                        totalDiscountWrapper.style.display = data.total_discount > 0 ? '' : 'none';
                    }
                }

                if (data.send_free !== undefined) {
                    const freeShippingMsgEl = document.getElementById('free-shipping-msg');
                    if (freeShippingMsgEl) {
                        if (data.send_free <= 0) {
                            freeShippingMsgEl.textContent = 'ارسال شما رایگان است!';
                        } else {
                            freeShippingMsgEl.textContent = `${formatPrice(data.send_free)} تا ارسال رایگان`;
                        }
                    }
                }

            })
            .catch(errorData => {
                if (!messageEl) return;

                messageEl.style.color = 'red';

                if (errorData.errors) {
                    let errors;
                    if (typeof errorData.errors === 'string') {
                        try {
                            errors = JSON.parse(errorData.errors);
                        } catch {
                            errors = {'__all__': [errorData.errors]};
                        }
                    } else {
                        errors = errorData.errors;
                    }

                    const messages = Object.values(errors).flat().map(e => {
                        if (typeof e === 'string') return e;
                        if (e.message) return e.message;
                        return JSON.stringify(e);
                    });

                    messageEl.textContent = messages.join(' ');
                } else if (errorData.message) {
                    messageEl.textContent = errorData.message;
                } else {
                    messageEl.textContent = 'خطایی رخ داده است.';
                }
            });
    });

    function formatPrice(amount) {
        return new Intl.NumberFormat().format(amount) + ' تومان';
    }

    function updateQuantity(url, key, onRemove = false) {
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify({variant_key: key})
        })
            .then(res => res.json())
            .then(data => {
                if (data.error) return;

                const itemMeta = document.querySelector(`[data-variant-key="${key}"]`);
                if (!itemMeta) return;
                const cartItem = itemMeta.closest('.cart-item');
                const quantitySpan = itemMeta.querySelector('.quantity');
                const priceEl = cartItem?.querySelector('.item-price');
                const discountEl = cartItem?.querySelector('.item-discount');

                if (onRemove || data.new_quantity === 0) {
                    cartItem?.remove();
                } else {
                    if (quantitySpan) {
                        quantitySpan.textContent = data.new_quantity;
                    }

                    const unitPrice = parseInt(itemMeta.dataset.unitPrice || '0');
                    if (priceEl) {
                        priceEl.textContent = formatPrice(unitPrice * data.new_quantity);
                    }

                    const unitDiscount = parseInt(itemMeta.dataset.unitDiscount || '0');
                    if (discountEl) {
                        discountEl.textContent = formatPrice(unitDiscount * data.new_quantity) + ' تخفیف';
                    }
                }

                // به‌روزرسانی بخش‌های سبد خرید (در صورت وجود)
                const totalPriceEl = document.getElementById('total-price');
                if (totalPriceEl && data.total_price !== undefined) {
                    totalPriceEl.textContent = formatPrice(data.total_price);
                }

                const totalOrgPriceEl = document.getElementById('total-org-price');
                if (totalOrgPriceEl && data.total_org_price !== undefined) {
                    totalOrgPriceEl.textContent = formatPrice(data.total_org_price);
                }

                const totalItemsEl = document.querySelector('.cart-summaryy h3');
                if (totalItemsEl && data.total_items !== undefined) {
                    totalItemsEl.textContent = data.total_items;
                }

                const cartCountMenu = document.getElementById('cart-count');
                if (cartCountMenu && data.total_items !== undefined) {
                    if (data.total_items > 0) {
                        cartCountMenu.textContent = data.total_items;
                        cartCountMenu.style.display = '';
                        cartCountMenu.classList.remove('animate');
                        void cartCountMenu.offsetWidth;
                        cartCountMenu.classList.add('animate');
                    } else {
                        cartCountMenu.textContent = '';
                        cartCountMenu.style.display = 'none';
                    }
                }

                const freeShippingMsgEl = document.getElementById('free-shipping-msg');
                if (freeShippingMsgEl && data.send_free !== undefined) {
                    if (data.send_free <= 0) {
                        freeShippingMsgEl.textContent = ' ارسال شما رایگان است!';
                    } else {
                        freeShippingMsgEl.textContent = `${formatPrice(data.send_free)} تا ارسال رایگان`;
                    }
                }

                const totalDiscountWrapper = document.getElementById('total-discount-wrapper');
                if (totalDiscountWrapper) {
                    if (!data.total_discount || data.total_discount === 0) {
                        totalDiscountWrapper.style.display = 'none';
                    } else {
                        const totalDiscountEl = document.getElementById('total-discount');
                        if (totalDiscountEl) {
                            totalDiscountEl.textContent = formatPrice(data.total_discount);
                        }
                    }
                }

                // بررسی سبد خالی
                const remainingItems = document.querySelectorAll('.cart-item');
                const emptyCartMessage = document.getElementById('empty-detail');
                const cartContainer = document.querySelector('.cart-container');
                if (remainingItems.length === 0) {
                    if (cartContainer) cartContainer.style.display = 'none';
                    if (emptyCartMessage) emptyCartMessage.style.display = '';
                }
            });
    }

    // رویدادها
    document.querySelectorAll('.increase-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const parent = btn.closest('[data-variant-key]') || btn.closest('.item-meta');
            const key = parent?.dataset.variantKey;
            if (key) updateQuantity('/cart/increase/', key);
        });
    });

    document.querySelectorAll('.decrease-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const parent = btn.closest('[data-variant-key]') || btn.closest('.item-meta');
            const key = parent?.dataset.variantKey;
            if (key) updateQuantity('/cart/decrease/', key);
        });
    });

    document.querySelectorAll('.remove-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const key = btn.dataset.variantKey;
            if (key) updateQuantity('/cart/del/order/', key, true);
        });
    });
});



function formatPrice(amount) {
    if (!amount || isNaN(amount)) return '۰ تومان';
    return new Intl.NumberFormat().format(amount) + ' تومان';
}

function getCookie(name) {
    const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
    if (match) return match[2];
    return null;
}

