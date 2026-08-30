document.addEventListener("DOMContentLoaded", function () {

        // ==========================================
        // Revenue Trend (Bar Chart)
        // ==========================================

        const revenueCanvas = document.getElementById("financeRevenueChart");

        if (revenueCanvas) {

            const labels = JSON.parse(revenueCanvas.dataset.labels || "[]");
            const values = JSON.parse(revenueCanvas.dataset.values || "[]");

            new Chart(revenueCanvas, {

                type: "bar",

                data: {

                    labels: labels,

                    datasets: [{

                        label: "Collections (KSh)",

                        data: values,

                        backgroundColor:

                            "rgba(15, 118, 110, 0.85)",

                        hoverBackgroundColor:

                            "#0f766e",

                        borderRadius: 10,

                        borderSkipped: false,

                        maxBarThickness: 42

                    }]

                },

                options: {

                    responsive: true,

                    maintainAspectRatio: false,

                    animation: {

                        duration: 1200

                    },

                    plugins: {

                        legend: {

                            display: false

                        },

                        tooltip: {

                            backgroundColor: "#0f172a",

                            titleColor: "#fff",

                            bodyColor: "#fff",

                            padding: 12,

                            callbacks: {

                                label: function (context) {

                                    return " KSh " + Number(context.parsed.y).toLocaleString();

                                }

                            }

                        }

                    },

                    scales: {

                        x: {

                            grid: { display: false },

                            ticks: { color: "#64748b" }

                        },

                        y: {

                            beginAtZero: true,

                            grid: { color: "#eef2f7" },

                            ticks: {

                                color: "#64748b",

                                callback: function (value) {

                                    return Number(value).toLocaleString();

                                }

                            }

                        }

                    }

                }

            });

        }

        // ==========================================
        // Collections by Category (Doughnut)
        // ==========================================

        const categoryCanvas = document.getElementById("financeCategoryChart");

        if (categoryCanvas) {

            const labels = JSON.parse(categoryCanvas.dataset.labels || "[]");
            const values = JSON.parse(categoryCanvas.dataset.values || "[]");

            if (labels.length && values.length) {

                new Chart(categoryCanvas, {

                    type: "doughnut",

                    data: {

                        labels: labels,

                        datasets: [{

                            data: values,

                            backgroundColor: [

                                "#012169",

                                "#10b981",

                                "#FFC107",

                                "#0ea5e9",

                                "#8b5cf6",

                                "#ef4444",

                                "#06b6d4",

                                "#84cc16"

                            ],

                            borderWidth: 3,

                            borderColor: "#ffffff",

                            hoverOffset: 8

                        }]

                    },

                    options: {

                        responsive: true,

                        maintainAspectRatio: false,

                        cutout: "62%",

                        animation: {

                            animateRotate: true,

                            duration: 1200

                        },

                        plugins: {

                            legend: {

                                position: "bottom",

                                labels: {

                                    padding: 16,

                                    usePointStyle: true,

                                    pointStyle: "circle",

                                    color: "#0f172a"

                                }

                            },

                            tooltip: {

                                backgroundColor: "#0f172a",

                                titleColor: "#fff",

                                bodyColor: "#fff",

                                padding: 12

                            }

                        }

                    }

                });

            } else {

                categoryCanvas.parentElement.innerHTML = `

                    <div class="text-center text-muted py-5">

                        <i class="fa-solid fa-chart-pie fa-3x mb-3"></i>

                        <p class="mb-0">No category data available.</p>

                    </div>

                `;

            }

        }

    });
