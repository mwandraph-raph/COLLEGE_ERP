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
  /* =========================================================
       STICKY FINANCIAL ANALYTICS
    ========================================================= */
    const analyseButton =
        document.getElementById("financeAnalyseBtn");

    const academicYear =
        document.getElementById("financeAcademicYear");

    const semester =
        document.getElementById("financeSemester");

    if (!analyseButton || !academicYear || !semester) {
        return;
    }

    analyseButton.addEventListener("click", function () {

        const yearId = academicYear.value;
        const semesterId = semester.value;

        if (!yearId || !semesterId) {
            return;
        }

        const url = new URL(
            window.location.href
        );

        /*
         * Remove the old period selections.
         */
        url.searchParams.set(
            "academic_year",
            yearId
        );

        url.searchParams.set(
            "semester",
            semesterId
        );

        /*
         * Return directly to Financial Analytics
         * after Django reloads the dashboard.
         */
        window.location.href =
            url.pathname +
            "?" +
            url.searchParams.toString() +
            "#finance-period-performance";

    });

    /* =====================================================
       BILLING VS COLLECTION
    ===================================================== */

    const collectionCanvas =
        document.getElementById(
            "financePeriodCollectionChart"
        );

    if (collectionCanvas && typeof Chart !== "undefined") {

        const labels = JSON.parse(
            collectionCanvas.dataset.labels || "[]"
        );

        const billed = JSON.parse(
            collectionCanvas.dataset.billed || "[]"
        );

        const collected = JSON.parse(
            collectionCanvas.dataset.collected || "[]"
        );

        new Chart(collectionCanvas, {

            type: "bar",

            data: {
                labels: labels,

                datasets: [
                    {
                        label: "Billed",
                        data: billed,

                        borderWidth: 1,
                        borderRadius: 8,

                        barPercentage: 0.65,
                        categoryPercentage: 0.7
                    },

                    {
                        label: "Collected",
                        data: collected,

                        borderWidth: 1,
                        borderRadius: 8,

                        barPercentage: 0.65,
                        categoryPercentage: 0.7
                    }
                ]
            },

            options: {

                responsive: true,

                maintainAspectRatio: false,

                plugins: {

                    legend: {
                        display: true,
                        position: "top"
                    },

                    tooltip: {

                        callbacks: {

                            label: function (context) {

                                return (
                                    context.dataset.label +
                                    ": KSh " +
                                    Number(
                                        context.parsed.y || 0
                                    ).toLocaleString(
                                        "en-KE",
                                        {
                                            minimumFractionDigits: 2,
                                            maximumFractionDigits: 2
                                        }
                                    )
                                );
                            }
                        }
                    }
                },

                scales: {

                    x: {
                        grid: {
                            display: false
                        }
                    },

                    y: {

                        beginAtZero: true,

                        ticks: {

                            callback: function (value) {

                                return (
                                    "KSh " +
                                    Number(value).toLocaleString(
                                        "en-KE"
                                    )
                                );
                            }
                        }
                    }
                }
            }
        });
    }


    /* =====================================================
       COLLECTION RATE
    ===================================================== */

    const rateCanvas =
        document.getElementById(
            "financePeriodRateChart"
        );

    if (rateCanvas && typeof Chart !== "undefined") {

        const labels = JSON.parse(
            rateCanvas.dataset.labels || "[]"
        );

        const rates = JSON.parse(
            rateCanvas.dataset.values || "[]"
        );

        new Chart(rateCanvas, {

            type: "line",

            data: {

                labels: labels,

                datasets: [
                    {
                        label: "Collection Rate",

                        data: rates,

                        fill: true,

                        tension: 0.35,

                        borderWidth: 3,

                        pointRadius: 4,

                        pointHoverRadius: 6
                    }
                ]
            },

            options: {

                responsive: true,

                maintainAspectRatio: false,

                plugins: {

                    legend: {
                        display: true,
                        position: "top"
                    },

                    tooltip: {

                        callbacks: {

                            label: function (context) {

                                return (
                                    "Collection Rate: " +
                                    Number(
                                        context.parsed.y || 0
                                    ).toFixed(2) +
                                    "%"
                                );
                            }
                        }
                    }
                },

                scales: {

                    x: {
                        grid: {
                            display: false
                        }
                    },

                    y: {

                        beginAtZero: true,

                        suggestedMax: 100,

                        ticks: {

                            callback: function (value) {

                                return value + "%";
                            }
                        }
                    }
                }
            }
        });
    }

});