document.addEventListener('DOMContentLoaded', () => {

    // ---- توابع اصلی ----
    function updateShippingAndTotal(shippingCost, finalPrice, method) {
        const shippingCostEl = document.getElementById('shipping-cost');
        const totalPriceEl = document.getElementById('total-price');

        if (shippingCostEl) {
            if (method === 'tipax') {
                shippingCostEl.textContent = ''; // حذف نمایش هزینه برای تیپاکس
            } else if (shippingCost > 0) {
                shippingCostEl.textContent = `هزینه ارسال ${formatPrice(shippingCost)}`;
            } else {
                shippingCostEl.textContent = 'ارسال رایگان';
            }
        }

        if (window.location.pathname === '/cart/information/') {
            if (totalPriceEl) {
                totalPriceEl.textContent = formatPrice(finalPrice);
            }
        }
    }

    function updateFreeShippingMessage(remaining, method) {
        const freeShippingMsgEl = document.getElementById('free-shipping-msg');
        if (!freeShippingMsgEl) return;

        if (method === 'tipax') {
            freeShippingMsgEl.textContent = ''; // هیچ پیامی برای تیپاکس
            return;
        }

        if (remaining === undefined || remaining === null || isNaN(remaining)) {
            freeShippingMsgEl.textContent = '';
            return;
        }

        if (remaining <= 0) {
            freeShippingMsgEl.textContent = 'ارسال شما رایگان است!';
        } else {
            freeShippingMsgEl.textContent = `${formatPrice(remaining)} تا ارسال رایگان`;
        }
    }

    function formatPrice(amount) {
        if (!amount || isNaN(amount)) return '۰ تومان';
        return new Intl.NumberFormat().format(amount) + ' تومان';
    }

    function setShippingMethodRadio(method) {
        document.querySelectorAll('input[name="shipping_method"]').forEach(radio => {
            radio.checked = radio.value === method;
        });
    }

    function fetchShippingDataAndUpdateUI() {
        fetch("/cart/set-shipping-method/", {
            method: 'GET',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            }
        })
            .then(res => res.json())
            .then(data => {
                if (data.status === 'ok') {
                    setShippingMethodRadio(data.shipping_method);
                    updateFreeShippingMessage(data.send_free, data.shipping_method);
                    updateShippingAndTotal(data.shipping_cost, data.final_price, data.shipping_method);
                }
            });
    }

    function fillFormWithAddress(element) {
        const firstName = element.dataset.first_name;
        const lastName = element.dataset.last_name;
        const province = element.dataset.province;
        const city = element.dataset.city;
        const address = element.dataset.address;
        const postalCode = element.dataset.postal_code;
        const phone = element.dataset.phone;

        document.getElementById('id_first_name').value = firstName;
        document.getElementById('id_last_name').value = lastName;
        document.getElementById('id_address').value = address;
        document.getElementById('id_postal_code').value = postalCode;
        document.getElementById('id_phone').value = phone;
        document.getElementById('input-province').value = province;
        document.getElementById('input-city').value = city;

        document.querySelector('#dropdown-province .dropdown-selected').textContent = province;
        document.querySelector('#dropdown-city .dropdown-selected').textContent = city;
        document.getElementById('dropdown-city').classList.remove('disabled');

        document.querySelectorAll('.address-card').forEach(card => card.classList.remove('selected'));
        element.classList.add('selected');
    }

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

    // ---- رویداد کلیک روی کارت‌های آدرس برای پر کردن فرم ----
    document.querySelectorAll('.address-card').forEach(card => {
        card.addEventListener('click', () => {
            fillFormWithAddress(card);
        });
    });

    // ---- دریافت داده‌های حمل و نقل ----
    fetchShippingDataAndUpdateUI();

    // ---- تغییر متد ارسال ----
    document.querySelectorAll('input[name="shipping_method"]').forEach(radio => {
        radio.addEventListener('change', function () {
            const selectedMethod = this.value;

            fetch("/cart/set-shipping-method/", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: new URLSearchParams({method: selectedMethod}),
            })
                .then(res => res.json())
                .then(data => {
                    if (data.status === 'ok') {
                        setShippingMethodRadio(data.shipping_method);
                        updateFreeShippingMessage(data.send_free, data.shipping_method);
                        updateShippingAndTotal(data.shipping_cost, data.final_price, data.shipping_method);
                    }
                });
        });
    });

    // ---- ایجاد گزینه‌های استان و شهر ----
    const provinceDrop = document.getElementById('dropdown-province');
    const cityDrop = document.getElementById('dropdown-city');
    const inputProvince = document.getElementById('input-province');
    const inputCity = document.getElementById('input-city');

    const createOptions = (wrapper, options, inputField, callback) => {
        if (!wrapper) return;

        const list = wrapper.querySelector('.dropdown-options');
        const display = wrapper.querySelector('.dropdown-selected');

        if (!list || !display || !inputField) return;

        list.innerHTML = '';
        options.forEach(opt => {
            const li = document.createElement('li');
            li.textContent = opt;
            li.addEventListener('click', () => {
                display.textContent = opt;
                inputField.value = opt;
                wrapper.classList.remove('open');
                if (callback) callback(opt);
            });
            list.appendChild(li);
        });
    };

    fetch('/static/json/provinces_cities.json')
        .then(res => res.json())
        .then(data => {
            const provinces = data.map(p => p.name);
            createOptions(provinceDrop, provinces, inputProvince, selectedProvince => {
                const selected = data.find(p => p.name === selectedProvince);
                if (selected?.Cities?.length) {
                    const cities = selected.Cities.map(c => c.name);
                    createOptions(cityDrop, cities, inputCity);
                    cityDrop.classList.remove('disabled');
                    cityDrop.querySelector('.dropdown-selected').textContent = 'انتخاب شهر';
                    inputCity.value = '';
                }
            });
        });

    // ---- منوی کشویی سفارشی ----
    document.querySelectorAll('.custom-dropdown').forEach(drop => {
        const selected = drop.querySelector('.dropdown-selected');
        selected.addEventListener('click', () => {
            document.querySelectorAll('.custom-dropdown').forEach(d => {
                if (d !== drop) d.classList.remove('open');
            });
            drop.classList.toggle('open');
        });
    });

    document.addEventListener('click', e => {
        if (!e.target.closest('.custom-dropdown')) {
            document.querySelectorAll('.custom-dropdown').forEach(d => d.classList.remove('open'));
        }
    });

    // ---- اعتبارسنجی فرم استان/شهر ----
    const form = document.getElementById('address-form');
    if (form && inputProvince && inputCity) {
        form.addEventListener('submit', function (e) {
            let hasError = false;

            const provinceVal = inputProvince.value.trim();
            const cityVal = inputCity.value.trim();
            const provinceError = document.getElementById("error-province");
            const cityError = document.getElementById("error-city");

            if (!provinceVal) {
                e.preventDefault();
                provinceDrop.classList.add('error');
                provinceError.textContent = "لطفاً استان را انتخاب کنید.";
                provinceError.style.display = "block";
                hasError = true;
            } else {
                provinceError.style.display = "none";
                provinceDrop.classList.remove('error');
            }

            if (!cityVal) {
                e.preventDefault();
                cityDrop.classList.add('error');
                cityError.textContent = "لطفاً شهر را انتخاب کنید.";
                cityError.style.display = "block";
                hasError = true;
            } else {
                cityError.style.display = "none";
                cityDrop.classList.remove('error');
            }
        });
    }
});