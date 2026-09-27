document.addEventListener("DOMContentLoaded", function () {

    // ==========================================================
    // PRINCIPAL DASHBOARD
    // XORADEX EDUCORE
    // ==========================================================


    // ==========================================================
    // CHART.JS CHECK
    // ==========================================================

    if (typeof Chart === "undefined") {

        console.error("Chart.js is not loaded.");

        return;
    }


    // ==========================================================
    // SAFE CHART DATA READER
    // ==========================================================

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

            labels = JSON.parse(
                canvas.dataset.labels || "[]"
            );

            values = JSON.parse(
                canvas.dataset.values || "[]"
            );

        } catch (error) {

            console.error(
                "Unable to parse chart data:",
                error
            );

        }

        return {
            labels: labels,
            values: values
        };

    }


    // ==========================================================
    // 01. ADMISSIONS
    // ==========================================================

    const admissionsCanvas =
        document.getElementById(
            "principalAdmissionsChart"
        );

    if (admissionsCanvas) {

        const chartData =
            getChartData(admissionsCanvas);

        new Chart(
            admissionsCanvas,
            {

                type: "doughnut",

                data: {

                    labels:
                        chartData.labels,

                    datasets: [

                        {

                            data:
                                chartData.values,

                            borderWidth: 0

                        }

                    ]

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

            }
        );

    }


    // ==========================================================
    // 02. EXAMINATION WORKFLOW
    // ==========================================================

    const resultsCanvas =
        document.getElementById(
            "principalResultsChart"
        );

    if (resultsCanvas) {

        const chartData =
            getChartData(resultsCanvas);

        new Chart(
            resultsCanvas,
            {

                type: "bar",

                data: {

                    labels:
                        chartData.labels,

                    datasets: [

                        {

                            label:
                                "Result Batches",

                            data:
                                chartData.values,

                            borderRadius: 8,

                            borderWidth: 0

                        }

                    ]

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

            }
        );

    }


    // ==========================================================
    // 03. ENROLMENT BY PROGRAMME
    // ==========================================================

    const enrollmentCanvas =
        document.getElementById(
            "principalEnrollmentChart"
        );

    if (enrollmentCanvas) {

        const chartData =
            getChartData(enrollmentCanvas);

        new Chart(
            enrollmentCanvas,
            {

                type: "bar",

                data: {

                    labels:
                                chartData.labels,

                    datasets: [

                        {

                            label:
                                "Students",

                            data:
                                chartData.values,

                            borderRadius: 8,

                            borderWidth: 0

                        }

                    ]

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

                                label:
                                    function (context) {

                                        return (
                                            " Students: " +
                                            context.raw
                                        );

                                    }

                            }

                        }

                    }

                }

            }
        );

    }


    // ==========================================================
    // 04. EXAMINATION PERFORMANCE BY PROGRAMME
    // ==========================================================

    const examCanvas =
        document.getElementById(
            "principalExamChart"
        );

    if (examCanvas) {

        const chartData =
            getChartData(examCanvas);

        new Chart(
            examCanvas,
            {

                type: "bar",

                data: {

                    labels:
                        chartData.labels,

                    datasets: [

                        {

                            label:
                                "Pass Rate (%)",

                            data:
                                chartData.values,

                            borderRadius: 8,

                            borderWidth: 0

                        }

                    ]

                },

                options: {

                    responsive: true,

                    maintainAspectRatio: false,

                    scales: {

                        y: {

                            beginAtZero: true,

                            max: 100,

                            ticks: {

                                callback:
                                    function (value) {

                                        return (
                                            value +
                                            "%"
                                        );

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

                                label:
                                    function (context) {

                                        return (
                                            " Pass Rate: " +
                                            context.raw +
                                            "%"
                                        );

                                    }

                            }

                        }

                    }

                }

            }
        );

    }


    // ==========================================================
    // 05. FINANCE PERIOD FILTER
    // ==========================================================

    const academicYear =
        document.getElementById(
            "financeAcademicYear"
        );

    const semester =
        document.getElementById(
            "financeSemester"
        );


    if (
        academicYear &&
        semester
    ) {


        // ======================================================
        // CONVERT ANY SEMESTER NAME INTO A RELIABLE KEY
        //
        // Examples recognised:
        //
        // January-March
        // January - March
        // Jan-March
        // Jan - March
        // January–March
        // January — March
        // January to March
        //
        // ======================================================

        function getSemesterKey(name) {

            const value =
                String(name || "")
                    .trim()
                    .toLowerCase()
                    .replace(/[–—]/g, "-")
                    .replace(/\s+/g, " ");


            // Remove spaces for easier comparison
            const compact =
                value
                    .replace(/\s+/g, "")
                    .replace(/_/g, "")
                    .replace(/\./g, "");


            // --------------------------------------------------
            // JANUARY - MARCH
            // --------------------------------------------------

            if (
                (
                    compact.includes("january") ||
                    compact.includes("jan")
                ) &&
                compact.includes("march")
            ) {

                return "january-march";

            }


            // --------------------------------------------------
            // APRIL - JUNE
            // --------------------------------------------------

            if (
                compact.includes("april") &&
                compact.includes("june")
            ) {

                return "april-june";

            }


            // --------------------------------------------------
            // JULY - SEPTEMBER
            // --------------------------------------------------

            if (
                (
                    compact.includes("july") ||
                    compact.includes("jul")
                ) &&
                (
                    compact.includes("september") ||
                    compact.includes("sep")
                )
            ) {

                return "july-september";

            }


            // --------------------------------------------------
            // OCTOBER - DECEMBER
            // --------------------------------------------------

            if (
                (
                    compact.includes("october") ||
                    compact.includes("oct")
                ) &&
                (
                    compact.includes("december") ||
                    compact.includes("dec")
                )
            ) {

                return "october-december";

            }


            return "";

        }


        // ======================================================
        // STANDARD DISPLAY NAMES
        // ======================================================

        const semesterDefinitions = [

            {
                key: "january-march",
                name: "January - March"
            },

            {
                key: "april-june",
                name: "April - June"
            },

            {
                key: "july-september",
                name: "July - September"
            },

            {
                key: "october-december",
                name: "October - December"
            }

        ];


        // ======================================================
        // SAVE ALL ORIGINAL DATABASE SEMESTERS
        // ======================================================

        const semesterDatabase = {};


        Array.from(
            semester.options
        ).forEach(
            function (option) {

                const yearId =
                    String(
                        option.dataset.academicYearId || ""
                    ).trim();


                const semesterId =
                    String(
                        option.value || ""
                    ).trim();


                const rawName =
                    option.dataset.semesterName ||
                    option.textContent ||
                    "";


                const semesterKey =
                    getSemesterKey(rawName);


                console.log(
                    "Finance semester detected:",
                    {
                        yearId: yearId,
                        semesterId: semesterId,
                        rawName: rawName,
                        semesterKey: semesterKey
                    }
                );


                if (
                    !yearId ||
                    !semesterId ||
                    !semesterKey
                ) {

                    return;

                }


                if (
                    !semesterDatabase[yearId]
                ) {

                    semesterDatabase[yearId] = {};

                }


                semesterDatabase[yearId][
                    semesterKey
                ] =
                    semesterId;

            }
        );


        // ======================================================
        // DEBUG DATABASE
        // ======================================================

        console.log(
            "Finance semester database:",
            semesterDatabase
        );


        // ======================================================
        // BUILD FINANCE SEMESTERS
        // ======================================================

        function updateFinanceSemesters() {

            const selectedYearId =
                String(
                    academicYear.value || ""
                ).trim();


            console.log(
                "Selected finance academic year:",
                selectedYearId
            );


            const yearSemesters =
                semesterDatabase[
                    selectedYearId
                ] || {};


            console.log(
                "Semesters for selected year:",
                yearSemesters
            );


            // --------------------------------------------------
            // REMEMBER CURRENT VALUE
            // --------------------------------------------------

            const currentSemesterId =
                String(
                    semester.value || ""
                ).trim();


            // --------------------------------------------------
            // CLEAR DROPDOWN
            // --------------------------------------------------

            semester.innerHTML = "";


            // --------------------------------------------------
            // CREATE FOUR STANDARD OPTIONS
            // --------------------------------------------------

            semesterDefinitions.forEach(
                function (definition) {

                    const option =
                        document.createElement(
                            "option"
                        );


                    const semesterId =
                        String(
                            yearSemesters[
                                definition.key
                            ] || ""
                        ).trim();


                    option.value =
                        semesterId;


                    option.textContent =
                        definition.name;


                    option.dataset.academicYearId =
                        selectedYearId;


                    option.dataset.semesterName =
                        definition.name;


                    option.dataset.semesterKey =
                        definition.key;


                    semester.appendChild(
                        option
                    );


                    console.log(
                        "Created finance option:",
                        {
                            name:
                                definition.name,

                            key:
                                definition.key,

                            id:
                                semesterId
                        }
                    );

                }
            );


            // ==================================================
            // SELECT PREVIOUS VALUE IF IT STILL EXISTS
            // ==================================================

            let selectedOption = null;


            if (currentSemesterId) {

                selectedOption =
                    Array.from(
                        semester.options
                    ).find(
                        function (option) {

                            return (
                                option.value ===
                                currentSemesterId
                            );

                        }
                    );

            }


            // ==================================================
            // OTHERWISE SELECT FIRST VALID DATABASE RECORD
            // ==================================================

            if (!selectedOption) {

                selectedOption =
                    Array.from(
                        semester.options
                    ).find(
                        function (option) {

                            return (
                                option.value &&
                                option.value.trim() !== ""
                            );

                        }
                    );

            }


            // ==================================================
            // SELECT VALID OPTION
            // ==================================================

            if (selectedOption) {

                semester.value =
                    selectedOption.value;

                selectedOption.selected =
                    true;

                console.log(
                    "Finance semester selected:",
                    {
                        name:
                            selectedOption.textContent,

                        id:
                            selectedOption.value
                    }
                );

            } else {

                // ==============================================
                // NO DATABASE SEMESTER FOUND
                // ==============================================

                console.error(
                    "No valid semester records found for academic year:",
                    selectedYearId
                );


                semester.innerHTML = "";


                const emptyOption =
                    document.createElement(
                        "option"
                    );


                emptyOption.value = "";


                emptyOption.textContent =
                    "No semesters available";


                emptyOption.selected =
                    true;


                semester.appendChild(
                    emptyOption
                );

            }

        }


        // ======================================================
        // ACADEMIC YEAR CHANGE
        // ======================================================

        academicYear.addEventListener(
            "change",
            function () {

                updateFinanceSemesters();

            }
        );


        // ======================================================
        // INITIALISE
        // ======================================================

        updateFinanceSemesters();

    }


    // ==========================================================
    // 05B. PRINCIPAL ACADEMIC YEAR / SEMESTER FILTER
    // ==========================================================

    function initializePrincipalSemesterFilter() {

        const principalAcademicYear =
            document.getElementById(
                "principalAcademicYear"
            );

        const principalSemester =
            document.getElementById(
                "principalSemester"
            );

        if (
            !principalAcademicYear ||
            !principalSemester
        ) {
            return;
        }

        // ------------------------------------------------------
        // READ CURRENT SEMESTER OPTIONS
        // ------------------------------------------------------

        const principalSemesterOptions =
            Array.from(
                principalSemester.options
            ).map(function (option) {

                return {
                    value:
                        option.value,

                    text:
                        option.textContent.trim(),

                    year:
                        option.dataset.year,

                    semesterName:
                        option.dataset.semesterName
                };

            });


        // ------------------------------------------------------
        // FILTER SEMESTERS FOR SELECTED YEAR
        // ------------------------------------------------------

        function filterPrincipalSemesters() {

            const selectedYear =
                String(
                    principalAcademicYear.value
                );


            const currentSemester =
                String(
                    principalSemester.value
                );


            principalSemester.innerHTML = "";


            principalSemesterOptions.forEach(
                function (item) {

                    if (
                        String(item.year) !==
                        selectedYear
                    ) {
                        return;
                    }


                    const option =
                        document.createElement(
                            "option"
                        );


                    option.value =
                        item.value;

                    option.textContent =
                        item.text;

                    option.dataset.year =
                        item.year;

                    option.dataset.semesterName =
                        item.semesterName;


                    principalSemester.appendChild(
                        option
                    );

                }
            );


            // --------------------------------------------------
            // RESTORE PREVIOUS SEMESTER IF STILL AVAILABLE
            // --------------------------------------------------

            const stillExists =
                Array.from(
                    principalSemester.options
                ).some(
                    function (option) {

                        return (
                            option.value ===
                            currentSemester
                        );

                    }
                );


            if (stillExists) {

                principalSemester.value =
                    currentSemester;

            } else if (
                principalSemester.options.length
            ) {

                principalSemester.selectedIndex =
                    0;

            }

        }


        // ------------------------------------------------------
        // ACADEMIC YEAR CHANGE
        // ------------------------------------------------------

        principalAcademicYear.addEventListener(
            "change",
            function () {

                filterPrincipalSemesters();

            }
        );


        // ------------------------------------------------------
        // INITIAL FILTER
        // ------------------------------------------------------

        filterPrincipalSemesters();

    }


    // ----------------------------------------------------------
    // INITIALIZE ON PAGE LOAD
    // ----------------------------------------------------------

    initializePrincipalSemesterFilter();

        // ==========================================================
    // 06. FINANCE PERIOD ANALYSIS - NO PAGE REFRESH
    // ==========================================================

    const financePeriodForm =
        document.getElementById(
            "financePeriodForm"
        );

    const financeAnalyseBtn =
        document.getElementById(
            "financeAnalyseBtn"
        );

    if (
        financePeriodForm &&
        financeAnalyseBtn
    ) {

        financeAnalyseBtn.addEventListener(
            "click",
            async function (event) {

                event.preventDefault();

                const academicYear =
                    document.getElementById(
                        "financeAcademicYear"
                    );

                const semester =
                    document.getElementById(
                        "financeSemester"
                    );

                if (
                    !academicYear ||
                    !semester
                ) {
                    return;
                }

                if (
                    !academicYear.value ||
                    !semester.value
                ) {
                    financePeriodForm.reportValidity();
                    return;
                }

                // --------------------------------------------------
                // SAVE CURRENT SCROLL POSITION
                // --------------------------------------------------

                const currentScrollPosition =
                    window.scrollY;

                // --------------------------------------------------
                // SAVE BUTTON CONTENT
                // --------------------------------------------------

                const originalButtonContent =
                    financeAnalyseBtn.innerHTML;

                financeAnalyseBtn.disabled = true;

                financeAnalyseBtn.innerHTML =
                    '<i class="fa-solid fa-spinner fa-spin"></i>' +
                    '<span>Analysing...</span>';

                try {

                    // ------------------------------------------------
                    // BUILD EXACT SAME GET PARAMETERS
                    // ------------------------------------------------

                    const formData =
                        new FormData(
                            financePeriodForm
                        );

                    const params =
                        new URLSearchParams(
                            formData
                        );

                    const action =
                        financePeriodForm.getAttribute(
                            "action"
                        ) ||
                        window.location.pathname;

                    const requestUrl =
                        action +
                        "?" +
                        params.toString();

                    console.log(
                        "Finance analysis request:",
                        requestUrl
                    );

                    // ------------------------------------------------
                    // REQUEST UPDATED DJANGO PAGE
                    // WITHOUT NAVIGATING TO IT
                    // ------------------------------------------------

                    const response =
                        await fetch(
                            requestUrl,
                            {
                                method: "GET",
                                headers: {
                                    "X-Requested-With":
                                        "XMLHttpRequest"
                                }
                            }
                        );

                    if (!response.ok) {
                        throw new Error(
                            "Finance analysis request failed: " +
                            response.status
                        );
                    }

                    const html =
                        await response.text();

                    // ------------------------------------------------
                    // PARSE DJANGO RESPONSE
                    // ------------------------------------------------

                    const parser =
                        new DOMParser();

                    const newDocument =
                        parser.parseFromString(
                            html,
                            "text/html"
                        );

                    // ------------------------------------------------
                    // UPDATE KPI GRID
                    // ------------------------------------------------

                    const currentKpis =
                        document.querySelector(
                            ".finance-period-kpis"
                        );

                    const newKpis =
                        newDocument.querySelector(
                            ".finance-period-kpis"
                        );

                    if (
                        currentKpis &&
                        newKpis
                    ) {

                        currentKpis.replaceWith(
                            newKpis
                        );
                    }

                    // ------------------------------------------------
                    // UPDATE SECONDARY SUMMARY
                    // ------------------------------------------------

                    const currentSummary =
                        document.querySelector(
                            ".finance-period-summary"
                        );

                    const newSummary =
                        newDocument.querySelector(
                            ".finance-period-summary"
                        );

                    if (
                        currentSummary &&
                        newSummary
                    ) {

                        currentSummary.replaceWith(
                            newSummary
                        );
                    }

                    // ------------------------------------------------
                    // UPDATE BILLING VS COLLECTION CHART
                    // ------------------------------------------------

                    const currentCollectionCanvas =
                        document.getElementById(
                            "financePeriodCollectionChart"
                        );

                    const newCollectionCanvas =
                        newDocument.getElementById(
                            "financePeriodCollectionChart"
                        );

                    if (
                        currentCollectionCanvas &&
                        newCollectionCanvas
                    ) {

                        /*
                         * Destroy existing Chart.js instance
                         * before replacing the canvas.
                         */

                        const existingChart =
                            Chart.getChart(
                                currentCollectionCanvas
                            );

                        if (existingChart) {
                            existingChart.destroy();
                        }

                        const replacement =
                            newCollectionCanvas.cloneNode(
                                true
                            );

                        currentCollectionCanvas.replaceWith(
                            replacement
                        );
                    }

                    // ------------------------------------------------
                    // UPDATE COLLECTION RATE CHART
                    // ------------------------------------------------

                    const currentRateCanvas =
                        document.getElementById(
                            "financePeriodRateChart"
                        );

                    const newRateCanvas =
                        newDocument.getElementById(
                            "financePeriodRateChart"
                        );

                    if (
                        currentRateCanvas &&
                        newRateCanvas
                    ) {

                        /*
                         * Destroy existing Chart.js instance
                         * before replacing the canvas.
                         */

                        const existingChart =
                            Chart.getChart(
                                currentRateCanvas
                            );

                        if (existingChart) {
                            existingChart.destroy();
                        }

                        const replacement =
                            newRateCanvas.cloneNode(
                                true
                            );

                        currentRateCanvas.replaceWith(
                            replacement
                        );
                    }

                    // ------------------------------------------------
                    // UPDATE URL WITHOUT PAGE RELOAD
                    // ------------------------------------------------

                    window.history.replaceState(
                        {},
                        "",
                        requestUrl
                    );

                    // ------------------------------------------------
                    // RESTORE SCROLL POSITION
                    // ------------------------------------------------

                    window.scrollTo(
                        0,
                        currentScrollPosition
                    );

                    // ------------------------------------------------
                    // REBUILD BILLING VS COLLECTION CHART
                    // ------------------------------------------------

                    const collectionCanvas =
                        document.getElementById(
                            "financePeriodCollectionChart"
                        );

                    if (collectionCanvas) {

                        const labels =
                            JSON.parse(
                                collectionCanvas.dataset.labels ||
                                "[]"
                            );

                        const billed =
                            JSON.parse(
                                collectionCanvas.dataset.billed ||
                                "[]"
                            );

                        const collected =
                            JSON.parse(
                                collectionCanvas.dataset.collected ||
                                "[]"
                            );

                        new Chart(
                            collectionCanvas,
                            {
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
                                                label:
                                                    function (context) {

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
                                                callback:
                                                    function (value) {

                                                        return (
                                                            "KSh " +
                                                            Number(
                                                                value
                                                            ).toLocaleString(
                                                                "en-KE"
                                                            )
                                                        );
                                                    }
                                            }
                                        }
                                    }
                                }
                            }
                        );
                    }

                    // ------------------------------------------------
                    // REBUILD COLLECTION RATE CHART
                    // ------------------------------------------------

                    const rateCanvas =
                        document.getElementById(
                            "financePeriodRateChart"
                        );

                    if (rateCanvas) {

                        const labels =
                            JSON.parse(
                                rateCanvas.dataset.labels ||
                                "[]"
                            );

                        const rates =
                            JSON.parse(
                                rateCanvas.dataset.values ||
                                "[]"
                            );

                        new Chart(
                            rateCanvas,
                            {
                                type: "line",

                                data: {
                                    labels: labels,

                                    datasets: [
                                        {
                                            label:
                                                "Collection Rate",

                                            data:
                                                rates,

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
                                                label:
                                                    function (context) {

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
                                                callback:
                                                    function (value) {

                                                        return (
                                                            value +
                                                            "%"
                                                        );
                                                    }
                                            }
                                        }
                                    }
                                }
                            }
                        );
                    }

                    // ------------------------------------------------
                    // RESTORE SCROLL AGAIN AFTER CHART RENDERING
                    // ------------------------------------------------

                    requestAnimationFrame(
                        function () {

                            window.scrollTo(
                                0,
                                currentScrollPosition
                            );
                        }
                    );

                } catch (error) {

                    console.error(
                        "Finance period analysis failed:",
                        error
                    );

                } finally {

                    financeAnalyseBtn.disabled = false;

                    financeAnalyseBtn.innerHTML =
                        originalButtonContent;
                }
            }
        );
    }


    // ==========================================================
    // 06B. SEMESTER PERFORMANCE ANALYSIS - NO PAGE REFRESH
    // ==========================================================

    async function analysePrincipalPeriod(event) {

        event.preventDefault();

        const principalPeriodForm =
            document.getElementById(
                "principalPeriodForm"
            );

        const principalAnalyseBtn =
            document.getElementById(
                "principalAnalyseBtn"
            );

        const academicYear =
            document.getElementById(
                "principalAcademicYear"
            );

        const semester =
            document.getElementById(
                "principalSemester"
            );

        if (
            !principalPeriodForm ||
            !principalAnalyseBtn ||
            !academicYear ||
            !semester
        ) {
            return;
        }

        if (
            !academicYear.value ||
            !semester.value
        ) {
            principalPeriodForm.reportValidity();
            return;
        }

        // ----------------------------------------------------------
        // SAVE CURRENT SCROLL POSITION
        // ----------------------------------------------------------

        const currentScrollPosition =
            window.scrollY;


        // ----------------------------------------------------------
        // SAVE BUTTON CONTENT
        // ----------------------------------------------------------

        const originalButtonContent =
            principalAnalyseBtn.innerHTML;

        principalAnalyseBtn.disabled = true;

        principalAnalyseBtn.innerHTML =
            '<i class="fa-solid fa-spinner fa-spin"></i>' +
            '<span>Analysing...</span>';


        try {

            // ------------------------------------------------------
            // BUILD SAME GET PARAMETERS USED BY DJANGO
            // ------------------------------------------------------

            const formData =
                new FormData(
                    principalPeriodForm
                );

            const params =
                new URLSearchParams(
                    formData
                );


            // ------------------------------------------------------
            // REMOVE #semester-performance FROM ACTION
            // ------------------------------------------------------

            const action =
                principalPeriodForm.getAttribute(
                    "action"
                ) ||
                window.location.pathname;

            const cleanAction =
                action.split("#")[0];


            // ------------------------------------------------------
            // BUILD REQUEST URL
            // ------------------------------------------------------

            const requestUrl =
                cleanAction +
                (
                    cleanAction.includes("?")
                        ? "&"
                        : "?"
                ) +
                params.toString();


            console.log(
                "Semester performance analysis request:",
                requestUrl
            );


            // ------------------------------------------------------
            // FETCH UPDATED DJANGO PAGE
            // WITHOUT PAGE NAVIGATION
            // ------------------------------------------------------

            const response =
                await fetch(
                    requestUrl,
                    {
                        method: "GET",

                        headers: {
                            "X-Requested-With":
                                "XMLHttpRequest"
                        },

                        cache: "no-store"
                    }
                );


            if (!response.ok) {

                throw new Error(
                    "Semester performance request failed: " +
                    response.status
                );

            }


            // ------------------------------------------------------
            // READ RESPONSE
            // ------------------------------------------------------

            const html =
                await response.text();


            // ------------------------------------------------------
            // PARSE RETURNED HTML
            // ------------------------------------------------------

            const parser =
                new DOMParser();

            const newDocument =
                parser.parseFromString(
                    html,
                    "text/html"
                );


            // ------------------------------------------------------
            // GET CURRENT SEMESTER PERFORMANCE SECTION
            // ------------------------------------------------------

            const currentSection =
                document.getElementById(
                    "semester-performance"
                );


            // ------------------------------------------------------
            // GET UPDATED SEMESTER PERFORMANCE SECTION
            // ------------------------------------------------------

            const newSection =
                newDocument.getElementById(
                    "semester-performance"
                );


            if (
                !currentSection ||
                !newSection
            ) {

                throw new Error(
                    "Updated #semester-performance section was not found."
                );

            }


            // ------------------------------------------------------
            // REPLACE ONLY THIS SECTION
            // ------------------------------------------------------

            currentSection.replaceWith(
                newSection
            );

            // ------------------------------------------------------
            // REINITIALIZE PRINCIPAL SEMESTER FILTER
            // ------------------------------------------------------

            initializePrincipalSemesterFilter();

            // ------------------------------------------------------
            // UPDATE URL WITHOUT PAGE RELOAD
            // ------------------------------------------------------

            window.history.replaceState(
                {},
                "",
                requestUrl +
                "#semester-performance"
            );


            // ------------------------------------------------------
            // RESTORE SCROLL POSITION
            // ------------------------------------------------------

            requestAnimationFrame(
                function () {

                    window.scrollTo(
                        0,
                        currentScrollPosition
                    );

                }
            );


            console.log(
                "Semester performance updated successfully."
            );


        } catch (error) {

            console.error(
                "Semester performance analysis failed:",
                error
            );

            alert(
                "Unable to analyse the selected semester. Please try again."
            );


        } finally {

            // ------------------------------------------------------
            // RESTORE BUTTON
            // ------------------------------------------------------

            const currentButton =
                document.getElementById(
                    "principalAnalyseBtn"
                );

            if (currentButton) {

                currentButton.disabled = false;

                currentButton.innerHTML =
                    originalButtonContent;

            }

        }

    }


    // ==========================================================
    // SEMESTER PERFORMANCE BUTTON
    // EVENT DELEGATION
    // ==========================================================
    //
    // Event delegation is intentional.
    //
    // The entire #semester-performance section is replaced
    // after every successful analysis. Therefore the button
    // itself is recreated. Delegation ensures the new button
    // continues working on the next analysis.
    // ==========================================================

    document.addEventListener(
        "click",
        function (event) {

            const button =
                event.target.closest(
                    "#principalAnalyseBtn"
                );

            if (!button) {
                return;
            }

            analysePrincipalPeriod(
                event
            );

        }
    );


    // ==========================================================
    // PREVENT NORMAL SEMESTER FORM SUBMISSION
    // ==========================================================

    document.addEventListener(
        "submit",
        function (event) {

            const form =
                event.target.closest(
                    "#principalPeriodForm"
                );

            if (!form) {
                return;
            }

            event.preventDefault();

            const button =
                form.querySelector(
                    "#principalAnalyseBtn"
                );

            if (button) {

                button.click();

            }

        }
    );


    // ==========================================================
    // 07. BILLING VS COLLECTION
    // ==========================================================

    const collectionCanvas =
        document.getElementById(
            "financePeriodCollectionChart"
        );


    if (collectionCanvas) {

        const labels =
            JSON.parse(
                collectionCanvas.dataset.labels ||
                "[]"
            );


        const billed =
            JSON.parse(
                collectionCanvas.dataset.billed ||
                "[]"
            );


        const collected =
            JSON.parse(
                collectionCanvas.dataset.collected ||
                "[]"
            );


        new Chart(
            collectionCanvas,
            {

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

                                label:
                                    function (context) {

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

                                callback:
                                    function (value) {

                                        return (
                                            "KSh " +
                                            Number(
                                                value
                                            ).toLocaleString(
                                                "en-KE"
                                            )
                                        );

                                    }

                            }

                        }

                    }

                }

            }
        );

    }


    // ==========================================================
    // 08. COLLECTION RATE
    // ==========================================================

    const rateCanvas =
        document.getElementById(
            "financePeriodRateChart"
        );


    if (rateCanvas) {

        const labels =
            JSON.parse(
                rateCanvas.dataset.labels ||
                "[]"
            );


        const rates =
            JSON.parse(
                rateCanvas.dataset.values ||
                "[]"
            );


        new Chart(
            rateCanvas,
            {

                type: "line",

                data: {

                    labels: labels,

                    datasets: [

                        {

                            label:
                                "Collection Rate",

                            data:
                                rates,

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

                                label:
                                    function (context) {

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

                                callback:
                                    function (value) {

                                        return (
                                            value +
                                            "%"
                                        );

                                    }

                            }

                        }

                    }

                }

            }
        );

    }

});