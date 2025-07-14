document.addEventListener('DOMContentLoaded', function () {

    // گرفتن داده‌ها با بررسی وجود عنصر
    const getJSON = id => {
        const el = document.getElementById(id);
        return el ? JSON.parse(el.textContent) : [];
    };

    const labels = getJSON('chart-labels');
    const sales = getJSON('chart-sales');
    const commission = getJSON('chart-commission');

    // بررسی هماهنگی طول داده‌ها
    if (!(labels.length === sales.length && sales.length === commission.length)) {
        console.warn('طول داده‌های نمودار هماهنگ نیست');
        return;
    }

    const ctx = document.getElementById('monthlyChart')?.getContext('2d');
    if (!ctx) return;

    new Chart(ctx, {
        data: {
            labels,
            datasets: [
                {
                    type: 'line',
                    label: 'تعداد فروش',
                    data: sales,
                    borderColor: 'rgb(0,0,0)',
                    backgroundColor: 'rgba(101,101,101,0.2)',
                    fill: false,
                    tension: 0.3,
                    yAxisID: 'y',
                    pointRadius: 4,
                    pointHoverRadius: 6,
                },
                {
                    type: 'line',
                    label: 'پورسانت ماهانه (تومان)',
                    data: commission,
                    borderColor: 'rgb(255,175,0)',
                    backgroundColor: 'rgba(255,211,99,0.4)',
                    fill: true,
                    tension: 0.3,
                    yAxisID: 'y1',
                    pointRadius: 0,
                    pointHoverRadius: 6,
                }
            ]
        },
        options: {
            responsive: true,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            stacked: false,
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    beginAtZero: true,
                    ticks: {font: {size: 13}}
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    beginAtZero: true,
                    grid: {drawOnChartArea: false},
                    ticks: {font: {size: 13}}
                },
                x: {
                    ticks: {
                        maxRotation: 45,
                        minRotation: 20,
                        autoSkip: false,
                        font: {size: 13}
                    }
                }
            },
            plugins: {
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: context =>
                            `${context.dataset.label}: ${context.parsed.y.toLocaleString()}`
                    }
                },
                legend: {
                    labels: {
                        font: {size: 14}
                    }
                }
            }
        }
    });

    // انیمیشن نوار پیشرفت
    const fills = document.querySelectorAll('.progress-fill');

    fills.forEach(fill => {
        const targetWidth = parseFloat(fill.dataset.width);
        if (isNaN(targetWidth)) return;

        fill.style.width = '0%';

        const duration = 500; // زمان کلی انیمیشن (ms)
        const frameRate = 30; // فریم بر ثانیه
        const totalSteps = duration / (1000 / frameRate);
        const step = targetWidth / totalSteps;

        let width = 0;
        const interval = setInterval(() => {
            width += step;
            if (width >= targetWidth) {
                width = targetWidth;
                clearInterval(interval);

                const tick = fill.querySelector('.tick-mark');
                if (tick) tick.style.opacity = '1';
            }
            fill.style.width = width.toFixed(1) + '%';
        }, 1000 / frameRate);
    });

});