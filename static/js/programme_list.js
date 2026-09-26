document.addEventListener("DOMContentLoaded", function () {

    console.log("Programme filter JS loaded");


    /* =========================================================
       ELEMENTS
       ========================================================= */

    const searchInput =
        document.getElementById("programmeSearch");

    const courseFilter =
        document.getElementById("programmeCourseFilter");

    const awardFilter =
        document.getElementById("programmeAwardFilter");

    const statusFilter =
        document.getElementById("programmeStatusFilter");

    const filterButton =
        document.getElementById("programmeFilterBtn");

    const clearButton =
        document.getElementById("programmeClearBtn");

    const noResults =
        document.getElementById("programmeNoFilterResults");

    const programmeRows =
        document.querySelectorAll(".programme-row");


    /* =========================================================
       FILTER PROGRAMMES
       ========================================================= */

    function filterProgrammes() {

        const searchValue =
            searchInput
                ? searchInput.value.trim().toLowerCase()
                : "";


        const selectedCourse =
            courseFilter
                ? courseFilter.value.trim().toLowerCase()
                : "";


        const selectedAward =
            awardFilter
                ? awardFilter.value.trim().toLowerCase()
                : "";


        const selectedStatus =
            statusFilter
                ? statusFilter.value.trim().toLowerCase()
                : "";


        let visibleCount = 0;


        programmeRows.forEach(function (row) {

            const searchText =
                (
                    row.getAttribute("data-search") || ""
                )
                .replace(/\s+/g, " ")
                .trim()
                .toLowerCase();


            const rowCourse =
                (
                    row.getAttribute("data-course") || ""
                )
                .trim()
                .toLowerCase();


            const rowAward =
                (
                    row.getAttribute("data-award") || ""
                )
                .trim()
                .toLowerCase();


            const rowStatus =
                (
                    row.getAttribute("data-status") || ""
                )
                .trim()
                .toLowerCase();


            const searchMatches =
                searchValue === "" ||
                searchText.includes(searchValue);


            const courseMatches =
                selectedCourse === "" ||
                rowCourse === selectedCourse;


            const awardMatches =
                selectedAward === "" ||
                rowAward === selectedAward;


            const statusMatches =
                selectedStatus === "" ||
                rowStatus === selectedStatus;


            const matches =
                searchMatches &&
                courseMatches &&
                awardMatches &&
                statusMatches;


            if (matches) {

                row.style.display = "";

                visibleCount++;

            } else {

                row.style.display = "none";

            }

        });


        if (noResults) {

            if (visibleCount === 0) {

                noResults.classList.remove("d-none");

            } else {

                noResults.classList.add("d-none");

            }

        }

    }


    /* =========================================================
       FILTER BUTTON
       ========================================================= */

    if (filterButton) {

        filterButton.addEventListener(
            "click",
            function () {

                filterProgrammes();

            }
        );

    }


    /* =========================================================
       CLEAR BUTTON
       ========================================================= */

    if (clearButton) {

        clearButton.addEventListener(
            "click",
            function () {

                if (searchInput) {
                    searchInput.value = "";
                }

                if (courseFilter) {
                    courseFilter.value = "";
                }

                if (awardFilter) {
                    awardFilter.value = "";
                }

                if (statusFilter) {
                    statusFilter.value = "";
                }


                programmeRows.forEach(function (row) {

                    row.style.display = "";

                });


                if (noResults) {
                    noResults.classList.add("d-none");
                }


                if (searchInput) {
                    searchInput.focus();
                }

            }
        );

    }


    /* =========================================================
       ENTER KEY
       ========================================================= */

    if (searchInput) {

        searchInput.addEventListener(
            "keydown",
            function (event) {

                if (event.key === "Enter") {

                    event.preventDefault();

                    filterProgrammes();

                }

            }
        );

    }

});