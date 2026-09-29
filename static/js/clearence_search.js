/* =========================================================
   XORADEX EDUCORE ERP
   FINANCIAL CLEARANCE
   ---------------------------------------------------------
   RESPONSIBILITY:
   - Live student search
   - Search by student name
   - Search by admission number
   ========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    const searchInput = document.getElementById("clearanceSearch");
    const table = document.getElementById("clearanceTable");

    if (!searchInput || !table) {
        return;
    }

    const tableBody = table.querySelector("tbody");

    if (!tableBody) {
        return;
    }

    const rows = Array.from(
        tableBody.querySelectorAll("tr")
    );

    searchInput.addEventListener("input", function () {

        const searchTerm = this.value
            .trim()
            .toLowerCase();

        rows.forEach(function (row) {

            /*
             * Empty / placeholder rows should not interfere
             * with the search.
             */
            if (
                row.querySelector(
                    ".clearance-empty-row"
                )
            ) {
                return;
            }

            const studentName = (
                row.dataset.studentName || ""
            ).toLowerCase();

            const admissionNo = (
                row.dataset.admissionNo || ""
            ).toLowerCase();

            /*
             * Fallback: search the complete row text if
             * data attributes are not present.
             */
            const rowText = row.textContent
                .trim()
                .toLowerCase();

            const matches =
                searchTerm === "" ||
                studentName.includes(searchTerm) ||
                admissionNo.includes(searchTerm) ||
                rowText.includes(searchTerm);

            row.style.display = matches
                ? ""
                : "none";
        });

    });

});