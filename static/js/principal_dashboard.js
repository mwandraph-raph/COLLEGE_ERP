document.addEventListener("DOMContentLoaded", function () {

    if (typeof Chart === "undefined") {
        console.error("Chart.js is not loaded.");
        return;
    }

    function getChartData(canvas) {
        if (!canvas) {
            return {
                labels: [],
                values: []
            };
        }

        let labels = [];
        let values = [];

        try {
            labels = JSON.parse(canvas.dataset.labels || "[]");
            values = JSON.parse(canvas.dataset.values || "[]");
        } catch (error) {
            console.error("Unable to parse chart data:", error);
        }

        return {
            labels: labels,
            values: values
        };
    }


    /* =========================================================
       ADMISSIONS
    ========================================================= */

    const admissionsCanvas =
        document.getElementById("principalAdmissionsChart");

    if (admissionsCanvas) {

        const chartData = getChartData(admissionsCanvas);

        new Chart(admissionsCanvas, {
            type: "doughnut",

            data: {
                labels: chartData.labels,

                datasets: [{
                    data: chartData.values,
                    borderWidth: 0
                }]
            },

            options: {
                responsive: true,
                maintainAspectRatio: false,

                cutout: "68%",

                plugins: {
                    legend: {
                        position: "bottom",

                        labels: {
                            usePointStyle: true,
                            padding: 18
                        }
                    }
                }
            }
        });
    }


    /* =========================================================
       EXAMINATION WORKFLOW
    ========================================================= */

    const resultsCanvas =
        document.getElementById("principalResultsChart");

    if (resultsCanvas) {

        const chartData = getChartData(resultsCanvas);

        new Chart(resultsCanvas, {
            type: "bar",

            data: {
                labels: chartData.labels,

                datasets: [{
                    label: "Result Batches",

                    data: chartData.values,

                    borderRadius: 8,

                    borderWidth: 0
                }]
            },

            options: {
                responsive: true,
                maintainAspectRatio: false,

                scales: {

                    y: {
                        beginAtZero: true,

                        ticks: {
                            precision: 0
                        }
                    },

                    x: {
                        grid: {
                            display: false
                        }
                    }
                },

                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }


    /* =========================================================
       ENROLMENT BY PROGRAMME
    ========================================================= */

    const enrollmentCanvas =
        document.getElementById("principalEnrollmentChart");

    if (enrollmentCanvas) {

        const chartData = getChartData(enrollmentCanvas);

        new Chart(enrollmentCanvas, {
            type: "bar",

            data: {
                labels: chartData.labels,

                datasets: [{
                    label: "Students",

                    data: chartData.values,

                    borderRadius: 8,

                    borderWidth: 0
                }]
            },

            options: {
                responsive: true,
                maintainAspectRatio: false,

                scales: {

                    y: {
                        beginAtZero: true,

                        ticks: {
                            precision: 0
                        }
                    },

                    x: {
                        grid: {
                            display: false
                        },

                        ticks: {
                            autoSkip: false
                        }
                    }
                },

                plugins: {

                    legend: {
                        display: false
                    },

                    tooltip: {
                        callbacks: {

                            label: function (context) {
                                return " Students: " + context.raw;
                            }
                        }
                    }
                }
            }
        });
    }


    /* =========================================================
       EXAMINATION PERFORMANCE BY PROGRAMME
    ========================================================= */

    const examCanvas =
        document.getElementById("principalExamChart");

    if (examCanvas) {

        const chartData = getChartData(examCanvas);

        new Chart(examCanvas, {
            type: "bar",

            data: {
                labels: chartData.labels,

                datasets: [{
                    label: "Pass Rate (%)",

                    data: chartData.values,

                    borderRadius: 8,

                    borderWidth: 0
                }]
            },

            options: {
                responsive: true,
                maintainAspectRatio: false,

                scales: {

                    y: {
                        beginAtZero: true,

                        max: 100,

                        ticks: {
                            callback: function (value) {
                                return value + "%";
                            }
                        }
                    },

                    x: {
                        grid: {
                            display: false
                        },

                        ticks: {
                            autoSkip: false
                        }
                    }
                },

                plugins: {

                    legend: {
                        display: false
                    },

                    tooltip: {
                        callbacks: {

                            label: function (context) {
                                return " Pass Rate: "
                                    + context.raw
                                    + "%";
                            }
                        }
                    }
                }
            }
        });
    }

});