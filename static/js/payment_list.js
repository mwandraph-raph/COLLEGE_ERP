document.addEventListener("DOMContentLoaded", function () {

    /*
     * =========================================================
     * PAYMENT HISTORY TOGGLE
     * =========================================================
     */

    const buttons = document.querySelectorAll(
        ".payment-history-toggle"
    );

    buttons.forEach(function (button) {

        button.addEventListener("click", function () {

            const targetId = button.getAttribute(
                "data-target"
            );

            const target = document.getElementById(
                targetId
            );

            if (!target) {
                return;
            }

            const icon = button.querySelector("i");

            const text = button.querySelector(
                ".payment-toggle-text"
            );

            const isHidden =
                target.classList.contains("d-none");


            if (isHidden) {

                target.classList.remove("d-none");

                button.setAttribute(
                    "aria-expanded",
                    "true"
                );

                if (text) {
                    text.textContent =
                        "Hide Payments";
                }

                if (icon) {

                    icon.classList.remove(
                        "fa-eye"
                    );

                    icon.classList.add(
                        "fa-eye-slash"
                    );

                }

            } else {

                target.classList.add("d-none");

                button.setAttribute(
                    "aria-expanded",
                    "false"
                );

                if (text) {
                    text.textContent =
                        "View Payments";
                }

                if (icon) {

                    icon.classList.remove(
                        "fa-eye-slash"
                    );

                    icon.classList.add(
                        "fa-eye"
                    );

                }

            }

        });

    });


    /*
     * =========================================================
     * LIVE STUDENT PAYMENT SEARCH
     * =========================================================
     */

    const searchInput = document.getElementById(
        "paymentSearch"
    );

    const paymentRegister = document.getElementById(
        "paymentRegister"
    );

    const noResults = document.getElementById(
        "paymentNoResults"
    );


    if (searchInput && paymentRegister) {

        const studentGroups = Array.from(
            paymentRegister.querySelectorAll(
                ".payment-student-group"
            )
        );


        searchInput.addEventListener(
            "input",
            function () {

                const searchTerm =
                    searchInput.value
                        .trim()
                        .toLowerCase();

                let visibleStudents = 0;


                studentGroups.forEach(function (group) {

                    const studentName =
                        (
                            group.dataset.studentName || ""
                        ).toLowerCase();

                    const admissionNo =
                        (
                            group.dataset.admissionNo || ""
                        ).toLowerCase();

                    const groupText =
                        (
                            group.textContent || ""
                        ).toLowerCase();


                    /*
                     * Search student name,
                     * admission number,
                     * payment number,
                     * invoice,
                     * payment method,
                     * reference,
                     * etc.
                     */

                    const matches =
                        searchTerm === "" ||
                        studentName.includes(searchTerm) ||
                        admissionNo.includes(searchTerm) ||
                        groupText.includes(searchTerm);


                    if (matches) {

                        group.classList.remove(
                            "d-none"
                        );

                        visibleStudents++;

                    } else {

                        group.classList.add(
                            "d-none"
                        );


                        /*
                         * Close payment history when
                         * the student is hidden.
                         */

                        const history =
                            group.querySelector(
                                ".payment-history"
                            );

                        const button =
                            group.querySelector(
                                ".payment-history-toggle"
                            );

                        const text =
                            group.querySelector(
                                ".payment-toggle-text"
                            );

                        const icon =
                            button
                                ? button.querySelector("i")
                                : null;


                        if (history) {

                            history.classList.add(
                                "d-none"
                            );

                        }


                        if (button) {

                            button.setAttribute(
                                "aria-expanded",
                                "false"
                            );

                        }


                        if (text) {

                            text.textContent =
                                "View Payments";

                        }


                        if (icon) {

                            icon.classList.remove(
                                "fa-eye-slash"
                            );

                            icon.classList.add(
                                "fa-eye"
                            );

                        }

                    }

                });


                /*
                 * Show / hide "No students match"
                 */

                if (noResults) {

                    if (
                        searchTerm !== "" &&
                        visibleStudents === 0
                    ) {

                        noResults.classList.remove(
                            "d-none"
                        );

                    } else {

                        noResults.classList.add(
                            "d-none"
                        );

                    }

                }

            }
        );

    }


    /*
     * =========================================================
     * LIVE FEE STATEMENT SEARCH
     * =========================================================
     */

    const statementSearch = document.getElementById(
        "statementSearch"
    );

    const statementTable = document.getElementById(
        "statementTable"
    );

    const statementNoResults = document.getElementById(
        "statementNoResults"
    );


    if (statementSearch && statementTable) {

        const statementRows = Array.from(
            statementTable.querySelectorAll(
                "tbody .statement-row"
            )
        );


        statementSearch.addEventListener(
            "input",
            function () {

                const searchTerm =
                    statementSearch.value
                        .trim()
                        .toLowerCase();

                let visibleRows = 0;


                statementRows.forEach(function (row) {

                    const studentNameElement =
                        row.querySelector(
                            ".student-name"
                        );

                    const admissionNoElement =
                        row.querySelector(
                            ".admission-no"
                        );


                    const studentName =
                        studentNameElement
                            ? studentNameElement.textContent
                                .trim()
                                .toLowerCase()
                            : "";


                    const admissionNo =
                        admissionNoElement
                            ? admissionNoElement.textContent
                                .trim()
                                .toLowerCase()
                            : "";


                    const matches =
                        searchTerm === "" ||
                        studentName.includes(searchTerm) ||
                        admissionNo.includes(searchTerm);


                    if (matches) {

                        row.style.display = "";

                        visibleRows++;

                    } else {

                        row.style.display = "none";

                    }

                });


                /*
                 * Show / hide "No students match"
                 */

                if (statementNoResults) {

                    if (
                        searchTerm !== "" &&
                        visibleRows === 0
                    ) {

                        statementNoResults.style.display =
                            "";

                    } else {

                        statementNoResults.style.display =
                            "none";

                    }

                }

            }
        );

    }

});