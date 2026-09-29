/* =========================================================
   XORADEX EDUCORE ERP
   STUDENT INVOICES
   ---------------------------------------------------------
   RESPONSIBILITY:
   - Student invoice search
   - Search by student name
   - Search by admission number
   ========================================================= */


document.addEventListener("DOMContentLoaded", function () {

    const searchInput = document.getElementById("studentSearch");
    const rows = document.querySelectorAll(".student-row");
    const noResults = document.getElementById("noSearchResults");


    /* =====================================================
       SAFETY CHECK
       ===================================================== */

    if (!searchInput) {
        return;
    }


    /* =====================================================
       STUDENT SEARCH
       ===================================================== */

    searchInput.addEventListener("input", function () {

        const searchTerm = this.value
            .toLowerCase()
            .trim();

        let visibleRows = 0;


        rows.forEach(function (row) {

            const studentNameElement =
                row.querySelector(".student-name");

            const admissionNoElement =
                row.querySelector(".admission-no");


            const studentName =
                studentNameElement
                    ? studentNameElement.textContent.toLowerCase()
                    : "";

            const admissionNo =
                admissionNoElement
                    ? admissionNoElement.textContent.toLowerCase()
                    : "";


            const matches =
                studentName.includes(searchTerm) ||
                admissionNo.includes(searchTerm);


            if (matches) {

                row.style.display = "";

                visibleRows++;

            } else {

                row.style.display = "none";

            }

        });


        /* =================================================
           NO SEARCH RESULTS
           ================================================= */

        if (noResults) {

            if (searchTerm !== "" && visibleRows === 0) {

                noResults.style.display = "";

            } else {

                noResults.style.display = "none";

            }

        }

    });

});