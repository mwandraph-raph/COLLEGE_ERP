document.addEventListener("DOMContentLoaded", function () {

    console.log("Lecturer Assignments JS loaded");


    /* =========================================================
       LECTURER SEARCH
       ========================================================= */

    const searchInput =
        document.getElementById("lecturerSearch");

    const searchButton =
        document.getElementById("lecturerSearchBtn");

    const clearSearchButton =
        document.getElementById("lecturerSearchClearBtn");

    const searchNoResults =
        document.getElementById("lecturerSearchNoResults");


    const lecturerRows =
        document.querySelectorAll(".lecturer-summary-row");


    function searchLecturers() {

        if (!searchInput) {
            return;
        }


        const searchValue =
            searchInput.value
                .trim()
                .toLowerCase();


        let visibleCount = 0;


        lecturerRows.forEach(function (row) {

            const lecturerName =
                (
                    row.getAttribute("data-lecturer-name") || ""
                )
                .trim()
                .toLowerCase();


            const lecturerUsername =
                (
                    row.getAttribute("data-lecturer-username") || ""
                )
                .trim()
                .toLowerCase();


            const matches =
                searchValue === "" ||
                lecturerName.includes(searchValue) ||
                lecturerUsername.includes(searchValue);


            const detailsRow =
                row.nextElementSibling;


            if (matches) {

                row.style.display = "";


                if (detailsRow) {
                    detailsRow.style.display = "";
                }


                visibleCount++;

            } else {

                row.style.display = "none";


                if (detailsRow) {

                    /*
                     * Hide the expanded details row as well
                     * when the lecturer does not match.
                     */

                    detailsRow.style.display = "none";

                }

            }

        });


        if (searchNoResults) {

            if (visibleCount === 0) {

                searchNoResults.classList.remove("d-none");

            } else {

                searchNoResults.classList.add("d-none");

            }

        }


        console.log(
            "Lecturer search:",
            searchValue,
            "Visible lecturers:",
            visibleCount
        );

    }


    /* =========================================================
       SEARCH BUTTON
       ========================================================= */

    if (searchButton) {

        searchButton.addEventListener(
            "click",
            function (event) {

                event.preventDefault();

                searchLecturers();

            }
        );

    }


    /* =========================================================
       CLEAR SEARCH BUTTON
       ========================================================= */

    if (clearSearchButton) {

        clearSearchButton.addEventListener(
            "click",
            function (event) {

                event.preventDefault();


                if (searchInput) {

                    searchInput.value = "";

                }


                searchLecturers();


                if (searchInput) {

                    searchInput.focus();

                }

            }
        );

    }


    /* =========================================================
       SEARCH USING ENTER KEY
       ========================================================= */

    if (searchInput) {

        searchInput.addEventListener(
            "keydown",
            function (event) {

                if (event.key === "Enter") {

                    event.preventDefault();

                    searchLecturers();

                }

            }
        );

    }


    /* =========================================================
       ASSIGNMENT FILTER BUTTONS
       ========================================================= */

    document
        .querySelectorAll(".assignment-filter-btn")
        .forEach(function (button) {


            button.addEventListener(
                "click",
                function (event) {

                    event.preventDefault();
                    event.stopPropagation();


                    const details =
                        button.closest(".lecturer-details");


                    if (!details) {

                        console.log(
                            "Lecturer details section not found"
                        );

                        return;

                    }


                    const yearSelect =
                        details.querySelector(
                            ".assignment-year-filter"
                        );


                    const semesterSelect =
                        details.querySelector(
                            ".assignment-semester-filter"
                        );


                    const selectedYear =
                        yearSelect
                            ? yearSelect.value.trim()
                            : "";


                    const selectedSemester =
                        semesterSelect
                            ? semesterSelect.value.trim()
                            : "";


                    const rows =
                        details.querySelectorAll(
                            ".assignment-row"
                        );


                    const noResults =
                        details.querySelector(
                            ".assignment-no-results"
                        );


                    let visibleCount = 0;


                    rows.forEach(function (row) {


                        const rowYear =
                            (
                                row.getAttribute(
                                    "data-year"
                                ) || ""
                            )
                            .trim();


                        const rowSemester =
                            (
                                row.getAttribute(
                                    "data-semester"
                                ) || ""
                            )
                            .trim();


                        /* =========================================
                           YEAR MATCH
                           ========================================= */

                        let yearMatches = true;


                        if (selectedYear !== "") {

                            yearMatches =
                                rowYear === selectedYear;

                        }


                        /* =========================================
                           SEMESTER MATCH
                           ========================================= */

                        let semesterMatches = true;


                        if (selectedSemester !== "") {


                            const normalizedRowSemester =
                                rowSemester
                                    .toLowerCase()
                                    .replace(/\s+/g, " ")
                                    .trim();


                            const normalizedSelectedSemester =
                                selectedSemester
                                    .toLowerCase()
                                    .replace(/\s+/g, " ")
                                    .trim();


                            semesterMatches =
                                normalizedRowSemester.includes(
                                    normalizedSelectedSemester
                                );

                        }


                        /* =========================================
                           SHOW / HIDE ROW
                           ========================================= */

                        if (
                            yearMatches &&
                            semesterMatches
                        ) {

                            row.style.display = "";

                            visibleCount++;

                        } else {

                            row.style.display = "none";

                        }

                    });


                    /* =============================================
                       NO RESULTS MESSAGE
                       ============================================= */

                    if (noResults) {

                        if (visibleCount === 0) {

                            noResults.classList.remove(
                                "d-none"
                            );

                        } else {

                            noResults.classList.add(
                                "d-none"
                            );

                        }

                    }


                    console.log(
                        "Lecturer filter applied:",
                        selectedYear,
                        selectedSemester,
                        "Visible:",
                        visibleCount
                    );

                }
            );

        });


    /* =========================================================
       ASSIGNMENT CLEAR BUTTONS
       ========================================================= */

    document
        .querySelectorAll(".assignment-clear-btn")
        .forEach(function (button) {


            button.addEventListener(
                "click",
                function (event) {

                    event.preventDefault();
                    event.stopPropagation();


                    const details =
                        button.closest(".lecturer-details");


                    if (!details) {

                        console.log(
                            "Lecturer details section not found"
                        );

                        return;

                    }


                    const yearSelect =
                        details.querySelector(
                            ".assignment-year-filter"
                        );


                    const semesterSelect =
                        details.querySelector(
                            ".assignment-semester-filter"
                        );


                    const rows =
                        details.querySelectorAll(
                            ".assignment-row"
                        );


                    const noResults =
                        details.querySelector(
                            ".assignment-no-results"
                        );


                    /* =========================================
                       RESET YEAR
                       ========================================= */

                    if (yearSelect) {

                        yearSelect.value = "";

                    }


                    /* =========================================
                       RESET SEMESTER
                       ========================================= */

                    if (semesterSelect) {

                        semesterSelect.value = "";

                    }


                    /* =========================================
                       SHOW ALL ASSIGNMENTS
                       ========================================= */

                    rows.forEach(function (row) {

                        row.style.display = "";

                    });


                    /* =========================================
                       HIDE NO RESULTS MESSAGE
                       ========================================= */

                    if (noResults) {

                        noResults.classList.add(
                            "d-none"
                        );

                    }


                    console.log(
                        "Lecturer filters cleared"
                    );

                }
            );

        });

});