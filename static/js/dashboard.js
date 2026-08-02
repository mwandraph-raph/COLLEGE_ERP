document.addEventListener("DOMContentLoaded", function () {

    console.log("Dashboard Loaded");

    // ==========================================
    // Admissions Trend
    // ==========================================

    const admissionsCanvas = document.getElementById("admissionsChart");

    if (admissionsCanvas) {

        const labels = JSON.parse(admissionsCanvas.dataset.labels || "[]");
        const values = JSON.parse(admissionsCanvas.dataset.values || "[]");

        new Chart(admissionsCanvas, {

            type: "bar",

            data: {

                labels: labels,

                datasets: [{

                    label: "Admissions",

                    data: values,

                    backgroundColor: [
                        "#2563eb",
                        "#3b82f6",
                        "#60a5fa",
                        "#93c5fd",
                        "#bfdbfe",
                        "#1d4ed8",
                        "#0284c7",
                        "#0ea5e9"
                    ],

                    borderRadius: 8,
                    borderSkipped: false,
                    maxBarThickness: 45

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

                        backgroundColor: "#111827",

                        titleColor: "#fff",

                        bodyColor: "#fff",

                        padding: 12

                    }

                },

                scales: {

                    x: {

                        grid: {
                            display: false
                        },

                        ticks: {

                            color: "#555"

                        }

                    },

                    y: {

                        beginAtZero: true,

                        ticks: {

                            precision: 0,

                            color: "#555"

                        }

                    }

                }

            }

        });

    }


    // ==========================================
    // Student Distribution
    // ==========================================

    const studentCanvas = document.getElementById("studentChart");

    if (studentCanvas) {

        const labels = JSON.parse(studentCanvas.dataset.labels || "[]");
        const values = JSON.parse(studentCanvas.dataset.values || "[]");

        new Chart(studentCanvas, {

            type: "doughnut",

            data: {

                labels: labels,

                datasets: [{

                    data: values,

                    backgroundColor: [

                        "#2563eb",
                        "#10b981",
                        "#f59e0b",
                        "#ef4444",
                        "#8b5cf6",
                        "#06b6d4",
                        "#84cc16",
                        "#ec4899",
                        "#f97316",
                        "#6366f1"

                    ],

                    borderWidth: 2,

                    borderColor: "#ffffff"

                }]

            },

            options: {

                responsive: true,

                maintainAspectRatio: false,

                cutout: "60%",

                animation: {

                    animateRotate: true,

                    duration: 1200

                },

                plugins: {

                    legend: {

                        position: "bottom",

                        labels: {

                            padding: 20,

                            usePointStyle: true

                        }

                    }

                }

            }

        });

    }

/*=========================================================
    STUDENT ACADEMIC ANALYTICS
=========================================================*/

const analyticsChart = document.getElementById("studentAnalyticsChart");

if (analyticsChart) {

    const registered = parseInt(
        analyticsChart.dataset.registered || 0
    );

    const total = parseInt(
        analyticsChart.dataset.total || 8
    );

    new Chart(analyticsChart, {

        type: "doughnut",

        data: {

            labels: [

                "Registered Units",

                "Remaining Units"

            ],

            datasets: [{

                data: [

                    registered,

                    Math.max(total - registered, 0)

                ],

                backgroundColor: [

                    "#2563eb",

                    "#e2e8f0"

                ],

                borderColor: "#ffffff",

                borderWidth: 2

            }]

        },

        options: {

            responsive: true,

            maintainAspectRatio: false,

            cutout: "70%",

            plugins: {

                legend: {

                    position: "bottom",

                    labels: {

                        usePointStyle: true,

                        padding: 20

                    }

                }

            }

        }

    });

}

});