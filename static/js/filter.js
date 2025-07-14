let selectedCategory = null;
let totalPages = 1;
let currentPage = 1;

function openDrawer(type) {
    document.getElementById("overlay").classList.add("active");
    closeDrawer(); // بستن قبلی‌ها

    document.getElementById("drawer-" + type).classList.add("active");
}

function closeDrawer() {
    document.getElementById("overlay").classList.remove("active");
    document.querySelectorAll(".drawer").forEach(d => d.classList.remove("active"));
}

const header = document.getElementById("header");
const bar = document.getElementById("mobile-filter-bar");

let lastScrollHeader = 0;
let lastScrollBar = 0;

function handleScroll() {
    const currentScroll = window.scrollY;

    // برای هدر
    if (window.innerWidth <= 768) {
        if (currentScroll > lastScrollHeader && currentScroll > 50) {
            header.style.transform = "translateY(-100%)";
        } else {
            header.style.transform = "translateY(0)";
        }
        lastScrollHeader = currentScroll;
    } else {
        header.style.transform = "translateY(0)";
    }

    // برای نوار فیلتر
    if (window.innerWidth <= 768) {
        if (currentScroll > lastScrollBar) {
            bar.style.top = "0px";
        } else {
            bar.style.top = "65px";
        }
        lastScrollBar = currentScroll;
    }
}

window.addEventListener("scroll", handleScroll);

window.addEventListener("resize", () => {
    if (window.innerWidth > 768) {
        header.style.transform = "translateY(0)";
        bar.style.top = "";
    }
});

const form = document.getElementById('filter-form');
const clearFiltersBtn = document.getElementById('clear-filters');
document.querySelectorAll('.filter-input').forEach(input => {
    input.addEventListener('change', () => {
        const formData = new FormData(document.getElementById('filter-form'));
        const filters = Object.fromEntries(formData.entries());
        updateProducts(filters);
    });
});

const wrapper = document.getElementById('product_wrapper');
if (wrapper) {
    const cards = wrapper.querySelectorAll('.product-card');
    const noProduct = wrapper.querySelector('.no-product');
    if (cards.length === 0 && noProduct) {
        wrapper.classList.remove("product-grid");
        wrapper.style.display = "flex";
        wrapper.style.flexDirection = "column";
        wrapper.style.alignItems = "center";
        wrapper.style.justifyContent = "center";
    }
}

function updatePriceDisplay() {
    // دسکتاپ
    const min = document.getElementById('price_min');
    const max = document.getElementById('price_max');
    const minVal = document.getElementById('price_min_val');
    const maxVal = document.getElementById('price_max_val');

    if (min && minVal) minVal.textContent = Number(min.value || 0).toLocaleString();
    if (max && maxVal) maxVal.textContent = Number(max.value || 0).toLocaleString();

    // موبایل
    const minMobile = document.getElementById('price_min_mobile');
    const maxMobile = document.getElementById('price_max_mobile');
    const minValMobile = document.getElementById('price_min_val_mobile');
    const maxValMobile = document.getElementById('price_max_val_mobile');

    if (minMobile && minValMobile) minValMobile.textContent = Number(minMobile.value || 0).toLocaleString();
    if (maxMobile && maxValMobile) maxValMobile.textContent = Number(maxMobile.value || 0).toLocaleString();
}


function checkActiveFilters(filters) {
    const clearFiltersBtn = document.getElementById('clear-filters');
    if (!clearFiltersBtn) return;  // اگر وجود نداشت، ادامه نده

    // فقط پارامترهایی که واقعا فیلتر هستند رو چک کن، exclude page و ordering
    const hasActive = Object.entries(filters).some(([key, value]) => {
        if (key === 'page' || key === 'ordering') return false;
        if (Array.isArray(value)) return value.some(v => v && v !== 'all');
        return value && value !== 'all';
    });

    clearFiltersBtn.style.display = hasActive ? 'inline-block' : 'none';
}

function updateURL(filters, replace = false) {
    const url = new URL(window.location);
    const params = new URLSearchParams();

    for (const key in filters) {
        // حذف فیلترهای خاص از URL
        if (['price_min', 'price_max', 'page'].includes(key)) continue;

        const val = filters[key];

        if (Array.isArray(val)) {
            val.forEach(v => {
                if (v && v !== 'all') params.append(key, v);
            });
        } else {
            if (val && val !== 'all') params.set(key, val);
        }
    }

    url.search = params.toString();
    url.hash = '';

    if (replace) {
        history.replaceState(filters, '', url.toString());
    } else {
        history.pushState(filters, '', url.toString());
    }
}

function getFiltersFromForm() {
    let form = document.getElementById('filter-form');
    const mobileForm = document.getElementById('filter-form-mobile');
    if (window.innerWidth <= 768 && mobileForm) {
        form = mobileForm;
    }

    if (!form || !(form instanceof HTMLFormElement)) {
        return {};
    }

    const formData = new FormData(form);
    const filters = {};

    for (const [key, value] of formData.entries()) {
        if (filters[key]) {
            filters[key] = Array.isArray(filters[key]) ? [...filters[key], value] : [filters[key], value];
        } else {
            filters[key] = value;
        }
    }

    if (typeof selectedCategory !== 'undefined' && selectedCategory) {
        filters['category'] = selectedCategory;
    }

    const searchInput = document.getElementById('searchInput');
    if (searchInput && searchInput.value.trim() !== '') {
        filters['q'] = searchInput.value.trim();
    }

    const orderingInput = document.getElementById('orderingInput');
    if (orderingInput && orderingInput.value) {
        filters['ordering'] = orderingInput.value;
    } else {
        const urlParams = new URLSearchParams(window.location.search);
        const orderingFromURL = urlParams.get('ordering');
        if (orderingFromURL) {
            filters['ordering'] = orderingFromURL;
        }
    }

    // *** اینجا اضافه می‌کنیم مقادیر موبایل اگر فرم موبایل فعال است ***
    if (window.innerWidth <= 768 && mobileForm) {
        const colorMobile = document.getElementById('colorInputMobile');
        if (colorMobile && colorMobile.value) {
            filters.color = colorMobile.value;
        }

        const genderMobile = document.getElementById('genderInputMobile');
        if (genderMobile && genderMobile.value) {
            filters.gender = genderMobile.value;
        }

        const sizeCheckboxesMobile = mobileForm.querySelectorAll('input[type=checkbox][name=size]:checked');
        if (sizeCheckboxesMobile.length) {
            filters.size = Array.from(sizeCheckboxesMobile).map(chk => chk.value);
        }
    }

    // حذف فیلترهای بی‌مقدار
    for (const key in filters) {
        const val = filters[key];
        if (
            key !== 'page' &&
            (val === '' || val === 'all' || (Array.isArray(val) && val.every(v => v === '' || v === 'all')))
        ) {
            delete filters[key];
        }
    }

    return filters;
}

function getFiltersFromURL() {
    const params = new URLSearchParams(window.location.search);
    const filters = {};

    for (const [key, value] of params.entries()) {
        if (!filters[key]) {
            filters[key] = [];
        }
        filters[key].push(value);
    }

    if (filters.page) delete filters.page;

    return filters;
}

function setFiltersToForm(filters) {
    const desktopForm = document.getElementById('filter-form');
    const mobileForm = document.getElementById('filter-form-mobile');

    // دسکتاپ
    if (desktopForm) {
        for (const key in filters) {
            const inputs = desktopForm.querySelectorAll(`input[name="${key}"]`);

            if (inputs.length > 0) {
                const values = Array.isArray(filters[key]) ? filters[key] : [filters[key]];

                inputs.forEach(input => {
                    input.checked = values.includes(input.value);
                });

                continue;
            }

            const el = desktopForm.elements[key];
            if (!el) continue;

            el.value = filters[key];
        }

        // انتخاب رنگ دسکتاپ
        if (filters.color && document.getElementById('colorInput')) {
            const colorInput = document.getElementById('colorInput');
            const selected = document.querySelector('#colorSelect .selected-option');
            const match = document.querySelector(`.option-item[data-value="${filters.color}"]`);
            colorInput.value = filters.color;
            if (selected) {
                if (filters.color === 'all') {
                    selected.textContent = 'نمایش همه';
                    selected.style.backgroundColor = 'transparent';
                } else if (match) {
                    selected.textContent = '';
                    selected.style.backgroundColor = match.style.backgroundColor;
                }
            }
        }

        // جنسیت دسکتاپ
        if (filters.gender) selectGender(filters.gender);
    }

    // موبایل
    if (mobileForm) {
        // رنگ موبایل
        if (filters.color) {
            const colorInputMobile = document.getElementById('colorInputMobile');
            if (colorInputMobile) colorInputMobile.value = filters.color;
        }

        // جنسیت موبایل
        if (filters.gender) {
            const genderInputMobile = document.getElementById('genderInputMobile');
            if (genderInputMobile) genderInputMobile.value = filters.gender;
        }

        // سایز موبایل
        if (filters.size && Array.isArray(filters.size)) {
            mobileForm.querySelectorAll('input[type=checkbox][name=size]').forEach(input => {
                input.checked = filters.size.includes(input.value);
            });
        } else if (filters.size) {
            // اگر فقط یک مقدار بود
            mobileForm.querySelectorAll('input[type=checkbox][name=size]').forEach(input => {
                input.checked = input.value === filters.size;
            });
        }
    }

    // مرتب‌سازی
    if (filters.ordering && document.getElementById('orderingInput')) {
        document.getElementById('orderingInput').value = filters.ordering;

        document.querySelectorAll('.sort-btn').forEach(btn => {
            btn.classList.remove('active');
            if (btn.dataset.ordering === filters.ordering) {
                btn.classList.add('active');
            }
        });
    }

    // دسته‌بندی
    if (filters.category) selectedCategory = filters.category;
}

function updateProducts(filters) {
    const queryObj = {...filters};


    if (queryObj.price_min) {
        queryObj.price__gt = queryObj.price_min;
        delete queryObj.price_min;
    }
    if (queryObj.price_max) {
        queryObj.price__lt = queryObj.price_max;
        delete queryObj.price_max;
    }

    const query = new URLSearchParams(queryObj).toString();

    fetch(`/product/ajax/filter-products/?${query}`)
        .then(res => {
            if (!res.ok) throw new Error('خطا در دریافت اطلاعات محصولات');
            return res.json();
        })
        .then(data => {
            const list = document.getElementById('product-list');
            if (!list) return;

            list.innerHTML = data.html || '';
            totalPages = data.total_pages || 1;
            currentPage = data.current_page || 1;

            updatePagination(currentPage);
        })
        .catch(err => {
            console.error(err);
        });
}

function updatePagination(current) {
    currentPage = current;
    const container = document.querySelector('.pagination');
    if (!container) return;

    container.innerHTML = '';

    if (totalPages <= 1) {
        container.style.display = 'none';
        return;
    }

    container.style.display = 'flex';

    function makePage(page, label = page, disabled = false, active = false) {
        const li = document.createElement('li');
        li.className = `page-item${active ? ' active' : ''}`;
        li.innerHTML = `<a href="#" class="page-link" data-page="${page}">${label}</a>`;
        return li;
    }

    // صفحه قبلی (اگر صفحه 1 بود، باز هم فعال هست ولی شماره صفحه 0 نداریم، برای ایمنی محدود می‌کنیم)
    container.appendChild(makePage(Math.max(1, current - 1), '«'));

    const start = Math.max(1, current - 2);
    const end = Math.min(totalPages, current + 2);

    for (let i = start; i <= end; i++) {
        container.appendChild(makePage(i, i, false, i === current));
    }

    // صفحه بعدی (اگر صفحه آخر بود، باز هم فعال هست ولی شماره صفحه بزرگتر از totalPages نداریم)
    container.appendChild(makePage(Math.min(totalPages, current + 1), '»'));
}

function triggerFilter(page = 1, pushState = true) {
    const filters = getFiltersFromForm();
    filters.page = page;

    checkActiveFilters(filters);
    updateProducts(filters);

    if (pushState) {
        const filtersForURL = {...filters};

        // حذف تمام فیلترهای مربوط به قیمت از URL
        delete filtersForURL.price_min;
        delete filtersForURL.price_max;
        delete filtersForURL.price__gt;
        delete filtersForURL.price__lt;

        updateURL(filtersForURL);
    }
}

document.addEventListener('DOMContentLoaded', function () {
    const clearFiltersBtn = document.getElementById('clear-filters');

    if (clearFiltersBtn) {
        clearFiltersBtn.addEventListener('click', e => {
            e.preventDefault();

            form.reset();
            selectedCategory = null;

            const genderInput = document.getElementById('gender-input');
            if (genderInput) genderInput.value = '';

            const colorInput = document.getElementById('colorInput');
            if (colorInput) colorInput.value = 'all';

            document.querySelectorAll('.active').forEach(el => el.classList.remove('active'));

            const selectedColor = document.querySelector('#colorSelect .selected-option');
            if (selectedColor) {
                selectedColor.textContent = 'نمایش همه';
                selectedColor.style.backgroundColor = 'transparent';
            }

            triggerFilter();
        });
    }
});

['price_min', 'price_max', 'price_min_mobile', 'price_max_mobile'].forEach(id => {
    const input = document.getElementById(id);
    if (input) {
        input.addEventListener('input', () => {
            updatePriceDisplay();
            triggerFilter();
        });
    }
});

const colorSelect = document.getElementById('colorSelect');
if (colorSelect) {
    const selected = colorSelect.querySelector('.selected-option');
    const list = colorSelect.querySelector('.options-list');
    const input = document.getElementById('colorInput');

    selected.addEventListener('click', e => {
        e.stopPropagation();
        list.style.display = (list.style.display === 'block') ? 'none' : 'block';
    });

    list.querySelectorAll('.option-item').forEach(option => {
        option.addEventListener('click', () => {
            const val = option.dataset.value;
            if (val === 'all') {
                selected.textContent = 'نمایش همه';
                selected.style.backgroundColor = 'transparent';
            } else {
                selected.textContent = '';
                selected.style.backgroundColor = option.style.backgroundColor;
            }
            input.value = val;
            list.style.display = 'none';
            triggerFilter();
        });
    });

    document.addEventListener('click', () => {
        list.style.display = 'none';
    });
}

const genderInput = document.getElementById('gender-input');
if (genderInput) {
    genderInput.addEventListener('change', () => {
        triggerFilter();
    });
}

document.querySelectorAll('.gender-item').forEach(item => {
    item.addEventListener('click', () => {
        const gender = item.dataset.value;
        selectGender(gender);
        // اینجا نباید دوباره event listener اضافه کنیم
    });
});

document.addEventListener('DOMContentLoaded', () => {
    const filters = getFiltersFromURL();

    const {page, ...realFilters} = filters;

    setFiltersToForm(realFilters);
    updatePriceDisplay();


    const hasFilter = Object.keys(realFilters).length > 0;
    if (!hasFilter) {
        updateURL({}, true);
    } else {
        updateURL(filters, true);
    }

    triggerFilter(page ? parseInt(page) : 1, false);


    const sortMenu = document.querySelector('.sort-menu');
    if (sortMenu) {
        sortMenu.addEventListener('click', (event) => {
            if (event.target.classList.contains('sort-btn')) {
                const orderingValue = event.target.getAttribute('data-ordering');
                const orderingInput = document.getElementById('orderingInput');
                if (orderingInput) orderingInput.value = orderingValue;

                document.querySelectorAll('.sort-btn').forEach(btn => btn.classList.remove('active'));
                event.target.classList.add('active');

                triggerFilter(1); // صفحه رو ۱ می‌گذاریم چون مرتب‌سازی عوض شده
            }
        });
    }
});
const paginationContainer = document.querySelector('.pagination');
if (paginationContainer) {
    paginationContainer.addEventListener('click', e => {
        e.preventDefault();
        if (e.target.classList.contains('page-link')) {
            const page = parseInt(e.target.dataset.page);
            if (page && page >= 1 && page <= totalPages && page !== currentPage) {
                triggerFilter(page);
                window.scrollTo({top: 0, behavior: 'smooth'});
            }
        }
    });
}

window.addEventListener('popstate', (event) => {
    const state = event.state;
    if (state) {
        setFiltersToForm(state);
        updatePriceDisplay();
        triggerFilter(state.page ? parseInt(state.page) : 1, false);
    } else {
        form.reset();
        selectedCategory = null;
        updatePriceDisplay();
        triggerFilter(1, false);
        updateURL({}, true);
    }
});

document.querySelectorAll('.dropdown-toggle').forEach(btn => {
    btn.addEventListener('click', e => {
        e.stopPropagation();
        const menu = btn.nextElementSibling; // فرض می‌کنیم منو بعد از دکمه است
        if (!menu) return;

        if (menu.style.display === 'block') {
            menu.style.display = 'none';
        } else {
            // اول همه منوها رو ببند
            document.querySelectorAll('.dropdown-menu').forEach(m => m.style.display = 'none');
            // منوی این دکمه رو باز کن
            menu.style.display = 'block';
        }
    });
});

document.addEventListener('click', () => {
    document.querySelectorAll('.dropdown-menu').forEach(m => m.style.display = 'none');
});

document.querySelectorAll('.category-filter').forEach(link => {
    link.addEventListener('click', e => {
        e.preventDefault();
        e.stopPropagation();


        const slug = link.dataset.categorySlug || null;
        selectedCategory = slug;


        triggerFilter(1);


        const dropdownMenu = link.closest('.dropdown-menu');
        if (dropdownMenu) {
            dropdownMenu.style.display = 'none';
        }
    });
});

function selectGender(gender) {
    const input = document.getElementById('gender-input');
    if (input) {
        input.value = gender;
        // ارسال رویداد تغییر دستی به input تا هر جایی که به تغییر این فیلد گوش میده اجرا شود
        input.dispatchEvent(new Event('change'));
    }

    ['boy-btn', 'girl-btn'].forEach(id => {
        const btn = document.getElementById(id);
        if (!btn) return;
        btn.classList.remove('active');
    });

    if (gender === 'boys') {
        const boyBtn = document.getElementById('boy-btn');
        if (boyBtn) boyBtn.classList.add('active');
    } else if (gender === 'girls') {
        const girlBtn = document.getElementById('girl-btn');
        if (girlBtn) girlBtn.classList.add('active');
    }
}

document.addEventListener('click', (e) => {
    const pageLink = e.target.closest('.page-link');
    if (pageLink) {
        e.preventDefault();

        const page = parseInt(pageLink.dataset.page);
        if (!isNaN(page)) {
            triggerFilter(page);
            window.scrollTo({top: 0, behavior: 'smooth'});
        }
    }
});
document.querySelectorAll('#drawer-sort .sort-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const orderingValue = btn.getAttribute('data-ordering');
        const orderingInput = document.getElementById('orderingInput');
        if (orderingInput) {
            orderingInput.value = orderingValue;
        }

        // هایلایت دکمه فعال (اختیاری)
        document.querySelectorAll('#drawer-sort .sort-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        // بستن drawer و اعمال مرتب‌سازی
        closeDrawer();
        triggerFilter(1);  // صفحه ۱ رو بزن
    });
});

const filterDetail = document.getElementById('filter-detail');
const filterMain = document.getElementById('filter-main');
const drawerTitle = document.getElementById('drawerTitle');
const backBtn = document.getElementById('backBtn');

const filterContents = {
    "دسته بندی‌ها": "filter-category",
    "رنگ‌ها": "filter-color",
    "جنسیت": "filter-gender",
    "قیمت": "filter-price",
    "سایز": "filter-size"
};

let currentFilter = null; // ذخیره فیلتر فعلی برای جلوگیری از رفرش بی‌مورد

document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const filterName = btn.getAttribute('data-filter');

        // اگر فیلتر انتخابی الان باز است، کاری نکن
        if (currentFilter === filterName) {
            return;
        }
        currentFilter = filterName;

        // مخفی کردن همه محتوای فیلترها و حذف کلاس active
        Object.values(filterContents).forEach(id => {
            const el = document.getElementById(id);
            el.classList.remove('active');
            el.style.display = 'none';
        });

        // نمایش محتوای فیلتر انتخاب شده
        const contentId = filterContents[filterName];
        if (contentId) {
            const el = document.getElementById(contentId);
            el.style.display = 'block';
            requestAnimationFrame(() => {
                el.classList.add('active');
            });
        }

        // نمایش و انیمیت صفحه جزئیات
        filterMain.style.display = 'none';

        // اگر صفحه جزئیات قبلاً باز نبود، نمایش و انیمیت کن
        if (!filterDetail.classList.contains('active')) {
            filterDetail.style.display = 'block';
            requestAnimationFrame(() => {
                filterDetail.classList.add('active');
            });
        }

        drawerTitle.textContent = filterName;
        backBtn.style.display = 'inline-block';
    });
});

backBtn.addEventListener('click', () => {
    currentFilter = null;

    // حذف انیمیشن و پنهان کردن صفحه جزئیات
    filterDetail.classList.remove('active');

    // حذف active و مخفی کردن محتواها بعد از اتمام انیمیشن
    Object.values(filterContents).forEach(id => {
        const el = document.getElementById(id);
        el.classList.remove('active');
        el.style.display = 'none';
    });

    filterDetail.addEventListener('transitionend', function handler() {
        filterDetail.style.display = 'none';
        filterDetail.removeEventListener('transitionend', handler);
    });

    filterMain.style.display = 'block';
    drawerTitle.textContent = 'فیلترها';
    backBtn.style.display = 'none';
});

// دکمه لغو فیلتر موبایل
const clearFiltersBtnMobile = document.getElementById('clear-filters-mobile');
const mobileForm = document.getElementById('filter-form-mobile');
if (clearFiltersBtnMobile && mobileForm) {
    clearFiltersBtnMobile.addEventListener('click', e => {
        e.preventDefault();

        mobileForm.reset();

        selectedCategory = null;

        // پاک کردن inputs مخفی موبایل
        const genderInputMobile = document.getElementById('genderInputMobile');
        if (genderInputMobile) genderInputMobile.value = '';

        const colorInputMobile = document.getElementById('colorInputMobile');
        if (colorInputMobile) colorInputMobile.value = '';

        // پاک کردن انتخاب های بصری (اگر لازم است، مثلا رنگ یا دکمه‌ها)

        triggerFilter();
        closeDrawer();
    });
}

// چک‌باکس‌های سایز موبایل
if (mobileForm) {
    mobileForm.querySelectorAll('input[type=checkbox][name=size]').forEach(checkbox => {
        checkbox.addEventListener('change', () => {
            triggerFilter();
        });
    });
}

// تغییر رنگ موبایل - اگر مثل دسکتاپ انتخاب رنگ داری
const colorFilterMobile = document.getElementById('color-filter');
if (colorFilterMobile) {
    colorFilterMobile.querySelectorAll('.option-item').forEach(option => {
        option.addEventListener('click', () => {
            const colorInputMobile = document.getElementById('colorInputMobile');
            if (!colorInputMobile) return;

            const val = option.dataset.value;
            if (val === 'all') {
                // اگر نمایش همه است
                colorInputMobile.value = '';
            } else {
                colorInputMobile.value = val;
            }

            triggerFilter();
        });
    });
}

// جنسیت موبایل - دکمه‌ها
const genderButtonsMobile = document.getElementById('gender-buttons');
if (genderButtonsMobile) {
    genderButtonsMobile.querySelectorAll('button.gender-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const genderInputMobile = document.getElementById('genderInputMobile');
            if (!genderInputMobile) return;

            const gender = btn.textContent.trim().toLowerCase().includes('پسرانه') ? 'boys' : 'girls';
            genderInputMobile.value = gender;

            triggerFilter();
        });
    });
}

// دکمه اعمال فیلتر موبایل
const applyBtnMobile = document.querySelector('.apply-btn');
if (applyBtnMobile) {
    applyBtnMobile.addEventListener('click', () => {
        closeDrawer();
        triggerFilter();
    });
}
document.querySelectorAll('#color-filter .option-item').forEach(item => {
    item.addEventListener('click', () => {
        document.querySelectorAll('#color-filter .option-item').forEach(i => i.classList.remove('active'));
        item.classList.add('active');
        // مقدار به input مخفی هم بده اگر لازم داری
        const colorInput = document.getElementById('colorInputMobile');
        if (colorInput) colorInput.value = item.dataset.value;
    });
});

function selectGenderMobile(gender) {
    document.querySelectorAll('.gender-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    const selectedBtn = document.querySelector(`.gender-btn.${gender === 'boys' ? 'boy' : 'girl'}`);
    if (selectedBtn) {
        selectedBtn.classList.add('active');
    }
}