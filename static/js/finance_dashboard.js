document.addEventListener("DOMContentLoaded", function () {

    // ==========================================================
    // FINANCE DASHBOARD CHARTS
    // XORADEX EDUCORE
    // ==========================================================

    /*
     * Safely read JSON stored inside data attributes.
     */
    function readChartData(canvas, attribute) {

        if (!canvas) {
            return [];
        }

        const raw = canvas.dataset[attribute];

        if (!raw) {
            return [];
        }

        try {
            return JSON.parse(raw);
        } catch (error) {
            console.error(
                "Finance chart JSON error:",
                attribute,
                raw,
                error
            );

            return [];
        }
    }


    // ==========================================================
    // 01. REVENUE TREND
    // ==========================================================

    const revenueCanvas = document.getElementById(
        "financeRevenueChart"
    );

    if (revenueCanvas) {

        const labels = readChartData(
            revenueCanvas,
            "labels"
        );

        const values = readChartData(
            revenueCanvas,
            "values"
        );

        console.log(
            "Finance Revenue Chart:",
            labels,
            values
        );

        if (
            typeof Chart !== "undefined" &&
            labels.length &&
            values.length
        ) {

            new Chart(
                revenueCanvas,
                {
                    type: "bar",

                    data: {
                        labels: labels,

                        datasets: [
                            {
                                label: "Collections (KSh)",

                                data: values,

                                backgroundColor:
                                    "rgba(15, 118, 110, 0.85)",

                                hoverBackgroundColor:
                                    "#0f766e",

                                borderRadius: 10,

                                borderSkipped: false,

                                maxBarThickness: 42,
                            }
                        ],
                    },

                    options: {

                        responsive: true,

                        maintainAspectRatio: false,

                        animation: {
                            duration: 1000,
                        },

                        plugins: {

                            legend: {
                                display: false,
                            },

                            tooltip: {

                                backgroundColor: "#0f172a",

                                titleColor: "#ffffff",

                                bodyColor: "#ffffff",

                                padding: 12,

                                callbacks: {

                                    label: function (context) {

                                        return (
                                            " KSh " +
                                            Number(
                                                context.parsed.y || 0
                                            ).toLocaleString()
                                        );

                                    },

                                },

                            },

                        },

                        scales: {

                            x: {

                                grid: {
                                    display: false,
                                },

                                ticks: {
                                    color: "#64748b",
                                },

                            },

                            y: {

                                beginAtZero: true,

                                grid: {
                                    color: "#eef2f7",
                                },

                                ticks: {

                                    color: "#64748b",

                                    callback: function (value) {

                                        return Number(
                                            value
                                        ).toLocaleString();

                                    },

                                },

                            },

                        },

                    },

                }
            );

        } else {

            console.warn(
                "Revenue chart has no usable data."
            );

        }

    }


    // ==========================================================
    // 02. PAYMENT METHODS
    // ==========================================================

   const canvas = document.getElementById("financeCategoryChart");

if (canvas) {
    const mpesa = parseFloat(canvas.dataset.mpesa) || 0;
    const bank = parseFloat(canvas.dataset.bank) || 0;
    const cash = parseFloat(canvas.dataset.cash) || 0;

    new Chart(canvas, {
        type: "doughnut",

        data: {
            labels: ["M-Pesa", "Bank", "Cash"],

            datasets: [{
            data: [mpesa, bank, cash],

            backgroundColor: [
                "#16A34A",  // M-Pesa
                "#2563EB",  // Bank
                "#F59E0B"   // Cash
            ],

            hoverBackgroundColor: [
                "#15803D",
                "#1D4ED8",
                "#D97706"
            ],

            borderColor: "#FFFFFF",

            borderWidth: 4,

            hoverOffset: 8
        }]
        },

        options: {
        responsive: true,
        maintainAspectRatio: false,

        cutout: "58%",

        plugins: {
            legend: {
                display: true,
                position: "bottom",

                labels: {
                    usePointStyle: true,
                    pointStyle: "circle",
                    padding: 18,

                    font: {
                        size: 12,
                        weight: "600"
                    }
                }
            },

            tooltip: {
                callbacks: {
                    label: function(context) {

                        return context.label + ": KSh " +
                            Number(context.raw).toLocaleString(
                                "en-KE",
                                {
                                    minimumFractionDigits: 2,
                                    maximumFractionDigits: 2
                                }
                            );
                    }
                }
            }
        }
    }
    });
}

    // ==========================================================
    // 03. CHART.JS CHECK
    // ==========================================================

    if (typeof Chart === "undefined") {

        console.error(
            "Chart.js is NOT loaded. Finance charts cannot render."
        );

    }

});