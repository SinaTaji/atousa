function openDrawer(type) {
    document.getElementById("overlay").classList.add("active");
    closeDrawer(); // بستن قبلی‌ها
    document.getElementById("drawer-" + type).classList.add("active");
}

function closeDrawer() {
    document.getElementById("overlay").classList.remove("active");
    document.querySelectorAll(".drawer").forEach(d => d.classList.remove("active"));
}

document.addEventListener("DOMContentLoaded", function () {
    const header = document.getElementById("header");
    const bar = document.getElementById("mobile-filter-bar");

    let lastScrollHeader = 0;
    let lastScrollBar = 0;

    function handleScroll() {
        const currentScroll = window.scrollY;

        if (window.innerWidth <= 768) {
            if (currentScroll > lastScrollHeader && currentScroll > 50) {
                header.style.transform = "translateY(-100%)";
            } else {
                header.style.transform = "translateY(0)";
            }
            lastScrollHeader = currentScroll;

            if (currentScroll > lastScrollBar) {
                bar.style.top = "0px";
            } else {
                bar.style.top = "65px";
            }
            lastScrollBar = currentScroll;
        } else {
            header.style.transform = "translateY(0)";
        }
    }

    window.addEventListener("scroll", handleScroll);

    window.addEventListener("resize", () => {
        if (window.innerWidth > 768) {
            header.style.transform = "translateY(0)";
            bar.style.top = "";
        }
    });
    const mobileDrawer = document.querySelector(".drawer-body.mobile");
    if (mobileDrawer) {
        mobileDrawer.addEventListener("click", function (e) {
            if (e.target.classList.contains("category-link")) {
                e.preventDefault();
                const categorySlug = e.target.dataset.slug;

                fetch(`/article/ajax/${categorySlug}/`)
                    .then(res => res.json())
                    .then(data => {
                        const container = document.getElementById("articleContainer");
                        if (container) {
                            container.innerHTML = data.html;
                        }
                        closeDrawer(); // بستن دراور بعد از کلیک
                    })
                    .catch(err => {
                        console.error("خطا در فیلتر مقالات (موبایل):", err);
                    });
            }
        });
    }
    const sidebar = document.querySelector(".sidebar");
    if (sidebar) {
        sidebar.addEventListener("click", function (e) {
            if (e.target.classList.contains("category-link")) {
                e.preventDefault();
                const categorySlug = e.target.dataset.slug;

                fetch(`/article/ajax/${categorySlug}/`)
                    .then(res => res.json())
                    .then(data => {
                        const container = document.getElementById("articleContainer");
                        if (container) {
                            container.innerHTML = data.html;
                        }
                    })
                    .catch(err => {
                        console.error("خطا در فیلتر مقالات:", err);
                    });
            }
        });

    }
});
