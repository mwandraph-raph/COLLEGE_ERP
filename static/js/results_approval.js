document.addEventListener("DOMContentLoaded", function () {

    console.log("Results Approval JS loaded");


    /* =========================================================
       SEARCH ELEMENTS
       ========================================================= */

    const searchInput =
        document.getElementById("resultsSearch");

    const yearFilter =
        document.getElementById("resultsYearFilter");

    const semesterFilter =
        document.getElementById("resultsSemesterFilter");

    const statusFilter =
        document.getElementById("resultsStatusFilter");

    const filterButton =
        document.getElementById("resultsFilterBtn");

    const clearButton =
        document.getElementById("resultsClearBtn");

    const noResults =
        document.getElementById("resultsNoFilterResults");


    const resultRows =
        document.querySelectorAll(".results-approval-row");


    /* =========================================================
       FILTER FUNCTION
       ========================================================= */

    function filterResults() {

        const searchValue =
            searchInput
                ? searchInput.value
                    .trim()
                    .toLowerCase()
                : "";


        const selectedYear =
            yearFilter
                ? yearFilter.value
                    .trim()
                    .toLowerCase()
                : "";


        const selectedSemester =
            semesterFilter
                ? semesterFilter.value
                    .trim()
                    .toLowerCase()
                : "";


        const selectedStatus =
            statusFilter
                ? statusFilter.value
                    .trim()
                    .toLowerCase()
                : "";


        let visibleCount = 0;


        resultRows.forEach(function (row) {


            /* =================================================
               SEARCH TEXT
               ================================================= */

            const searchText =
                (
                    row.getAttribute("data-search") || ""
                )
                .replace(/\s+/g, " ")
                .trim()
                .toLowerCase();


            /* =================================================
               YEAR
               ================================================= */

            const rowYear =
                (
                    row.getAttribute("data-year") || ""
                )
                .trim()
                .toLowerCase();


            /* =================================================
               SEMESTER
               ================================================= */

            const rowSemester =
                (
                    row.getAttribute("data-semester") || ""
                )
                .trim()
                .toLowerCase();


            /* =================================================
               STATUS
               ================================================= */

            const rowStatus =
                (
                    row.getAttribute("data-status") || ""
                )
                .trim()
                .toLowerCase();


            /* =================================================
               SEARCH MATCH
               ================================================= */

            const searchMatches =
                searchValue === "" ||
                searchText.includes(searchValue);


            /* =================================================
               YEAR MATCH
               ================================================= */

            const yearMatches =
                selectedYear === "" ||
                rowYear === selectedYear;


            /* =================================================
               SEMESTER MATCH
               ================================================= */

            let semesterMatches = true;


            if (selectedSemester !== "") {

                semesterMatches =
                    rowSemester.includes(
                        selectedSemester
                    );

            }


            /* =================================================
               STATUS MATCH
               ================================================= */

            const statusMatches =
                selectedStatus === "" ||
                rowStatus === selectedStatus;


            /* =================================================
               FINAL MATCH
               ================================================= */

            const matches =
                searchMatches &&
                yearMatches &&
                semesterMatches &&
                statusMatches;


            /* =================================================
               SHOW / HIDE
               ================================================= */

            if (matches) {

                row.style.display = "";

                visibleCount++;

            } else {

                row.style.display = "none";

            }

        });


        /* =====================================================
           NO RESULTS MESSAGE
           ===================================================== */

        if (noResults) {

            if (visibleCount === 0) {

                noResults.classList.remove("d-none");

            } else {

                noResults.classList.add("d-none");

            }

        }


        console.log(
            "Results filter applied:",
            {
                search: searchValue,
                year: selectedYear,
                semester: selectedSemester,
                status: selectedStatus,
                visible: visibleCount
            }
        );

    }


    /* =========================================================
       FILTER BUTTON
       ========================================================= */

    if (filterButton) {

        filterButton.addEventListener(
            "click",
            function (event) {

                event.preventDefault();

                filterResults();

            }
        );

    }


    /* =========================================================
       CLEAR BUTTON
       ========================================================= */

    if (clearButton) {

        clearButton.addEventListener(
            "click",
            function (event) {

                event.preventDefault();


                /* CLEAR SEARCH */

                if (searchInput) {

                    searchInput.value = "";

                }


                /* CLEAR YEAR */

                if (yearFilter) {

                    yearFilter.value = "";

                }


                /* CLEAR SEMESTER */

                if (semesterFilter) {

                    semesterFilter.value = "";

                }


                /* CLEAR STATUS */

                if (statusFilter) {

                    statusFilter.value = "";

                }


                /* SHOW ALL */

                resultRows.forEach(function (row) {

                    row.style.display = "";

                });


                /* HIDE NO RESULTS */

                if (noResults) {

                    noResults.classList.add(
                        "d-none"
                    );

                }


                console.log(
                    "Results filters cleared"
                );


                /* RETURN CURSOR TO SEARCH */

                if (searchInput) {

                    searchInput.focus();

                }

            }
        );

    }


    /* =========================================================
       ENTER KEY SEARCH
       ========================================================= */

    if (searchInput) {

        searchInput.addEventListener(
            "keydown",
            function (event) {

                if (event.key === "Enter") {

                    event.preventDefault();

                    filterResults();

                }

            }
        );

    }

});